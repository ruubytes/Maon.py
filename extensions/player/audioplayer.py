from async_timeout import timeout
from discord import PCMVolumeTransformer
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from youtube_dl import DownloadError
import configuration as config
import asyncio


class AudioPlayer:
    __slots__ = ["client", "audio", "message", "voice_client", "volume", "looping", "sfx_volume", "player_timeout",
                 "queue", "next", "running", "player_task", "active_task"]

    def __init__(self, client, message):
        self.client = client
        self.audio = self.client.get_cog("Audio")
        self.message = message
        self.voice_client = message.guild.voice_client
        self.volume = 0.1
        self.looping = "off"  # off / song / playlist
        self.sfx_volume = config.SFX_VOLUME
        self.player_timeout = config.PLAYER_TIMEOUT
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.running = True

        print("[{}|{}] Creating audioplayer...".format(self.message.guild.name, self.message.guild.id))
        self.player_task = self.client.loop.create_task(self.player_loop())
        print("[{}|{}] Audioplayer created.".format(self.message.guild.name, self.message.guild.id))

    async def player_loop(self):
        await self.client.wait_until_ready()

        # To close the player if the channel is empty
        self.active_task = self.client.loop.create_task(self.active_loop())
        track = None
        try:
            while self.running:
                self.next.clear()

                if self.looping != "song":
                    track = None
                    async with timeout(self.player_timeout):
                        track = await self.queue.get()
                #track = await self.prepare_audio_track(track)

                if track["track_type"] == "link":  # link / music / sfx
                    self.voice_client.play(PCMVolumeTransformer(
                        FFmpegPCMAudio(track.get("url"), options=config.FFMPEG_OPTIONS)),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))

                    """ Old streaming functionality, but since YT doesn't want streamed songs to finish,
                        a downloaded version is needed.
                    self.voice_client.play(PCMVolumeTransformer(
                        FFmpegPCMAudio(track.get("url"),
                                       before_options=config.BEFORE_ARGS,
                                       options=config.FFMPEG_OPTIONS)),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                    """
                else:
                    self.voice_client.play(PCMVolumeTransformer(
                        FFmpegPCMAudio(track.get("url"), options=config.FFMPEG_OPTIONS)),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))

                if track["track_type"] != "sfx":
                    self.voice_client.source.volume = self.volume
                    await self.message.send(":cd: Now playing: {}, at {}% volume.".format(
                        track.get("title"), (int(self.volume * 100))))
                else:
                    self.voice_client.source.volume = self.sfx_volume

                await self.next.wait()
                # Playlist loop
                if self.looping == "playlist" and track["track_type"] != "sfx":
                    await self.queue.put(track)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("[{}|{}] Cancelling audioplayer...".format(self.message.guild.name, self.message.guild.id))
            self.running = False
            self.active_task.cancel()
            await self.voice_client.disconnect()
            return self.audio.destroy_player(self.message)

    async def active_loop(self):
        try:
            while self.running:
                if len(self.message.guild.voice_client.channel.members) < 2:
                    print("[{}|{}] Users left the voice channel, destroying audioplayer.".format(self.message.guild.name,
                                                                                                self.message.guild.id))
                    self.running = False
                    await self.voice_client.disconnect()
                    return self.audio.destroy_player(self.message)
                else:
                    await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass

    async def prepare_audio_track(self, track):
        track_old = track
        if track["track_type"] == "link":
            try:
                track = YoutubeDL(config.YTDL_PLAY_OPTIONS).extract_info(track["url"], download=False)
                if track is None:
                    await self.message.send("Youtube link machine broke.")
                    return track
                elif track["protocol"] == "m3u8":
                    await self.message.send("Streams are not supported yet, sorry! :pray:")
                    return None
                if "entries" in track:
                    track = track["entries"][0]
                track["track_type"] = 1
                track["title"] = track_old["title"]
                track["original_url"] = track_old["url"]
                return track

            except DownloadError:
                await self.message.send("Something went wrong with that Youtube link.")
                return None
        else:
            return track
