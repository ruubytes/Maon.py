from discord.ext import commands
from lxml import etree
from urllib import request
from asyncio import sleep
import configuration as config
import discord
import schedule


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
    async def corona(self, message, *, args = None):
        return await message.send("Corona is over, I've disabled this command.")
        """
        sozial_feed = etree.HTML(request
                .urlopen("https://www.sozialministerium.at/Informationen-zum-Coronavirus/Neuartiges-Coronavirus-(2019-nCov).html")
                .read())
        date_item = sozial_feed.xpath("//th")
        date_string = etree.tostring(date_item[11], encoding="unicode")
        cases_item = sozial_feed.xpath("//td")
        cases_string = etree.tostring(cases_item[9], encoding="unicode")

        date = date_string[date_string.find("Stand") + 6 : date_string.find("/th") - 6]
        value = cases_string[4 : cases_string.find("/td") - 1]
        report = "Austria has `" + value + "` confirmed cases. (`" + date + "`)"

        return await message.send(report)
        """ 


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Basic(client))


def teardown(client):
    client.remove_cog(Basic)
