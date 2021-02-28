import asyncio
from configs import custom
from configs import settings
from async_timeout import timeout
from discord import PCMVolumeTransformer
from discord import FFmpegPCMAudio
from discord.errors import ClientException
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
from time import time


class AudioPlayer:
    __slots__ = ["client", "audio", "message", "voice_client", "volume", "looping", "sfx_volume", "player_timeout",
                 "now_playing", "queue", "next", "running", "player_task", "active_task"]

    def __init__(self, client, message):
        self.client = client
        self.audio = self.client.get_cog("Audio")
        self.message = message
        self.voice_client = message.guild.voice_client
        self.volume = 0.1
        self.looping = "off"  # off / song / playlist
        self.sfx_volume = settings.SFX_VOLUME
        self.player_timeout = settings.PLAYER_TIMEOUT
        self.now_playing = ""
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.running = True

        print("[{}] Creating audioplayer...".format(self.message.guild.name))
        self.player_task = self.client.loop.create_task(self.player_loop())
        print("[{}] Audioplayer created.".format(self.message.guild.name))

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

                if track["track_type"] == "stream":     # stream / music / sfx
                    # Refresh the streaming url if the track has been too long in the Q and is in danger of expiring
                    if (time() - track.get("time_stamp")) >  600:
                        track = await self.refresh_url(track)
                        if track is None: continue

                    self.voice_client.play(
                        PCMVolumeTransformer(
                            FFmpegPCMAudio(
                                track.get("url"),
                                before_options=settings.BEFORE_ARGS,
                                options=settings.FFMPEG_OPTIONS
                            )
                        ),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set)
                    )
                    
                else:
                    self.voice_client.play(PCMVolumeTransformer(
                        FFmpegPCMAudio(track.get("url"), options=settings.FFMPEG_OPTIONS)),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))

                if track["track_type"] != "sfx":
                    self.voice_client.source.volume = self.volume
                    if self.looping != "song":
                        await self.message.send(":cd: Now playing: {}, at {}% volume.".format(
                            track.get("title"), (int(self.volume * 100))))
                else:
                    self.voice_client.source.volume = self.sfx_volume
                self.now_playing = track.get("title")

                await self.next.wait()
                self.now_playing = ""

                # Playlist loop
                if self.looping == "playlist" and track["track_type"] != "sfx":
                    await self.queue.put(track)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("[{}] Cancelling audioplayer...".format(self.message.guild.name))
            self.running = False
            self.active_task.cancel()
            await self.voice_client.disconnect()
            return self.audio.destroy_player(self.message)
        
        except ClientException:
            print("[{}] ClientException - Cancelling audioplayer...".format(self.message.guild.name))
            self.running = False
            self.active_task.cancel()
            try:
                await self.message.channel.send("I ran into a big error, shutting down my audioplayer...")
                await self.voice_client.disconnect()
            finally:
                return self.audio.destroy_player(self.message)


    async def active_loop(self):
        """ Periodically checks if Maon is alone in a voice channel and disconnects if True """
        try:
            while self.running:
                if len(self.message.guild.voice_client.channel.voice_states) < 2:
                    print("[{}] Users left the voice channel, destroying audioplayer.".format(self.message.guild.name))
                    self.running = False
                    return await self.player_task.cancel()
                    #await self.voice_client.disconnect()
                    #return self.audio.destroy_player(self.message)
                
                else:
                    await asyncio.sleep(10)

        except asyncio.CancelledError:
            pass

    async def refresh_url(self, track):
        """ Refreshes the stream url of a track in case it is in danger of expiring. """
        message = track.get("message")
        try:
            video_info = await self.client.loop.run_in_executor(
                None, lambda: YoutubeDL(settings.YTDL_INFO_OPTIONS).extract_info(track.get("original_url"), download=False))

            if video_info.get("protocol"):
                track["url"] = video_info.get("url")
            else:
                formats = video_info.get("formats", [video_info])
                for f in formats:
                    if f["format_id"] == "251":
                        track["url"] = f.get("url")
            track["time_stamp"] = time()

            return track
        except DownloadError:
            await message.channel.send("{}'s streaming link probably expired and I ran into an error.".format(track.get("title")))
            return None
