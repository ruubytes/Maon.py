import asyncio
import os.path
import time
import logger
import musicplayer
import configuration
import youtube_dl
import discord
from discord.ext import commands
from mp3_tagger import MP3File, VERSION_BOTH
from mp3_tagger.exceptions import MP3OpenFileError
from itertools import islice

ytdl = youtube_dl.YoutubeDL(configuration.ytdl_format_options)
youtube_dl.utils.bug_reports_message = lambda: '' # Suppress noise about console usage from errors
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

# TODO: info extraction from yt links contains different protocol for streams:
#   https for videos, m3u8 for streams. Use to separate and implement streaming

class Music(commands.Cog):
    __slots__ = ("client", "players")
    def __init__(self, client):
        self.client = client
        self.players = {}

    def player_exit(self, guild):
        try:
            del self.players[guild.id]
            logger.log_info("({}, gid: {}) musicplayer destroyed".format(guild.name, guild.id))
        except (AttributeError, KeyError) as e:
            logger.log_error("({}, gid: {}) musicplayer could not be destroyed".format(guild.name, guild.id))
            pass

    # Cog Commands ═════════════════════════════════════════════════════════════
    # Play Command -------------------------------------------------------------
    @commands.command()
    async def play(self, message, *, url: str = None):
        await message.trigger_typing()

        if message.guild.voice_client is None:
            if (message.author.voice):
                await message.author.voice.channel.connect()
            else:
                return await message.send("You're not in a voice channel, silly.", delete_after = 15)
        if url is None:
            return await message.send("I need a Youtube link or local file name to play music. You can also browse the music folder for local files to play by using `browse music`.", delete_after = 20)
        elif url.startswith("https://"): # Links ---
            try:
                src = ytdl.extract_info(url, download = False)
                if src is None:
                    return message.send("That's not a valid Youtube link.", delete_after = 15)
                elif src["protocol"] == "m3u8":
                    return await message.send("Streams don't work yet, sorry. :pray:")
                if "entries" in src:
                    src = src["entries"][0]
                src["type_link"] = 1    # yt link
                src["type_audio"] = 0   # music
            except youtube_dl.DownloadError as e:
                return await message.send("That's not a valid Youtube link.", delete_after = 15)

        elif (os.path.exists(configuration.MUSIC_PATH + url + ".mp3")):
            filepath = "".join([configuration.MUSIC_PATH + url + ".mp3"])
            src = {"title": "", "url": "", "type_link": 0, "type_audio": 0}
            try:
                meta = MP3File(filepath)
            except MP3OpenFileError:
                return await message.send("...eeh, I can't play that.", delete_after = 20)
            meta = meta.get_tags()
            try:
                if meta["ID3TagV1"]["song"]:
                    src["title"] = meta["ID3TagV1"]["song"]
                elif meta["ID3TagV2"]["song"]:
                    src["title"] = meta["ID3TagV2"]["song"]
                else:
                    src["title"] = url
            except KeyError:
                src["title"] = url

            src["url"] = filepath
        else:
            return await message.send("That's not a valid Youtube link or file name.", delete_after = 15)

        try:
            player = self.players[message.guild.id]
        except KeyError:
            player = musicplayer.MusicPlayer(message)
            self.players[message.guild.id] = player

        await self.players[message.guild.id].queue.put(src)
        if message.guild.voice_client.is_playing():
            await message.send("{} has been added to the queue.".format(src.get("title")))

    # SFX Command --------------------------------------------------------------
    @commands.command()
    async def sfx(self, message, *, url: str = None):
        if message.guild.voice_client is None:
            if (message.author.voice):
                await message.author.voice.channel.connect()
            else:
                return await message.send("You're not in a voice channel, silly.", delete_after = 15)

        if url is None:
            return await message.send("You can browse the sfx folder by using `browse sfx`, if you're looking for something specific.", delete_after = 20)
        elif (os.path.exists(configuration.SFX_PATH + url + ".mp3")):
            filepath = "" + configuration.SFX_PATH + url + ".mp3"
            data = {"title": "", "url": "", "type_link": 0, "type_audio": 1} # 0: local, 1: sfx
            data["title"] = url
            data["url"] = filepath
        elif (os.path.exists(configuration.SFX_PATH + url + ".wav")):
            filepath = "" + configuration.SFX_PATH + url + ".wav"
            data = {"title": "", "url": "", "type_link": 0, "type_audio": 1} # 0: local, 1: sfx
            data["title"] = url
            data["url"] = filepath
        else:
            return await message.send("Couldn't find the sound effect you were looking for...", delete_after = 20)

        try:
            player = self.players[message.guild.id]
        except KeyError:
            player = musicplayer.MusicPlayer(message)
            self.players[message.guild.id] = player
        await self.players[message.guild.id].queue.put(data)

    # Stop Command -------------------------------------------------------------
    @commands.command(aliases = ["leave"])
    async def stop(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I am not even playing anything. :eyes:")

        await message.guild.voice_client.disconnect()
        if self.players[message.guild.id]:
            self.player_exit(message.guild)

    # Stop Command -------------------------------------------------------------
    @commands.command(aliases = ["next"])
    async def skip(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)

        if not message.guild.voice_client.is_playing():
            return

        message.guild.voice_client.stop()
        return await message.send(":track_next: Skipping...")

    # Volume Command -----------------------------------------------------------
    @commands.command(aliases = ["vol"])
    async def volume(self, message, *, vol = None):
        try:
            if not message.guild.voice_client or not message.guild.voice_client.is_connected():
                return await message.send("I'm not even playing anything. :eyes:", delete_after = 20)
            if vol == None:
                return await message.send("The volume is set to {}%.".format(int(self.players[message.guild.id].volume * 100)))
            if not isinstance(int(vol), int):
                return await message.send("Please enter a number ranging from 0 to 100.", delete_after = 20)
            vol = int(vol)
            if not (-1 < vol < 101):
                return await message.send("Please enter a number ranging from 0 to 100.", delete_after = 20)
        except (TypeError, ValueError) as e:
            return await message.send("Please enter a number ranging from 0 to 100.", delete_after = 20)

        vol_old = self.players[message.guild.id].volume
        if vol_old == (vol / 100):
            return await message.send("The volume is set to {}%.".format(int(self.players[message.guild.id].volume * 100)))
        elif vol == 0:
            vol_old = vol_old * 100
            while vol_old != 0:
                vol_old = vol_old - 1
                message.guild.voice_client.source.volume = (vol_old / 100)
                time.sleep(0.015)
            self.players[message.guild.id].volume = 0
            message.guild.voice_client.source.volume = 0
            return await message.send("Okay, I'm quietly playing for myself then.")
        if vol_old > (vol / 100):
            vol_old = vol_old * 100
            diff = vol_old - vol
            if diff < 0:
                return await message.send("Oops, something went wrong.")
            while diff != 0:
                vol_old = vol_old - 1
                message.guild.voice_client.source.volume = (vol_old / 100)
                diff = diff - 1
                time.sleep(0.015)
            self.players[message.guild.id].volume = (vol / 100)
            return await message.send(":arrow_down_small: I've set the volume to {}%.".format(int(vol)))
        else:
            vol_old = vol_old * 100
            diff = vol - vol_old
            if diff < 0:
                return await message.send("Oops, something went wrong.")
            while diff != 0:
                vol_old = vol_old + 1
                message.guild.voice_client.source.volume = (vol_old / 100)
                diff = diff - 1
                time.sleep(0.015)
            self.players[message.guild.id].volume = (vol / 100)
            return await message.send(":arrow_up_small: I've set the volume to {}%.".format(int(vol)))

    # Loop Command -------------------------------------------------------------
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

    # Queue Command ------------------------------------------------------------
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

    # Pause Command ------------------------------------------------------------
    @commands.command()
    async def pause(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)
        elif message.guild.voice_client.is_paused():
            return

        message.guild.voice_client.pause()
        return await message.send(":pause_button: Paused.")

    # Resume Command -----------------------------------------------------------
    @commands.command(aliases = ["continue", "cont"])
    async def resume(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:", delete_after = 20)
        elif message.guild.voice_client.is_playing():
            return

        message.guild.voice_client.resume()
        return await message.send(":arrow_forward: Continuing.")

    # Download Command (still needs refining)-----------------------------------
    @commands.command()
    @commands.is_owner()
    async def download(self, message, media: str = None, *, url: str = None):
        if media is None:
            return await message.send("Do you want to download something as `video` or `audio`?")
        elif url is None:
            return await message.send("I need a valid Youtube link.")
        elif (media == "video"):
            to_edit = await message.send("Downloading...")
            youtube_dl.YoutubeDL(configuration.download_video_opts).download([url])
            return await to_edit.edit(content = "Download finished.")
        elif (media == "audio"):
            to_edit = await message.send("Downloading...")
            youtube_dl.YoutubeDL(configuration.download_audio_opts).download([url])
            return await to_edit.edit(content = "Download finished.")
        else:
            return await message.send("Usage: maon download <audio/video> <link>")

    # Normal Class Functions ═══════════════════════════════════════════════════
    # Browser Play Command -----------------------------------------------------
    async def browser_play(self, message, url):
        if message.guild.voice_client is None:
            if (message.author.voice):
                await message.author.voice.channel.connect()
            else:
                return await message.send("You have to join a voice channel, silly.", delete_after = 15)

        src = {"title": "", "url": "", "type_link": 0, "type_audio": 0} # 0: local, 0: music
        src["url"] = url

        file_type = url[(len(url) - 4):]
        if file_type == ".wav":
            src["title"] = url[url.rfind('/'):]
        else:
            try:
                meta = MP3File(url)
            except MP3OpenFileError:
                return await message.send("...eeh, I can't play that.", delete_after = 20)
            meta = meta.get_tags()
            try:
                if meta["ID3TagV1"]["song"]:
                    src["title"] = meta["ID3TagV1"]["song"]
                elif meta["ID3TagV2"]["song"]:
                    src["title"] = meta["ID3TagV2"]["song"]
                else:
                    src["title"] = url
            except KeyError:
                src["title"] = url

        try:
            player = self.players[message.guild.id]
        except KeyError:
            player = musicplayer.MusicPlayer(message)
            self.players[message.guild.id] = player

        await self.players[message.guild.id].queue.put(src)
        if message.guild.voice_client.is_playing():
            await message.send("{} has been added to the queue.".format(src.get("title")), delete_after = 10)

    # Browser SFX Command ------------------------------------------------------
    async def browser_sfx(self, message, url):
        if message.guild.voice_client is None:
            if (message.author.voice):
                await message.author.voice.channel.connect()
            else:
                return await message.send("You have to join a voice channel, silly.", delete_after = 15)

        src = {"title": "", "url": "", "type_link": 0, "type_audio": 1} # 0: local, 0: sfx
        src["url"] = url
        src["title"] = url[url.rfind('/'):]

        try:
            player = self.players[message.guild.id]
        except KeyError:
            player = musicplayer.MusicPlayer(message)
            self.players[message.guild.id] = player

        await self.players[message.guild.id].queue.put(src)

def setup(client):
    client.add_cog(Music(client))
