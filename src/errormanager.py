from discord.ext import commands


class ErrorManager(commands.Cog):
    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_command_error(self, message, error):
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner) or isinstance(error, commands.NoPrivateMessage):
            return
        elif isinstance(error, commands.MissingPermissions):
            return print("User lacks permissions for this command.")
        else:
            raise error


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(ErrorManager(client))


def teardown(client):
    client.remove_cog(ErrorManager)
