import json
from os import path
from src import logbook

from discord.ext.commands.context import Context


ACHIEVEMENTS = {
    "1gb": 0,
    "25gb": 0,
    "50gb": 0,
    "100gb": 0,
    "test": 0
}

log = logbook.getLogger("GuildData")


class GuildData():
    def __init__(
            self, guild_id: int, 
            summoned_from_channels: dict = {}, 
            music_cached_total_mb: float = 0,
            achievements: dict = {}
        ):
        self.guild_id = guild_id
        self.summoned_from_channels: dict = summoned_from_channels
        self.music_cached_total_mb: float = music_cached_total_mb
        if achievements:
            self.achievements = achievements
        else:
            self.achievements = ACHIEVEMENTS


    def __repr__(self):
        return json.dumps(self, default=vars, indent=4)
        
    
    @staticmethod
    def get_guild_data(guild_id: int):
        id_str = str(guild_id)
        if not path.exists(f"./src/data/{id_str}.json"):
            return GuildData(guild_id)
        else:
            with open(f"./src/data/{id_str}.json") as gdjson:
                return GuildData(**json.load(gdjson))


    # Keep in mind, keys are str in json, always needs converting if it's an id that's used as int.
    def get_music_channel_id(self) -> int | None:
        if len(self.summoned_from_channels) < 1:    # Hasn't been summoned to a voice channel before
            return None
        mc_id_str = max(self.summoned_from_channels, key=self.summoned_from_channels.get)
        return int(mc_id_str) if self.summoned_from_channels.get(mc_id_str) > 2 else None


    def inc_summoned_from(self, channel_id: int):
        id_str = str(channel_id)
        if self.summoned_from_channels.get(id_str) != None:
            self.summoned_from_channels[id_str] += 1
        else:
            self.summoned_from_channels[id_str] = 1
        self.save_guild_data()


    def get_music_cached_size(self):
        return self.music_cached_total_mb


    async def inc_cached_music_size(self, megabytes: float):
        self.music_cached_total_mb += megabytes
        self.save_guild_data()
        return self.music_cached_total_mb


    async def check_cached_music_achievements(self, message: Context):
        if ((self.music_cached_total_mb / 1024) > 100) and (self.achievements.get("100gb") <= 0):
            if message.guild.system_channel:
                await message.guild.system_channel.send("Holy cow, this server made me download over 100 GB of music. Like this achievement will ever get unlocked lmao.") 
            self.set_achievement("100gb")
            log.info(f"{message.guild.name} unlocked 100gb achievement!")
        elif ((self.music_cached_total_mb / 1024) > 50) and (self.achievements.get("50gb") <= 0):
            if message.guild.system_channel:
                await message.guild.system_channel.send("I just crossed the 50 GB of music downloaded by this server mark. Where do I put all these songs, I'm drowning in them...") 
            self.set_achievement("50gb")
            log.info(f"{message.guild.name} unlocked 50gb achievement!")
        elif ((self.music_cached_total_mb / 1024) > 25) and (self.achievements.get("25gb") <= 0):
            if message.guild.system_channel:
                await message.guild.system_channel.send("You guys have managed to make me download over 25 GB of... music?. Most of it is trash but you love that trash like noone else.") 
            self.set_achievement("25gb")
            log.info(f"{message.guild.name} unlocked 25gb achievement!")
        elif ((self.music_cached_total_mb / 1024) > 1) and (self.achievements.get("1gb") <= 0):
            if message.guild.system_channel:
                await message.guild.system_channel.send("Hey, you just reached your first GB of music downloaded with me. Ya disc jockeys!") 
            self.set_achievement("1gb")
            log.info(f"{message.guild.name} unlocked 1gb achievement!")
        else:
            return None

    
    def set_achievement(self, achievement: str):
        if achievement not in self.achievements:
            return None
        self.achievements[achievement] = 1
        self.save_guild_data()
        return achievement


    def save_guild_data(self):
        with open(f"./src/data/{self.guild_id}.json", "w") as gdjson:
            json.dump(self, gdjson, default=vars, indent=4)

