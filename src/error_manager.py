import logbook
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import CommandError
from discord.ext.commands import CommandInvokeError
from discord.ext.commands import Context
from logging import Logger
from maon import Maon
from traceback import print_tb

log: Logger = logbook.getLogger("error_manager")


class ErrorManager(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon

    
    @Cog.listener()
    async def on_command_error(self, ctx: Context, err: CommandError) -> None | Message:
        if isinstance(err, CommandInvokeError):
            if "Missing Permissions" in err.__str__():
                log.error(f"{ctx.guild.name if ctx.guild else ctx.author.name}: I don't have the permissions to perform '{ctx.message.content}' for {ctx.author.name}\nCause: {err.__cause__}\n{print_tb(err.__traceback__) if err.__traceback__ else ''}")
        else:
            log.error(f"Unhandled error occurred!\n{err}\n{print_tb(err.__traceback__) if err.__traceback__ else ''}")


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(ErrorManager(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("ErrorManager")
