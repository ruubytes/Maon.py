import discord
import asyncio
from async_timeout import timeout
from os.path import isdir
from os.path import isfile
from math import ceil
from os import walk
from configs import custom
from configs import settings


class GuildBrowser:
    __slots__ = ["client", "audio", "filebrowser", "browser_type", "message", "channel", "window_message", "id",
                 "title", "home_dir", "current_dir", "dir_list", "dir_items", "current_page", "max_pages", "slot_names",
                 "slot_types", "cmd_queue", "cmd_reaction", "cmd_slot_list", "cmd_nav_list", "emoji_list", "running",
                 "filebrowser_task"]

    def __init__(self, client, message, browser_type: int):
        self.client = client
        self.audio = self.client.get_cog("Audio")
        self.filebrowser = self.client.get_cog("FileBrowser")
        self.browser_type = browser_type
        self.message = message
        self.channel = message.channel
        self.window_message = {}
        self.id = 0
        if browser_type == 0:
            self.title = "Music Browser"
            self.home_dir = settings.MUSIC_PATH
        else:
            self.title = "Sound Effects (SFX) Browser"
            self.home_dir = settings.SFX_PATH
        self.current_dir = self.home_dir
        self.dir_list = []
        self.dir_items = []
        self.current_page = 1
        self.max_pages = 1
        self.slot_names = []
        self.slot_types = []

        self.cmd_queue = asyncio.Queue()
        self.cmd_slot_list = settings.CMD_SLOT_REACTIONS
        self.cmd_nav_list = settings.CMD_NAV_REACTIONS
        self.emoji_list = settings.EMOJI_LIST
        self.running = True

        print("[{}] Creating file browser...".format(self.message.guild.name))
        self.filebrowser_task = self.client.loop.create_task(self.filebrowser_window(message))
        print("[{}] File browser created.".format(self.message.guild.name))

    async def filebrowser_window(self, message):
        """ The main loop of the file browser. Waits for a reaction and then updates the contents
        accordingly. """ 
        self.running = True
        await self.client.wait_until_ready()
        await self.set_content()
        self.window_message = await message.send("Generating browser...")
        self.client.loop.create_task(self.load_navigation(message))
        await self.display_window()

        try:
            while self.running:
                async with timeout(900):
                    command = await self.cmd_queue.get()
                await self.update(command)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("[{}] Closing file browser...".format(self.message.guild.name))
            browser_embed = discord.Embed(title="Media browser closed.", description="", color=custom.COLOR_HEX)
            try:
                await self.window_message.edit(content="", embed=browser_embed)
            except (discord.NotFound, RuntimeError):
                pass
            return self.filebrowser.browser_exit(self.message)
            

    async def update(self, command):
        """ Chains the functions to update the contents and edit the embed message. """
        if self.running:
            await self.execute(command)
            await self.set_content()
            await self.display_window()
        else:
            self.filebrowser_task.cancel()

    async def execute(self, command):
        """ Executes the requested command reaction and edits the browser contents accordingly. """
        if command.emoji in self.cmd_slot_list:         # A selection
            try:
                i = self.cmd_slot_list.index(command.emoji)
                if self.slot_types[i] == 0:     # directory
                    self.current_page = 1
                    self.current_dir += self.slot_names[i] + "/"

                else:                           # file
                    url = "" + self.current_dir + self.slot_names[i]
                    if self.browser_type == 0:
                        await self.audio.fb_play(self.message, url)
                    else:
                        await self.audio.fb_sfx(self.message, url)
            except IndexError:
                return

        elif command.emoji == self.cmd_nav_list[0]:     # Back
            if self.current_dir != self.home_dir:
                self.current_page = 1
                self.current_dir = self.current_dir[:self.current_dir.rfind("/")]
                cut_dir = (self.current_dir.rfind("/") + 1)
                self.current_dir = self.current_dir[:cut_dir]

        elif command.emoji == self.cmd_nav_list[1]:     # Previous Page
            if self.current_page > 1:
                self.current_page -= 1

        elif command.emoji == self.cmd_nav_list[2]:     # Next Page
            if self.current_page < self.max_pages:
                self.current_page += 1

        elif command.emoji == self.cmd_nav_list[3]:     # Close Browser
            self.running = False
            self.filebrowser_task.cancel()
            return

        else:
            return print("{} not recognized...")

    async def display_window(self):
        """ Builds the embed message view of the file browser. """
        content = "Directory: " + self.current_dir[1:] + "\n\n"
        if self.current_dir != self.home_dir:
            content += ":leftwards_arrow_with_hook: Back\n"

        i = 0
        for slot_type in self.slot_types:
            number_emoji = self.emoji_list[i]
            if slot_type == 0:
                item_string = "" + number_emoji + " :file_folder: " + self.slot_names[i] + "\n"
            else:
                item_string = "" + number_emoji + " :musical_note: " + self.slot_names[i] + "\n"
            content += item_string
            i += 1

        content += "\n"
        if self.current_page > 1:
            content += ":arrow_left: "
        content += "{} / {} pages ".format(self.current_page, self.max_pages)
        if self.current_page < self.max_pages:
            content += ":arrow_right:"

        browser_embed = discord.Embed(title=self.title, description=content, color=custom.COLOR_HEX)
        return await self.window_message.edit(content="", embed=browser_embed)

    async def set_content(self):
        """ Builds lists of the folder contents for the file browser. """
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

        self.slot_names.clear()
        self.slot_types.clear()
        diff = self.dir_items - self.max_pages * 11
        if self.current_page == self.max_pages:
            page_items_end = ((self.current_page * 11) - diff)
        else:
            page_items_end = (self.current_page * 11)
        page_items_start = ((self.current_page * 11) - 11)

        for item in self.dir_list[page_items_start:page_items_end]:
            self.slot_names.append(item)
            if isdir((self.current_dir + item)):
                self.slot_types.append(0)
            elif isfile((self.current_dir + item)):
                self.slot_types.append(1)

    async def load_navigation(self, message):
        """ Adds all the reactions to the browser message the user can navigate the browser with. """
        self.id = self.window_message.id
        await self.window_message.add_reaction("\u21A9")  # Back
        await self.window_message.add_reaction("\u0030\u20E3")  # 0
        await self.window_message.add_reaction("\u0031\u20E3")  # 1
        await self.window_message.add_reaction("\u0032\u20E3")  # 2
        await self.window_message.add_reaction("\u0033\u20E3")  # 3
        await self.window_message.add_reaction("\u0034\u20E3")  # 4
        await self.window_message.add_reaction("\u0035\u20E3")  # 5
        await self.window_message.add_reaction("\u0036\u20E3")  # 6
        await self.window_message.add_reaction("\u0037\u20E3")  # 7
        await self.window_message.add_reaction("\u0038\u20E3")  # 8
        await self.window_message.add_reaction("\u0039\u20E3")  # 9
        await self.window_message.add_reaction("\N{KEYCAP TEN}")  # 10
        await self.window_message.add_reaction("\u2B05")  # prev
        return await self.window_message.add_reaction("\u27A1")  # next
        # return await self.window_message.add_reaction("\u274E")  # close
