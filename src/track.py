import logbook
from discord import Interaction
from discord import Message
from discord.ext.commands import Context
from logging import Logger

log: Logger = logbook.getLogger("track")


class Track():
    def __new__(cls):
        return super(Track, cls).__new__(cls)
    

    def __init__(self) -> None:
        return


async def create_local_track(cim: Context | Interaction | Message, url: str) -> None | Track:
    return


async def create_stream_track(cim: Context | Interaction | Message, url: str) -> None | Track:
    return
