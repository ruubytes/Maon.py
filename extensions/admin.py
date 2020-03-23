from asyncio import sleep
from asyncio import CancelledError
from discord.ext import commands
from random import choice
import configuration as config
import subprocess
import discord


# TODO restart subprocess doesn't work
class Admin(commands.Cog):
    __slots__ = ["client", "status_task", "running"]

    def __init__(self, client):
        self.client = client
        self.running = True

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["kill"])
    @commands.is_owner()
    async def shutdown(self, message):
        print("\tI stopped myself from taking over the world.\n")
        await self.client.close()
        raise SystemExit

    @commands.command()
    @commands.is_owner()
    async def restart(self, message):
        await self.client.close()
        subprocess.call(["./run.sh"])
        raise SystemExit

    @commands.command()
    @commands.is_owner()
    async def reload(self, message, *, extension: str = None):
        if extension is None:
            return await message.send("Do you want me to reload a specific extension or `all`?")
        elif extension in config.EXTENSION_LIST:
            print("Reloading {} extension...".format(extension))
            self.client.reload_extension(config.EXTENSION_PATH + extension)
            return await message.send("{} extension reloaded!".format(extension))
        elif extension == "all":
            for ext in config.EXTENSION_LIST:
                print("Reloading {} extension...".format(ext))
                self.client.reload_extension(config.EXTENSION_PATH + ext)
            return await message.send("All extensions reloaded!")
        else:
            return await message.send("I don't think I have an extension called {}.".format(extension))

    @commands.command(aliases=["clear", "delete"])
    @commands.is_owner()
    @commands.guild_only()
    async def remove(self, message, *, number: int = None):
        if number is None:
            return await message.send("How many messages do you want me to delete? (max 50 messages)")
        else:
            try:
                amount = int(number)
                if (amount <= 50) and (amount >= 1):
                    await message.channel.purge(limit = amount + 1)
                    return await message.send("{} messages deleted.".format(amount), delete_after = 5)
                else:
                    return await message.send("How many messages do you want me to delete? (max 50 messages)")
            except (TypeError, ValueError):
                return await message.send("How many messages do you want me to delete? (max 50 messages)")

    @commands.command()
    @commands.is_owner()
    async def status(self, message, *, activity: str = None):
        if activity is None:
            return await message.send("Usage: <prefix> status `listening`/`playing`/`watching` <text>")

        try:
            if activity.lower().startswith("cancel"):
                print("[{}|{}] Cancelling status loop...".format(message.guild.name, message.guild.id))
                self.status_task.cancel()
                return await message.send("Cancelled my status update loop.")

            text = activity.split(" ", 1)[1]
            if activity.lower().startswith("listening"):
                if text.lower().startswith("to "):
                    text = text[3:]
                await self.client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name=text))
                return await message.send("Changed my status, I'm now listening to {}".format(text))
            elif activity.lower().startswith("playing"):
                await self.client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.playing, name=text))
                return await message.send("Changed my status, I'm now playing {}".format(text))
            elif activity.lower().startswith("watching"):
                await self.client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.watching, name=text))
                return await message.send("Changed my status, I'm now watching {}".format(text))
            else:
                return await message.send("Usage: <prefix> status `listening`/`playing`/`watching` <text>")

        except IndexError:
            return await message.send("Usage: <prefix> status `listening`/`playing`/`watching` <text>")

    @commands.command()
    async def emojiname(self, message, emoji):
        return await message.send(emoji.encode('ascii', 'namereplace'))

    async def status_loop(self):
        while self.running:
            activity = choice(["listening", "watching", "playing"])
            if activity == "listening":
                text = choice(config.STATUS_TEXT_LISTENING_TO)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.listening, name=text))

            elif activity == "watching":
                text = choice(config.STATUS_TEXT_WATCHING)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=text))

            else:
                text = choice(config.STATUS_TEXT_PLAYING)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.playing, name=text))

            try:
                await sleep(3600)
            except CancelledError:
                self.running = False
                return

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_ready(self):
        print("\tI'm ready!\n")
        self.status_task = self.client.loop.create_task(self.status_loop())


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Admin(client))


def teardown(client):
    client.remove_cog(Admin)
