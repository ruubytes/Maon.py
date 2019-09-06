import asyncio
import os.path
import logger
import configuration
import audioplayer
import discord
import urllib.request
from time import sleep
from lxml import etree
from discord.ext import commands
from tinytag import TinyTag
from tinytag import TinyTagException

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class Audio(commands.Cog):
    __slots__ = ("client", "players", "history")
    def __init__(self, client):
        self.client = client
        self.players = {}
        self.history = {}
        self.sfx_shortcut = configuration.SFX_SHORTCUT

    def player_exit(self, guild):
        try:
            del self.players[guild.id]
            logger.log_info("({}, gid: {}) musicplayer destroyed".format(guild.name, guild.id))
        except (AttributeError, KeyError) as e:
            logger.log_error("({}, gid: {}) musicplayer could not be destroyed".format(guild.name, guild.id))
            pass

    # Play Command ═════════════════════════════════════════════════════════════
    @commands.command()
    async def play(self, message, *, url: str = None):
        await message.trigger_typing()
        if not await check_voice_connectivity(message):
            return

        if url is None:
            return await message.send("I need a Youtube link or file path to play.", delete_after = 20)
        elif url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/"):
            queue_item = prepare_queue_link_source(url)
        elif (os.path.exists(configuration.MUSIC_PATH + url + ".mp3")):
            queue_item = prepare_queue_local_source(url, ".mp3")
        elif (os.path.exists(configuration.MUSIC_PATH + url + ".wav")):
            queue_item = prepare_queue_local_source(url, ".wav")
        else:
            return await message.send("I need a Youtube link or file path to play.", delete_after = 20)

        try:
            player = self.players[message.guild.id]
        except KeyError:
            self.players[message.guild.id] = audioplayer.AudioPlayer(message)
        await self.players[message.guild.id].queue.put(queue_item)
        if message.guild.voice_client.is_playing():
            await message.send("{} has been added to the queue.".format(queue_item.get("title")), delete_after = 20)

    # Browser Play Command -----------------------------------------------------
    async def browser_play(self, message, url):
        try:
            tag = TinyTag.get(url)
        except TinyTagException:
            return

        if not await check_voice_connectivity(message):
            return

        if (tag.title == None):
            tag.title = url[url.rfind('/'):]
        queue_item = {}
        queue_item["title"] = tag.title
        queue_item["url"] = url
        queue_item["source_type"] = 0

        try:
            player = self.players[message.guild.id]
        except KeyError:
            self.players[message.guild.id] = audioplayer.AudioPlayer(message)
        await self.players[message.guild.id].queue.put(queue_item)
        if message.guild.voice_client.is_playing():
            await message.send("{} has been added to the queue.".format(queue_item.get("title")), delete_after = 20)

    # SFX Command ══════════════════════════════════════════════════════════════
    @commands.command()
    async def sfx(self, message, *, url: str = None):
        if url is None:
            return await message.send("You can browse the sfx folder by using `browse sfx`, if you're looking for something specific.", delete_after = 20)
        elif (os.path.exists(configuration.SFX_PATH + url + ".mp3")):
            queue_item = {}
            queue_item["url"] = (configuration.SFX_PATH + url + ".mp3")
            queue_item["title"] = url
            queue_item["source_type"] = 2
        elif (os.path.exists(configuration.SFX_PATH + url + ".wav")):
            queue_item = {}
            queue_item["url"] = (configuration.SFX_PATH + url + ".wav")
            queue_item["title"] = url
            queue_item["source_type"] = 2
        else:
            return await message.send("Couldn't find the sound effect you were looking for...", delete_after = 20)

        if not await check_voice_connectivity(message):
            return

        try:
            player = self.players[message.guild.id]
        except KeyError:
            self.players[message.guild.id] = audioplayer.AudioPlayer(message)
        await self.players[message.guild.id].queue.put(queue_item)

    # Browser SFX Command ------------------------------------------------------
    async def browser_sfx(self, message, url):
        try:
            tag = TinyTag.get(url)
        except TinyTagException:
            return

        if not await check_voice_connectivity(message):
            return

        if (tag.title == None):
            tag.title = url[url.rfind('/'):]
        queue_item = {}
        queue_item["title"] = tag.title
        queue_item["url"] = url
        queue_item["source_type"] = 2

        try:
            player = self.players[message.guild.id]
        except KeyError:
            self.players[message.guild.id] = audioplayer.AudioPlayer(message)
        await self.players[message.guild.id].queue.put(queue_item)

    # Stop Command ═════════════════════════════════════════════════════════════
    @commands.command(aliases = ["leave"])
    async def stop(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I am not even playing anything. :eyes:", delete_after = 20)

        await message.guild.voice_client.disconnect()
        if self.players[message.guild.id]:
            self.player_exit(message.guild)

    # Skip Command ═════════════════════════════════════════════════════════════
    @commands.command(aliases = ["next"])
    async def skip(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)

        if not message.guild.voice_client.is_playing():
            return

        message.guild.voice_client.stop()
        return await message.send(":track_next: Skipping...", delete_after = 20)

    # Volume Command ═══════════════════════════════════════════════════════════
    @commands.command(aliases = ["vol"])
    async def volume(self, message, *, vol = None):
        if (message.guild.voice_client is None) or (not message.guild.voice_client.is_connected()):
            return await message.send("I'm not even playing anything. :eyes:", delete_after = 20)
        if vol is None:
            return await message.send("The volume is set to {}%.".format(
                int(self.players[message.guild.id].volume * 100)))
        if not await check_volume_value(vol):
            return await message.send("Please enter a number ranging from 0 to 100.", delete_after = 20)

        vol = int(vol)
        vol_old = int((self.players[message.guild.id].volume * 100))
        await volume_gradient(self.players[message.guild.id], message, vol, vol_old)

    # Loop Command ═════════════════════════════════════════════════════════════
    @commands.command()
    async def loop(self, message, *, option: str = None):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)
        if option is None:
            return await message.send("Do you want me to loop the `queue`/`playlist`, the `song` or turn it `off`?", delete_after = 20)

        if (option.lower() == self.players[message.guild.id].looping):
            return await message.send("The loop is currently set to *{}*.".format(option.lower()))
        elif (option.lower() == "song"):
            self.players[message.guild.id].looping = 1
            return await message.send(":repeat: I'm looping this song now.")
        elif (option.lower() == "queue") or (option.lower() == "playlist"):
            self.players[message.guild.id].looping = 2
            return await message.send(":repeat: I'm looping the {} now.".format(option.lower()))
        elif (option.lower() == "off"):
            self.players[message.guild.id].looping = 0
            return await message.send(":repeat_one: I've turned off the loop.")
        else:
            return await message.send("Do you want me to loop the `queue`/`playlist`, the `song` or turn it `off`?", delete_after = 20)

    # Queue Command ════════════════════════════════════════════════════════════
    @commands.command(aliases = ["playlist"])
    async def queue(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not even playing anything. :eyes:", delete_after = 20)

        if self.players[message.guild.id].queue.empty():
            return await message.send("The queue is empty.")

        songs = list(islice(self.players[message.guild.id].queue._queue, 0, 20))
        queuelist = '\n'.join("-{}".format(iterator["title"]) for iterator in songs)
        new_embed = discord.Embed(title = "Upcoming {}:".format(len(songs)), description = queuelist)

        return await message.send(embed = new_embed)

    # Pause Command ════════════════════════════════════════════════════════════
    @commands.command()
    async def pause(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)
        elif message.guild.voice_client.is_paused():
            return

        message.guild.voice_client.pause()
        return await message.send(":pause_button: Paused.")

    # Resume Command ═══════════════════════════════════════════════════════════
    @commands.command(aliases = ["continue", "cont"])
    async def resume(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)
        elif message.guild.voice_client.is_playing():
            return

        message.guild.voice_client.resume()
        return await message.send(":arrow_forward: Continuing.")

    # Resume Command ═══════════════════════════════════════════════════════════
    @commands.command()
    async def join(self, message):
        if not await check_voice_connectivity(message):
            return

    # Events ═══════════════════════════════════════════════════════════════════
    # SFX Shortcut Event -------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.voice and message.guild.voice_client:
            if (message.author.voice.channel == message.guild.voice_client.channel):
                if message.guild.voice_client.is_playing():
                    return
                elif message.content.lower() in self.sfx_shortcut:
                    url = message.content.lower()
                    if (os.path.exists(configuration.SFX_PATH + url + ".mp3")):
                        queue_item = {}
                        queue_item["url"] = (configuration.SFX_PATH + url + ".mp3")
                        queue_item["title"] = url
                        queue_item["source_type"] = 2
                    elif (os.path.exists(configuration.SFX_PATH + url + ".wav")):
                        queue_item = {}
                        queue_item["url"] = (configuration.SFX_PATH + url + ".wav")
                        queue_item["title"] = url
                        queue_item["source_type"] = 2
                    else:
                        return

                    try:
                        player = self.players[message.guild.id]
                    except KeyError:
                        return
                    await self.players[message.guild.id].queue.put(queue_item)

            else:
                return
        else:
            return

# Functions ════════════════════════════════════════════════════════════════════
async def volume_gradient(player, message, vol, vol_old):
    if (vol == 0):
        while vol_old != 0:
            vol_old = vol_old - 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.015)
        player.volume = 0
        message.guild.voice_client.source.volume = 0
        return await message.send("Okay, I'm quietly playing for myself then.")

    elif (vol < vol_old):
        while vol_old > vol:
            vol_old = vol_old - 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.015)
        player.volume = (vol / 100)
        return await message.send(":arrow_down_small: I've set the volume to {}%.".format(vol))
    else:
        while vol_old < vol:
            vol_old = vol_old + 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.015)
        player.volume = (vol / 100)
        return await message.send(":arrow_up_small: I've set the volume to {}%.".format(vol))


