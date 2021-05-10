import os.path
import asyncio
import subprocess
from configs import custom
from configs import settings
from discord import Embed
from discord.ext import commands
from src import audioplayer
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
from tinytag import TinyTag, TinyTagException
from time import sleep
from time import time
from pathlib import Path
from os import listdir


class Audio(commands.Cog):
    __slots__ = ["client", "players", "cached_songs", "running",
                "info_queue", "info_task", "download_queue", "download_task", "cache_queue",
                "cache_task", "track_queue", "track_task"]

    def __init__(self, client):
        self.client = client
        self.players = {}
        self.cached_songs = {}
        self.running = True
        self.info_queue = asyncio.Queue()
        self.info_task = self.client.loop.create_task(self.info_loop())
        self.download_queue = asyncio.Queue()
        self.download_task = self.client.loop.create_task(self.download_loop())
        self.cache_queue = asyncio.Queue()
        self.cache_task = self.client.loop.create_task(self.cache_loop())
        self.track_queue = asyncio.Queue()
        self.track_task = self.client.loop.create_task(self.track_loop())

    async def prep_link_track(self, message, url: str):
        """ Looks up the requested `url` in the cached_songs dictionary to see if the track exists in the
        temp folder. If not, starts the download / streaming process. """
        # All we know at this point is the url and who requested it. Get the video_id from the url.
        video_id = await get_video_id(url)
        if video_id is None:
            return await message.send("That link looks invalid to me.")
        
        # Look up video_id in cached_songs dictionary and build a track if an entry exists.
        filename = self.cached_songs.get(video_id)
        if (filename is not None) and (os.path.exists(settings.TEMP_PATH + filename)):
            track_title = filename[:len(filename) - 16]
            track_url = settings.TEMP_PATH + filename
            track = {"title": track_title, "url": track_url, "track_type": "music", "message": message}

            await self.track_queue.put(track)
        
        else: # Track is not in temp folder, hand it over to info_queue and start the downloading or streaming process.
            url = "https://www.youtube.com/watch?v=" + video_id
            req = {"message": message, "url": url, "video_id": video_id}
            return await self.info_queue.put(req)


    async def prep_local_track(self, message, url: str):
        """ Builds local track information for the audioplayer. """
        tag = TinyTag.get(settings.MUSIC_PATH + url)
        if tag.title is None:
            tag.title = url
        track = {"title": tag.title, "url": settings.MUSIC_PATH + url, "track_type": "music", "message": message}
        return await self.track_queue.put(track)


    async def track_loop(self):
        """ Centralizes the queuing of tracks in this task. Will turn this loop into a function instead later. """
        try:
            while self.running:
                track = await self.track_queue.get()
                message = track.get("message")

                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
                await self.players[message.guild.id].queue.put(track)
                if message.guild.voice_client.is_playing() or message.guild.voice_client.is_paused():
                    await message.channel.send("{} has been added to the queue.".format(track.get("title")))
        
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


    async def info_loop(self):
        """ Gather information about the requested song and process it. Also manages the music cache folder
        for now so it is a centralized task. """
        try:
            while self.running:
                req = await self.info_queue.get()
                message = req.get("message")
                # Find out if the video is a normal video or live stream.
                # If it's a video longer than 15 minutes, maybe also stream it?
                video_info = {}
                try:
                    video_info = await self.client.loop.run_in_executor(
                        None, lambda: YoutubeDL(settings.YTDL_INFO_OPTIONS).extract_info(req.get("url"), download=False))
                except DownloadError as e:
                    if "looks truncated." in str(e):
                        await message.channel.send("Your link looks incomplete, paste the command again, please.")
                    else:
                        await message.channel.send("I could not download the video's meta data... maybe try again in a few seconds.")
                    continue

                # Find out if the video is a live stream or is longer than n seconds (config)
                # Stream it if yes, preload would take too long.
                
                # Check if normal video has its duration stripped, sometimes this occures.
                if (video_info.get("protocol") is None) and (video_info.get("duration") is None):
                    video_info["duration"] = settings.SONG_DURATION_MAX

                if video_info.get("protocol") or (video_info.get("duration") >= settings.SONG_DURATION_MAX) or (settings.SONG_DURATION_MAX == 0):
                    track = {
                        "title": video_info.get("title"), 
                        "url": video_info.get("url"), 
                        "track_type": "stream", 
                        "message": message, 
                        "original_url": req.get("url"), 
                        "video_info": video_info,
                        "time_stamp": time()
                    }
                    if (video_info.get("duration") >= settings.SONG_DURATION_MAX):
                        formats = video_info.get("formats", [video_info])
                        for f in formats:
                            if f.get("format_id") == "251":
                                track["url"] = f.get("url")
                                break
                    await self.track_queue.put(track)

                else:
                    # It's a normal short video
                    # Get the best audio format id and attach it to the request
                    formats = video_info.get("formats", [video_info])
                    req["formats"] = formats
                    format_ids = []
                    for f in formats:
                        format_ids.append(f['format_id'])
                    if "251" in format_ids:
                        req["format_id"] = "251"
                        try:
                            await self.manage_temp_size(req)
                        except OSError as e:
                            print(e)
                            await message.channel.send("The requested download is larger than what I'm allowed to have, defaulting to stream.")
                            await self.track_rescue(req, video_info)
                            continue
                    else:
                        req["format_id"] = "140"
                        try:
                            await self.manage_temp_size(req)
                        except OSError as e:
                            print(e)
                            await message.channel.send("The requested download is larger than what I'm allowed to have, defaulting to stream.")
                            await self.track_rescue(req, video_info)
                            continue

                    await message.channel.send("Preparing {}...".format(video_info.get("title")))
                    await self.download_queue.put(req)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    async def track_rescue(self, req, video_info):
        """ Creates a track of streaming type for the player as a fallback solution if the meta data
        obtained from Youtube is faulty for download. """
        message = req.get("message")
        track = {
            "title": video_info.get("title"), 
            "url": video_info.get("url"), 
            "track_type": "stream", 
            "message": message, 
            "original_url": req.get("url"), 
            "video_info": video_info,
            "time_stamp": time()
        }
        formats = video_info.get("formats", [video_info])
        for f in formats:
            if f["format_id"] == "251":
                track["url"] = f.get("url")
        await self.track_queue.put(track)

    async def manage_temp_size(self, req):
        """ Removes items from the temp folder in FIFO order if a new addition would go over the 
        max-size stated in the configuration file """
        try:
            size_in_mb = (sum(f.stat().st_size for f in Path(settings.TEMP_PATH).glob('**/*') if f.is_file())) / (1024 * 1024)
            filesize_in_mb = 0
            for f in req.get("formats"):
                if f["format_id"] == req.get("format_id"):
                    if f.get("filesize"):
                        filesize_in_mb = (f.get("filesize") / (1024 * 1024))
                        if filesize_in_mb > settings.TEMP_FOLDER_MAX_SIZE_IN_MB:
                            raise OSError("[Audio Ext] Requested download is larger than the allowed size of the temp folder. ({} > {})".format(filesize_in_mb, settings.TEMP_FOLDER_MAX_SIZE_IN_MB))
                        break
                    else:
                        break
            size_in_mb += filesize_in_mb
            while (settings.TEMP_FOLDER_MAX_SIZE_IN_MB < size_in_mb):
                first_file = min(Path(settings.TEMP_PATH).glob('**/*'), key=os.path.getmtime)
                size_first_file = os.path.getsize(first_file)
                os.remove(first_file)
                size_in_mb -= size_first_file
        except ValueError:
            print("[Audio Ext] Temp folder is empty or does not exist.")

    async def download_loop(self):
        """ Downloads a requested song and stores it in the music cache folder for ease of access and replayability """ 
        try:
            while self.running:
                req = await self.download_queue.get()
                message = req.get("message")

                command = settings.AUDIO_DOWNLOAD_CMD_DEFAULT
                command[10] = req.get("format_id")
                command[11] = req.get("url")

                result = await self.client.loop.run_in_executor(
                    None, lambda: subprocess.run(command, stdout=subprocess.PIPE).returncode)
                if result == 0:
                    await self.cache_queue.put(req)
                else:
                    await message.channel.send("I ran into an error during download... maybe try again in a few seconds.")

        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    async def cache_loop(self):
        """ Keeps track of files in the temp folder and queues newly added songs. """
        # Load the cache first
        temp_list = {}
        try:
            temp_list = listdir(settings.TEMP_PATH)
            for filename in temp_list:
                if filename.endswith(".mp3"):
                    video_id = filename[len(filename) - 15 : len(filename) - 4]
                    self.cached_songs[video_id] = filename
        except FileNotFoundError:
            print("[Audio] The temp folder does not exist, skipped loading the cache.")

        try:
            while self.running:
                req = await self.cache_queue.get()
                video_id = req.get("video_id")
                
                # Find file by video_id because the ytdl library filters chars out, title != filename
                track_title = ""
                track_url = ""
                temp_list = listdir(settings.TEMP_PATH)
                for filename in temp_list:
                    if filename.endswith(video_id + ".mp3"):
                        self.cached_songs[video_id] = filename
                        track_title = filename[:len(filename) - 16]
                        track_url = settings.TEMP_PATH + filename

                if (track_title == "") or (track_url == ""):
                    message = req.get("message")
                    await message.channel.send("I could not find the downloaded file within my cache... sorry!")

                else:
                    track = {"title": track_title, "url": track_url, "track_type": "music", "message": req.get("message")}

                    # Throw the track into the queue of the audioplayer
                    await self.track_queue.put(track)

        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


    # Used invocations:
    # play p sfx s volume v vol j next ...
    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["p", "stream", "yt"])
    @commands.guild_only()
    async def play(self, message, *, url: str = None):
        """ Makes Maon play an url linking to a Youtube video or filepath to a local mp3 / wav file in the music folder
        specified in `url`. Maon joins the requestee's voice channel and parses the `url`. """ 
        if message.guild.voice_client is None:
            if message.author.voice:
                await message.author.voice.channel.connect()
                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
            else:
                return await message.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice is None:
            return await message.send("Come in here if you want me to play something. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("Come in here if you want me to play something. :eyes:")
    
        if url is None:
            return await message.send(
                "You can browse the music folder with `browse music`, if you're looking for something specific.")
        elif url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/") or url.startswith("https://m.youtube.com/"):
            await self.prep_link_track(message, url)
        elif os.path.exists(settings.MUSIC_PATH + url + ".mp3"):
            await self.prep_local_track(message, url + ".mp3")
        elif os.path.exists(settings.MUSIC_PATH + url + ".wav"):
            await self.prep_local_track(message, url + ".wav")
        else:
            return await message.send("I need a Youtube link or file path to play.")

    async def fb_play(self, message, url):
        """ Play command for the filebrowser to play songs selected with reactions. """
        # Check if the requested track is within the cache folder or not because cached mp3s
        # should not have meta data. The track title is in the filename, though.
        track_title = ""
        if url[:url.rfind("/") + 1] == settings.TEMP_PATH:
            track_title = url[url.rfind("/") + 1 : len(url) - 16]

        else:
            # Try to extract meta data with tinytag, most normal mp3 files should have at least a title
            try:
                tag = TinyTag.get(url)
                if tag.title is None:
                    track_title = url[url.rfind("/") + 1 : len(url) - 4]
                else:
                    track_title = tag.title
            except TinyTagException:
                return
        
        track = {"title": track_title, "url": url, "track_type": "music", "message": message}
        
        # Connection check
        if message.guild.voice_client is None:
            if message.author.voice:
                await message.author.voice.channel.connect()
                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
            else:
                return await message.channel.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice is None:
            return await message.send("Come in here if you want me to play something. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.channel.send("Come in here if you want me to play something. :eyes:")

        await self.track_queue.put(track)

    @commands.command(aliases=["s", "effects", "effect"])
    @commands.guild_only()
    async def sfx(self, message, *, url: str = None):
        """ Plays a local sound effect from the sfx folder specified by a filepath or filename in `url`. """
        track = {}
        if url is None:
            return await message.send(
                "You can browse the sfx folder with `browse sfx`, if you're looking for something specific.")
        elif os.path.exists(settings.SFX_PATH + url + ".mp3"):
            track["url"] = settings.SFX_PATH + url + ".mp3"
        elif os.path.exists(settings.SFX_PATH + url + ".wav"):
            track["url"] = settings.SFX_PATH + url + ".wav"
        else:
            return await message.send("Couldn't find the sound effect you were looking for...")

        track["title"] = url
        track["track_type"] = "sfx"  # link / music / sfx

        # Connection check
        if message.guild.voice_client is None:
            if message.author.voice:
                await message.author.voice.channel.connect()
                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
            else:
                return await message.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice is None:
            return await message.send("Come in here if you want me to play something. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("Come in here if you want me to play something. :eyes:")

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        return await self.players[message.guild.id].queue.put(track)

    async def fb_sfx(self, message, url):
        """ Sfx play command for the file browser to play a sound effect selected with a reaction. """ 
        try:
            tag = TinyTag.get(url)
        except TinyTagException:
            return

        # Connection check
        if message.guild.voice_client is None:
            if message.author.voice:
                await message.author.voice.channel.connect()
                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
            else:
                return await message.channel.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice is None:
            return await message.send("Come in here if you want me to play something. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.channel.send("Come in here if you want me to play something. :eyes:")

        if tag.title is None:
            tag.title = url[url.rfind("/") + 1:]
        track = {"title": tag.title, "url": url, "track_type": "sfx"}

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        await self.players[message.guild.id].queue.put(track)

    @commands.command(aliases=["v", "vol"])
    @commands.guild_only()
    async def volume(self, message, *, vol=None):
        """ Sets the volume for the audioplayer. If the audioplayer is already playing, sets the volume
        gradually and not instant for a smoother listening experience. """
        if message.author.voice is None:
            return await message.send("You're not in a voice channel, silly.")
        elif message.guild.voice_client is None:
            return await message.send("I'm not even playing anything. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("You're not in the voice channel, silly.")
        elif message.guild.id not in self.players:
            return await message.send("I'm not even playing anything. :eyes:")
        elif vol is None:
            return await message.send("The volume is set to {}%.".format(
                int(self.players[message.guild.id].volume * 100)))
        elif not await check_volume(vol):
            return await message.send("Please enter a number ranging from 0 to 100.")
        elif self.players[message.guild.id].now_playing:
            return await volume_gradient(self.players[message.guild.id], message, int(vol))
        else:
            return await volume_no_gradient(self.players[message.guild.id], message, int(vol))

    @commands.command(aliases=["j"])
    @commands.guild_only()
    async def join(self, message):
        """ Makes Maon join the voice channel. Returns if the requestee is not in a voice channel. Also
        makes Maon switch channels if the requestee is in another voice channel. """ 
        # Connection check
        if message.guild.voice_client is None:
            if message.author.voice:
                await message.author.voice.channel.connect()
                if message.guild.id not in self.players:
                    self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
            else:
                return await message.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice is None:
            return
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.guild.voice_client.move_to(message.author.voice.channel)

    @commands.command(aliases=["next", "n", "ne", "nxt", "nx", "sk", "skp"])
    @commands.guild_only()
    async def skip(self, message):
        """ Skips a currently playing song. """ 
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")
        elif not message.guild.voice_client.is_playing():
            return
        else:
            message.guild.voice_client.stop()
            return await message.send(":track_next: Skipping...")

    @commands.command()
    @commands.guild_only()
    async def loop(self, message, *, option: str = None):
        """ Loops a song or the whole playlist. `off` as `option` turns off the loop. """ 
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.guild.id not in self.players:
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")

        if option is None:
            return await message.send(
                "Do you want me to loop the `playlist`/`queue`/`q`, the `song`, or turn it `off`?")
        option = option.lower()
        if option == self.players[message.guild.id].looping:
            return await message.send("Looping is currently set to `{}`.".format(option))
        elif option == "off":
            self.players[message.guild.id].looping = "off"
            return await message.send(":repeat_one: I've turned off looping.")
        elif option == "song":
            self.players[message.guild.id].looping = "song"
            return await message.send(":repeat: I'm looping this song now.")
        elif (option == "playlist") or (option == "queue") or (option == "q"):
            self.players[message.guild.id].looping = "playlist"
            return await message.send(":repeat: I'm looping the playlist now.")
        else:
            return await message.send(
                "Do you want me to loop the `playlist`/`queue`/`q`, the `song`, or turn it `off`?")

    @commands.command()
    @commands.guild_only()
    async def shuffle(self, message, *, option: str = None):
        """ Shuffle play; prefix shuffle off to turn it off """
        # Check if there even is an active audioplayer for this guild
        if message.guild.id not in self.players:
            return await message.channel.send("I don't have an active audioplayer for this server.")

        elif option is None:
            # Check if shuffle is already on
            if not self.players[message.guild.id].shuffle:
                self.players[message.guild.id].shuffle = True
                return await message.channel.send(":twisted_rightwards_arrows: I've turned shuffle play on.")
            else:
                return await message.channel.send(":twisted_rightwards_arrows: Shuffle play is on. You can turn it off with `{}shuffle off`".format(custom.PREFIX[0]))

        elif (option == "off") or (option == "stop") or (option == "quit"):
            # Check if shuffle is on
            if not self.players[message.guild.id].shuffle:
                return await message.channel.send("Shuffle play is off.")
            else:
                self.players[message.guild.id].shuffle = False
                return await message.channel.send("I've turned shuffle play off.")

    @commands.command()
    @commands.guild_only()
    async def pause(self, message):
        """ Pauses the currently playing song. """ 
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")
        elif message.guild.voice_client.is_paused():
            return await message.send(":pause_button: I'm paused right now.")
        elif not message.guild.voice_client.is_playing():
            return
        else:
            message.guild.voice_client.pause()
            return await message.send(":pause_button: Paused.")

    @commands.command(aliases=["res", "cont", "continue", "re", "co"])
    @commands.guild_only()
    async def resume(self, message):
        """ Continues a paused song. """ 
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")
        elif message.guild.voice_client.is_playing():
            return
        elif message.guild.id in self.players and message.guild.voice_client.is_paused():
            message.guild.voice_client.resume()
            return await message.send(":arrow_forward: Continuing...")
        else:
            return await message.send("I'm not playing anything right now.")

    @commands.command(aliases=["leave", "l"])
    @commands.guild_only()
    async def stop(self, message):
        """ Stops any currently playing song, cancels the audioplayer and makes Maon leave the voice channel. """ 
        if message.author.voice is None:
            return await message.send("Don't tell me what to do. :eyes:")
        elif not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not even playing anything...")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("Come in here first.")
        else:
            if message.guild.id in self.players:
                self.players[message.guild.id].player_task.cancel()
            else:
                await message.guild.voice_client.disconnect()

    @commands.command(aliases=["queue", "q"])
    @commands.guild_only()
    async def playlist(self, message, *args):
        """ Displays the current playlist if no `args`. Can rearrange the songs in the playlist with integers describing
        the current entry position of a song in the playlist and moves them to the front of the playlist. If the first arg is `copy`
        all following positions are copied to the front of the playlist. If the first arg is `remove` all following positions in the
        playlist are deleted. """ 
        if not message.guild.id in self.players:
            return
        elif (not self.players[message.guild.id].now_playing) and (self.players[message.guild.id].queue.qsize() == 0):
            return await message.send("I'm not playing anything right now.")

        q_list = list(self.players[message.guild.id].queue._queue)

        # No args, just print the current playlist
        if not args:
            now_playing_str = ":cd: Now Playing: " + self.players[message.guild.id].now_playing
            playlist_description = ""
            
            if len(q_list) > 0:
                i = 1
                playlist_description += "**Up Next:**\n"
                
                for item in q_list:
                    playlist_description += "  `" + str(i).zfill(2) + "`: " + item.get("title") + "\n"
                    i += 1
                    if i > settings.PLAYLIST_MSG_MAX_LEN:
                        playlist_description += "  •\n  •\n  •"
                        break

            playlist_embed = Embed(title=now_playing_str, description=playlist_description, color=custom.COLOR_HEX)
            return await message.send(embed=playlist_embed)

        else:
            # See if the args are only valid integers to restructure the current playlist
            try:
                positions = await parse_playlist_positions(args, len(q_list))
                
                # With valid positions, begin restructuring the queue.                
                new_q_list = []
                for pos in positions:
                    new_q_list.append(q_list[pos - 1])
                    q_list[pos - 1] = 0
                for item in q_list:
                    if item == 0:
                        continue
                    new_q_list.append(item)

                self.players[message.guild.id].queue = asyncio.Queue()
                for item in new_q_list:
                    await self.players[message.guild.id].queue.put(item)
                
                if len(positions) == 1:
                    return await message.send("Next up: " + new_q_list[0].get("title"))
                else:
                    return await message.send("Playlist reorganized, next up: " + new_q_list[0].get("title"))

            # See if the first arg is a command to remove songs from the playlist
            except ValueError:
                try:
                    if str(args[0]) in ["clear", "delete", "del", "d", "remove", "rm", "r", "copy"] and args[1]:
                        positions = await parse_playlist_positions(args[1:], len(q_list))
                    else:
                        raise ValueError

                    changed_list = []
                    if args[0] != "copy":
                        cleared_list = q_list
                        q_list = []
                        for pos in positions:
                            changed_list.append(cleared_list[pos - 1])
                            cleared_list[pos - 1] = 0
                        for item in cleared_list:
                            if item != 0:
                                q_list.append(item)

                    else:
                        copied_list = q_list
                        q_list = []
                        for pos in positions:
                            changed_list.append(copied_list[pos - 1])
                            q_list.append(copied_list[pos - 1])
                        for item in copied_list:
                            q_list.append(item)

                    self.players[message.guild.id].queue = asyncio.Queue()
                    for item in q_list:
                        await self.players[message.guild.id].queue.put(item)
                    
                    if args[0] != "copy":
                        if len(positions) == 1:
                            return await message.send("Removed " + changed_list[0].get("title") + " from the playlist.")
                        else:
                            return await message.send("Removed selected tracks from the playlist.")
                    else:
                        if len(positions) == 1:
                            return await message.send("Copied " + changed_list[0].get("title") + " to the beginning of the playlist.")
                        else:
                            return await message.send("Copied the selected tracks.")

                # If arg at this point is not a plain clear command, args are invalid, print usage
                except (ValueError, IndexError):
                    if args[0] in ["clear", "delete", "del", "d", "remove", "rm", "r"] and (len(args) == 1):
                        self.players[message.guild.id].queue = asyncio.Queue()
                        return await message.send("I've cleared the playlist.")
                    await message.send("Usage for my playlist command is `" + custom.PREFIX[0] + "playlist <1 - " + str(settings.PLAYLIST_MSG_MAX_LEN) + ">` if you want to prioritize a song.")   

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        """ Event listener for the prefix- and command-less sound effect functionality. """
        if message.author.id != self.client.user.id:
            if not message.guild:
                return
            elif message.guild.id in self.players:
                if message.channel == self.players[message.guild.id].message.channel:
                    if os.path.exists(settings.SFX_PATH + message.content + ".mp3"):
                        return await self.fb_sfx(message, settings.SFX_PATH + message.content + ".mp3")
                    elif os.path.exists(settings.SFX_PATH + message.content + ".wav"):
                        return await self.fb_sfx(message, settings.SFX_PATH + message.content + ".wav")

    # ═══ Helper Methods ═══════════════════════════════════════════════════════════════════════════════════════════════
    def destroy_player(self, message):
        if message.guild.id in self.players:
            del self.players[message.guild.id]


# ═══ Functions ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def parse_playlist_positions(args, list_length: int):
    positions = []
    for a in args:
        a = int(a)
        if (a > 0) and (a <= settings.PLAYLIST_MSG_MAX_LEN) and (a <= list_length) and (a not in positions):
            positions.append(int(a))
    if len(positions) > 0:
        return positions
    else:
        raise ValueError


async def volume_gradient(player, message, vol):
    """ Increments or decrements the volume of the audioplayer in small intervals to generate a 
    gradient volume increase or decrease for listening comfort. `vol` being the requested volume level.""" 
    vol_old = int(message.guild.voice_client.source.volume * 100)
    if vol == 0:
        while vol_old > 0:
            vol_old -= 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.010)
        player.volume = 0
        return await message.send("Okay, I'm playing quietly for myself then...")
    elif vol < vol_old:
        while vol_old > vol:
            vol_old -= 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.010)
        player.volume = vol / 100
        return await message.send(":arrow_down_small: I've set the volume to {}%.".format(vol))
    else:
        while vol_old < vol:
            vol_old += 1
            message.guild.voice_client.source.volume = (vol_old / 100)
            sleep(0.010)
        player.volume = vol / 100
        return await message.send(":arrow_up_small: I've set the volume to {}%.".format(vol))


async def volume_no_gradient(player, message, vol):
    """ If no song is playing, sets the volume level `vol` for the audioplayer instantly. """ 
    vol_old = player.volume * 100
    if vol == 0:
        player.volume = 0
        return await message.channel.send("I've muted my music player.")
    elif vol < vol_old:
        player.volume = vol / 100
        return await message.channel.send(":arrow_down_small: I've set the volume to {}%.".format(vol))
    else:
        player.volume = vol / 100
        return await message.send(":arrow_up_small: I've set the volume to {}%.".format(vol))


async def check_volume(vol):
    """ Checks if `vol` is a valid integer ranging from 0 to 100. """ 
    try:
        vol = int(vol)
        if (-1 < vol) and (vol < 101):
            return True
        else:
            return False
    except (TypeError, ValueError):
        return False


async def get_video_id(url: str):
    """ Get the 11 chars long video id from a Youtube link. """
    if url.find("?v=") > 0:
        return url[url.find("?v=") + 3 : url.find("?v=") + 14] 
    elif url.find("&v=") > 0:
        return url[url.find("&v=") + 3 : url.find("&v=") + 14]
    elif url.find(".be/") > 0:
        return url[url.find(".be/") + 4 : url.find(".be/") + 15]
    else:
        return None


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Audio(client))


def teardown(client):
    client.remove_cog(Audio)
