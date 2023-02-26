import logbook
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import Context
from logging import Logger
from maon import Maon
from traceback import print_tb

from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandError
from discord.ext.commands import CommandInvokeError

log: Logger = logbook.getLogger("error_manager")


class ErrorManager(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon

    
    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: CommandError) -> None | Message:
        user: str = f"{ctx.author.name}#{ctx.author.discriminator}"
        if isinstance(e, CommandInvokeError):
            if "Missing Permissions" in e.__str__():
                log.error(f"{ctx.guild.name if ctx.guild else user}: I don't have the permissions to perform '{ctx.message.content}' for {ctx.author.name}\nCause: {e.__cause__}\n{print_tb(e.__traceback__) if e.__traceback__ else ''}")
        elif isinstance(e, CheckFailure):
            if "You are missing" in e.__str__():
                log.error(f"{user} lacked the permissions for: {ctx.invoked_with}")
            else:
                log.error(f"{ctx.guild.name if ctx.guild else user}: {e.__str__()} ({ctx.invoked_with})")
        else:
            log.error(f"Unhandled error occurred!\n{e}\n{print_tb(e.__traceback__) if e.__traceback__ else ''}")


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(ErrorManager(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("ErrorManager")
