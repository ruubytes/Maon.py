# Prefix And Embed Color:
PREFIX = ["maon ", "Maon ", "mAon ", "maOn ", "maoN ", "MAon ", "mAOn ", "maON ", "MAOn ", "mAON ", "MAON "]
COLOR_HEX = 0xf8d386

# Media Paths:
MUSIC_PATH = "./music/"
SFX_PATH = "./sfx/"
DOWNLOADS_PATH = "./downloads/"

# Audio Settings:
SFX_VOLUME = 0.4
PLAYER_TIMEOUT = 7200
before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
ffmpeg_options = {'options': '-vn'}
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

# Activity Texts:
STATUS_TEXT_LISTENING_TO = [
    "chillhop",
    "the flushing toilet",
    "the cats outside",
    "toilet paper ASMR"
]

STATUS_TEXT_WATCHING = [
    "the invisible people", 
    "the server",
    "the clock",
    "boring late night shows",
    "animu and mango",
    "Rudel's shenanigans",
    "the toilet paper cache"
]

STATUS_TEXT_PLAYING = [
    "with fire",
    "with the server settings",
    "with toilet paper"
]

# Browser Configuration:
CMD_SLOT_REACTIONS = [
    "0\N{COMBINING ENCLOSING KEYCAP}", "1\N{COMBINING ENCLOSING KEYCAP}",
    "2\N{COMBINING ENCLOSING KEYCAP}", "3\N{COMBINING ENCLOSING KEYCAP}",
    "4\N{COMBINING ENCLOSING KEYCAP}", "5\N{COMBINING ENCLOSING KEYCAP}",
    "6\N{COMBINING ENCLOSING KEYCAP}", "7\N{COMBINING ENCLOSING KEYCAP}",
    "8\N{COMBINING ENCLOSING KEYCAP}", "9\N{COMBINING ENCLOSING KEYCAP}",
    "\N{KEYCAP TEN}"
]
CMD_NAV_REACTIONS = [
    "\N{LEFTWARDS ARROW WITH HOOK}", "\N{LEFTWARDS BLACK ARROW}", "\N{BLACK RIGHTWARDS ARROW}",
    "\N{NEGATIVE SQUARED CROSS MARK}"
]
EMOJI_LIST = [
    ":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"
]

# Maon's Extensions:
EXTENSION_PATH = "extensions." # Use . instead of / for folders as required by Discord.py
EXTENSION_LIST = ["admin", "audio", "basic", "errormanager", "filebrowser", "fun"]

# Help Command Embed:
COMMANDLIST_EMBED_PREP_START = "Prefix: Maon (case insensitive)\n\n"

COMMANDLIST_EMBED_ADMIN_PREP = [
    ":flag_kp: ***Admin Commands:*** (requires ownership)\n",
    ":white_small_square: kill - Shuts Maon down.\n",
    ":white_small_square: reload <extension / all> - Unloads and loads extensions.\n",
    ":white_small_square: remove <number> - Removes messages in the channel.\n",
    ":white_small_square: status <listening/playing/watching> <status> - Sets Maon's status.\n",
    ":white_small_square: status cancel - Cancels Maon's looping status updates.\n",
    "\n"
]

COMMANDLIST_EMBED_PREP = [
    ":beginner: ***Useful Commands:***\n",
    ":white_small_square: ping - Maon's latency.\n",
    ":white_small_square: help / info - What you're looking at right now.\n",
    "\n",
    ":notes: ***Music Commands:***\n",
    ":white_small_square: browse <music / sfx> - Opens the file browser.\n",
    ":white_small_square: play <link / filepath> - Plays a Youtube video or local file.\n",
    ":white_small_square: sfx <link / filepath> - Plays a local sound effect.\n",
    ":white_small_square: stop / leave - Turns off the music player.\n",
    ":white_small_square: skip - Skips the current song.\n",
    ":white_small_square: loop <song / queue> - Loops the current song or queue.\n",
    ":white_small_square: volume / vol <number 0 - 100> - Changes the music player volume.\n",
    ":white_small_square: pause - Pauses the music player.\n",
    ":white_small_square: resume / cont / continue - Resumes the music player.\n",
    "\n",
    ":juggling: ***Fun Commands:***\n",
    ":white_small_square: <question> - Maon will reply to your question.\n",
    ":white_small_square: toss - Coin toss.\n",
    ":white_small_square: roll / rng / dice <number> - Roll a number.\n"
]

# Maon Version:
SIGNATURE = '''
|   __                __            |
|  /__\ __ _  ___  /\ \ \___  _ __  |
| / \/// _` |/ _ \/  \/ / _ \| '_ \ |
|/ _  \ (_| |  __/ /\  / (_) | | | ||
|\/ \_/\__,_|\___\_\ \/ \___/|_| |_||
       Maon v0.07 - 2020-03-23
'''
VERSION = "Maon v0.07 - 2020-03-23"
