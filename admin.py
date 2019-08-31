import asyncio
import login
import logger
import configuration
import discord
from discord.ext import commands
from datetime import datetime
from time import time
from time import monotonic

class Admin(commands.Cog):
    __slots__ = ("client", "owner_id")
    def __init__(self, client):
        self.client = client
        self.owner_id = login.OWNER_ID

    @commands.command()
    async def test(self, message):
        return await message.send("Test very successful.")

    @commands.command()
    async def ping(self, message):
        start = monotonic()
        pong = await message.send("Pong!")
        delta = (monotonic() - start) * 1000
        logger.log_info("ping: {}ms".format(round(delta, 2)))
        return await pong.edit(content = "Pong! `{}ms`".format(round(delta, 2)))

    @commands.command(aliases = ["help"])
    async def infocard(self, message):
        command_print = "".join(configuration.COMMANDLIST_EMBED_PREP)
        new_title = "```" + configuration.SIGNATURE + "```"
        new_embed = discord.Embed(title = new_title, description = command_print,
            color = configuration.COLOR_HEX)
        new_embed.set_thumbnail(url = self.client.user.avatar_url)
        return await message.send(embed = new_embed)

    @commands.command()
    @commands.is_owner()
    async def refresh(self, message, *, extension: str = None):
        if extension is None:
            return await message.send(dialogue.ADMIN_HELP_REFRESH, delete_after = 20)
        elif extension in configuration.EXTENSION_LIST:
            logger.log_info("refreshing {}...".format(extension))
            self.client.unload_extension(extension)
            self.client.load_extension(extension)
            logger.log_info("{} refreshed".format(extension))
            return await message.send("{} extension refreshed".format(extension))
        elif extension == "all":
            for ext in configuration.EXTENSION_LIST:
                logger.log_info("refreshing {}...".format(ext))
                self.client.unload_extension(ext)
                self.client.load_extension(ext)
                logger.log_info("{} refreshed".format(ext))
            return await message.send("All extensions refreshed.")
        else:
            return await message.send(dialogue.ADMIN_EM_EXT_NOT_FOUND.format(extension))

    @commands.command()
    @commands.is_owner()
    async def echo(self, message, *, input: str = None):
        if input is None:
            return await message.send("...psst, I need an input to echo~", delete_after = 10)
        else:
            await message.channel.purge(limit = 1)
            return await message.send(input)

    @commands.command(aliases = ["clear", "delete"])
    @commands.is_owner()
    async def remove(self, message, amount = None):
        try:
            if amount is None:
                return await message.send("How many messages do you want me to delete?", delete_after = 10)
            elif (int(amount) > 100):
                return await message.send("You can't purge more than 100 messages at a time.", delete_after = 10)
            else:
                await message.channel.purge(limit = (int(float(amount)) + 1))
                return await message.send("{} messages deleted.".format(int(amount)), delete_after = 5)
        except (TypeError, ValueError) as e:
            return await message.send("I need a valid number...", delete_after = 10)

    @commands.command()
    @commands.is_owner()
    async def shutmedown(self, message):
        raise SystemExit

    @commands.command()
    async def emojiname(self, message, emoji):
        return await message.send(get_emojiname(emoji))

    # Events ═══════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        #log = "({}) {}#{}: {}".format(
        #    datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S"),
        #    message.author.name,
        #    message.author.discriminator,
        #    message.content)
        #print(log)
        #with open("log.txt", "a+") as log_file:
        #    print(log, file = log_file)
        logger.log_messages(message)

    @commands.Cog.listener()
    async def on_ready(self):
        print("       I'm ready, master!        \n")

def get_emojiname(emoji):
    return emoji.encode('ascii', 'namereplace')

def setup(client):
    client.add_cog(Admin(client))
