import asyncio
import logger
import configuration
import youtube_dl
import discord
from discord.ext import commands
from async_timeout import timeout

ytdl = youtube_dl.YoutubeDL(configuration.ytdl_format_options)
youtube_dl.utils.bug_reports_message = lambda: '' # Suppress noise about console usage from errors

class AudioPlayer:
    __slots__ = ("client", "guild", "channel", "audio", "queue", "next", "looping", "volume", "sfx_volume", "timeout_value")
    def __init__(self, message):
        self.client = message.bot
        self.guild = message.guild
        self.channel = message.channel
        self.audio = self.client.get_cog("Audio")
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.looping = 0 #0: off, 1: song, 2: playlist
        self.volume = 0.1
        self.sfx_volume = configuration.SFX_VOLUME
        self.timeout_value = configuration.PLAYER_TIMEOUT_VALUE

        self.client.loop.create_task(self.player_loop())
        self.client.loop.create_task(self.connection_loop())
        logger.log_info("({} , gid: {}) Audioplayer created".format(self.guild.name, self.guild.id))

    # Player Loop ══════════════════════════════════════════════════════════════
    async def player_loop(self):
        await self.client.wait_until_ready()
        while self.guild.voice_client.is_connected():
            self.next.clear()

            audio_source = None
            while audio_source is None:
                try:
                    async with timeout(self.timeout_value):
                        audio_source_raw = await self.queue.get()
                except asyncio.TimeoutError:
                    await self.guild.voice_client.disconnect()
                    return self.audio.player_exit(self.guild)

                audio_source = await prepare_audio_source(self.channel, audio_source_raw)

            audio_source["title"] = audio_source_raw["title"]
            audio_source["original_link"] = audio_source_raw["url"]

            if (audio_source.get("source_type") == 1):  #0: local, 1: link, 2: local sfx
                self.guild.voice_client.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(audio_source.get("url"),
                        before_options = configuration.before_args,
                        options = configuration.ffmpeg_options)),
                    after = lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                self.guild.voice_client.source.volume = self.volume

            else:
                self.guild.voice_client.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(audio_source.get("url"),
                        options = configuration.ffmpeg_options)),
                    after = lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                if audio_source["source_type"] == 0:
                    self.guild.voice_client.source.volume = self.volume
                else:
                    self.guild.voice_client.source.volume = self.sfx_volume

            if (self.looping != 1) and (audio_source.get("source_type") != 2):
                await self.channel.send(":cd: Now playing: {}, at {}% volume.".format(
                    audio_source.get("title"),(int(self.volume*100))))

            await self.next.wait()
            if (self.looping == 2) and (audio_source.get("source_type") != 2):
                await self.queue.put(audio_source_raw)

    # Connection Loop ══════════════════════════════════════════════════════════
    async def connection_loop(self):
        await self.client.wait_until_ready()
        try:
            while self.guild.voice_client.is_connected():
                if (len(self.guild.voice_client.channel.members) < 2):
                    try:
                        logger.log_info("({} , gid: {}) All users left the voice channel".format(self.guild.name, self.guild.id))
                        await self.guild.voice_client.disconnect()
                        return self.audio.player_exit(self.guild)
                    except AttributeError:
                        pass
                else:
                    await asyncio.sleep(10)
        except AttributeError:
            pass

# Functions ════════════════════════════════════════════════════════════════════
async def prepare_audio_source(channel, audio_source_raw):
    if (audio_source_raw["source_type"] == 1):
        try:
            audio_source = ytdl.extract_info(audio_source_raw["url"], download = False)
            if audio_source is None:
                await channel.send("That's not a valid Youtube link.", delete_after = 15)
                return None
            elif (audio_source["protocol"] == "m3u8"):
                await channel.send("Streams don't work yet, sorry. :pray:", delete_after = 20)
                return None
            if "entries" in audio_source:
                audio_source = audio_source["entries"][0]
            audio_source["source_type"] = 1     #0: local, 1: link, 2: local sfx

        except youtube_dl.DownloadError as e:
            await channel.send("That's not a valid Youtube link.", delete_after = 20)
            return None

        return audio_source
    else:
        return audio_source_raw
