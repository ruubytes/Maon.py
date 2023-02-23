import logbook
import sys
from asyncio import all_tasks
from asyncio import CancelledError
from asyncio import create_task
from asyncio import get_running_loop
from asyncio import sleep
from asyncio import Task
from discord import Activity
from discord import ActivityType
from discord import Message
from discord import TextChannel
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import is_owner
from logging import Logger
from maon import Maon
from os import close
from os import execl
from os import getpid
from psutil import Process
from random import choice

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
            return await ctx.channel.send(f"{ext.lower()} extension reloaded.")
        elif ext.lower() == "all":
            for ext in self.maon.extensions_list:
                log.info(f"Reloading {ext.lower()} extension...")
                await self.maon.reload_extension(f"{ext.lower()}")
            log.info("All extensions reloaded.")
            return await ctx.channel.send("All extensions reloaded.")
        else:
            return await ctx.channel.send(f"I can't find an extension called {ext.lower()}.")

    
    @command(aliases=["clear", "delete"])
    @guild_only()
    async def remove(self, ctx: Context, amount: int | None) -> None | Message:
        if not isinstance(ctx.channel, TextChannel): return
        channel: TextChannel = ctx.channel
        if not amount:
            return await channel.send("How many messages do you want me to purge from the chat? (Max 50 messages)")
        if amount > 0 and amount < 51:
            await channel.purge(limit=amount + 1)
        else:
            return await channel.send("I can only delete 50 messages at a time.")

    
    @command()
    async def emojiname(self, ctx: Context, emoji: str | None) -> None | Message:
        if emoji: return await ctx.channel.send(f"`{str(emoji.encode('ascii', 'namereplace'))}`")

    
    @command()
    async def ping(self, ctx: Context) -> None | Message:
        lat: int = int(self.maon.latency * 1000)
        log.info(f"WebSocket latency: {lat}ms")
        return await ctx.channel.send(f"Pong! `WebSocket {lat}ms`")

    
    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════
    @Cog.listener()
    async def on_ready(self) -> None:
        log.log(logbook.RAW, "\n\tI'm ready\n")


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        log.info("Cancelling status_task...")
        self.status_task.cancel()


async def setup(maon: Maon) -> None:
    await maon.add_cog(Admin(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Admin")
