import asyncio
import traceback
from time import time
from src import audio
from src import logbook
from configs import settings
from logging import Logger
from yt_dlp import YoutubeDL
from async_timeout import timeout
from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer

from asyncio import TimeoutError
from asyncio import CancelledError
from discord.errors import ClientException

from discord.voice_client import VoiceClient
from discord.message import Message
from discord.ext.commands import Bot
from discord.ext.commands import Context


class AudioPlayer:
    __slots__ = ["log", "client", "audio", "message", "voice_client", "volume", "looping", "sfx_volume", "player_timeout",
                 "now_playing", "queue", "next", "track", "running", "player_task", "refresh_live_stream_task"]

    def __init__(self, client: Bot, message: Context | Message):
        self.log: Logger = logbook.getLogger(self.__class__.__name__)
        self.client: Bot = client
        self.audio: audio.Audio = self.client.get_cog("Audio")
        self.message: Context | Message = message
        self.voice_client: VoiceClient = message.guild.voice_client
        self.volume: float = 0.1
        self.looping: str = "off"  # off / song / playlist
        self.sfx_volume: float = settings.SFX_VOLUME
        self.player_timeout: int = settings.PLAYER_TIMEOUT
        self.now_playing: str = ""
        self.queue: asyncio.Queue = asyncio.Queue()
        self.next: asyncio.Event = asyncio.Event()
        self.track: dict = {}
        self.running: bool = True
        self.player_task: asyncio.Task = asyncio.create_task(self._player_loop())
        self.refresh_live_stream_task: asyncio.Task = None
        self.log.info(f"{self.message.guild.name} audioplayer created.")


    async def _player_loop(self):
        try:
            await self.client.wait_until_ready()
            while self.running:
                self.next.clear()

                await self._get_track()
                await self._refresh_url()
                await self._play(self._set_options())

                await self.next.wait()
                if self.looping == "playlist" and self.track.get("track_type") != "sfx":
                    await self.queue.put(self.track)

        except CancelledError:
            self.log.info(f"{self.message.guild.name}: Cancelling audioplayer...")

        except TimeoutError:
            self.log.info(f"{self.message.guild.name}: Audioplayer has been inactive for {settings.PLAYER_TIMEOUT} seconds, cancelling...")

        except ClientException as e:
            # This usually happens if the audioplayer runs but the voice_client is not connected to voice
            self.log.error(f"{self.message.guild.name}: ClientException - cancelling audioplayer...\n{traceback.format_exc()}")
            await self.message.channel.send("I ran into a big error, shutting down my audioplayer...")

        except Exception as e:
            self.log.error(f"{self.message.guild.name}: _player_loop exception: {type(e)}\n{traceback.format_exc()}")

        finally:
            self.running = False
            if self.refresh_live_stream_task is not None:
                self.refresh_live_stream_task.cancel()
            if self.voice_client.is_playing():
                self.voice_client.stop()
            try:
                await self.voice_client.disconnect(force=True)
            except ConnectionResetError:
                self.log.error(f"{self.message.guild.name}: Disconnecting the voice_client ran into a ConnectionResetError, because the connection is already closing.")
            return self.audio.destroy_player(self.message)

    
    async def _get_track(self):
        """ Get the next track or keep the current one if the player is set to loop the current song. """
        if self.looping != "song":
            async with timeout(self.player_timeout):
                self.track = await self.queue.get()
        if self.track.get("track_type") == "stream":
            filename = self.audio.cached_songs.get(self.track.get("video_id"))
            if filename:
                self.track["title"] = filename[:len(filename) - 16]
                self.track["url"] = settings.TEMP_PATH + filename
                self.track["track_type"] = "music"
                self.log.info(f"{self.message.guild.name}: Changed stream to local file stream for {self.track.get('title')}.")


    async def _refresh_url(self):
        """ Refresh the stream url to avoid its expiration """
        if self.track.get("track_type") == "live_stream":
            if self.refresh_live_stream_task is not None: 
                self.refresh_live_stream_task.cancel()
            self.refresh_live_stream_task = asyncio.create_task(self._refresh_live_stream(self.track))
        
        if self.track.get("track_type") not in ["live_stream", "stream"] or (time() - self.track.get("time_stamp")) < 600:
            return

        self.log.info(f"{self.message.guild.name}: Refreshing the streaming url for {self.track.get('title')}.")
        video_info = await self.client.loop.run_in_executor(
            None, lambda: YoutubeDL(settings.YTDL_INFO_OPTIONS).extract_info(self.track.get("original_url"), download=False))

        if self.track.get("track_type") == "live_stream":
            self.track["url"] = video_info.get("url")
        else:
            format_urls = {}
            for f in video_info.get("formats", [video_info]):
                format_urls[f.get("format_id")] = f.get("url")

            if   "251" in format_urls: self.track["url"] = format_urls.get("251")   # webm
            elif "140" in format_urls: self.track["url"] = format_urls.get("140")   # m4a
            elif "250" in format_urls: self.track["url"] = format_urls.get("250")   # webm
            elif "249" in format_urls: self.track["url"] = format_urls.get("249")   # webm
            elif "139" in format_urls: self.track["url"] = format_urls.get("139")   # m4a
            else: self.log.error(f"{self.message.guild.name}: For some reason the track {self.track.get('title')} doesn't have any valid format IDs anymore.")

        self.track["time_stamp"] = time()

    
    async def _refresh_live_stream(self, track: dict):
        """ Refresh the live stream url every 10 minutes and restart the play process because live streams have been lagging and
            doing weird things after ~15 minutes for a while now """
        try:
            await asyncio.sleep(600)
            if self.now_playing != track.get("title"): return

            self.log.info(f"{self.message.guild.name}: Refreshing the streaming url for {track.get('title')}.")
            video_info = await self.client.loop.run_in_executor(
                None, lambda: YoutubeDL(settings.YTDL_INFO_OPTIONS).extract_info(track.get("original_url"), download=False))
            
            track["url"] = video_info.get("url")
            track["time_stamp"] = time()
            track["live_refresh"] = True

            await self.play_next(track)

            if self.voice_client.is_playing():
                self.voice_client.stop()

        except CancelledError:
            self.log.info(f"{self.message.guild.name}: Live stream refresh task cancelled.")


    def _set_options(self):
        """ Set reconnect arguments for ffmpeg if it's a stream """
        if self.track.get("track_type") in ["live_stream", "stream"]:
            return settings.BEFORE_ARGS
        return None


    async def _play(self, before_options: str = None):
        """ `before_options`: optional List[str] \n\n Extra command line arguments to pass to ffmpeg before the -i flag. """
        try:
            self.log.info(f"{self.message.guild.name}: Now playing {self.track.get('title')}.")
            self.voice_client.play(
                PCMVolumeTransformer(
                    FFmpegPCMAudio(
                        self.track.get("url"),
                        before_options=before_options,
                        options=settings.FFMPEG_OPTIONS
                    )
                ),
                after=lambda e: self._play_after_call(e)
            )

            if self.track.get("track_type") == "sfx":
                self.voice_client.source.volume = self.sfx_volume
            else:
                self.voice_client.source.volume = self.volume
                if self.now_playing != self.track.get("title"):
                    self.now_playing = self.track.get("title")
                    if self.track.get("live_refresh") is None:
                        await self.message.send(f":cd: Now playing: {self.track.get('title')}, at {int(self.volume * 100)}% volume.")

        except Exception as e:
            self.log.error(f"{self.message.guild.name}: Error outside of play function: {type(e)}\n{traceback.format_exc()}")


    def _play_after_call(self, error: Exception = None):
        if error:
            self.log.error(f"{self.message.guild.name}: Error within play function: {type(error)}\n{traceback.format_exc()}")
        self.next.set()
        self.now_playing = ""


    async def play_next(self, track: dict):
        """ Prepend a track to the player's queue instead of appending it. """
        if self.queue.qsize() > 0:
            self.log.info(f"{self.message.guild.name}: Prepending {track.get('title')} and rebuilding the player's queue...")
            new_queue = [track] + list(self.queue._queue)
            self.queue: asyncio.Queue = asyncio.Queue()
            for t in new_queue:
                await self.queue.put(t)
        else:
            await self.queue.put(track)
            

    def shutdown(self):
        """ Shut the audioplayer down """
        self.player_task.cancel()
