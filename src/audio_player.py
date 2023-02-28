import logbook
from discord import Interaction
from discord import Message
from discord import TextChannel
from discord.ext.commands import Context
from logging import Logger
from maon import Maon

log: Logger = logbook.getLogger("audio_player")


class AudioPlayer():
    def __new__(cls, maon: Maon, cim: Context | Interaction | Message):
        if cim.channel and isinstance(cim.channel, TextChannel):
            return super(AudioPlayer, cls).__new__(cls, maon, cim, cim.channel)
        else:
            return None


    def __init__(self, maon: Maon, cim: Context | Interaction | Message, channel: TextChannel) -> None:
        self.maon: Maon = maon
        self.channel: TextChannel = channel
        self.volume: float = self._set_volume_default()
        self.volume_sfx: float = self._set_volume_sfx()


    def _set_channel(self, cim: Context | Interaction | Message) -> TextChannel:
        return cim.channel # type: ignore


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
    
