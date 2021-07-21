import discord
from discord.ext import commands
from asyncio import sleep
from src import version
from src import minfo
from configs import custom
from configs import settings


class Basic(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client = client
        self.log = minfo.getLogger(self.__class__.__name__, 0)
        self.corona_last_message = ""
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

        # In case of footer with owner ID
        """
        icon_url, user_name, user_discriminator = "", "", ""
        try:
            user_name = self.client.get_user(self.client.owner_id).name
            user_discriminator = self.client.get_user(self.client.owner_id).discriminator
            icon_url = self.client.get_user(self.client.owner_id).avatar_url
        except AttributeError:
            user_name = ""

        if (user_name != ""):
            help_embed.set_footer(text="Owner: " + 
                    user_name + "#" +
                    user_discriminator, 
                icon_url=icon_url)
        """

        if message.author.id == self.client.owner_id:
            commands_print_bot += "".join(settings.COMMANDLIST_EMBED_ADMIN_PREP)
        help_embed_bot = discord.Embed(
                title=version.VERSION,
                description=commands_print_bot,
                color=custom.COLOR_HEX)
        help_embed_bot.set_thumbnail(url=self.client.user.avatar_url)

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
def setup(client):
    client.add_cog(Basic(client))


def teardown(client):
    client.remove_cog(Basic)
