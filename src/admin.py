from __future__ import annotations
import logbook
import sys
from asyncio import all_tasks
from asyncio import create_task
from asyncio import get_running_loop
from asyncio import sleep
from asyncio import Task
from discord import Activity
from discord import ActivityType
from discord import app_commands
from discord import Guild
from discord import Interaction
from discord import Message
from discord import TextChannel
from discord.ext.commands import bot_has_guild_permissions
from discord.ext.commands import bot_has_permissions
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import has_guild_permissions
from discord.ext.commands import has_permissions
from discord.ext.commands import is_owner
from logging import Logger
from os import close
from os import execl
from os import getpid
from psutil import Process
from random import choice

from asyncio import CancelledError
from discord.app_commands import AppCommandError
from discord.ext.commands import CheckFailure

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from maon import Maon

log: Logger = logbook.getLogger("admin")


class Admin(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon
        self.status_task: Task = create_task(self.status_loop(), name="status_task")

    
    async def status_loop(self) -> None:
        await self.maon.wait_until_ready()
        try:
            while True:            
                activity: str = choice(["listening", "playing", "watching"])
                text_list: str | list[str] | None = self.maon.custom.get(f"status_{activity}")
                if not text_list or isinstance(text_list, str):
                    continue
                if activity == "listening":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.listening, name=choice(text_list)))
                elif activity == "playing":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.playing, name=choice(text_list)))
                elif activity == "watching":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.watching, name=choice(text_list)))
                else:
                    continue
                log.info(f"Set new hourly {activity} status.")
                await sleep(3600)
        except CancelledError:
            log.info(f"status_task cancelled.")

    
    async def _status_cancel(self) -> None:
        if not self.status_task.done():
            self.status_task.cancel()

    
    async def _status_restart(self) -> None:
        if self.status_task.done():
            self.status_task: Task = create_task(self.status_loop(), name="status_task")
        else:
            log.info("status_task still running.")


    @command(aliases=["kill"])
    @is_owner()
    async def shutdown(self, ctx: Context) -> None:
        log.warning("Shutting down...")
        await self.maon.close()


    @command()
    @is_owner()
    async def restart(self, ctx: Context) -> None:
        await self._restart()

    
    async def _restart(self) -> None:
        log.warning("Restarting...\n\n---\n")
        for task in [*all_tasks(get_running_loop())]:
            if not task.cancelled():
                task.cancel()
        p: Process = Process(getpid())
        for handler in p.open_files() + p.connections():
            try:
                close(handler.fd)
            except Exception as e:
                pass
        execl(sys.executable, sys.executable, *sys.argv)


    @command()
    @is_owner()
    async def reload(self, ctx: Context, ext: str | None) -> None | Message:
        if not ext:
            return await ctx.channel.send("Do you want to reload a specific extension, like `audio` or `all` all of them?")
        if ext.lower() in self.maon.extensions_list:
            log.info(f"Reloading {ext.lower()} extension...")
            await self.maon.reload_extension(f"{ext.lower()}")
            log.info(f"{ext.lower()} extension reloaded.")
            await ctx.channel.send(f"{ext.lower()} extension reloaded.")
        elif ext.lower() == "all":
            for ext in self.maon.extensions_list:
                log.info(f"Reloading {ext.lower()} extension...")
                await self.maon.reload_extension(f"{ext.lower()}")
            log.info("All extensions reloaded.")
            await ctx.channel.send("All extensions reloaded.")
        else:
            return await ctx.channel.send(f"I can't find an extension called {ext.lower()}.")
        await self.maon.sync_app_cmds()


    @app_commands.command(name="delete", description="Delete a number of messages in a channel. (Max 75)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def _remove_ac(self, itc: Interaction, amount: app_commands.Range[int, 1, 75]) -> None | Message:
        if not isinstance(itc.channel, TextChannel) or not itc.guild: return
        log.info(f"Trying to delete {amount} messages in {itc.guild.name}: {itc.channel.name} for {itc.user.name}#{itc.user.discriminator}.")
        await itc.response.send_message(f"Deleting {amount} messages.", ephemeral=True, delete_after=16)
        await itc.channel.purge(limit=amount + 1, bulk=True)

    
    @_remove_ac.error
    async def _remove_ac_error(self, itc: Interaction, e: AppCommandError) -> None:
        if isinstance(e, app_commands.CheckFailure):
            if "Bot requires Manage" in e.__str__():
                await itc.response.send_message("I lack the permissions to manage messages.")
            elif "Bot requires Read Message" in e.__str__():
                await itc.response.send_message("I lack the permissions to read the message history.")
            else:
                await itc.response.send_message("You lack the permissions to manage messages.")


    @command(aliases=["remove", "clear", "delete"])
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def _remove(self, ctx: Context, amount: int | None) -> None | Message:
        if not isinstance(ctx.channel, TextChannel) or not ctx.guild: return
        if not amount:
            return await ctx.channel.send("How many messages do you want me to purge from the chat? (Max 75 messages)")
        if amount > 0 and amount < 76:
            log.info(f"Trying to delete {amount} messages in {ctx.guild.name}: {ctx.channel.name} for {ctx.author.name}#{ctx.author.discriminator}.")
            await ctx.channel.purge(limit=amount + 1, bulk=True)
            return await ctx.channel.send(f"{amount} messages deleted.", delete_after=16)
        else:
            return await ctx.channel.send("I can only delete 75 messages at a time.")
        
    
    @_remove.error
    async def _remove_error(self, ctx: Context, e: Exception) -> None:
        if isinstance(e, CheckFailure):
            if "Bot requires Manage" in e.__str__():
                await ctx.channel.send("I lack the permissions to manage messages.")
            if "Bot requires Read Message" in e.__str__():
                await ctx.channel.send("I lack the permissions to read the message history.")
            else:
                await ctx.channel.send("You don't have permissions to manage messages.")

    
    @command()
    async def emojiname(self, ctx: Context, emoji: str | None) -> None | Message:
        if emoji: return await ctx.channel.send(f"`{str(emoji.encode('ascii', 'namereplace'))}`")

    
    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════
    @Cog.listener()
    async def on_ready(self) -> None:
        if len(self.maon.guilds) < 11:
            log.info("Maon is a member of:")
            for g in self.maon.guilds:
                log.info(f"{g.id} | {g.name}")
        log.log(logbook.RAW, "\n\tI'm ready\n")


    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        log.info(f"Joined a new guild! {guild.id} | {guild.name}")


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        log.info("Cancelling status_task...")
        self.status_task.cancel()


async def setup(maon: Maon) -> None:
    await maon.add_cog(Admin(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Admin")
