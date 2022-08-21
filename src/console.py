import os
import sys
import psutil
import asyncio
from src import logbook
from aioconsole import ainput
from discord.ext import commands

from discord import VoiceClient
from src.audioplayer import AudioPlayer


class Console(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client: commands.Bot):
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
        self.console_task: asyncio.Task = asyncio.create_task(self.console_loop(), name="console_task")


    async def console_loop(self):
        try:
            while True:
                cmd_str: str = await ainput(loop = self.client.loop)
                cmd = cmd_str.split(" ")
                self.log.info(f"> {cmd_str}")
                try:
                    await self.execute.get(cmd[0])()
                except TypeError:
                    self.log.error(f"Command {cmd_str} not found.")
                    await self.execute.get("usage")()

        except asyncio.CancelledError as e:
            pass

    
    async def usage(self, argv: 'list[str]' = None):
        self.log.info("Available commands:")
        for key in self.execute:
            self.log.info(f"\t{str(key)}")


    async def shutdown(self, argv: 'list[str]' = None):
        """ Shuts down Maon gracefully by closing all event loops and logging out. """
        self.log.warn("Shutting down Maon...")
        player: AudioPlayer
        for player in self.client.get_cog("Audio").players.values():
            player.shutdown()
        vc: VoiceClient
        for vc in self.client.voice_clients:
            await vc.disconnect()
        self.log.log(logbook.RAW, "\nMaybe I'll take over the world some other time.\n")
        await self.client.close()

    
    async def restart(self, argv: 'list[str]' = None):
        """ Restarts Maon by killing all connections and then restarts the process with the same arguments. """
        self.log.warn("Restarting Maon...")
        player: AudioPlayer
        for player in self.client.get_cog("Audio").players.values():
            player.shutdown()
        vc: VoiceClient
        for vc in self.client.voice_clients:
            await vc.disconnect()
        
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            try:
                os.close(handler.fd)
            except Exception as e:
                pass

        os.execl(sys.executable, sys.executable, *sys.argv)


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def setup(maon: commands.Bot):
    await maon.add_cog(Console(maon))


async def teardown(maon: commands.Bot):
    maon.get_cog("Console").console_loop.cancel()
    await maon.remove_cog(Console)
