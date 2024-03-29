# Maon Discord Bot

[![Issues][issues-shield]][issues-url]
[![Issues-Closed][issues-closed-shield]][issues-closed-url]

Maon is a hobby project, a highly personalized discord bot, and a project to get to know the Git workflow.
Maon is written in **Python3.9+** and tested on **Ubuntu 22.04 Server / WSL Ubuntu 22**, but should run on most UNIX platforms, if you can install the required libraries below. 

## Table of Contents:

- [List of Commands](#list-of-commands)
    - [Owner Commands](#--owner)
    - [Moderators](#--moderators)
    - [Music](#--music)
    - [Misc](#--misc)
- [Installation](#installation)
    - [Discord Tokens & IDs](#discord-tokens--ids)
    - [Linux](#linux)
- [Troubleshooting](#troubleshooting)

## List of Commands

The commands require Maon's prefix (`m ` or `maon `) and some are also available as "slash" commands.

For example `maon play despacito` or `/play despacito`.

### 🇰🇵 Owner

Requires ownership of Maon.

```
shutdown, kill
        Shuts down Maon.

restart
        Restarts Maon with the same arguments.

reload <extension / all>
        Reloads one or all of Maon's extensions like "audio".
```

### 🏳️‍🌈 Moderators

Requires `Manage Messages` and `Read Message History` permissions.

```
/delete <1 - 75>
remove, clear, delete <1 - 75>
        Deletes a number of messages from the channel.
        Requires manage_messages permissions for both the
        requestee and Maon.

```

### 🎶 Music

Requires `Connect` and `Speak` permissions.

```
/play <link / path>
p, play, yt, stream <link / path>
        Maon will join and play a Youtube link or a local file
        from the music or sfx folder.
        If Maon is already in the voice channel, or has
        recognized the bot channel after having been summoned
        more than 2 times, the command is no longer necessary.
        A youtube link or file path alone will suffice to play
        it.
        This also resumes a paused audio player.

s, sfx, sound, effect <path>
        Maon will join and play a sound effect from the sfx 
        folder. If Maon is already in the voice channel, or has
        recognized the bot channel after having been summoned
        more than 3 times, the command is no longer necessary.
        The name of the sound effect alone will suffice to play
        it.

/join
j, join
        Maon will join the voice channel.

/stop
stop, exit, quit, leave
        Maon will stop playing audio and leave the voice
        channel.

/volume <0 - 100>
v, vol, volume <0 - 100>
        Changes the audio player's volume, 0 pauses it.
        Unpause with an empty play command.

/skip
n, next, nxt, skip
        Skips to the next song in the audio player's queue or
        just skips over the current song.

/loop <playlist / song / off>
l, loop, repeat <playlist / song / off>
        Loops the playlist, a song or turns looping off.

/playlist
q, queue, playlist
        Shows the current playlist in the audio player.

/pause
pause, halt
        Pause Maon's audio player. Continue with an empty play
        command.
```

### 🔰 Misc

```
/help
h, help, info, infocard
        Maon will paste several embeds containing her commands,
        which depend on the requestee's permissions.

/ping
ping, latency
        Maon will reply with a message containing the websocket
        latency.

/coin
coin, flip, toss
        Flips a coin! Heads or tails.

/anime <search term>
/manga <search term>
mal, anime, animu, manga, mango, myanimelist <search term>
        Will search for an anime or manga on MyAnimeList and
        replies with the top-most result.

/roll <ndn / number>
r, roll, rng, dice <ndn / number>
        Maon will roll some dices. Examples:
        "maon r 1d6" will roll a 6-sided die once.
        "maon r 999" will roll for a number between 0 and 999.

<closed question>, eightball
        Maon will reply to a closed question. Example:
        "Maon do you like pineapple pizza?" - "Yah."
```

### ⌨️ Console

```
help, info, usage, unrecognized input
        Prints the available console commands to the console.

q, quit, exit, kill, shutdown
        Shuts down Maon.

restart
        Restarts Maon with the same arguments.

reload <extension / all>
        Reloads one or all of Maon's extensions like "audio".

save <custom / settings>
        Saves the current customizations or settings to their
        respective files in the configs folder.

status <cancel / restart>
        Cancels the hourly status change loop or restarts it.

status <listening / playing / watching> <text>
        Sets a custom status message.
```

## Installation:

### Discord Tokens & IDs:

Maon needs a **discord API token**, your **discord ID**, and some **intents** enabled.

### Linux:

Required packages for maon to function are `python3-pip`, `ffmpeg` and `opus-tools`. These can be installed with:

    sudo apt-get install python3-pip ffmpeg opus-tools -y

Next give the run script executable permissions and run it like

        chmod +x run
        ./run

The script will install some python dependencies, then Maon will ask for the **discord API token** and your **discord ID**.

Additional run arguments are `./run noupdate` to skip the update check, and `./run setup` to re-setup the **discord API token** and **discord ID**.

## Troubleshooting:

- ClientException when trying to play audio.

ffmpeg needs to be in the system path, because the audio_player creates a subprocess with ffmpeg to stream audio.


[issues-shield]: https://img.shields.io/github/issues-raw/raesoft/Maon.py?color=F8D386&style=flat-square
[issues-url]: https://github.com/raesoft/Maon.py/issues
[issues-closed-shield]: https://img.shields.io/github/issues-closed-raw/raesoft/Maon.py?color=AAF786&style=flat-square
[issues-closed-url]: https://github.com/raesoft/Maon.py/issues?q=is%3Aissue+is%3Aclosed
[discord-developer-url]: https://discord.com/developers/applications
