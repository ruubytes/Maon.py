import logbook
import sys
from aioconsole import ainput
from asyncio import create_task
from asyncio import Task
from discord.ext.commands import Cog
from logging import Logger
from maon import Maon
from os import close
from os import execl
from os import getpid
from psutil import Process
from typing import Callable

from asyncio import CancelledError

log: Logger = logbook.getLogger("console")


class Console(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon
        self.commands: dict[str, Callable] = {
            "help": self.usage,
            "usage": self.usage,
            "q": self.shutdown,
            "quit": self.shutdown,
            "exit": self.shutdown,
            "kill": self.shutdown,
            "shutdown": self.shutdown,
            "restart": self.restart
        }
        self.console_task: Task = create_task(self.console_loop(), name="console_task")

    
    async def console_loop(self) -> None:
        try:
            while True:
                cmd: str = await ainput(loop = self.maon.loop)
                log.info(f"> {cmd}")
                call: Callable | None = self.commands.get(cmd)
                if call is None:
                    log.error(f"Command {cmd} not found.")
                    await self.usage()
                else:
                    await call()
        except CancelledError:
            pass


    async def usage(self) -> None:
        log.log(logbook.RAW, "Available commands:")
        for key in self.commands:
            log.log(logbook.RAW, f"\t{str(key)}")


    async def shutdown(self) -> None:
        log.warning("Shutting down...")
        log.log(logbook.RAW, "\nMaybe I'll take over the world some other time.\n")
        await self.maon.close()


    async def restart(self) -> None:
        log.warning("Restarting...\n\n---\n")
        p: Process = Process(getpid())
        for handler in p.open_files() + p.connections():
            try:
                close(handler.fd)
            except Exception as e:
                log.warning(f"{handler} already closed.\n{e}")
        execl(sys.executable, sys.executable, *sys.argv)


async def setup(maon: Maon) -> None:
    await maon.add_cog(Console(maon))


async def teardown(maon: Maon) -> None:
    """ Clean up here, if needed, before unloading the extension """
    await maon.remove_cog("Console")
