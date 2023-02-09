import json
from os import path


class GuildData():
    def __init__(
            self, guild_id: int, 
            summoned_from_channels: dict = {}, 
            music_cached_total_mb: int = 0, 
            music_channel_id: int = 0):
        self.guild_id = guild_id
        self.summoned_from_channels: dict = summoned_from_channels
        self.music_cached_total_mb: int = music_cached_total_mb


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
            print("Incrementing")
            self.summoned_from_channels[id_str] += 1
        else:
            print("Creating")
            self.summoned_from_channels[id_str] = 1
        self.save_guild_data()


    def get_music_cached_size(self):
        return self.music_cached_total_mb


    def inc_music_cached_size(self, megabytes: int):
        self.music_cached_total_mb += megabytes
        self.save_guild_data()
        return self.music_cached_total_mb


    def save_guild_data(self):
        with open(f"./src/data/{self.guild_id}.json", "w") as gdjson:
            json.dump(self, gdjson, default=vars, indent=4)

