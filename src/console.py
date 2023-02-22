import logbook
import sys
from aioconsole import ainput
from asyncio import create_task
from asyncio import Task
from audio import Audio
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
            "restart": self.restart,
            "reload": self.reload        
        }
        self.console_task: Task = create_task(self.console_loop(), name="console_task")

    
    async def console_loop(self) -> None:
        try:
            while True:
                cmd: str = await ainput(loop = self.maon.loop)
                log.info(f"> {cmd}")
                argv: list[str] = cmd.split(" ")
                call: Callable | None = self.commands.get(argv[0])
                if not call:
                    log.error(f"Command {cmd} not found.")
                    await self.usage()
                else:
                    await call(argv)
        except CancelledError:
            log.info(f"console_task cancelled.")


    async def usage(self, argv: list[str] | None = None) -> None:
        log.log(logbook.RAW, "Available commands:")
        for key in self.commands:
            log.log(logbook.RAW, f"\t{str(key)}")


    async def shutdown(self, argv: list[str] | None = None) -> None:
        log.warning("Shutting down...")
        await self.maon.close()


    async def restart(self, argv: list[str] | None = None) -> None:
        log.warning("Restarting...\n\n---\n")
        p: Process = Process(getpid())
        for handler in p.open_files() + p.connections():
            try:
                close(handler.fd)
            except Exception as e:
                log.warning(f"{handler} already closed.\n{e}")
        execl(sys.executable, sys.executable, *sys.argv)


    async def reload(self, argv: list[str] | None = None) -> None:
        log.info("Reload called")
        if not argv or len(argv) < 2:
            return await self.usage()
        if argv[1].lower() in self.maon.extensions_list:
            log.info(f"Reloading {argv[1].lower()} extension...")
            await self.maon.reload_extension(f"{argv[1].lower()}")
            log.info(f"{argv[1].lower()} extension reloaded.")
        elif argv[1].lower() == "all":
            for ext in self.maon.extensions_list:
                log.info(f"Reloading {ext.lower()} extension...")
                await self.maon.reload_extension(f"{ext.lower()}")
            log.info("All extensions reloaded.")
        else:
            log.info(f"I can't find an extension called {argv[1].lower()}.")

    
    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        log.info("Cancelling console_task...")
        self.console_task.cancel()


async def setup(maon: Maon) -> None:
    await maon.add_cog(Console(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Console")
