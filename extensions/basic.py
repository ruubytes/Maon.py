from discord.ext import commands
from asyncio import sleep
import configuration as config
import discord

class Basic(commands.Cog):
    __slots__ = ["client"]

    def __init__(self, client):
        self.client = client
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
            return await message.send("`{}`".format(config.VERSION))

        commands_print_bot = config.COMMANDLIST_EMBED_PREP_START

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
            commands_print_bot += "".join(config.COMMANDLIST_EMBED_ADMIN_PREP)
        help_embed_bot = discord.Embed(
                title=config.VERSION,
                description=commands_print_bot,
                color=config.COLOR_HEX)
        help_embed_bot.set_thumbnail(url=self.client.user.avatar_url)

        commands_print_basic = "".join(config.COMMANDLIST_EMBED_BASIC_PREP)
        help_embed_basic = discord.Embed(description=commands_print_basic, color=config.COLOR_HEX)
        
        commands_print_music = "".join(config.COMMANDLIST_EMBED_MUSIC_PREP)
        help_embed_music = discord.Embed(description=commands_print_music, color=config.COLOR_HEX)
        
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
