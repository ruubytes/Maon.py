import asyncio
import logger
import login
import configuration
import browserinstance
import discord
from discord.ext import commands

class Browser(commands.Cog):
    __slots__ = ("client", "cmd_reactions", "browsers")
    def __init__(self, client):
        self.client = client
        self.cmd_reactions = configuration.CMD_REACTIONS
        self.browsers = {}

    def browser_exit(self, guild):
        try:
            del self.browsers[guild.id]
            logger.log_info("({}, gid: {}) browser destroyed".format(guild.name, guild.id))
        except (AttributeError, KeyError) as e:
            logger.log_error("({}, gid: {}) browser could not be destroyed".format(guild.name, guild.id))
            pass

    # Browse Command -----------------------------------------------------------
    @commands.command()
    async def browse(self, message, *, type: str = None):
        if type is None:
            return await message.send("Do you want to browse the `music` or `sfx` folder? Or do you want to `exit` the current browser?")
        elif (type.lower() == "music") or (type.lower() == "audio"):
            type = 0
        elif (type.lower() == "sfx") or (type.lower() == "sound effects") or (type.lower() == "effects"):
            type = 1
        elif (type.lower() == "exit") or (type.lower() == "quit"):
            try:
                if self.browsers[message.guild.id]:
                    browser_embed = discord.Embed(title = "Browser closed. (Exit)",
                        description = "", color = configuration.COLOR_HEX)
                    await self.browsers[message.guild.id].browser_message.edit(content = "", embed = browser_embed)
                    await message.send("I closed the browser.", delete_after = 15)
                    return self.browser_exit(message.guild)
            except KeyError:
                return await message.send("There is no active browser.", delete_after = 15)
        else:
            return await message.send("Do you want to browse the `music` or `sfx` folder?")

        try:
            if self.browsers[message.guild.id]:
                return await message.send("A browser is currently active for your guild.", delete_after = 20)
        except KeyError:
            new_browser = browserinstance.BrowserInstance(message, type)
            self.browsers[message.guild.id] = new_browser

    # Events ═══════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (user.id == login.CLIENT_ID):
            return
        elif reaction.emoji in self.cmd_reactions:
            try:
                if (reaction.message.id == self.browsers[reaction.message.guild.id].browser_message.id):
                    await self.browsers[reaction.message.guild.id].browser_cmd.put(reaction)
                else:
                    return
            except KeyError:
                return
        else:
            return

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if (user.id == login.CLIENT_ID):
            return
        elif reaction.emoji in self.cmd_reactions:
            try:
                if (reaction.message.id == self.browsers[reaction.message.guild.id].browser_message.id):
                    await self.browsers[reaction.message.guild.id].browser_cmd.put(reaction)
                else:
                    return
            except KeyError:
                return
        else:
            return

def setup(client):
    client.add_cog(Browser(client))
