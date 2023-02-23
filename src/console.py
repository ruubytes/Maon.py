import logbook
from admin import Admin
from aioconsole import ainput
from asyncio import create_task
from asyncio import Task
from discord import Activity
from discord import ActivityType
from discord.ext.commands import Cog
from logging import Logger
from maon import Maon
from random import choice
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
            "reload": self.reload,
            "save": self.save,
            "status": self.status
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
        admin: Admin | None = self.maon.get_cog("Admin") # type: ignore
        if admin: await admin._restart()


    async def reload(self, argv: list[str] | None = None) -> None:
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
        elif argv[1].lower() == "settings":
            await self.maon.reload_settings()
        elif argv[1].lower() in ["custom", "customization"]:
            await self.maon.reload_customization()
        else:
            log.info(f"I can't find an extension or configuration file called {argv[1].lower()}.")

    
    async def save(self, argv: list[str] | None = None) -> None:
        if not argv or len(argv) < 2:
            return await self.usage()
        if argv[1].lower() == "settings":
            await self.maon.save_settings()
        elif argv[1].lower() in ["custom", "customization"]:
            await self.maon.save_customization()  
        else:
            log.info("Usage: save <settings/custom>")


    async def status(self, argv: list[str] | None = None) -> None:
        if not argv or len(argv) < 2:
            return log.info("Usage: \n\tstatus <(cancel / restart)>\n\tstatus <listening / playing / watching> <text>")
        admin: Admin | None = self.maon.get_cog("Admin") # type: ignore
        if admin and argv[1].lower() == "cancel":
            await admin._status_cancel()
        elif admin and argv[1].lower() == "restart":
            await admin._status_restart()
        elif admin and len(argv) > 2:
            if argv[1].lower() == "listening":
                argv.pop(0)
                argv.pop(0)
                text: str = " ".join(argv)
                await self.maon.change_presence(activity=Activity(type=ActivityType.listening, name=text))
            elif argv[1].lower() == "playing":
                argv.pop(0)
                argv.pop(0)
                text: str = " ".join(argv)
                await self.maon.change_presence(activity=Activity(type=ActivityType.playing, name=text))
            elif argv[1].lower() == "watching":
                argv.pop(0)
                argv.pop(0)
                text: str = " ".join(argv)
                await self.maon.change_presence(activity=Activity(type=ActivityType.watching, name=text))
            else:
                log.info("Usage: \n\tstatus <(cancel / restart)>\n\tstatus <listening / playing / watching> <text>")
        else:
            log.info("Usage: \n\tstatus <(cancel / restart)>\n\tstatus <listening / playing / watching> <text>")

    
    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        log.info("Cancelling console_task...")
        self.console_task.cancel()


async def setup(maon: Maon) -> None:
    await maon.add_cog(Console(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Console")
