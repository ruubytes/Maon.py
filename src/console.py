import asyncio
from src import admin
from src import logbook
from aioconsole import ainput
from discord.ext import commands


class Console(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client: commands.Bot = client
        self.log = logbook.getLogger(self.__class__.__name__)
        self.execute: dict = {
            "help": self.usage,
            "info": self.usage,
            "usage": self.usage,
            "kill": self.shutdown,
            "quit": self.shutdown,
            "stop": self.shutdown,
            "exit": self.shutdown,
            "restart": self.restart
        }
        self.console_task: asyncio.Task = self.client.loop.create_task(self.console_loop(), name="console_task")


    async def console_loop(self):
        try:
            while True:
                cmd_str: str = await ainput(loop = self.client.loop)
                cmd = cmd_str.split(" ")
                self.log.info(f"> {cmd_str}")
                try:
                    await self.execute.get(cmd[0])()
                except TypeError:
                    await self.execute.get("usage")()

        except asyncio.CancelledError as e:
            pass

    
    async def usage(self, argv: 'list[str]' = None):
        self.log.info("Available commands:")
        for key in self.execute:
            self.log.info(f"\t{str(key)}")


    async def shutdown(self, argv: 'list[str]' = None):
        admin_cog: admin.Admin = self.client.get_cog("Admin")
        await admin_cog.shutdown()

    
    async def restart(self, argv: 'list[str]' = None):
        admin_cog: admin.Admin = self.client.get_cog("Admin")
        await admin_cog.restart()


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Console(client))


def teardown(client):
    client.remove_cog(Console)
