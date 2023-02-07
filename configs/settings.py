# Audio Settings:
SFX_VOLUME = 0.25           # Volume of special effects
PLAYER_TIMEOUT = 5400       # Seconds until Maon disconnects from a voice channel without any interaction
SONG_DURATION_MAX = 4000    # How long songs can be in seconds to be downloaded and stored locally, 0 to turn it off

DOWNLOAD_RATE_LIMITER = "3M"    # Limit the bandwith for downloading songs (e.g. 3M for 3 MegaBytes / s)

# Media Paths:
MUSIC_PATH = "./music/"
SFX_PATH = "./sfx/"
DOWNLOADS_PATH = "./downloads/"
TEMP_PATH = "./music/.Cached Songs/"

TEMP_FOLDER_MAX_SIZE_IN_MB = 51200

# Audioplayer Settings:
AUDIO_DOWNLOAD_CMD_DEFAULT = [
    "yt-dlp", 
    "--extract-audio", 
    "--audio-format",
    "mp3", 
    "--audio-quality",
    "192K",
    "--prefer-ffmpeg",
    "-o",
    f"{TEMP_PATH[2:]}%(title)s-%(id)s.%(ext)s",
    "-f",
    "format id goes into 10",
    "url goes into 11", 
    "--limit-rate",
    DOWNLOAD_RATE_LIMITER,
    "--embed-thumbnail"
]

BEFORE_ARGS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10"
FFMPEG_OPTIONS = {'options': '-vn'}
YTDL_INFO_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

PLAYLIST_MSG_MAX_LEN = 20

# Web Settings:
RFC_3986_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%"
MAL_API_ANIME_SEARCH_URL = "https://api.jikan.moe/v4/anime?q="
MAL_API_MANGA_SEARCH_URL = "https://api.jikan.moe/v4/manga?q="
MAL_API_ANIME_SEARCH_URL_OLD = "https://api.jikan.moe/v3/search/anime?q="

# Server Manager Settings:
SM_ENABLED = False
SM_ACCEPTED_GUILDS = [
    1234567890
]
SM_MINECRAFT_URL = ""
SM_MINECRAFT_API = "https://api.mojang.com/users/profiles/minecraft/"
SM_MINECRAFT_WL_RELOAD = ""

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
    ":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", 
    ":eight:", ":nine:", ":keycap_ten:"
]

# Maon's Extensions:
EXTENSION_PATH = "src." # Use . instead of / for folders as required by Discord.py
EXTENSION_LIST = [
    "admin", "audio", "basic", "console", "errormanager", "filebrowser", "fun", 
    "servermanager"
]

# Logging Settings:
LOGGING_DISCORD_PATH = "./src/logs/"
LOGGING_DISCORD_PATH_FILE = "./src/logs/maon"

# Help Command Embed:
from configs.custom import PREFIX
COMMANDLIST_EMBED_PREP_START = f"Prefix: {PREFIX[1]} (case insensitive)\n\n"

COMMANDLIST_EMBED_ADMIN_PREP = [
    ":flag_kp: ***Admin Commands:***\n",
    f":white_small_square: {PREFIX[1]}kill - Shuts Maon down.\n",
    f":white_small_square: {PREFIX[1]}reload <extension / all> - Unloads and loads extensions.\n",
    f":white_small_square: {PREFIX[1]}remove <number> - Removes messages in the channel.\n",
    f":white_small_square: {PREFIX[1]}status <listening/playing/watching> <status> - Sets Maon's status.\n",
    f":white_small_square: {PREFIX[1]}status cancel - Cancels Maon's looping status updates.\n",
    "\n"
]

COMMANDLIST_EMBED_BASIC_PREP = [
    ":beginner: ***Basic Commands:***\n",
    f":white_small_square: {PREFIX[1]}ping - Maon's latency.\n",
    f":white_small_square: {PREFIX[1]}<question> - Maon will reply to a closed (is, are, do, can...) question.\n",
    f":white_small_square: {PREFIX[1]}toss - Coin toss.\n",
    f":white_small_square: {PREFIX[1]}roll <number> - Roll a number from 1 to number.\n",
    f":white_small_square: {PREFIX[1]}poll <question> -o <choice 1 text> -o <choice 2 text>... - Make a quick poll\n",
    f":white_small_square: {PREFIX[1]}anime <search term> - Posts an anime title link closest to the search term.\n",
    f":white_small_square: {PREFIX[1]}manga <search term> - Posts a manga title link closest to the search term.\n",
    "\n"
]

COMMANDLIST_EMBED_MUSIC_PREP = [
    ":notes: ***Music Commands:***\n",
    f":white_small_square: {PREFIX[1]}reset - In case the audio module gets stuck\n",
    f":white_small_square: {PREFIX[1]}b <music / sfx> - Opens the file browser.\n",
    f":white_small_square: {PREFIX[1]}p <link / filepath / filename> - Plays a Youtube video or local music file.\n",
    f":white_small_square: {PREFIX[1]}s <filepath / filename> - Plays a local sound effect.\n",
    f":white_small_square: {PREFIX[1]}stop - Turns off the music player and makes Maon leave.\n",
    f":white_small_square: {PREFIX[1]}n - Skips to the next song.\n",
    f":white_small_square: {PREFIX[1]}v <0 - 100> - Changes the music player volume.\n",
    "\n:notes: ***Advanced Music Commands:***\n",
    f":white_small_square: {PREFIX[1]}pause - Pauses the music player.\n",
    f":white_small_square: {PREFIX[1]}res - Resumes the music player.\n",
    f":white_small_square: {PREFIX[1]}l <song / playlist / off> - Loops the current song or playlist.\n",
    f":white_small_square: {PREFIX[1]}shuffle - Shuffles the current playlist.\n",
    f":white_small_square: {PREFIX[1]}q - Displays the current playlist.\n",
    f":white_small_square: {PREFIX[1]}q <1 - 20> - Puts an entry to the front.\n",
    f":white_small_square: {PREFIX[1]}q r - Clears the playlist.\n",
    f":white_small_square: {PREFIX[1]}q r <1 - 20> - Removes a song from the playlist.\n",
    f":white_small_square: {PREFIX[1]}q copy <1 - 20> - Copies a track and inserts it at the beginning.\n",
    "\n"
]
