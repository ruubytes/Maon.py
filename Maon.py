from discord.ext import commands
from aiohttp.client_exceptions import ClientConnectorError
from discord.errors import LoginFailure
import logging
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
        try:
            self.client.run(login.TOKEN)
        except TypeError:
            print("\nI need my discord API token to log in. Please add it to my login file!\n")
        except LoginFailure:
            print("\nIt looks like my API token is faulty, make sure you have entered it correctly!\n")
        except ClientConnectorError:
            print("\nI can't connect right now, please try again later.\n")


logging.basicConfig(level=logging.WARNING)
Maon = Maon()
Maon.load_extensions()
Maon.run()
