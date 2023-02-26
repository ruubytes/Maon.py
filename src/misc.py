import logbook
import requests
from asyncio import sleep
from discord import app_commands
from discord import Interaction
from discord import Member
from discord import Message
from discord import Embed
from discord import TextChannel
from discord import User
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
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


# TODO Help: only show commands applicable to the permissions of the user asking for help
class Misc(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon


    @app_commands.command(name="ping", description="Shows Maon's websocket latency")
    async def _ac_ping(self, itc: Interaction) -> None | Message:
        return await itc.response.send_message(f"Pong! `WebSocket {await self.ping()}ms`")


    @command(aliases=["ping", "latency"])
    async def _c_ping(self, ctx: Context) -> None | Message:
        return await ctx.channel.send(f"Pong! `WebSocket {await self.ping()}ms`")
    

    async def ping(self) -> int:
        lat: int = int(self.maon.latency * 1000)
        log.info(f"WebSocket latency: {lat}ms")
        return lat


    @app_commands.command(name="help", description="Display all of Maon's available commands and functionalities")
    async def _ac_help(self, itc: Interaction) -> None | Message:
        embeds: list[Embed] = await self.get_help_embeds(itc.user)
        await itc.response.send_message(embed=embeds[0])
        embeds.pop(0)
        await sleep(.25)
        for embed in embeds:
            if isinstance(itc.channel, TextChannel):
                await itc.channel.send(embed=embed)
                await sleep(.25)
    

    @command(aliases=["h", "help", "info", "infocard"])
    async def _c_help(self, ctx: Context) -> None | Message:
        embeds: list[Embed] = await self.get_help_embeds(ctx.author)
        for embed in embeds:
            await ctx.channel.send(embed=embed)
            await sleep(.25)
    

    async def get_help_embeds(self, user: User | Member) -> list[Embed]:
        prefix: str = await self.maon.get_prefix_str()
        color: int = await self.maon.get_color_accent()
        embeds: list[Embed] = []
        if user.id == self.maon.owner_id:
            cmds_embed_admin_title: str = f":flag_kp: ***Owner Commands***:"
            cmds_embed_admin_list: list[str] = [
                f"`{prefix}shutdown`　Shuts Maon down.\n",
                f"`{prefix}reload <ext / config / all>`　Reload an extension or all of them, or reload from the custom or settings files.\n",
                f"`{prefix}status <cancel / restart>`　Cancels the hourly status message change or restarts it.\n",
                f"`{prefix}status <listening / watching / playing> <text>`　Sets Maon's status message.\n"
            ]
            embeds.append(Embed(title=cmds_embed_admin_title, description="".join(cmds_embed_admin_list), color=color))

        cmds_embed_mod_title: str = f":rainbow_flag: ***Moderator Commands***:"
        cmds_embed_mod_list: list[str] = [
            f"`{prefix}remove <0 - 50>`　Delete a number of messages in bulk.\n"
        ]
        embeds.append(Embed(title=cmds_embed_mod_title, description="".join(cmds_embed_mod_list), color=color))
        cmds_embed_misc_title: str = f":beginner: ***Misc Commands***:"
        cmds_embed_misc_list: list[str] = [
            f"`{prefix}ping`　Displays Maon's websocket latency.\n",
            f"`{prefix}flip`　Flip a coin.\n",
            f"`{prefix}anime <search query>`　Look up an anime show on MyAnimeList.\n",
            f"`{prefix}manga <search query>`　Look up a manga on MyAnimeList.\n",
            f"`{prefix}<question>`　Maon will reply to a closed (am, is, are, do, can...) question.\n"
        ]
        embeds.append(Embed(title=cmds_embed_misc_title, description="".join(cmds_embed_misc_list), color=color))
        return embeds



    @app_commands.command(name="coin", description="Flip a coin!")
    async def _ac_flip(self, itc: Interaction) -> None | Message:
        return await itc.response.send_message(f"It's {choice(['heads', 'tails'])}!")

    
    @command(aliases=["coin", "flip", "toss"])
    async def _c_flip(self, ctx: Context) -> None | Message:
        return await ctx.channel.send(f"It's {choice(['heads', 'tails'])}!")


    @app_commands.command(name="anime", description="Search for an anime on MyAnimeList")
    @app_commands.describe(search="Search query for an anime on MyAnimeList. (min 3 characters)")
    async def _ac_mal_anime(self, itc: Interaction, search: str) -> None | Message:
        return await itc.response.send_message(await self.mal(search))
    

    @app_commands.command(name="manga", description="Search for a manga on MyAnimeList")
    @app_commands.describe(search="Search query for a manga on MyAnimeList. (min 3 characters)")
    async def _ac_mal_manga(self, itc: Interaction, search: str) -> None | Message:
        return await itc.response.send_message(await self.mal(search, anime=False))
    

    @command(aliases=["mal", "anime", "animu", "manga", "mango", "myanimelist"])
    async def _c_mal(self, ctx: Context, *argv: str) -> None | Message:
        prefix: str = await self.maon.get_prefix_str()
        if not argv:
            return await ctx.channel.send(f"You can search for an anime or manga if you provide me a search term, like `{prefix}anime Psycho-Pass`")
        query: str = " ".join(argv)
        if ctx.invoked_with == "manga":
            return await ctx.channel.send(await self.mal(query, anime=False))
        else:
            return await ctx.channel.send(await self.mal(query))


    async def mal(self, query: str, anime: bool = True) -> str:
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
            else: r: Response = requests.get(f"{MAL_API_M_SEARCH_URL}{search_query}")

            if r.status_code == 200:
                data: list[dict] | None = r.json().get("data")
                if not data: 
                    log.info(f"No MyAnimeList entry found for: {query}")
                    return f"I could not find an entry for the requested query: {query}"
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
