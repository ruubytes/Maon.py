import login as login
from src import guildbrowser
from src import minfo
from discord.ext import commands
from configs import custom
from configs import settings


class FileBrowser(commands.Cog):
    __slots__ = ["client", "log", "CALL_MUSIC", "CALL_SFX", "CALL_CLOSE", "filebrowsers"]

    def __init__(self, client):
        self.client = client
        self.log = minfo.getLogger(self.__class__.__name__, 0)
        self.call_music = ["music", "audio"]
        self.call_sfx = ["sfx", "effects", "sound effects"]
        self.call_close = ["exit", "quit", "close"]
        self.close_reason = ["Exit", "Timeout"]
        self.filebrowsers = {}

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["b", "browser"])
    @commands.guild_only()
    async def browse(self, message, *, folder: str = None):
        """ Opens a file browser as embed message in the chat for the specified `folder` to browse local music
        or sound effects. The browser can then be navigated with emojis. """
        if folder is None:
            return await message.send(
                "You can browse the `sfx` or `music` folder, or close an existing browser with `exit`.")
        elif folder.lower() in self.call_music:
            if message.guild.id not in self.filebrowsers:
                self.filebrowsers[message.guild.id] = guildbrowser.GuildBrowser(self.client, message, 0)
            else:
                return await message.send(
                    "There is an active file browser in the server right now. You can close it with `" + custom.PREFIX[0] + "browse exit`")
        elif folder.lower() in self.call_sfx:
            if message.guild.id not in self.filebrowsers:
                self.filebrowsers[message.guild.id] = guildbrowser.GuildBrowser(self.client, message, 1)
            else:
                return await message.send(
                    "There is an active file browser in the server right now. You can close it with `" + custom.PREFIX[0] + "browse exit`")
        elif folder.lower() in self.call_close:
            if message.guild.id in self.filebrowsers:
                self.filebrowsers[message.guild.id].filebrowser_task.cancel()
            else:
                return await message.send("There is no active file browser at the moment.")
        else:
            return await message.send(
                "You can browse the `sfx` or `music` folder, or close an existing browser with `exit`. Command: `" + custom.PREFIX[0] + "browse <option>`")

    # ═══ Helper Methods ═══════════════════════════════════════════════════════════════════════════════════════════════
    def browser_exit(self, message):
        if message.guild.id in self.filebrowsers:
            del self.filebrowsers[message.guild.id]
            self.log.info(f"{message.guild.name}: File browser destroyed.")
        else:
            self.log.warn(f"{message.guild.name}: Skipped browser exit.")

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.id == login.MAON_ID:
            if (reaction.emoji in settings.CMD_SLOT_REACTIONS) or (reaction.emoji in settings.CMD_NAV_REACTIONS):
                if reaction.message.guild.id in self.filebrowsers:
                    if reaction.message.id == self.filebrowsers[reaction.message.guild.id].id:
                        await self.filebrowsers[reaction.message.guild.id].cmd_queue.put(reaction)


    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if not user.id == login.MAON_ID:
            if reaction.message.guild.id in self.filebrowsers:
                if (reaction.emoji in settings.CMD_SLOT_REACTIONS) or (reaction.emoji in settings.CMD_NAV_REACTIONS):
                    if reaction.message.id == self.filebrowsers[reaction.message.guild.id].id:
                        await self.filebrowsers[reaction.message.guild.id].cmd_queue.put(reaction)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """ Cancels the file browser if the browser message is deleted. """
        if message.guild.id in self.filebrowsers:
            if message.id == self.filebrowsers[message.guild.id].id:
                self.filebrowsers[message.guild.id].filebrowser_task.cancel()
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        """ Cancels the file browser if the browser message is deleted. """
        for m in messages:
            if m.guild.id in self.filebrowsers:
                if m.id == self.filebrowsers[m.guild.id].id:
                    self.filebrowsers[m.guild.id].filebrowser_task.cancel()



# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(FileBrowser(client))


def teardown(client):
    client.remove_cog(FileBrowser)
