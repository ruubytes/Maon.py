import discord
from discord.ext import commands
from asyncio import sleep
from src import version
from src import logbook
from configs import custom
from configs import settings


class Basic(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client = client
        self.log = logbook.getLogger(self.__class__.__name__)
        self.running = True

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command()
    async def ping(self, message):
        return await message.send("Pong! `WebSocket: {}ms`".format(int(self.client.latency * 1000)))

    @commands.command(aliases=["info", "infocard", "version"])
    async def help(self, message):
        """ Returns an embed message with all the available commands. If the owner is the requestee, also 
        adds the admin commands. """ 
        if "version" in message.invoked_with:
            return await message.send("`{}`".format(version.VERSION))

        commands_print_bot = settings.COMMANDLIST_EMBED_PREP_START

        if message.author.id == self.client.owner_id:
            commands_print_bot += "".join(settings.COMMANDLIST_EMBED_ADMIN_PREP)
        help_embed_bot = discord.Embed(
                title=version.VERSION,
                description=commands_print_bot,
                color=custom.COLOR_HEX)
        help_embed_bot.set_thumbnail(url=self.client.user.display_avatar.url)

        commands_print_basic = "".join(settings.COMMANDLIST_EMBED_BASIC_PREP)
        help_embed_basic = discord.Embed(description=commands_print_basic, color=custom.COLOR_HEX)
        
        commands_print_music = "".join(settings.COMMANDLIST_EMBED_MUSIC_PREP)
        help_embed_music = discord.Embed(description=commands_print_music, color=custom.COLOR_HEX)
        
        await message.send(embed=help_embed_bot)
        await sleep(0.25)
        await message.send(embed=help_embed_basic)
        await sleep(0.25)
        await message.send(embed=help_embed_music)


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def setup(maon: commands.Bot):
    await maon.add_cog(Basic(maon))


async def teardown(maon: commands.Bot):
    await maon.remove_cog(Basic)
