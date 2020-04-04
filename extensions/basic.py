from discord.ext import commands
from lxml import etree
from urllib import request
import configuration as config
import discord


class Basic(commands.Cog):
    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command()
    async def ping(self, message):
        return await message.send("Pong! `WebSocket: {}ms`".format(int(self.client.latency * 1000)))

    @commands.command(aliases=["info", "infocard"])
    async def help(self, message):
        command_print = config.COMMANDLIST_EMBED_PREP_START
        if message.author.id == self.client.owner_id:
            command_print += "".join(config.COMMANDLIST_EMBED_ADMIN_PREP)
        command_print += "".join(config.COMMANDLIST_EMBED_PREP)
        help_embed = discord.Embed(title=config.VERSION, description=command_print, color=config.COLOR_HEX)
        help_embed.set_thumbnail(url=self.client.user.avatar_url)
        help_embed.set_footer(text="Owner: " + 
                self.client.get_user(self.client.owner_id).name + "#" +
                self.client.get_user(self.client.owner_id).discriminator, 
            icon_url=self.client.get_user(self.client.owner_id).avatar_url)
        return await message.send(embed=help_embed)

    @commands.command()
    async def corona(self, message):
        sozial_feed = etree.HTML(request
            .urlopen("https://www.sozialministerium.at/Informationen-zum-Coronavirus/Neuartiges-Coronavirus-(2019-nCov).html")
            .read())
        cases_item = sozial_feed.xpath("//strong")
        cases_string = etree.tostring(cases_item[1], encoding="unicode")

        cases_string = cases_string.replace("<strong>Bestätigte Fälle, ", "")
        cases_string = cases_string.replace("</strong>", "")

        return await message.send(cases_string)


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Basic(client))


def teardown(client):
    client.remove_cog(Basic)
