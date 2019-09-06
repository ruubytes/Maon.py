PREFIX = ["wmaon ", "Maon ", "mAon ", "maOn ", "maoN ", "MAon ", "mAOn ", "maON ",
    "MAOn ", "mAON ", "MAON "]
PREFIX_FAST = "wmaon"
COLOR_HEX = 0xf8d386

# Admin Configuration:
EXTENSION_LIST = ["admin", "errorhandler", "audio", "browser", "fun"]

# Music Configuration:
IMG_PATH = "./img/"
MUSIC_PATH = "./music/"
SFX_PATH = "./sfx/"
SFX_VOLUME = 0.5
PLAYER_TIMEOUT_VALUE = 7200
SFX_SHORTCUT = ["oof", "oh no", "d", "c", "b", "a", "s", "ss", "sss", "hahaha",
    "you never see it coming"]

# Browser Configuration:
CMD_REACTIONS = [
    "0\N{COMBINING ENCLOSING KEYCAP}", "1\N{COMBINING ENCLOSING KEYCAP}",
    "2\N{COMBINING ENCLOSING KEYCAP}", "3\N{COMBINING ENCLOSING KEYCAP}",
    "4\N{COMBINING ENCLOSING KEYCAP}", "5\N{COMBINING ENCLOSING KEYCAP}",
    "6\N{COMBINING ENCLOSING KEYCAP}", "7\N{COMBINING ENCLOSING KEYCAP}",
    "8\N{COMBINING ENCLOSING KEYCAP}", "9\N{COMBINING ENCLOSING KEYCAP}",
    "\N{KEYCAP TEN}", "\N{LEFTWARDS ARROW WITH HOOK}",
    "\N{LEFTWARDS BLACK ARROW}", "\N{BLACK RIGHTWARDS ARROW}"
]

# AudioPlayer Configuration:
AP_CMD_REACTIONS = [
    "0\N{COMBINING ENCLOSING KEYCAP}", "1\N{COMBINING ENCLOSING KEYCAP}",
    "2\N{COMBINING ENCLOSING KEYCAP}", "3\N{COMBINING ENCLOSING KEYCAP}",
    "4\N{COMBINING ENCLOSING KEYCAP}", "5\N{COMBINING ENCLOSING KEYCAP}",
    "6\N{COMBINING ENCLOSING KEYCAP}", "7\N{COMBINING ENCLOSING KEYCAP}",
    "8\N{COMBINING ENCLOSING KEYCAP}", "9\N{COMBINING ENCLOSING KEYCAP}",
    "\N{KEYCAP TEN}", "\N{LEFTWARDS ARROW WITH HOOK}",
    "\N{LEFTWARDS BLACK ARROW}", "\N{BLACK RIGHTWARDS ARROW}"
]

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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

download_video_opts = {
    'format': 'best',
    'outtmpl': './downloads/%(title)s-%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True
}

download_audio_opts = {
    'format': 'bestaudio',
    'outtmpl': './downloads/%(title)s-%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }]
}

ffmpeg_options = {
    'options': '-vn'
}

before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

COMMANDLIST_EMBED_PREP = [
    "Prefix: Maon (case insensitive)\n\n",
    ":beginner: ***Useful Commands:***\n",
    ":white_small_square: ping - Maon's latency.\n",
    ":white_small_square: help / infocard - What you're looking at right now.\n",
    "\n",
    ":flag_kp: ***Admin Commands:*** (requires ownership)\n",
    ":white_small_square: refresh <extension> - Unloads and loads an extension.\n",
    ":white_small_square: echo <input> - Maon will say <input> and delete the message to be echoed.\n",
    ":white_small_square: remove <number> - Removes <number> messages in the channel.\n",
    ":white_small_square: shutmedown - Shuts Maon down.\n",
    ":white_small_square: emojiname - Returns the unicode for an emoji.\n",
    "\n",
    ":notes: ***Music Commands:***\n",
    ":white_small_square: browse <music / sfx> - Opens the file browser.\n",
    ":white_small_square: play <link / filepath> - Plays a Youtube video or local file.\n",
    ":white_small_square: stop / leave - Turns off the music player.\n",
    ":white_small_square: queue - Lists the current playlist.\n",
    ":white_small_square: skip - Skips the current song.\n",
    ":white_small_square: loop song / queue - Loops the current song or queue.\n",
    ":white_small_square: volume / vol <number 0 - 100> - Changes the music player volume.\n",
    ":white_small_square: pause - Pauses the music player.\n",
    ":white_small_square: resume / cont / continue - Resumes the music player.\n",
    "\n",
    ":juggling: ***Fun Commands:***\n",
    ":white_small_square: <question> - Maon will reply to your question."
]

SIGNATURE = '''
|   __                __            |
|  /__\ __ _  ___  /\ \ \___  _ __  |
| / \/// _` |/ _ \/  \/ / _ \| '_ \ |
|/ _  \ (_| |  __/ /\  / (_) | | | ||
|\/ \_/\__,_|\___\_\ \/ \___/|_| |_||
       Maon v0.4 - 2019-09-06
'''
