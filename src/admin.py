import os
import psutil
import sys
import discord
from asyncio import sleep
from asyncio import CancelledError
from discord.ext import commands
from random import choice
from shutil import rmtree
from os import path
from src import version
from configs import custom
from configs import settings


class Admin(commands.Cog):
    __slots__ = ["client", "status_task", "running"]

    def __init__(self, client):
        self.client = client
        self.status_task = {}
        self.running = True

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["kill"])
    @commands.is_owner()
    async def shutdown(self, message):
        """ Shuts down Maon gracefully by first logging out and closing all event loops. """
        #await self.client.logout()
        await self.client.close()
        try:
            raise SystemExit
        except SystemExit:
            print("\nMaybe I'll take over the world some other time.\n")

    @commands.command()
    @commands.is_owner()
    async def restart(self, message):
        """ Restarts Maon by killing all connections and then restarts the process with the same 
        arguments. """
        #await self.client.logout()
        await self.client.close()
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            try:
                os.close(handler.fd)
            except Exception as e:
                print(e.__str__())
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command()
    @commands.is_owner()
    async def reload(self, message, *, extension: str = None):
        """ Reloads selected or all extension modules. """
        if extension is None:
            return await message.send("Do you want me to reload a specific extension or `all`?")
        elif extension.lower() in settings.EXTENSION_LIST:
            try:
                print("Reloading {} extension...".format(extension.lower()))
                self.client.reload_extension(settings.EXTENSION_PATH + extension.lower())
                return await message.send("{} extension reloaded!".format(extension.lower()))
            except discord.ext.commands.errors.ExtensionNotLoaded:
                return await message.send("Cannot reload {} because it is disabled. Did you want to `enable` it?".format(extension.lower()))
        elif extension.lower() == "all":
            for ext in settings.EXTENSION_LIST:
                try:
                    print("Reloading {} extension...".format(ext))
                    self.client.reload_extension(settings.EXTENSION_PATH + ext)
                except discord.ext.commands.errors.ExtensionNotLoaded:
                    pass
            return await message.send("All extensions reloaded!")
        else:
            return await message.send("I don't think I have an extension called {}.".format(extension.lower()))

    @commands.command()
    @commands.is_owner()
    async def disable(self, message, *, extension: str = None):
        """ Disables a specified `extension` or `all` of them. """
        if extension is None:
            return await message.send("Do you want me to disable a specific extension or `all`?")
        elif extension.lower() in settings.EXTENSION_LIST:
            try:
                print("Disabling {} extension...".format(extension.lower()))
                self.client.unload_extension(settings.EXTENSION_PATH + extension.lower())
                return await message.send("{} extension disabled!".format(extension.lower()))
            except discord.ext.commands.errors.ExtensionNotLoaded:
                return await message.send("{} extension is already disabled!".format(extension.lower()))

        elif extension.lower() == "all":
            for ext in settings.EXTENSION_LIST:
                try:
                    print("Disabling {} extension...".format(ext))
                    self.client.reload_extension(settings.EXTENSION_PATH + ext)
                except discord.ext.commands.errors.ExtensionNotLoaded:
                    pass
            return await message.send("All extensions disabled, I is small brain now and need to be restarted...")

        else:
            return await message.send("I don't think I have an extension called {}.".format(extension.lower()))
        
    @commands.command()
    @commands.is_owner()
    async def enable(self, message, *, extension: str = None):
        """ Enables a specified `extension` or `all` of them. """
        if extension is None:
            return await message.send("Do you want me to enable a specific extension or `all`?")

        elif extension.lower() in settings.EXTENSION_LIST:
            try:
                print("Enabling {} extension...".format(extension.lower()))
                self.client.load_extension(settings.EXTENSION_PATH + extension.lower())
                return await message.send("{} extension enabled!".format(extension.lower()))
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                return await message.send("{} extension is already enabled!".format(extension.lower()))

        elif extension.lower() == "all":
            for ext in settings.EXTENSION_LIST:
                try:
                    print("Enabling {} extension...".format(ext))
                    self.client.load_extension(settings.EXTENSION_PATH + ext)
                except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                    pass
            return await message.send("All disabled extensions are now enabled!")

        else:
            return await message.send("I don't think I have an extension called {}.".format(extension.lower()))

    @commands.command(aliases=["clear", "delete"])
    @commands.is_owner()
    @commands.guild_only()
    async def remove(self, message, *, number: int = None):
        """ Removes `number` `+ 1` messages from the channel the command is called in. +1 to also remove 
        the calling command. Max amount is 50 messages. """
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
        """ Sets the status message of Maon. `activity` has to start with one of the available activity
        types like `playing / watching / listening` followed by the status text that is to be displayed. """
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
    @commands.is_owner()
    async def scrub(self, message):
        """ Empties the music cache folder. """
        if path.exists(settings.TEMP_PATH):
            rmtree(settings.TEMP_PATH)
        return await message.send("Temp folder has been scrubbed.")

    @commands.command()
    async def emojiname(self, message, emoji):
        """ Returns the ASCII encode of the emoji sent with the message. """
        return await message.send(emoji.encode('ascii', 'namereplace'))

    async def status_loop(self):
        """ Updates the status message of Maon hourly. """
        server_count_flag = 0
        while self.running:
            activity = choice(["listening", "watching", "playing"])
            if server_count_flag == 0:
                text = "on " + str(len(self.client.guilds)) + " servers!"
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.playing, name=text))
                server_count_flag = 1

            elif activity == "listening":
                text = choice(custom.STATUS_TEXT_LISTENING_TO)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.listening, name=text))
                server_count_flag = 0

            elif activity == "watching":
                text = choice(custom.STATUS_TEXT_WATCHING)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=text))
                server_count_flag = 0

            else:
                text = choice(custom.STATUS_TEXT_PLAYING)
                await self.client.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.playing, name=text))
                server_count_flag = 0

            try:
                await sleep(3600)
            except CancelledError:
                self.running = False
                return

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_ready(self):
        print("\tI'm ready!\n")
        if not self.status_task:
            self.status_task = self.client.loop.create_task(self.status_loop())


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Admin(client))


def teardown(client):
    client.remove_cog(Admin)
