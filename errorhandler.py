import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    __slots__ = ("client")
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, message, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.errors.BadArgument):
            return
        else:
            raise error

def setup(client):
    client.add_cog(ErrorHandler(client))
