# Audio Settings:
SFX_VOLUME = 0.3            # Volume of special effects
PLAYER_TIMEOUT = 5400       # Seconds until Maon disconnects from a voice channel without any interaction
SONG_DURATION_MAX = 600     # How long songs can be in seconds to be downloaded and stored locally

DOWNLOAD_RATE_LIMITER = "3M"    # Limit the bandwith when Maon downloads songs (e.g. 3M for 3 MegaBytes / s)

# Media Paths:
MUSIC_PATH = "./music/"
SFX_PATH = "./sfx/"
DOWNLOADS_PATH = "./downloads/"
TEMP_PATH = "./music/.Cached Songs/"

TEMP_FOLDER_MAX_SIZE_IN_MB = 20480

# Audioplayer Settings:
AUDIO_DOWNLOAD_CMD_DEFAULT = [
    "youtube-dl", 
    "--extract-audio", 
    "--audio-format",
    "mp3", 
    "--audio-quality",
    "192K",
    "--prefer-ffmpeg",
    "-o",
    TEMP_PATH[2:] + "%(title)s-%(id)s.%(ext)s",
    "-f",
    "format id goes into 10",
    "url goes into 11", 
    "--limit-rate",
    DOWNLOAD_RATE_LIMITER
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
MAL_API_ANIME_SEARCH_URL = "https://api.jikan.moe/v3/search/anime?q="
MAL_API_MANGA_SEARCH_URL = "https://api.jikan.moe/v3/search/manga?q="

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
EXTENSION_PATH = "src." # Use . instead of / for folders as required by Discord.py
EXTENSION_LIST = ["admin", "audio", "basic", "errormanager", "filebrowser", "fun"]

# Logging Settings:
LOGGING_DISCORD_PATH = "./src/logs/discord"

# Help Command Embed:
from configs.custom import PREFIX
COMMANDLIST_EMBED_PREP_START = "Prefix: " + PREFIX[0] + " (case insensitive)\n\n"

COMMANDLIST_EMBED_ADMIN_PREP = [
    ":flag_kp: ***Admin Commands:***\n",
    ":white_small_square: " + PREFIX[0] + "kill - Shuts Maon down.\n",
    ":white_small_square: " + PREFIX[0] + "reload <extension / all> - Unloads and loads extensions.\n",
    ":white_small_square: " + PREFIX[0] + "remove <number> - Removes messages in the channel.\n",
    ":white_small_square: " + PREFIX[0] + "status <listening/playing/watching> <status> - Sets Maon's status.\n",
    ":white_small_square: " + PREFIX[0] + "status cancel - Cancels Maon's looping status updates.\n",
    "\n"
]

COMMANDLIST_EMBED_BASIC_PREP = [
    ":beginner: ***Basic Commands:***\n",
    ":white_small_square: " + PREFIX[0] + "ping - Maon's latency.\n",
    ":white_small_square: " + PREFIX[0] + "<question> - Maon will reply to a closed (is, are, do, can...) question.\n",
    ":white_small_square: " + PREFIX[0] + "toss - Coin toss.\n",
    ":white_small_square: " + PREFIX[0] + "roll <number> - Roll a number from 1 to number.\n",
    ":white_small_square: " + PREFIX[0] + "anime <search term> - Posts an anime title link closest to the search term.\n",
    ":white_small_square: " + PREFIX[0] + "manga <search term> - Posts a manga title link closest to the search term.\n",
    "\n"
]

COMMANDLIST_EMBED_MUSIC_PREP = [
    ":notes: ***Music Commands:***\n",
    ":white_small_square: " + PREFIX[0] + "browse <music / sfx> - Opens the file browser.\n",
    ":white_small_square: " + PREFIX[0] + "play <link / filepath / filename> - Plays a Youtube video or local file.\n",
    ":white_small_square: " + PREFIX[0] + "sfx <filepath / filename> - Plays a local sound effect.\n",
    ":white_small_square: " + PREFIX[0] + "playlist - Displays the current playlist.\n",
    ":white_small_square: " + PREFIX[0] + "playlist <1 - 20> - Puts an entry to the front.\n",
    ":white_small_square: " + PREFIX[0] + "playlist remove - Clears the playlist.\n",
    ":white_small_square: " + PREFIX[0] + "playlist remove <1 - 20> - Removes a song from the playlist.\n",
    ":white_small_square: " + PREFIX[0] + "playlist copy <1 - 20> - Copies a track and inserts it at the beginning.\n",
    ":white_small_square: " + PREFIX[0] + "stop - Turns off the music player and makes Maon leave.\n",
    ":white_small_square: " + PREFIX[0] + "skip - Skips the current song.\n",
    ":white_small_square: " + PREFIX[0] + "loop <song / playlist / off> - Loops the current song or playlist.\n",
    ":white_small_square: " + PREFIX[0] + "shuffle <off> - Shuffles the current playlist after every song.\n",
    ":white_small_square: " + PREFIX[0] + "volume <0 - 100> - Changes the music player volume.\n",
    ":white_small_square: " + PREFIX[0] + "pause - Pauses the music player.\n",
    ":white_small_square: " + PREFIX[0] + "resume - Resumes the music player.\n",
    "\n"
]
