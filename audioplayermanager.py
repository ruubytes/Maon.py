import asyncio
import configuration
import discord
from discord.ext import commands

class AudioPlayerManager(commands.Cog):
    __slots__ = ("client", "ap_cmd_reactions","audioplayers")
    def __init__(self, client):
        self.client = client
        self.ap_cmd_reactions = configuration.AP_CMD_REACTIONS
        self.audioplayers = {}

    # Cog Commands ═════════════════════════════════════════════════════════════
    @commands.command(aliases = ["musicplayer", "mp3player"])
    async def audioplayer(self, message):
        return await message.send("WIP")

    # Events ═══════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (user.id == login.CLIENT_ID):
            return
        elif reaction.emoji in self.ap_cmd_reactions:
            try:
                if (reaction.message.id == self.audioplayers[reaction.message.guild.id].audioplayer_message.id):
                    await self.audioplayers[reaction.message.guild.id].audioplayer_cmd.put(reaction)
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
        elif reaction.emoji in self.ap_cmd_reactions:
            try:
                if (reaction.message.id == self.audioplayers[reaction.message.guild.id].audioplayer_message.id):
                    await self.audioplayers[reaction.message.guild.id].audioplayer_cmd.put(reaction)
                else:
                    return
            except KeyError:
                return
        else:
            return


def setup(client):
    client.add_cog(AudioPlayerManager(client))
