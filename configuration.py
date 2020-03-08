# Owner and Maon's IDs.
OWNER_ID = 0
MAON_ID = 0

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
EXTENSION_LIST = ["admin", "audio", "basic", "errormanager", "filebrowser"]

# Maon Version:
SIGNATURE = '''
|   __                __            |
|  /__\ __ _  ___  /\ \ \___  _ __  |
| / \/// _` |/ _ \/  \/ / _ \| '_ \ |
|/ _  \ (_| |  __/ /\  / (_) | | | ||
|\/ \_/\__,_|\___\_\ \/ \___/|_| |_||
       Maon v0.5 - 2020-03-08
'''
VERSION = "Maon v0.5 - 2020-03-08"
AUTHOR_ID = 0