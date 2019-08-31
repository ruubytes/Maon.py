import asyncio
import configuration
import discord

class AudioPlayer:
    __slots__ = ("client", "user_message", "guild", "channel", "audioplayer_message",
        "home_dir", "current_dir", "dir_list", "dir_items", "max_pages", "current_page",
        "slots_names", "slots_types", "music_cog")
