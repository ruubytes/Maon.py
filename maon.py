import asyncio
import login
import logger
import configuration
import discord
from discord.ext import commands

print(configuration.SIGNATURE)
client = commands.Bot(command_prefix = configuration.PREFIX,
    case_insensitive = True, owner_id = login.OWNER_ID)
client.remove_command("help")

for ext in configuration.EXTENSION_LIST:
    logger.log_info("loading {}...".format(ext))
    client.load_extension(ext)

logger.log_info("logging in...")
client.run(login.TOKEN)
