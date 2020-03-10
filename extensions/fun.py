from discord.ext import commands
from random import choice


class Fun(commands.Cog):
    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["coin", "toss"])
    async def flip(self, message):
        coin = ["heads", "tails"]
        return await message.send("It's {}!".format(choice(coin)))


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Fun(client))


def teardown(client):
    client.remove_cog(Fun)
