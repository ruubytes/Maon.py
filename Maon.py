import pkg_resources


installed_packages = "\n".join(sorted(["%s==%s" % (i.key, i.version) for i in pkg_resources.working_set]))
required_packages_list = [
    "aioconsole", "discord.py", "psutil", "pynacl", "requests", "simplejson", "tinytag", "yt-dlp"
]
missing_packages_list = []
for i in required_packages_list:
    if installed_packages.find(i) < 0:
        missing_packages_list.append(i)
if len(missing_packages_list) > 0:
    print(f"I am missing the following packages: {', '.join(missing_packages_list)}")
    print(f"You can install them via the command:  python3 -m pip install -U {' '.join(missing_packages_list)}")
    exit(1)


import login
import discord
import asyncio
from os import path
from os import makedirs
from src import version
from src import logbook
from configs import custom
from configs import settings
from discord.ext import commands
from discord.errors import LoginFailure
from aiohttp.client_exceptions import ClientConnectorError


class Maon(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=custom.PREFIX, help_command=None, intents=self.set_intents(), **kwargs)
        self.log = logbook.getLogger(self.__class__.__name__)
        self.log.log(level=logbook.RAW, msg=version.SIGNATURE)
        self.log.info(f"Discord.py Version: {discord.__version__}")
        self.set_ids()
        self.case_insensitive = True


    async def setup_hook(self) -> None:
        for ext in settings.EXTENSION_LIST:
            self.log.info(f"Loading {ext} extension...")
            await self.load_extension(f"{settings.EXTENSION_PATH}{ext}")


    def set_ids(self):
        if (len(login.TOKEN) < 55) or (not login.TOKEN) or (login.TOKEN == ""):
            self.log.error("Please add my API token to the login file so I can log into discord!\n")
            exit(1)
        if login.MAON_ID <= 0 or login.OWNER_ID <= 0:
            self.log.error("Please add my own ID and your ID to the login file so I can recognize us!\n")
            exit(1)
        self.owner_id = login.OWNER_ID
        self.id = login.MAON_ID
        

    def set_intents(self):
        """ Set events handled by the API """
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = False
        intents.reactions = True
        intents.typing = False
        intents.voice_states = True
        return intents


    async def run(self):
        try:
            await self.start(login.TOKEN)
        except TypeError:
            self.log.error("I need my discord API token to log in. Please add it to my login file!\n")
            exit(1)
        except LoginFailure:
            self.log.error("It looks like my API token is faulty, make sure you have entered it correctly!\n")
            exit(1)
        except ClientConnectorError:
            self.log.error("I can't connect right now, please try again later.\n")
            exit(1)
        

async def main():
    if not path.exists(settings.LOGGING_DISCORD_PATH):
        makedirs(settings.LOGGING_DISCORD_PATH)
    logbook.getLogger("discord")    # Format discord lib logging through the custom logging formatter in logbook
    
    maon = Maon()
    await maon.run()
    

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nShutting down...\n")
