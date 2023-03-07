from __future__ import annotations
import logbook
from discord import Guild
from discord.abc import GuildChannel
from discord import utils
from json import dump
from json import dumps
from json import load
from logging import Logger
from os.path import exists

from typing import Sequence
from _collections_abc import dict_keys

log: Logger = logbook.getLogger("guild_data")
ACHIEVEMENTS = {
    "1gb": False,
    "25gb": False,
    "50gb": False,
    "100gb": False
}


class GuildData():
    def __init__(
            self,
            gid: int,
            name: str,
            summoned_from_channels: dict[str, int] = {},
            music_cached_total_mb: float = 0,
            achievements: dict = {}
            ) -> None:
        self.gid: int = gid
        self.name: str = name
        self.summoned_from_channels: dict[str, int] = summoned_from_channels
        self.music_cached_total_mb: float = music_cached_total_mb
        self.achievements: dict[str, bool] = achievements if achievements else ACHIEVEMENTS
        

    def __repr__(self) -> str:
        return dumps(self, default=vars, indent=4, ensure_ascii=False)
    

    async def get_music_channel_id(self) -> int | None:
        if len(self.summoned_from_channels) < 1:
            return None
        mc_id_str = max(self.summoned_from_channels, key=lambda i: self.summoned_from_channels[i])
        return int(mc_id_str) if self.summoned_from_channels[mc_id_str] > 2 else None


    async def inc_summoned_from(self, channel_id: int) -> None:
        if self.summoned_from_channels.get(str(channel_id)):
            self.summoned_from_channels[str(channel_id)] += 1
        else:
            self.summoned_from_channels[str(channel_id)] = 1
        await self.save_guild_data()


    async def trim_summoned_from(self, guild_channels: Sequence[GuildChannel]) -> None:
        summoned_from: dict_keys[str, int] = self.summoned_from_channels.keys()
        for gid in summoned_from:
            if not utils.get(guild_channels, id=int(gid)):
                self.summoned_from_channels.pop(gid)


    async def inc_music_cached_total_mb(self, megabytes: float) -> float:
        self.music_cached_total_mb += megabytes
        await self.save_guild_data()
        return self.music_cached_total_mb
    

    async def save_guild_data(self) -> None:
        log.info(f"Saving {self.name} guild data...")
        with open(f"./src/data/{self.gid}.json", "w") as gdjson:
            dump(self, gdjson, default=vars, indent=4, ensure_ascii=False)

    
    async def reload_guild_data(self) -> None:
        log.info(f"Reloading {self.name} guild data...")
        if exists(f"./src/data/{self.gid}.json"):
            with open(f"./src/data/{self.gid}.json", "r") as gdjson:
                gd: dict = load(gdjson)
                self.gid = gd["gid"]
                self.name = gd["name"]
                self.summoned_from_channels = gd["summoned_from_channels"]
                self.music_cached_total_mb = gd["music_cached_total_mb"]
                self.achievements = gd["achievements"]
        else:
            log.warning(f"{self.name} guild data file does not exist yet.")


async def get_guild_data(guild: Guild) -> GuildData:
    if not exists(f"./src/data/{guild.id}.json"):
        return GuildData(guild.id, guild.name)
    else:
        with open(f"./src/data/{guild.id}.json", "r") as gdjson:
            return GuildData(**load(gdjson))
        