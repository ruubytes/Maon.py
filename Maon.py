import logging
import discord
import login
from src import version
from configs import custom
from configs import settings
from logging.handlers import TimedRotatingFileHandler
from discord.ext import commands
from discord.errors import LoginFailure
from aiohttp.client_exceptions import ClientConnectorError


class Maon:
    __slots__ = "client"

    def __init__(self):
        self.check_ids()
        print(version.SIGNATURE)
        print("Discord.py Version: {}".format(discord.__version__))
        self.client = commands.Bot(
            command_prefix=custom.PREFIX, 
            case_insensitive=True, 
            owner_id=login.OWNER_ID,
            intents=self.set_intents()
        )
        self.client.id = login.MAON_ID
        self.client.remove_command("help")

    def set_intents(self):
        # Set handled events by the API
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        return intents

    def check_ids(self):
        if (len(login.TOKEN) < 55) or (not login.TOKEN) or (login.TOKEN == ""):
            print("\nPlease add my API token to the login file so I can log into discord!\n")
            exit()
        elif login.MAON_ID < 1 or login.OWNER_ID < 1:
            print("\nPlease add my own ID and your ID to the login file so I can recognize us!\n")
            exit()

    def load_extensions(self):
        for ext in settings.EXTENSION_LIST:
            print("Loading {} extension...".format(ext))
            self.client.load_extension(settings.EXTENSION_PATH + ext)

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
logging.getLogger().addHandler(TimedRotatingFileHandler(
        filename=settings.LOGGING_DISCORD_PATH,
        when='midnight',
        interval=1,
        backupCount=7
    )
)
Maon = Maon()
Maon.load_extensions()
Maon.run()
