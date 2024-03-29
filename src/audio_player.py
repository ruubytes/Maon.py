from __future__ import annotations
import logbook
from asyncio import create_task
from asyncio import Event
from asyncio import Queue
from asyncio import sleep
from asyncio import Task
from async_timeout import timeout
from discord import FFmpegPCMAudio
from discord import Guild
from discord import Interaction
from discord import Message
from discord import PCMVolumeTransformer
from discord import TextChannel
from discord import VoiceChannel
from discord.ext.commands import Context
from logging import Logger
from traceback import format_exc
from track import create_local_track

from asyncio import CancelledError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from audio import Audio
    from maon import Maon
    from track import Track

log: Logger = logbook.getLogger("audio_player")


class AudioPlayer():
    def __init__(self, maon: Maon, cim: Context | Interaction | Message) -> None:
        self.maon: Maon = maon
        self.audio: Audio = self.maon.get_cog("Audio") # type: ignore
        self.channel: TextChannel = cim.channel # type: ignore
        self.voice_channel: VoiceChannel = cim.guild.voice_client.channel  # type: ignore
        self.cim: Context | Interaction | Message = cim
        self.guild: Guild = cim.guild       # type: ignore
        self.looping: str = "off"
        self.name: str = cim.guild.name     # type: ignore
        self._next: Event = Event()
        self.now_playing: str = ""
        self.queue: Queue[Track] = Queue()
        self.timeout: int = self._set_timeout()
        self.track: None | Track = None
        self.volume: float = self._set_volume_default()
        self.volume_sfx: float = self._set_volume_sfx()
        self.player_task: Task = create_task(self._player_loop(), name="audio_player_task")
        self.volume_controller: Queue[int] = Queue()
        self.volume_controller_task: Task = create_task(self._volume_controller_loop(), name="volume_controller_task")
        log.info(f"{self.name}: Audio player created.") # type: ignore


    def close(self):
        self.volume_controller_task.cancel()
        self.player_task.cancel()


    async def _volume_controller_loop(self) -> None:
        try:
            await self.maon.wait_until_ready()
            while True:
                v: int = await self.volume_controller.get()
                v_old: int = int(self.volume * 100)
                if self.guild.voice_client.is_playing():    # type: ignore
                    if v > v_old:
                        while v > v_old:
                            v_old += 1
                            self.guild.voice_client.source.volume = float(v_old / 100) if v_old != 0 else 0  # type: ignore
                            await sleep(0.01)
                        self.volume = float(v / 100)
                    elif v < v_old:
                        while v < v_old:
                            v_old -= 1
                            self.guild.voice_client.source.volume = float(v_old / 100) if v_old != 0 else 0  # type: ignore
                            await sleep(0.01)
                        self.volume = float(v / 100) if v != 0 else 0
                else:
                    self.volume = float(v / 100) if v != 0 else 0
        except CancelledError:
            log.info(f"{self.name}: Cancelling volume controller task..")
                


    async def _player_loop(self) -> None:
        try:
            await self.maon.wait_until_ready()
            while True:
                self._next.clear()

                await self._get_track()
                await self._refresh_url()
                await self._play()

                await self._next.wait()

        except CancelledError:
            log.info(f"{self.name}: Cancelling audio player...")

        except TimeoutError:
            log.info(f"{self.name}: Audio player has been inactive for {self.timeout} seconds, cancelling...")

        finally:
            if self.guild.voice_client:
                if self.guild.voice_client.is_playing():        # type: ignore
                    self.guild.voice_client.stop()              # type: ignore
            await self.guild.voice_client.disconnect()          # type: ignore
            return self.audio.remove_player(self.guild.id)


    async def _get_track(self) -> None:
        log.info(f"{self.name}: Grabbing track from queue...")
        async with timeout(self.timeout):
            if self.track and self.looping == "song": 
                return
            elif self.track and self.looping == "playlist": 
                await self.queue.put(self.track)
            self.track = await self.queue.get()
            if self.track.track_type == "stream" and self.track.video_id in self.audio.cached_tracks:
                log.info(f"{self.name}: {self.track.title} has already been added to the cache, changing to local stream...")
                self.track = await create_local_track(self.audio, self.cim, self.audio.cached_tracks[self.track.video_id], "music")
                

    async def _refresh_url(self) -> None:
        if self.track and not self.track.track_type in ["stream", "live"]:
            return
        #return log.info(f"{self.name}: Refreshing streaming url...")
        
    
    async def _play(self) -> None:
        if not self.track: return
        log.info(f"{self.name}: Playing {self.track.title if self.track else None} in voice channel at {int(self.voice_channel.bitrate / 1000)}kb/s.")
        volume: float = self.volume if self.track.track_type != "sfx" else self.volume_sfx
        before_options: str = f"-re" if self.track.track_type in ["music", "sfx"] else f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -re"
        options: str = f"-b:a {int(self.voice_channel.bitrate / 1000)}k"
        self.guild.voice_client.play(       # type: ignore
            PCMVolumeTransformer(
                FFmpegPCMAudio(
                    self.track.url,
                    before_options=before_options,
                    options=options
                ),
                volume
            ),
            after=lambda e: self._after_play(e)
        )
        if self.now_playing != self.track.title:
            self.now_playing = self.track.title
            if self.track.track_type != "sfx":
                await self.channel.send(f":cd: Now playing: {self.now_playing}, at {int(volume * 100)}% volume.")


    def _after_play(self, e: Exception | None) -> None:
        if e:
            log.error(f"{self.name}: Error within _play occurred: {e}\n{format_exc()}")
        self._next.set()


    def _set_timeout(self) -> int:
        player_timeout: float | str | int | None = self.maon.settings.get("audio_player_timeout")
        if isinstance(player_timeout, int):
            return player_timeout
        else:
            log.warning("My settings file doesn't have a valid player timeout set.")
            return 3600


    def _set_volume_default(self) -> float:
        vol_def: float | str | int | None = self.maon.settings.get("audio_volume_default")
        if isinstance(vol_def, float):
            return vol_def
        else:
            log.warning(f"My settings file doesn't have a valid default volume set.")
            return 0.15


    def _set_volume_sfx(self) -> float:
        sfx_vol: float | str | int | None = self.maon.settings.get("audio_volume_sfx")
        if isinstance(sfx_vol, float):
            return sfx_vol
        else:
            log.warning(f"My settings file doesn't have a valid default volume set for sound effects.")
            return 0.3
    


