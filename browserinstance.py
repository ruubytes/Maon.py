import asyncio
import logger
import configuration
import discord
from discord.ext import commands
from os.path import isdir
from os.path import isfile
from os import listdir
from os import walk
from async_timeout import timeout
from math import ceil

# TODO: Rewrite bottom functions into loops with lists

class BrowserInstance:
    __slots__ = ("client", "user_message", "guild", "channel", "browser_user", "browser_message",
        "type", "home_dir", "current_dir", "dir_list", "dir_items",
        "current_page", "max_pages", "slots_names", "slots_types", "audio_cog", "browser_cog",
        "browser_cmd", "cmd_list")
    def __init__(self, message, type):
        self.client = message.bot
        self.user_message = message
        self.guild = message.guild
        self.channel = message.channel
        self.browser_user = message.author
        self.browser_message = {}
        self.type = type # 0: music, 1: sfx
        self.home_dir = ""
        self.current_dir = ""
        self.dir_list = []
        self.dir_items = 0
        self.current_page = 1
        self.max_pages = 1
        self.slots_names = []
        self.slots_types = []
        self.audio_cog = self.client.get_cog("Audio")
        self.browser_cog = self.client.get_cog("Browser")
        self.browser_cmd = asyncio.Queue()
        self.cmd_list = configuration.CMD_REACTIONS

        if (self.type == 0):
            self.home_dir = configuration.MUSIC_PATH
            self.current_dir = self.home_dir
        else:
            self.home_dir = configuration.SFX_PATH
            self.current_dir = self.home_dir

        self.client.loop.create_task(self.browser_window())
        logger.log_info("({} , gid: {}) browser created".format(self.guild.name, self.guild.id))

    # Browser Window -----------------------------------------------------------
    async def browser_window(self):
        await self.client.wait_until_ready()
        self.browser_message = await self.channel.send("Generating browser...")
        await self.browser_data()
        await self.load_navigation()
        await self.browser_display()
        while not self.client.is_closed():
            try:
                async with timeout(900):
                    cmd = await self.browser_cmd.get()
            except asyncio.TimeoutError:
                browser_embed = discord.Embed(title = "Browser closed. (Timeout)",
                    description = "", color = configuration.COLOR_HEX)
                await self.browser_message.edit(content = "", embed = browser_embed)
                return self.browser_cog.browser_exit(self.guild)

            await self.browser_execute_cmd(cmd)
            await self.browser_data()
            await self.browser_display()

    # Browser Execute Command --------------------------------------------------
    async def browser_execute_cmd(self, cmd):
        if (cmd.emoji == self.cmd_list[0]):  # 0
            try:
                if self.slots_types[0] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[0] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[0]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[0]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[1]): # 1
            try:
                if self.slots_types[1] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[1] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[1]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[1]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[2]): # 2
            try:
                if self.slots_types[2] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[2] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[2]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[2]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[3]): # 3
            try:
                if self.slots_types[3] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[3] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[3]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[3]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[4]):
            try:
                if self.slots_types[4] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[4] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[4]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[4]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[5]):
            try:
                if self.slots_types[5] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[5] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[5]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[5]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[6]):
            try:
                if self.slots_types[6] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[6] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[6]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[6]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[7]):
            try:
                if self.slots_types[7] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[7] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[7]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[7]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[8]):
            try:
                if self.slots_types[8] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[8] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[8]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[8]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[9]):
            try:
                if self.slots_types[9] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[9] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[9]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[9]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[10]): # 10
            try:
                if self.slots_types[10] == 0: # 0 is directory
                    self.current_page = 1
                    self.current_dir = self.current_dir + self.slots_names[10] + "/"

                else:
                    if (self.type == 0):
                        url = "" + self.current_dir + self.slots_names[10]
                        await self.audio_cog.browser_play(self.user_message, url)
                    else:
                        url = "" + self.current_dir + self.slots_names[10]
                        await self.audio_cog.browser_sfx(self.user_message, url)
            except IndexError:
                return

        elif (cmd.emoji == self.cmd_list[11]): # Back
            if self.current_dir != self.home_dir:
                self.current_page = 1
                self.current_dir = self.current_dir[:self.current_dir.rfind('/')]
                cut_dir = (self.current_dir.rfind('/') + 1)
                self.current_dir = self.current_dir[:cut_dir]
                return
            else:
                return

        elif (cmd.emoji == self.cmd_list[12]): # Previous page
            if self.current_page > 1:
                self.current_page -= 1
            else:
                return

        elif (cmd.emoji == self.cmd_list[13]): # Next page
            if self.current_page < self.max_pages:
                self.current_page += 1
                return
            else:
                return

        else:
            return await self.channel.send("Command {} called.".format(cmd))

    # Browser Data -------------------------------------------------------------
    async def browser_data(self):
        self.dir_list.clear()
        for (root, dirs, files) in walk(self.current_dir):
            self.dir_list.extend(dirs)
            self.dir_list.sort()
            break
        for (root, dirs, files) in walk(self.current_dir):
            files.sort()
            self.dir_list.extend(files)
            break
        self.dir_items = len(self.dir_list)
        self.max_pages = int(ceil(float(self.dir_items) / 11))

        self.slots_names.clear()
        self.slots_types.clear()
        diff = self.dir_items - self.max_pages * 11
        if self.current_page == self.max_pages:
            page_items_end = ((self.current_page * 11) - diff)
        else:
            page_items_end = (self.current_page * 11)
        page_items_start = ((self.current_page * 11) - 11)

        for item in self.dir_list[page_items_start:page_items_end]:
            self.slots_names.append(item)
            if isdir((self.current_dir + item)):
                self.slots_types.append(0)
            elif isfile((self.current_dir + item)):
                self.slots_types.append(1)

    # Browser Display ----------------------------------------------------------
    async def browser_display(self):
        browser_title = ""
        if self.type == 0:
            browser_title = "Music Browser"
        else:
            browser_title = "Sound Effects (SFX) Browser"

        item_string = ""
        browser_content = "Directory: " + self.current_dir[1:] + "\n\n"
        if self.current_dir != self.home_dir:
            browser_content = browser_content + ":leftwards_arrow_with_hook: Back\n"

        counter = 0
        number_emoji = ""
        for type in self.slots_types:
            number_emoji = choose_symbol(counter)
            if type == 0:
                item_string = "" + number_emoji + " :file_folder: " + self.slots_names[counter] + "\n"
            else:
                item_string = "" + number_emoji + " :musical_note: " + self.slots_names[counter] + "\n"
            browser_content = browser_content + item_string
            counter += 1

        browser_content = browser_content + "\n"
        if self.current_page > 1:
            browser_content = browser_content + ":arrow_left: "
        browser_content = browser_content + "{} / {} pages ".format(self.current_page, self.max_pages)
        if self.current_page < self.max_pages:
            browser_content = browser_content + ":arrow_right:"

        browser_embed = discord.Embed(title = browser_title,
            description = browser_content, color = configuration.COLOR_HEX)

        return await self.browser_message.edit(content = "", embed = browser_embed)

    # Navigation Reactions -----------------------------------------------------
    async def load_navigation(self):
        await self.browser_message.add_reaction("\u21A9") # Back
        await self.browser_message.add_reaction("\u0030\u20E3") # 0
        await self.browser_message.add_reaction("\u0031\u20E3") # 1
        await self.browser_message.add_reaction("\u0032\u20E3") # 2
        await self.browser_message.add_reaction("\u0033\u20E3") # 3
        await self.browser_message.add_reaction("\u0034\u20E3") # 4
        await self.browser_message.add_reaction("\u0035\u20E3") # 5
        await self.browser_message.add_reaction("\u0036\u20E3") # 6
        await self.browser_message.add_reaction("\u0037\u20E3") # 7
        await self.browser_message.add_reaction("\u0038\u20E3") # 8
        await self.browser_message.add_reaction("\u0039\u20E3") # 9
        await self.browser_message.add_reaction("\N{KEYCAP TEN}") # 10
        await self.browser_message.add_reaction("\u2B05") # prev
        await self.browser_message.add_reaction("\u27A1") # next
        return

# Slot Emoji -------------------------------------------------------------------
def choose_symbol(counter):
    emoji = ""
    if counter == 0:
        emoji = ":zero:"
        return emoji
    elif counter == 1:
        emoji = ":one:"
        return emoji
    elif counter == 2:
        emoji = ":two:"
        return emoji
    elif counter == 3:
        emoji = ":three:"
        return emoji
    elif counter == 4:
        emoji = ":four:"
        return emoji
    elif counter == 5:
        emoji = ":five:"
        return emoji
    elif counter == 6:
        emoji = ":six:"
        return emoji
    elif counter == 7:
        emoji = ":seven:"
        return emoji
    elif counter == 8:
        emoji = ":eight:"
        return emoji
    elif counter == 9:
        emoji = ":nine:"
        return emoji
    elif counter == 10:
        emoji = ":keycap_ten:"
        return emoji
