import asyncio
import logger
import configuration
import discord
from discord.ext import commands
from async_timeout import timeout

class MusicPlayer:
    __slots__ = ("client", "guild", "channel", "music", "queue", "next", "volume", "looping", "timeout_value")
    def __init__(self, message):
        self.client = message.bot
        self.guild = message.guild
        self.channel = message.channel
        self.music = self.client.get_cog("Music")
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.volume = 0.1
        self.looping = 0 # 0: off, 1: song, 2: queue
        self.timeout_value = configuration.PLAYER_TIMEOUT_VALUE

        self.client.loop.create_task(self.player_loop())
        self.client.loop.create_task(self.connection_loop())
        logger.log_info("({} , gid: {}) musicplayer created".format(self.guild.name, self.guild.id))

    async def connection_loop(self):
        await self.client.wait_until_ready()
        while self.guild.voice_client.is_connected():
            if (len(self.guild.voice_client.channel.members) < 2):
                try:
                    await self.guild.voice_client.disconnect()
                    return self.music.player_exit(self.guild)
                except AttributeError:
                    pass
            else:
                await asyncio.sleep(10)

    async def player_loop(self):
        await self.client.wait_until_ready()
        while self.guild.voice_client.is_connected():
            self.next.clear()

            if self.looping != 1:
                try:
                    async with timeout(self.timeout_value):
                        src = await self.queue.get()
                except asyncio.TimeoutError:
                    await self.guild.voice_client.disconnect()
                    return self.music.player_exit(self.guild)

            if (src.get("type_link") == 1): # 0: local file, 1: yt link
                self.guild.voice_client.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(src.get("url"),
                        before_options = configuration.before_args,
                        options = configuration.ffmpeg_options)),
                    after = lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                self.guild.voice_client.source.volume = self.volume
            else:
                self.guild.voice_client.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(src.get("url"),
                        options = configuration.ffmpeg_options)),
                    after = lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                self.guild.voice_client.source.volume = self.volume

            if (self.looping != 1) and (src.get("type_audio") == 0):
                await self.channel.send(":cd: Now playing: {}, at {}% volume.".format(
                    src.get("title"),(int(self.volume*100))))

            await self.next.wait()
            if (self.looping == 2) and (src.get("type_audio") == 0):
                await self.queue.put(src)
