from discord.ext import commands
from random import choice
from random import randint
import configuration as config


class Fun(commands.Cog):
    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["coin", "toss"])
    async def flip(self, message):
        coin = ["heads", "tails"]
        return await message.send("It's {}!".format(choice(coin)))

    @commands.command(aliases=["dice", "roll"])
    async def rng(self, message, *, number: str = None):
        if number is None:
            return await message.send("I need a max number to roll.")
        try:
            number = int(number)
            if number < 1:
                return await message.send("I need a positive number to roll.")
            return await message.send("{} rolled `{}`.".format(message.author.name, randint(0, number)))
        except (TypeError, ValueError):
            return await message.send("I need a positive number to roll. :eyes:")

    @commands.command(aliases=config.QUESTION_TRIGGER)
    async def eightball(self, message, *, question:str = None):
        if question is None:
            return await message.send(choice(config.DEFAULT_REPLY))
        else:
            if "why" in message.invoked_with:
                return await message.send(choice(config.QUESTION_REPLY_WHY))
            return await message.send(choice(config.QUESTION_REPLY))

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.client.user.id:
            if message.content.lower() == config.PREFIX_FAST:
                return await message.channel.send(choice(config.DEFAULT_REPLY))


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Fun(client))


def teardown(client):
    client.remove_cog(Fun)
