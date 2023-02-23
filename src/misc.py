import logbook
import requests
from discord import app_commands
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import hybrid_command
from logging import Logger
from maon import Maon
from random import choice

from json import JSONDecodeError
from requests import ConnectionError

log: Logger = logbook.getLogger("misc")
RFC_3986_CHARS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%"
MAL_API_A_SEARCH_URL: str = "https://api.jikan.moe/v4/anime?q="
MAL_API_M_SEARCH_URL: str = "https://api.jikan.moe/v4/manga?q="


class Misc(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon


    @hybrid_command()
    @app_commands.describe(a="The first number to add", b="The second number to add")
    async def add(self, ctx: Context, a: app_commands.Range[int, 0, 100], b: app_commands.Range[int, 0, 200]):
        return await ctx.channel.send(f"{a+b}")

    
    @command(aliases=["coin", "toss"])
    async def flip(self, ctx: Context) -> None | Message:
        return await ctx.channel.send(f"It's {choice(['heads', 'tails'])}")


    @command(aliases=["anime", "animu", "manga", "mango", "myanimelist"])
    async def mal(self, ctx: Context, *args: str) -> None | Message:
        prefix: str | list[str] = await self.maon.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]
        if not args:
            return await ctx.channel.send(f"You can search for an anime or manga if you provide me a search term, like `{prefix}anime Psycho-Pass`")
        query: str = "%20".join(args)
        for c in query:
            if RFC_3986_CHARS.find(c) < 0:
                query = query.replace(c, "")

        if len(query) < 3:
            return await ctx.channel.send("Search queries have to be at least 3 characters long.")
        elif len(query) > 150:
            query = query[:150]
        
        try:
            log.info(f"Looking up {' '.join(args)} on MyAnimeList...")
            if ctx.invoked_with == "manga":
                r = requests.get(f"{MAL_API_M_SEARCH_URL}{query}")
            else:
                r = requests.get(f"{MAL_API_A_SEARCH_URL}{query}")
            if r.status_code == 200:
                r_content: dict = r.json()
                data: list[dict] | None = r_content.get("data")
                if not data: raise TypeError
                first_entry: dict = data[0]
                url: str | None = first_entry.get("url")
                if not url: raise TypeError
                return await ctx.channel.send(url)
            elif r.status_code == 410:
                return await ctx.channel.send("I could not fetch any information, the MyAnimeList search API url has changed.")
            else:
                return await ctx.channel.send("I could not fetch any information, maybe try again in a few seconds.")
        except (ConnectionError, JSONDecodeError, TypeError) as e:
            log.error(f"Look up failed. \n{e}")
            return await ctx.channel.send("I could not fetch any information, maybe try again in a few seconds.")
            

    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(Misc(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Misc")
