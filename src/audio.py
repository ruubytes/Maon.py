from __future__ import annotations
import logbook
import subprocess
from asyncio import create_task
from asyncio import Queue
from asyncio import Task
from audio_player import AudioPlayer
from discord import app_commands
from discord import Embed
from discord import Interaction
from discord import Member
from discord import Message
from discord import VoiceClient
from discord.ext.commands import bot_has_guild_permissions
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import has_guild_permissions
from logging import Logger
from os import listdir
from os.path import exists
from os.path import getsize
from track import create_local_track
from track import create_stream_track
from utils import get_user
from utils import send_response

from asyncio import CancelledError
from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from maon import Maon
    from misc import Misc
    from track import Track

log: Logger = logbook.getLogger("audio")


# TODO Fetch bitrate of voice channel and adjust ffmpeg stream accordingly
# TODO Implement guild data again for incrementing cached tracks size
# TODO Volume of 0 not working
class Audio(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon
        self.path_music: str = self._set_path("music")
        self.path_sfx: str = self._set_path("sfx")
        self.rate_limit: str = self._set_rate_limit()
        self.cached_tracks: dict[str, str] = self._load_cache()
        self.players: dict[int, AudioPlayer] = {}
        self.download_q: Queue[Track] = Queue()
        self.cache_q: Queue[Track] = Queue()
        self.download_task: Task = create_task(self.download_loop(), name="download_task")


    def _set_path(self, folder_name: str) -> str:
        path: None | str | int | float = self.maon.settings.get(f"audio_path_{folder_name}")
        if isinstance(path, str) and exists(path):
            return path
        else:
            log.error(f"The path ({path}) to my {folder_name} folder is faulty, please change it in my settings.json file.")
            exit(1)


    def _set_rate_limit(self) -> str:
        rate: str | int | float | None = self.maon.settings.get("audio_download_rate_bandwidth_limit")
        if isinstance(rate, str):
            return rate
        else:
            log.error(f"The bandwidth limit is not set correctly in my settings file, please change it in my settings.json file.")
            return "3M"
        

    def _load_cache(self) -> dict[str, str]:
        log.info("Loading audio cache...")
        try:
            cache_dir: list[str] = listdir(f"{self.path_music}.Cached Tracks/")
            cached_tracks: dict[str, str] = {}
            for file_name in cache_dir:
                if file_name.endswith(".mp3"):
                    video_id = file_name[len(file_name) - 15 : len(file_name) - 4]
                    cached_tracks[video_id] = f"{self.path_music}.Cached Tracks/{file_name}"
            return cached_tracks
        except FileNotFoundError:
            log.warning("The '.Cached Tracks' folder does not exist, skipped loading the cache.")
            return {}


    async def download_loop(self) -> None:
        download_cmd: list[str] = [
            "yt-dlp", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "192K",
            "--prefer-ffmpeg", "--limit-rate", f"{self.rate_limit}", "--embed-thumbnail",
            "--age-limit", "21", "--windows-filenames", "-o",
            f"{self.path_music}.Cached Tracks/%(title)s-%(id)s.%(ext)s",
            "-f", "format id goes here (16)", "url goes here (17)"
        ]
        try:
            while True:
                track: Track = await self.download_q.get()
                if not track.video_id or not track.format or not track.url_original or track.video_id in self.cached_tracks: continue

                download_cmd[16] = track.format[0]
                download_cmd[17] = track.url_original
                log.info(f"Beginning background download for {track.title} with command:\n{' '.join(download_cmd)}")
                r = await self.maon.loop.run_in_executor(
                    None, lambda: subprocess.run(download_cmd, stdout=subprocess.PIPE).returncode
                )
                if r == 0:
                    await self._cache_track(track.video_id)
                else:
                    log.error(f"Background download failed for {track.title}. Error code: {r}")

        except CancelledError:
            pass


    async def _cache_track(self, video_id: str) -> None:
        try:
            track_size: float = 0
            cache_dir: list[str] = listdir(f"{self.path_music}.Cached Tracks/")
            for file_name in cache_dir:
                if file_name.endswith(f"{video_id}.mp3"):
                    self.cached_tracks[video_id] = f"{self.path_music}.Cached Tracks/{file_name}"
                    track_size = round(getsize(f"{self.path_music}.Cached Tracks/{file_name}") / (1024**2), 2)
                    log.info(f"Cached track: {self.path_music}.Cached Tracks/{file_name} | Size: {track_size} MB")
        except FileNotFoundError:
            log.error(f"I lost the track I should add to the cache directory... how did that happen.")


    @app_commands.command(name="play", description="Play a youtube link or a file from Maon's music folder.")
    @app_commands.describe(url="This can be a Youtube link or file path inside Maon's music folder.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(connect=True)
    @app_commands.checks.bot_has_permissions(connect=True, speak=True)
    async def _play_ac(self, itc: Interaction, url: str) -> None | Message:
        return await self.play(itc, url)


    @command(aliases=["p", "play", "stream", "yt"])
    @has_guild_permissions(connect=True)
    @bot_has_guild_permissions(connect=True, speak=True)
    async def _play(self, ctx: Context, *, url: str) -> None | Message:
        return await self.play(ctx, url)
    

    async def play(self, cim: Context | Interaction | Message, url: str | None) -> None | Message:
        if not cim.guild: return
        log.info(f"{cim.guild}: Play request received for {url}")
        prefix: str = await self.maon.get_prefix_str()
        usage: str = f"You can play a Youtube link with `{prefix}p <link>` or play a file from my music folder like `{prefix}p <path>`."
        if isinstance(cim, Interaction) and isinstance(cim.user, Member):
            user: Member = cim.user
        elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
            user: Member = cim.author
        else: return

        if not url:
            if cim.guild.voice_client and isinstance(cim.guild.voice_client, VoiceClient) and cim.guild.voice_client.is_paused():
                cim.guild.voice_client.resume()
                return await send_response(cim, ":arrow_forward: Continuing...")
            return await send_response(cim, usage)
        
        track: None | Track = None
        if url.startswith("https://"):
            track = await create_stream_track(self, cim, url) 
        else:
            for ext in [".mp3", ".flac", ".ogg", ".wav"]:
                if exists(f"{self.path_music}{url}{ext}"):
                    track = await create_local_track(self, cim, f"{self.path_music}{url}{ext}")
                elif exists(f"{self.path_sfx}{url}{ext}"):
                    track = await create_local_track(self, cim, f"{self.path_sfx}{url}{ext}")
        if not track:
            if isinstance(cim, Interaction) and cim.response.is_done(): return
            if url.startswith("https://"):
                return await send_response(cim, f"This link doesn't look like a valid Youtube link to me.")
            else: 
                return await send_response(cim, f"I could not find that song in my folders.\n{usage}")
        log.info(f"{cim.guild.name}: Track created: \n{track}")
        
        await self.join_voice(cim)
        if not cim.guild.voice_client: return

        log.info("Fetching audio player...")
        player: None | AudioPlayer = self.players.get(cim.guild.id)
        if not player:
            log.info(f"{cim.guild.name}: Creating new audio player...")
            player = AudioPlayer(self.maon, cim)
            if player: 
                self.players[cim.guild.id] = player
            else: 
                log.error(f"{cim.guild.name}: Creation of my audio player failed.")
                return await send_response(cim, f"I could not create my audio player.")
        await player.queue.put(track) 
        if isinstance(cim, Interaction):
            if not cim.response.is_done():
                return await send_response(cim, f"{track.title} added to queue.")
            else: return
        return await send_response(cim, f"{track.title} added to queue.")


    def remove_player(self, id: int):
        if id in self.players.keys():
            self.players.pop(id)


    @app_commands.command(name="join", description="Make Maon join your voice channel.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(connect=True)
    @app_commands.checks.bot_has_permissions(connect=True, speak=True)
    async def _join_ac(self, itc: Interaction) -> None | Message:
        if itc.guild and itc.guild.voice_client:
            return await itc.response.send_message("I'm already in a voice channel.")
        await self.join_voice(itc)


    @command(aliases=["j", "join"])
    @guild_only()
    @has_guild_permissions(connect=True)
    @bot_has_guild_permissions(connect=True, speak=True)
    async def _join(self, ctx: Context) -> None | Message:
        await self.join_voice(ctx)


    @_join.error
    async def _join_error(self, ctx: Context, e: CommandError) -> None:
        if isinstance(e, CheckFailure):
            if "Bot requires" in e.__str__():
                await ctx.channel.send("I lack permissions to join and speak in a voice channel.")
            else:
                return


    async def join_voice(self, cim: Context | Interaction | Message) -> None | Message:
        if not cim.guild: return
        user: Member | None = await get_user(cim)
        if not user: return

        if not user.voice or not user.voice.channel:
            return await send_response(cim, "You're not in a voice channel, if you are in a voice channel, I can't see it. :eyes:")
        if user.voice.channel.user_limit != 0 and user.voice.channel.user_limit - len(user.voice.channel.members) <= 0:
            return await send_response(cim, "The voice channel is full, someone has to scoot over. :flushed:")
        if cim.guild.voice_client:
            if user.voice.channel != cim.guild.voice_client.channel:
                return await send_response(cim, "We're not in the same voice channel. :eyes:")
            else: return

        try:
            voice_client: VoiceClient = await user.voice.channel.connect()
        except TimeoutError:
            return await send_response(cim, "I could not connect to the voice channel.")
        log.info(f"{cim.guild.name}: Joined voice channel '{voice_client.channel.name}'.")
        log.info(f"{cim.guild.name}: Creating new audio player...")
        player: AudioPlayer = AudioPlayer(self.maon, cim)
        if player: 
            self.players[cim.guild.id] = player
        else: 
            log.error(f"{cim.guild.name}: Creation of my audio player failed.")
            return await send_response(cim, f"I could not create my audio player.")
        
        misc: Misc | None = self.maon.get_cog("Misc") # type: ignore
        if misc:
            embed: Embed = await misc.get_cmds_embed_music()
            return await send_response(cim, embed)
        else:    
            return await send_response(cim, ":notes:")
        

    async def check_voice(self, cim: Context | Interaction | Message) -> bool:
        if not cim.guild: return False
        user: Member | None = await get_user(cim)
        if not user: return False

        if not user.voice:
            if isinstance(cim, Interaction):
                await cim.response.send_message("You are not connected to a voice channel.")
                return False
            else:
                return False
        if not cim.guild.voice_client or (cim.guild.id not in self.players):
            await send_response(cim, "I'm not connected to a voice channel.")
            return False
        if user.voice.channel != cim.guild.voice_client.channel:
            await send_response(cim, "You're not in the same voice channel as me.")
            return False
        return True

    
    @app_commands.command(name="stop", description="Maon will stop playing music and leave the voice channel.")
    @app_commands.guild_only()
    async def _stop_ac(self, itc: Interaction) -> None | Message:
        await self.stop(itc)
        

    @command(aliases=["stop", "exit", "quit", "leave"])
    async def _stop(self, ctx: Context) -> None | Message:
        await self.stop(ctx)
        

    async def stop(self, cim: Context | Interaction | Message) -> None | Message:
        if not cim.guild: return
        if not await self.check_voice(cim): return

        log.info(f"{cim.guild.name}: Stop request received for the audio player.")
        player: None | AudioPlayer = self.players.get(cim.guild.id)
        if not player:
            return await send_response(cim, "I lost track of my audio player... How did that happen.")
        player.close()
        if isinstance(cim, Interaction):
            return await cim.response.send_message("Disconnected from voice.")
        

    @app_commands.command(name="volume", description="Change Maon's audio player volume.")
    @app_commands.describe(volume="Enter an audio volume amount, ranging from 0 to 100.")
    @app_commands.guild_only()
    async def _volume_ac(self, itc: Interaction, volume: app_commands.Range[int, 0, 100]) -> None | Message:
        return await self.volume(itc, volume)


    @command(aliases=["v", "vol", "volume"])
    async def _volume(self, ctx: Context, v: int | None) -> None | Message:
        return await self.volume(ctx, v)


    # TODO volume of 0 not working
    async def volume(self, cim: Context | Interaction | Message, v: int | None) -> None | Message:
        if not cim.guild: return
        if not await self.check_voice(cim): return
        
        player: AudioPlayer | None = self.players.get(cim.guild.id)
        if not player:
            return await send_response(cim, "I'm not playing anything right now.")
        if not v:
            return await send_response(cim, f"The volume is set to {int(player.volume * 100)}%.")
        if v < 0 or v > 100:
            return await send_response(cim, f"The volume can only range from 0 to 100.")
        
        v_old: int = int(player.volume * 100)
        await player.volume_controller.put(v)
        log.info(f"{cim.guild.name}: Changed volume of audio player to {v}%.")
        if v > v_old:
            return await send_response(cim, f":arrow_up_small: Volume set to {v}%.")
        elif v < v_old:
            return await send_response(cim, f":arrow_down_small: Volume set to {v}%.")
        elif v == v_old:
            return await send_response(cim, f"The volume is set to {v}%.")
        else:
            # TODO Change this to pause the playback at some point.
            return await send_response(cim, "Okay, I'm quietly playing for myself, then.")
        

    @app_commands.command(name="skip", description="Skips the currently playing song.")
    @app_commands.guild_only()
    async def _skip_ac(self, itc: Interaction) -> None | Message:
        return await self.skip(itc)
    

    @command(aliases=["n", "next", "nxt", "skip"])
    async def _skip(self, ctx: Context) -> None | Message:
        return await self.skip(ctx)
    

    async def skip(self, cim: Context | Interaction | Message) -> None | Message:
        if not cim.guild: return
        if not await self.check_voice(cim): return

        player: AudioPlayer | None = self.players.get(cim.guild.id)
        if not player:
            return await send_response(cim, "I'm not playing anything right now.")
        if not cim.guild.voice_client.is_playing(): # type: ignore
            if isinstance(cim, Interaction):
                return await send_response(cim, "I'm not playing anything right now.")
            else:
                return
        else:
            cim.guild.voice_client.stop()   # type: ignore
            return await send_response(cim, ":track_next: Skipping...")


    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════
    @Cog.listener()
    async def on_message(self, msg: Message) -> None | Message:
        if not msg.guild or (msg.author.id == self.maon.user.id): return    # type: ignore
        try:
            if not msg.author.voice: return     # type: ignore
        except AttributeError:
            return log.info(f"{msg.guild.name}: Attribute error caught for author lacking a voice protocol.")
        
        log.info(f"A user in a voice channel posted a message.")
        # Is the message in the bot channel?
        # TODO Needs guild_data implemented

                
    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        log.info("Cancelling player tasks...")
        players = self.players.copy()
        for id, player in players.items():
            log.info(f"Closing {player.name} audio player...")
            player.close()


async def setup(maon: Maon) -> None:
    await maon.add_cog(Audio(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Audio")
