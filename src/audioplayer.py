import asyncio
import traceback
from src import audio
from src import logbook
from configs import custom
from configs import settings
from async_timeout import timeout
from discord import PCMVolumeTransformer
from discord import FFmpegPCMAudio
from discord.errors import ClientException
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from time import time
from random import shuffle

from discord.voice_client import VoiceClient
from discord.message import Message
from discord.ext.commands import Bot


class AudioPlayer:
    __slots__ = ["client", "log", "audio", "message", "voice_client", "volume", "looping", "sfx_volume", "player_timeout",
                 "now_playing", "queue", "next", "running", "player_task", "active_task", "shuffle"]

    def __init__(self, client, message):
        self.client: Bot = client
        self.audio: audio.Audio = self.client.get_cog("Audio")
        self.log = logbook.getLogger(self.__class__.__name__)
        self.message: Message = message
        self.voice_client: VoiceClient = message.guild.voice_client
        self.volume: float = 0.1
        self.looping: str = "off"  # off / song / playlist
        self.shuffle: bool = False
        self.sfx_volume: float = settings.SFX_VOLUME
        self.player_timeout: int = settings.PLAYER_TIMEOUT
        self.now_playing: str = ""
        self.queue: asyncio.Queue = asyncio.Queue()
        self.next: asyncio.Event = asyncio.Event()
        self.running: bool = True
        self.player_task: asyncio.Task = self.client.loop.create_task(self.player_loop())
        self.log.info(f"{self.message.guild.name} audioplayer created.")


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

                if track.get("track_type") == "stream":
                    # In case of a repeating song or multiple requested songs, check if it is available in the cache
                    #   now and overwrite if yes
                    filename = self.audio.cached_songs.get(track.get("video_id"))
                    if filename:
                        track["title"] = filename[:len(filename) - 16]
                        track["url"] = settings.TEMP_PATH + filename
                        track["track_type"] = "music"
                        self.log.info(f"{self.message.guild.name}: Changed stream to local file stream for {track.get('title')}")

                if track.get("track_type") == "stream":     # stream / music / sfx
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
                    self.voice_client.play(
                        PCMVolumeTransformer(
                            FFmpegPCMAudio(
                                track.get("url"), 
                                options=settings.FFMPEG_OPTIONS
                            )
                        ),
                        after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set)
                    )

                if track.get("track_type") != "sfx":
                    self.voice_client.source.volume = self.volume
                    if self.looping != "song":
                        await self.message.send(f":cd: Now playing: {track.get('title')}, at {int(self.volume * 100)}% volume.")
                        self.log.info(f"Now playing: {track.get('title')}, at {int(self.volume * 100)}% volume.")
                else:
                    self.voice_client.source.volume = self.sfx_volume
                self.now_playing = track.get("title")

                await self.next.wait()

                # If shuffle play is on, scramble the queue.
                #   Reminder to detect already played songs in the history when history is implented.
                if self.shuffle:
                    scrambled_q = self.queue._queue
                    shuffle(scrambled_q)
                    self.queue = asyncio.Queue()
                    for item in scrambled_q:
                        await self.queue.put(item)

                self.now_playing = ""

                # Playlist loop
                if self.looping == "playlist" and track["track_type"] != "sfx":
                    await self.queue.put(track)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            self.log.info(f"{self.message.guild.name}: Cancelling audioplayer...")
        
        except ClientException:
            self.log.error(f"{self.message.guild.name}: ClientException - Cancelling audioplayer...\n{traceback.format_exc()}")
            await self.message.channel.send("I ran into a big error, shutting down my audioplayer...")

        finally:
            self.running = False
            self.active_task.cancel()
            self.voice_client.stop()
            await self.voice_client.disconnect()
            return self.audio.destroy_player(self.message)


    async def active_loop(self):
        """ Periodically checks if Maon is alone in a voice channel and disconnects if True """
        try:
            while self.running:
                if len(self.message.guild.voice_client.channel.voice_states) < 2:
                    self.log.info(f"{self.message.guild.name}: Users left the voice channel, destroying audioplayer.")
                    self.running = False
                    return self.player_task.cancel()
                
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
