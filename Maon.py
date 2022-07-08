import pkg_resources
installed_packages = "\n".join(sorted(["%s==%s" % (i.key, i.version) for i in pkg_resources.working_set]))
required_packages_list = [
    "aioconsole", "discord.py", "psutil", "pynacl", "simplejson", "tinytag==1.7.0", "yt-dlp"
]
missing_packages_list = []
for i in required_packages_list:
    if installed_packages.find(i) < 0:
        missing_packages_list.append(i)
if len(missing_packages_list) > 0:
    print(f"I am missing the following packages: {', '.join(missing_packages_list)}")
    print(f"You can install them via the command:  python3 -m pip install -U {' '.join(missing_packages_list)}")
    exit()


import logging
import discord
import login
from os import path
from os import makedirs
from src import version
from src import minfo
from configs import custom
from configs import settings
from logging.handlers import TimedRotatingFileHandler
from discord.ext import commands
from discord.errors import LoginFailure
from aiohttp.client_exceptions import ClientConnectorError


class Maon:
    __slots__ = ["client", "log"]

    def __init__(self):
        self.log = minfo.getLogger(self.__class__.__name__, 0, "./src/logs/")
        self.check_ids()
        self.log.raw(version.SIGNATURE)
        self.log.info(f"Discord.py Version: {discord.__version__}")
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
        intents.voice_states = True
        return intents


    def check_ids(self):
        if (len(login.TOKEN) < 55) or (not login.TOKEN) or (login.TOKEN == ""):
            self.log.raw("\nPlease add my API token to the login file so I can log into discord!\n")
            exit()
        elif login.MAON_ID < 1 or login.OWNER_ID < 1:
            self.log.raw("\nPlease add my own ID and your ID to the login file so I can recognize us!\n")
            exit()


    def load_extensions(self):
        for ext in settings.EXTENSION_LIST:
            self.log.info("Loading {} extension...".format(ext))
            self.client.load_extension(settings.EXTENSION_PATH + ext)


    def run(self):
        try:
            self.client.run(login.TOKEN)
        except TypeError:
            self.log.raw("\nI need my discord API token to log in. Please add it to my login file!\n")
        except LoginFailure:
            self.log.raw("\nIt looks like my API token is faulty, make sure you have entered it correctly!\n")
        except ClientConnectorError:
            self.log.raw("\nI can't connect right now, please try again later.\n")


logging.basicConfig(level=logging.WARNING)
if not path.exists(settings.LOGGING_DISCORD_PATH):
    makedirs(settings.LOGGING_DISCORD_PATH)
logging.getLogger().addHandler(TimedRotatingFileHandler(
        filename=settings.LOGGING_DISCORD_PATH_FILE,
        when='midnight',
        interval=1,
        backupCount=7
    )
)
Maon = Maon()
Maon.load_extensions()
Maon.run()
