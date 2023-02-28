import logbook
from discord import app_commands
from discord import Guild
from discord import Interaction
from discord import Member
from discord import Message
from discord import User
from discord import VoiceClient
from discord.ext.commands import bot_has_guild_permissions
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import has_guild_permissions
from logging import Logger
from maon import Maon
from misc import Misc
from os.path import exists
from track import Track, create_local_track, create_stream_track
from utils import send_response

from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandError

log: Logger = logbook.getLogger("audio")


class Audio(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon
        self.path_music: str = self._set_path("music")
        self.path_sfx: str = self._set_path("sfx")


    def _set_path(self, folder_name: str) -> str:
        path: None | str | int | float = self.maon.settings.get(f"audio_path_{folder_name}")
        if isinstance(path, str) and exists(path):
            return path
        else:
            log.error(f"The path ({path}) to my {folder_name} folder is faulty, please change it in my settings.json file.")
            exit(1)


    @app_commands.command(name="play", description="Play a youtube link or a file from Maon's music folder.")
    @app_commands.describe(url="This can be a Youtube link or file path inside Maon's music folder.")
    @app_commands.checks.has_permissions(connect=True)
    @app_commands.checks.bot_has_permissions(connect=True, speak=True)
    async def _play_ac(self, itc: Interaction, url: str) -> None | Message:
        return await itc.response.send_message("Cool.")


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
        if url.startswith("https://"):
            await self.create_stream_track(cim, url) 
        elif exists(f"{self.path_music}{url}.mp3") or exists(f"{self.path_music}{url}.wav"):
            await self.create_local_track(cim, url)
        elif exists(f"{self.path_music}{url}.ogg") or exists(f"{self.path_music}{url}.flac"):
            await self.create_local_track(cim, url)
        elif exists(f"{self.path_sfx}{url}.mp3") or exists(f"{self.path_sfx}{url}.wav"):
            await self.create_local_track(cim, url)
        elif exists(f"{self.path_sfx}{url}.ogg") or exists(f"{self.path_sfx}{url}.flac"):
            await self.create_local_track(cim, url)
        else:
            return await send_response(cim, "I need a Youtube link to stream or a file path to play from my music folder.")

    
    async def create_stream_track(self, cim: Context | Interaction | Message, url: str) -> None | Message:
        log.info(f"{cim.guild}: Creating stream track for {url}")
        track: None | Track = await create_stream_track(cim, url)
        return
    

    async def create_local_track(self, cim: Context | Interaction | Message, url: str) -> None | Message:
        log.info(f"{cim.guild}: Creating local track for {url}")
        return


    @app_commands.command(name="join", description="Make Maon join your voice channel.")
    @app_commands.checks.has_permissions(connect=True)
    @app_commands.checks.bot_has_permissions(connect=True, speak=True)
    async def _join_ac(self, itc: Interaction) -> None | Message:
        await self.join_voice(itc)


    @command(aliases=["j", "join"])
    @guild_only()
    @has_guild_permissions(connect=True)
    @bot_has_guild_permissions(connect=True, speak=True)
    async def _join(self, ctx: Context) -> None | Message:
        await self.join_voice(ctx)


    @_play.error
    @_join.error
    async def _join_error(self, ctx: Context, e: CommandError):
        if isinstance(e, CheckFailure):
            if "Bot requires" in e.__str__():
                await ctx.channel.send("I lack permissions to join and speak in a voice channel.")
            else:
                return


    async def join_voice(self, cim: Context | Interaction | Message) -> None | Message:
        if not cim.guild: return
        guild: Guild = cim.guild
        if isinstance(cim, Interaction) and isinstance(cim.user, Member):
            user: Member = cim.user
        elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
            user: Member = cim.author
        else: return
        if not user.voice or not user.voice.channel:
            return await send_response(cim, "You're not in a voice channel, if you are in a voice channel, I can't see it. :eyes:")
        if user.voice.channel.user_limit != 0 and user.voice.channel.user_limit - len(user.voice.channel.members) <= 0:
            return await send_response(cim, "The voice channel is full, someone has to scoot over. :flushed:")
        if guild.voice_client:
            if user.voice.channel != guild.voice_client.channel:
                return await send_response(cim, "Come in my voice channel, if you want me to play something. :eyes:")
        await user.voice.channel.connect()
        misc: Misc | None = self.maon.get_cog("Misc") # type: ignore
        if misc:
            return await send_response(cim, await misc.get_cmds_embed_music())
        else:    
            return await send_response(cim, ":notes:")

    
    @app_commands.command(name="stop", description="Maon will stop playing music and leave the voice channel.")
    async def _stop_ac(self, itc: Interaction) -> None | Message:
        await self.stop(itc)
        

    @command(aliases=["stop", "exit", "quit", "leave"])
    async def _stop(self, ctx: Context) -> None | Message:
        await self.stop(ctx)
        

    async def stop(self, cim: Context | Interaction | Message) -> None | Message:
        if not cim.guild: return
        guild: Guild = cim.guild
        if isinstance(cim, Interaction) and isinstance(cim.user, Member):
            user: Member = cim.user
        elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
            user: Member = cim.author
        else: return
        if user.voice is None:
            if isinstance(cim, Interaction):
                return await cim.response.send_message("You are not connected to a voice channel.")
            return
        if not guild.voice_client:
            return await send_response(cim, "I'm not connected to a voice channel.")
        if user.voice.channel != guild.voice_client.channel:
            return await send_response(cim, "You're not in the same voice channel as me.")
        log.info(f"{guild.name}: Stop request received for the audio player.")
        await guild.voice_client.disconnect(force=True)
        if isinstance(cim, Interaction):
            return await cim.response.send_message("Disconnected from voice.")
    
                
    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(Audio(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Audio")
