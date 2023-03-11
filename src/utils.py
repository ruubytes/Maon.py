from discord import Embed
from discord import Interaction
from discord import Member
from discord import Message
from discord.ext.commands import Context


async def send_response(cim: Context | Interaction | Message, text: str | Embed) -> None | Message:
    """`Context` and `Message` reply to a channel, but `Interaction` responds explicitly
    to a specific message, so to reply to all command invocations, this can be used."""
    if isinstance(cim, Interaction):
        if isinstance(text, Embed):
            return await cim.response.send_message(embed=text)
        return await cim.response.send_message(text)
    else:
        if isinstance(text, Embed):
            return await cim.channel.send(embed=text)
        return await cim.channel.send(text)


async def get_user(cim: Context | Interaction | Message) -> Member | None:
    """Fetches the command requestee from `Context`, `Interaction` and `Message` objects."""
    if isinstance(cim, Interaction) and isinstance(cim.user, Member):
        return cim.user
    elif isinstance(cim, Context | Message) and isinstance(cim.author, Member):
        return cim.author
    else: return
    