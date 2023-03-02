from __future__ import annotations
import logbook
from discord import Interaction
from discord import Message
from discord.ext.commands import Context
from logging import Logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from audio import Audio

log: Logger = logbook.getLogger("track")


class Track():
    def __init__(self, title: str, url: str, track_type: str) -> None:
        self.title: str = title
        self.url: str = url
        self.track_type: str = track_type


async def create_local_track(audio: Audio, cim: Context | Interaction | Message, url: str, track_type: str = "music") -> None | Track:
    log.info(f"{cim.guild}: Creating local track from {url}")
    title: str = url[url.rfind("/") + 1:] if "/" in url else url
    title = title[:title.rfind(".")]
    return Track(title, url, track_type)


async def create_stream_track(audio: Audio, cim: Context | Interaction | Message, url: str, track_type: str = "stream") -> None | Track:
    log.info(f"{cim.guild}: Creating stream track from {url}")
    return
