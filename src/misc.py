import logbook
import requests
from discord import app_commands
from discord import Interaction
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import hybrid_command
from logging import Logger
from maon import Maon
from random import choice
from requests import Response

from json import JSONDecodeError
from requests import ConnectionError

log: Logger = logbook.getLogger("misc")
RFC_3986_CHARS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%"
MAL_API_A_SEARCH_URL: str = "https://api.jikan.moe/v4/anime?q="
MAL_API_M_SEARCH_URL: str = "https://api.jikan.moe/v4/manga?q="


class Misc(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon


    @command()
    async def ping(self, ctx: Context) -> None | Message:
        lat: int = int(self.maon.latency * 1000)
        log.info(f"WebSocket latency: {lat}ms")
        return await ctx.channel.send(f"Pong! `WebSocket {lat}ms`")
    

    @hybrid_command()
    async def help(self, ctx: Context) -> None | Message:
        if ctx.interaction:
            log.info("Correctly identified this as a slash command")
            await ctx.send("Replied as slash command reply")
        else:
            log.info("Hopefully correctly identified this as not a slash command")
            await ctx.channel.send("Replied as traditional command")

    
    async def _prepare_help_embed_music(self, is_interaction: bool = False) -> None | str:
        #prefix: str = "/" if is_interaction else await self.maon.get_prefix()
        return

    
    @command(aliases=["coin", "toss"])
    async def flip(self, ctx: Context) -> None | Message:
        return await ctx.channel.send(f"It's {choice(['heads', 'tails'])}")
    

    @app_commands.command()
    @app_commands.describe(a="The first number to add", b="The second number to add")
    async def add(self, interaction: Interaction, a: int, b: int) -> None | Message:
        await interaction.response.send_message(f"{a} + {b} = {a+b}")


    @app_commands.command(name="anime")
    @app_commands.describe(search="Search query for an anime on MyAnimeList. (min 3 characters)")
    async def _ac_anime(self, interaction: Interaction, search: str) -> None | Message:
        return await interaction.response.send_message(await self._mal(search))
    

    @app_commands.command(name="mal")
    @app_commands.describe(search="Search query for an anime on MyAnimeList. (min 3 characters)")
    async def _ac_mal(self, interaction: Interaction, search: str) -> None | Message:
        return await interaction.response.send_message(await self._mal(search))
    

    @app_commands.command(name="manga")
    @app_commands.describe(search="Search query for manga on MyAnimeList. (min 3 characters)")
    async def _ac_manga(self, interaction: Interaction, search: str) -> None | Message:
        return await interaction.response.send_message(await self._mal(search, anime=False))
    

    @command(aliases=["mal", "anime", "animu", "manga", "mango", "myanimelist"])
    async def _c_mal(self, ctx: Context, *argv: str) -> None | Message:
        prefix: str = await self.maon._get_prefix()
        if not argv:
            return await ctx.channel.send(f"You can search for an anime or manga if you provide me a search term, like `{prefix}anime Psycho-Pass`")
        query: str = " ".join(argv)
        if ctx.invoked_with == "manga":
            return await ctx.channel.send(await self._mal(query, anime=False))
        else:
            return await ctx.channel.send(await self._mal(query))


    async def _mal(self, query: str, anime: bool = True) -> str:
        search_query: str = query
        for c in search_query:
            if c == " ":
                search_query = search_query.replace(c, "%20")
            if RFC_3986_CHARS.find(c) < 0:
                search_query = search_query.replace(c, "")
        if len(search_query) < 3:
            return "Search queries have to be at least 3 characters long."
        elif len(search_query) > 150:
            search_query = search_query[:150]
        
        try:
            log.info(f"Looking up {query} on MyAnimeList...")
            if anime: r: Response = requests.get(f"{MAL_API_A_SEARCH_URL}{search_query}")
            else: r: Response = requests.get(f"{MAL_API_M_SEARCH_URL}{query}")

            if r.status_code == 200:
                data: list[dict] | None = r.json().get("data")
                if not data: raise TypeError
                first_entry: dict = data[0]
                url: str | None = first_entry.get("url")
                titles: list[dict] | None = first_entry.get("titles")
                if not url: raise TypeError
                if titles:
                    title: str | None = titles[0].get("title")
                    if title:
                        log.info(f"Found {title}")
                    else: log.info(f"Found {url}")
                else: log.info(f"Found {url}")
                return url
            elif r.status_code == 400:
                return "That was an invalid request"
            elif r.status_code == 410:
                return "I could not fetch any information, the MyAnimeList search API url has changed."
            elif r.status_code == 429:
                return "I'm being rate-limited because of too many requests, try again in a few seconds."
            else:
                log.error(f"Lookup failed ({r.status_code}).")
                return "I could not find an entry or could not fetch any information, maybe try again in a few seconds."
        except (ConnectionError, JSONDecodeError, TypeError) as e:
            log.error(f"Look up failed. {type(e)}\n{e.__str__()}")
            return "I could not find an entry or could not fetch any information, maybe try again in a few seconds."


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(Misc(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Misc")
