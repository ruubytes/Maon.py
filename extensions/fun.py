from json import loads
from urllib import request
from urllib.error import URLError, HTTPError
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
            return await message.send("{} rolled `{}`.".format(message.author.name, randint(1, number)))
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

    @commands.command(aliases=["anime", "animu", "hentai"])
    async def mal(self, message, *args: str):
        if not args:
            return await message.send(
                "You can search for an anime if you provide me a search term. I'll look for the closest one I can find `" + config.PREFIX[0] + "anime <key words>`")
        
        query = "%20".join(args)
        for char in query:
            if config.RFC_3986_CHARS.find(char) < 1:
                query = query.replace(char, "")
        
        try:
            resp = request.urlopen(request.Request(config.MAL_API_ANIME_SEARCH_URL + query))
            data = loads(resp.read().decode("utf-8"))
            first_entry = data.get("results")[0]
            return await message.send("Most relevant anime I could find: " + first_entry.get("url"))

        except (URLError, HTTPError):
            return await message.send("I could not fetch any information, maybe try again in a few seconds.")

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
