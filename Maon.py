from discord.ext import commands
import discord
import configuration as config
import login as login


class Maon:
    __slots__ = "client"

    def __init__(self):
        print(config.SIGNATURE)
        print("Discord.py Version: {}".format(discord.__version__))
        self.client = commands.Bot(command_prefix=config.PREFIX, case_insensitive=True, owner_id=login.OWNER_ID)
        self.client.remove_command("help")

    def load_extensions(self):
        for ext in config.EXTENSION_LIST:
            print("Loading {} extension...".format(ext))
            self.client.load_extension(config.EXTENSION_PATH + ext)

    def run(self):
        self.client.run(login.TOKEN)


Maon = Maon()
Maon.load_extensions()
Maon.run()
