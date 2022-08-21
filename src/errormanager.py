from discord.ext import commands
from discord.ext.commands import Context
from src import admin
from src import logbook


class ErrorManager(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client: commands.Bot = client
        self.log = logbook.getLogger(self.__class__.__name__)
        self.admin: admin.Admin = self.client.get_cog("Admin")


    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_command_error(self, message: Context, error):
        """ Invoked through faulty use of commands """
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            return self.log.error(f"{message.message.author} tried to invoke an invalid command in private: {message.message.content}")
        elif isinstance(error, commands.MissingPermissions):
            return self.log.error(f"{message.message.author} from {message.guild.name} tried to use \"{message.message.content}\" but I lack permissions to do that.")
        else:
            self.log.error(str(error))
            raise error


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def setup(maon: commands.Bot):
    await maon.add_cog(ErrorManager(maon))


async def teardown(maon: commands.Bot):
    await maon.remove_cog(ErrorManager)
