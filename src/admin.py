import logbook
import sys
from asyncio import CancelledError
from asyncio import create_task
from asyncio import sleep
from asyncio import Task
from discord import Activity
from discord import ActivityType
from discord import CustomActivity
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
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
                activity: str = choice(["listening", "playing", "watching", "custom"])
                text_list: str | list[str] | None = self.maon.custom.get(f"status_{activity}")
                if not text_list or isinstance(text_list, str):
                    continue
                if activity == "listening":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.listening, name=choice(text_list)))
                elif activity == "playing":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.playing, name=choice(text_list)))
                elif activity == "watching":
                    await self.maon.change_presence(activity=Activity(type=ActivityType.watching, name=choice(text_list)))
                elif activity == "custom":
                    await self.maon.change_presence(activity=CustomActivity(name=choice(text_list)))
                else:
                    continue
                log.info(f"Set new hourly {activity} status.")
                await sleep(3600)
        except CancelledError:
            pass


    @command(aliases=["kill"])
    @is_owner()
    async def shutdown(self, context: Context) -> None:
        log.warning("Shutting down...")
        log.log(logbook.RAW, "\nMaybe I'll take over the world some other time.\n")
        await self.maon.close()


    @command()
    @is_owner()
    async def restart(self, context: Context) -> None:
        log.warning("Restarting...\n\n---\n")
        p: Process = Process(getpid())
        for handler in p.open_files() + p.connections():
            try:
                close(handler.fd)
            except Exception as e:
                log.warning(f"{handler} already closed.\n{e}")
        execl(sys.executable, sys.executable, *sys.argv)

    
    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════
    @Cog.listener()
    async def on_ready(self) -> None:
        log.log(logbook.RAW, "\n\tI'm ready\n")


async def setup(maon: Maon) -> None:
    await maon.add_cog(Admin(maon))


async def teardown(maon: Maon) -> None:
    """ Clean up here, if needed, before unloading the extension """
    await maon.remove_cog("Admin")
