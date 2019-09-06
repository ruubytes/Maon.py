import asyncio
import configuration
import dialogue
import discord
from discord.ext import commands
from random import randint
from random import choice

class Fun(commands.Cog):
    __slots__ = ("client")
    def __init__(self, client):
        self.client = client
        self.prefix = configuration.PREFIX_FAST

        self.client.loop.create_task(self.activity_loop())

    # Activity Loop Task -------------------------------------------------------
    async def activity_loop(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            type_int = randint(1, 3)
            if (type_int == 1):
                activity_name = choice(dialogue.playing_strings)
            elif (type_int == 2):
                activity_name = choice(dialogue.listeningto_strings)
            elif (type_int == 3):
                activity_name = choice(dialogue.watching_strings)
            else:
                continue
            await self.client.change_presence(activity = discord.Activity(
                type = type_int, name = activity_name))
            await asyncio.sleep(7200)

    # Events ═══════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == self.prefix:
            await message.channel.trigger_typing()
            await asyncio.sleep(1)
            return await message.channel.send(choice(dialogue.default_reply))
        elif message.content.lower().startswith(self.prefix):
            for question in dialogue.eight_ball_question:
                if message.content.lower().startswith(question, (len(self.prefix) + 1)):
                    await message.channel.trigger_typing()
                    await asyncio.sleep(1)
                    return await message.channel.send(choice(dialogue.eight_ball_reply))

def setup(client):
    client.add_cog(Fun(client))
