from discord.ext import commands


class Basic(commands.Cog):
    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command()
    async def ping(self, message):
        return await message.send("Pong! `WebSocket: {}ms`".format(int(self.client.latency * 1000)))


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Basic(client))


def teardown(client):
    client.remove_cog(Basic)
