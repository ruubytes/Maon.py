import logbook
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Cog
from logging import Logger

log: Logger = logbook.getLogger("admin")


class Admin(Cog):
    def __init__(self, maon: Bot) -> None:
        self.maon: Bot = maon


async def setup(maon: Bot) -> None:
    await maon.add_cog(Admin(maon))


async def teardown(maon: Bot) -> None:
    """ Clean up here, if needed, before unloading the extension """
    await maon.remove_cog("Admin")
