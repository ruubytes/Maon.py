from urllib import request
from discord.ext import commands
from extensions.player import audioplayer
from youtube_dl import YoutubeDL
from tinytag import TinyTag, TinyTagException
from lxml import etree
from time import sleep
import configuration as config
import os.path


class Audio(commands.Cog):
    __slots__ = ["client", "players"]

    def __init__(self, client):
        self.client = client
        self.players = {}

    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, message, *, url: str = None):
        if url is None:
            return await message.send(
                "You can browse the music folder with `browse music`, if you're looking for something specific.")
        elif url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/"):
            track = await prepare_link_track(url)
        elif os.path.exists(config.MUSIC_PATH + url + ".mp3"):
            track = await prepare_local_track(url + ".mp3")
        elif os.path.exists(config.MUSIC_PATH + url + ".wav"):
            track = await prepare_local_track(url + ".wav")
        else:
            return await message.send("I need a Youtube link or file path to play.")
        if track is None:
            return await message.send("The provided link is invalid.")

        if not await check_voice_state(message):
            return

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        await self.players[message.guild.id].queue.put(track)
        if message.guild.voice_client.is_playing():
            return await message.send("{} has been added to the queue.".format(track.get("title")), delete_after=20)

    async def fb_play(self, message, url):
        try:
            tag = TinyTag.get(url)
        except TinyTagException:
            return
        
        if not await check_voice_state(message):
            return
        
        if tag.title is None:
            tag.title = url[url.rfind("/") + 1:]
        track = {"title": tag.title, "url": url, "track_type": "music"}

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        await self.players[message.guild.id].queue.put(track)

    @commands.command(aliases=["s"])
    @commands.guild_only()
    async def sfx(self, message, *, url: str = None):
        track = {}
        if url is None:
            return await message.send(
                "You can browse the sfx folder with `browse sfx`, if you're looking for something specific.")
        elif os.path.exists(config.SFX_PATH + url + ".mp3"):
            track["url"] = config.SFX_PATH + url + ".mp3"
        elif os.path.exists(config.SFX_PATH + url + ".wav"):
            track["url"] = config.SFX_PATH + url + ".wav"
        else:
            return await message.send("Couldn't find the sound effect you were looking for...")

        track["title"] = url
        track["track_type"] = "sfx"  # link / music / sfx

        if not await check_voice_state(message):
            return

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        await self.players[message.guild.id].queue.put(track)

    async def fb_sfx(self, message, url):
        try:
            tag = TinyTag.get(url)
        except TinyTagException:
            return

        if not await check_voice_state(message):
            return

        if tag.title is None:
            tag.title = url[url.rfind("/") + 1:]
        track = {"title": tag.title, "url": url, "track_type": "sfx"}

        if message.guild.id not in self.players:
            self.players[message.guild.id] = audioplayer.AudioPlayer(self.client, message)
        await self.players[message.guild.id].queue.put(track)

    @commands.command(aliases=["v", "vol"])
    @commands.guild_only()
    async def volume(self, message, *, vol=None):
        if message.author.voice is None:
            return await message.send("You're not in a voice channel, silly.")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("You're not in the voice channel, silly.")
        elif message.guild.voice_client is None:
            return await message.send("I'm not even playing anything. :eyes:")
        elif message.guild.id not in self.players:
            return await message.send("I'm not even playing anything. :eyes:")
        elif vol is None:
            return await message.send("The volume is set to {}%.".format(
                int(self.players[message.guild.id].volume * 100)))

        if not await check_volume(vol):
            return await message.send("Please enter a number ranging from 0 to 100.")

        await volume_gradient(self.players[message.guild.id], message, int(vol))

    @commands.command(aliases=["j"])
    @commands.guild_only()
    async def join(self, message):
        if message.guild.voice_client is None:
            if message.author.voice:
                return await message.author.voice.channel.connect()
            else:
                return await message.send("You're not in a voice channel, silly. :eyes:")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.guild.voice_client.move_to(message.author.voice.channel)

    @commands.command(aliases=["next"])
    @commands.guild_only()
    async def skip(self, message):
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
    async def pause(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")
        elif not message.guild.voice_client.is_playing():
            return
        else:
            message.guild.voice_client.pause()
            return await message.send(":pause_button: Paused.")

    @commands.command(aliases=["res", "cont", "continue"])
    @commands.guild_only()
    async def resume(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return await message.send("I'm not playing anything. :eyes:")
        elif message.author.voice is None:
            return await message.send("You're not in a voice channel~")
        elif message.author.voice.channel != message.guild.voice_client.channel:
            return await message.send("I'm not taking orders from someone outside of our voice channel.")
        elif message.guild.voice_client.is_playing():
            return
        elif message.guild.id in self.players:
            message.guild.voice_client.resume()
            return await message.send(":arrow_forward: Continuing...")

    @commands.command(aliases=["leave", "l"])
    @commands.guild_only()
    async def stop(self, message):
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

    @commands.command(aliases=["d"])
    @commands.is_owner()
    async def download(self, message, media_type:str = None, *, url:str = None):
        if media_type is None:
            return await message.send("Do you want me to download a full `video` or just the `audio`?")
        elif url is None:
            return await message.send("I need a Youtube link to download from.")
        elif not url.startswith("https://www.youtube.com/") and not url.startswith("https://youtu.be/"):
            return await message.send("I need a Youtube link to download from.")
        elif (media_type != "audio") and (media_type != "video"):
            return await message.send("Do you want me to download a full `video` or just the `audio`?")

        youtube_feed = etree.HTML(request.urlopen(url).read())
        title = "".join(youtube_feed.xpath("//span[@id='eow-title']/@title"))

        await message.send("Downloading {}...".format(title))
        if media_type == "audio":
            YoutubeDL(config.YTDL_DOWNLOAD_AUDIO_OPTIONS).download([url])
        else:
            YoutubeDL(config.YTDL_DOWNLOAD_VIDEO_OPTIONS).download([url])
        return await message.send("Finished downloading {}!".format(title))

    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id in self.players:
            if message.channel == self.players[message.guild.id].message.channel:
                if os.path.exists(config.SFX_PATH + message.content + ".mp3"):
                    return await self.fb_sfx(message, config.SFX_PATH + message.content + ".mp3")
                elif os.path.exists(config.SFX_PATH + message.content + ".wav"):
                    return await self.fb_sfx(message, config.SFX_PATH + message.content + ".wav")

    # ═══ Helper Methods ═══════════════════════════════════════════════════════════════════════════════════════════════
    def destroy_player(self, message):
        if message.guild.id in self.players:
            del self.players[message.guild.id]
            print("[{}|{}] Audioplayer destroyed.".format(message.guild.name, message.guild.id))


# ═══ Functions ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def volume_gradient(player, message, vol):
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


async def check_volume(vol):
    try:
        vol = int(vol)
        if (-1 < vol) and (vol < 101):
            return True
        else:
            return False
    except (TypeError, ValueError):
        return False


async def check_voice_state(message):
    if message.guild.voice_client is None:
        if message.author.voice:
            await message.author.voice.channel.connect()
            return True
        else:
            await message.send("You're not in a voice channel, silly. :eyes:")
            return False
    elif message.author.voice.channel != message.guild.voice_client.channel:
        await message.send("Come in here if you want me to play something. :eyes:")
        return False
    return True


async def prepare_link_track(url: str):
    youtube_feed = etree.HTML(request.urlopen(url).read())
    title = "".join(youtube_feed.xpath("//span[@id='eow-title']/@title"))
    if len(title) != 0:
        track = {"title": title, "url": url, "track_type": "link"}
        return track
    return None


async def prepare_local_track(url: str):
    tag = TinyTag.get(config.MUSIC_PATH + url)
    if tag.title is None:
        tag.title = url
    track = {"title": tag.title, "url": config.MUSIC_PATH + url, "track_type": "music"}
    return track


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
def setup(client):
    client.add_cog(Audio(client))


def teardown(client):
    client.remove_cog(Audio)
