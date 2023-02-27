import logbook
from discord import app_commands
from discord import Guild
from discord import Interaction
from discord import Member
from discord import Message
from discord import User
from discord.ext.commands import bot_has_guild_permissions
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import has_guild_permissions
from logging import Logger
from maon import Maon
from misc import Misc

from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandError

log: Logger = logbook.getLogger("audio")


class Audio(Cog):
    def __init__(self, maon: Maon) -> None:
        self.maon: Maon = maon

    
    @app_commands.command(name="join", description="Make Maon join your voice channel.")
    @app_commands.checks.has_permissions(connect=True)
    @app_commands.checks.bot_has_permissions(connect=True, speak=True)
    async def _join_ac(self, itc: Interaction) -> None | Message:
        ret: str | None = await self.join_voice(itc)
        if ret: 
            return await itc.response.send_message(ret)
        misc: Misc | None = self.maon.get_cog("Misc") # type: ignore
        if misc:
            return await itc.response.send_message(embed=await misc.get_cmds_embed_music())
        else:
            return await itc.response.send_message(":notes:")
    

    @command(aliases=["j", "join"])
    @guild_only()
    @has_guild_permissions(connect=True)
    @bot_has_guild_permissions(connect=True, speak=True)
    async def _join(self, ctx: Context) -> None | Message:
        ret: str | None = await self.join_voice(ctx)
        if ret:
            return await ctx.channel.send(ret)
        misc: Misc | None = self.maon.get_cog("Misc") # type: ignore
        if misc:
            return await ctx.channel.send(embed=await misc.get_cmds_embed_music())
        else:
            return await ctx.channel.send(":notes:")
    

    @_join.error
    async def _join_error(self, ctx: Context, e: CommandError):
        if isinstance(e, CheckFailure):
            if "Bot requires" in e.__str__():
                await ctx.channel.send("I lack permissions to join and speak in a voice channel.")
            else:
                return


    async def join_voice(self, cim: Context | Interaction | Message) -> None | str:
        if not cim.guild: return
        guild: Guild = cim.guild
        if isinstance(cim, Interaction) and isinstance(cim.user, Member):
            user: Member = cim.user
        elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
            user: Member = cim.author
        else: return
        if not user.voice or not user.voice.channel:
            return "You're not in a voice channel, if you are in a voice channel, I can't see it. :eyes:"
        if user.voice.channel.user_limit != 0 and user.voice.channel.user_limit - len(user.voice.channel.members) <= 0:
            return "The voice channel is full, someone has to scoot over. :flushed:"
        if guild.voice_client:
            if user.voice.channel != guild.voice_client.channel:
                return "Come in my voice channel, if you want me to play something. :eyes:"
        await user.voice.channel.connect()

    
    @app_commands.command(name="stop", description="Maon will stop playing music and leave the voice channel.")
    async def _stop_ac(self, itc: Interaction) -> None | Message:
        ret: str | None = await self.stop_voice(itc)
        if ret: return await itc.response.send_message(ret)
        return await itc.response.send_message("Disconnected from voice.")


    @command(aliases=["stop", "exit", "quit", "leave"])
    async def _stop(self, ctx: Context) -> None | Message:
        ret: str | None = await self.stop_voice(ctx)
        if ret: return await ctx.channel.send(ret)
    

    async def stop_voice(self, cim: Context | Interaction | Message) -> None | str:
        if not cim.guild: return
        guild: Guild = cim.guild
        if isinstance(cim, Interaction) and isinstance(cim.user, Member):
            user: Member = cim.user
        elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
            user: Member = cim.author
        else: return
        if user.voice is None:
            return
        if not guild.voice_client:
            return "I'm not connected to a voice channel."
        if user.voice.channel != guild.voice_client.channel:
            return "You're not in the same voice channel."
        log.info(f"{guild.name}: Stop request received for the audio player.")
        await guild.voice_client.disconnect(force=True)
    
                
    # ═══ Setup & Cleanup ══════════════════════════════════════════════════════════════════════════
    async def cog_unload(self) -> None:
        #log.info("Cancelling XXX_task...")
        #self.XXX_task.cancel()
        return


async def setup(maon: Maon) -> None:
    await maon.add_cog(Audio(maon))


async def teardown(maon: Maon) -> None:
    await maon.remove_cog("Audio")
