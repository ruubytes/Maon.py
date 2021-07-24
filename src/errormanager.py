import asyncio
from discord import errors
from discord.ext import commands
from src import minfo
from src import admin


class ErrorManager(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client: commands.Bot = client
        self.log: minfo.Minstance = minfo.getLogger(self.__class__.__name__, 0)
        self.admin: admin.Admin = self.client.get_cog("Admin")


    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_command_error(self, message, error):
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner) or isinstance(error, commands.NoPrivateMessage):
            return
        elif isinstance(error, commands.MissingPermissions):
            return self.log.error("I lack permissions for this command.")
        else:
            raise error


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(ErrorManager(client))


def teardown(client):
    client.remove_cog(ErrorManager)
