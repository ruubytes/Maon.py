import logbook
from discord.ext.commands import Cog
from logging import Logger
from maon import Maon

log: Logger = logbook.getLogger("audio")


class Audio(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon


    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(Audio(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Audio")
