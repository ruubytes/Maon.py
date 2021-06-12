import os
import json
import requests
from configs import custom
from configs import settings
from discord.ext import commands
from json.decoder import JSONDecodeError


class ServerManager(commands.Cog):
    __slots__ = "client"


    def __init__(self, client: 'commands.Bot'):
        self.client: commands.Bot = client
    

    @commands.command(aliases=["reg", "whitelist"])
    @commands.guild_only()
    async def register(self, message, *, username: str = None):
        if not settings.SM_ENABLED:
            return
        if message.guild.id not in settings.SM_ACCEPTED_GUILDS:
            return
        if username is None:
            return await message.channel.send(f"You can whitelist your minecraft account with \n\t`{custom.PREFIX[0]}register YourMinecraftUsername` \nfor example:\n\t`{custom.PREFIX[0]}register TheRuu`")
        if username.lower() == "yourminecraftusername":
            return await message.channel.send("Haha, very funny.")
        if len(username) > 32:
            return await message.channel.send(f"You can whitelist your minecraft account with \n\t`{custom.PREFIX[0]}register YourMinecraftUsername` \nfor example:\n\t`{custom.PREFIX[0]}register TheRuu`")
        for char in username:
            if settings.RFC_3986_CHARS[:len(settings.RFC_3986_CHARS) - 20].find(char) < 0:
                return await message.channel.send("Please only user valid characters.")
        if not os.path.exists(settings.SM_MINECRAFT_URL + "whitelist.json"):
            return

        whitelist = {}
        with open(settings.SM_MINECRAFT_URL + "whitelist.json", "r") as f:
            whitelist = json.load(f)

        for user in whitelist:
            if user.get("name").lower() == username.lower():
                return await message.channel.send(f":thumbsup: {username} is already registered.")

        # Fetch UUID from Mojang
        data = {}
        try:
            data = requests.get(settings.SM_MINECRAFT_API + username).json()
        except requests.HTTPError:
            return await message.channel.send("Mojang is not responding to me right now, please try again later.")
        except JSONDecodeError:
            return await message.channel.send(f"Mojang said {username} doesn't exist. :face_with_monocle:")

        # Parse UUID and save to whitelist
        uuid_raw = data.get("id")
        uuid = ""
        if uuid_raw.find("-") < 0:
            uuid = uuid_raw[:8] + '-' + uuid_raw[8:12] + '-' + uuid_raw[12:16] + '-' + uuid_raw[16:20] + '-' + uuid_raw[20:]
        else:
            uuid = uuid_raw
        new_player = {"uuid": uuid, "name": data.get("name")}
        whitelist.append(new_player)

        with open(settings.SM_MINECRAFT_URL + "whitelist.json", "w") as f:
            json.dump(whitelist, f, indent=4)

        return await message.channel.send(f":thumbsup: {username} has been registered.")


    @commands.command(aliases=["unreg"])
    @commands.guild_only()
    @commands.is_owner()
    async def unregister(self, message, *, username: str = None):
        if not settings.SM_ENABLED:
            return
        if message.guild.id not in settings.SM_ACCEPTED_GUILDS:
            return
        if username is None:
            return await message.channel.send(f"You can whitelist your minecraft account with \n\t`{custom.PREFIX[0]}register YourMinecraftUsername` \nfor example:\n\t`{custom.PREFIX[0]}register TheRuu`")
        if username.lower() == "yourminecraftusername":
            return await message.channel.send(":eyes:")
        if len(username) > 32:
            return await message.channel.send(f"You can whitelist your minecraft account with \n\t`{custom.PREFIX[0]}register YourMinecraftUsername` \nfor example:\n\t`{custom.PREFIX[0]}register TheRuu`")
        for char in username:
            if settings.RFC_3986_CHARS[:len(settings.RFC_3986_CHARS) - 20].find(char) < 0:
                return await message.channel.send("Please only user valid characters.")
        if not os.path.exists(settings.SM_MINECRAFT_URL + "whitelist.json"):
            return

        whitelist = {}
        with open(settings.SM_MINECRAFT_URL + "whitelist.json", "r") as f:
            whitelist = json.load(f)

        for user in whitelist:
            if user.get("name").lower() == username.lower():
                whitelist.remove(user)

                with open(settings.SM_MINECRAFT_URL + "whitelist.json", "w") as f:
                    json.dump(whitelist, f, indent=4)
                
                return await message.channel.send(f"{username} removed from the whitelist.")

        return await message.channel.send(f"Could not find {username} in the whitelist.")
    

# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client: 'commands.Bot'):
    client.add_cog(ServerManager(client))


def teardown(client: 'commands.Bot'):
    client.remove_cog(ServerManager)