async def check_volume_value(vol):
    try:
        vol = int(vol)
        if (-1 < vol) and (vol < 101):
            return True
        else:
            return False
    except (TypeError, ValueError) as e:
        return False

def prepare_queue_local_source(url: str, file_ending: str):
    tag = TinyTag.get(configuration.MUSIC_PATH + url + file_ending)
    if (tag.title == None):
        tag.title = url
    queue_item = {}
    queue_item["title"] = tag.title
    queue_item["url"] = (configuration.MUSIC_PATH + url + file_ending)
    queue_item["source_type"] = 0
    return queue_item

def prepare_queue_link_source(url: str):
    youtube_feed = etree.HTML(urllib.request.urlopen(url).read())
    queue_item = {}
    queue_item["title"] = "".join(youtube_feed.xpath("//span[@id='eow-title']/@title"))
    queue_item["url"] = url
    queue_item["source_type"] = 1   #0: local, 1: link, 2: local sfx
    return queue_item

async def check_voice_connectivity(message): #0: play, 1: other commands
    if message.guild.voice_client is None:
        if message.author.voice:
            return await message.author.voice.channel.connect()
        else:
            await message.send("You're not in a voice channel, silly.", delete_after = 15)
            return False
    elif (message.author.voice.channel != message.guild.voice_client.channel):
        return await message.guild.voice_client.move_to(message.author.voice.channel)
    else:
        return True


def setup(client):
    client.add_cog(Audio(client))
