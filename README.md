# Maon Discord Bot

[![Issues][issues-shield]][issues-url]
[![Issues-Closed][issues-closed-shield]][issues-closed-url]

Maon is a little hobby project, a highly personalized discord bot, as well as a project to get to know the Git workflow.
Maon is written in **Python3.9+** and tested on **Ubuntu 22.04 Server / WSL**, but should run on most UNIX platforms, 
if you can install the required libraries below. 

The most notable functionalities of Maon are:
- The audio player for Youtube videos / shorts and local files as well as prefix-less sound effects.
- The chat integrated media browser to browse media files and play them by navigating the browser with emojis,
which have been added to the media browser embed message.
- Minecraft server manager for whitelisting and removing users.

## Table of Contents:

- [List of Commands](#list-of-commands)
    - [Admin](#admin)
    - [Basic](#basic)
    - [Music](#music)
    - [Servermanager](#servermanager)
- [Installation](#installation)
    - [Discord Tokens & IDs](#discord-tokens--ids)
    - [Ubuntu / Debian / Raspbian](#ubuntu--debian--raspbian)
    - [Windows](#windows)

## List of Commands

### Admin

```
disable <extension / all>
        Disables an extension module like audio or all of them.

emojiname <emoji>
        Returns the ascii encoded name of an emoji.

enable <extension / all>
        Enables an extension module like audio or all of them.

reload <extension / all>
        Reloads an extension module like audio or all of them.

remove, clear, delete <number>
        Remove <number> of messages in a chat.

restart, reset
        Restarts Maon.

scrub
        Deletes the music cache folder.

shutdown, kill
        Shuts down Maon gracefully.

status <playing / watching / listening> <text>
        Sets a status for Maon.

status cancel
        Disables the hourly status text cycle.
```

### Basic

```
eightball
am, is, are, can, do, does, will...
        Maon will reply to a closed question or the eightball command.
        Example: Maon is pineapple pizza the best in the world?
        Maon will reply with some form of yes, no, maybe... I don't knoooow.

flip, coin, toss
        Flip a coin.

help, info, infocard
        Lists all commands.

mal, anime, animu, manga <search term>
        Maon will look up the requested search term and return the closest
        anime title linking to MyAnimeList.
        The alias manga will look for a manga title instead.

ping
        Shows the websocket ping in milliseconds.

poll, umfrage <poll question> -o <choice> -o <choice> ...
        Generate a quick poll. If no choices are specified, 
        it's going to be a poll with ✔️ and ❌ as choices.
        Example: m poll Are we going to play a game this evening?
        Example: m poll Fav ice cream? -o banana -o strawberry -o chocolate

rng, dice, roll <number> x <number>
        Roll the dice for a random number from 1 to <number> or
        roll the dice multiple times from 1 to <number> times <number>
        Example: m roll 20 x5   to roll from 1 to 20 5 times.

version
        Shows the current version of Maon.
```

### Music

```
browse, browser, b <music / sfx>
        Opens the chat embedded file browser to browse through either the music
        or sfx folder.

join, j
        Maon joins the voice channel and generates the audioplayer.

loop <song / playlist / queue / q / off>
        Loops the currently playing song, or the whole playlist or turns the
        looping function off.

pause
        Pauses the currently playing song or sound effect.

play, p, stream, yt <url / path / filename>
        Play a local file from the music folder or a Youtube link.
        Once Maon has joined a voice channel, using the prefix + command is
        no longer necessary for youtube links. <url> will suffice.

playlist, queue, q
        Shows the current playlist and the entry numbers of the songs.
        Due to text message length, the command currently only displays what
        is playing and the next ~20 entries.

playlist <number, number, ...>
        Pushes playlist entry <number> to the front of the playlist.

playlist <clear / delete / remove / d / r> <number, number, ...>
        Removes playlist entry <number> from the playlist.

playlist copy <number, number, ...>
        Copies playlist entry <number> to the front of the playlist.

resume, res, re, continue, cont, co
        Resumes the paused song or sound effect.

sfx, s, effects, effect <path / filename>
        Play a local file from the sfx folder.
        If Maon is already in the voice channel, the command can be omitted and
        only the sound effect's filename can be used to invoke the effect.

shuffle <off>
        Shuffles the current playlist after every song. The off keyword turns
        the shuffling off again.

skip, skp, sk, next, nxt, ne, n
        Skips the currently playing song or sound effect.

stop, leave, l
        Stops Maon's audioplayer and makes Maon leave the voice channel.

volume, vol, v <number between 0 and 100>
        Changes the volume of Maon. Default volume is set in the config file.
```

### Servermanager

```
register, reg, whitelist <username>
        Registers a user for a minecraft server, if it's hosted alongside Maon.
        This needs a path to the whitelist and a tmux session called
        "minecraft" from which the server console is accessible.

unregister, unreg <username>
        Removes a user from the minecraft server whitelist. (Admin only)
        This needs a path to the whitelist and a tmux session called
        "minecraft" from which the server console is accessible.
```

## Installation:

### Discord Tokens & IDs:

Maon needs a **bot token**, **Maon's ID** and the **ID** of the **bot owner** for a successful login.
The first step to get all of these is to create a new application on the [discord developer page][discord-developer-url].

There select **New Application** and give Maon her name. 
Once created, head over to the **Bot** page and click **Add Bot**. 
From there, click **copy** underneath the token to receive your bot token, 
then put it into the **login.py** file at `token = "token goes here"`.

Once Maon has a token, go back to **General Information** and copy the **Client ID** to the **login.py** file at `MAON_ID = id_goes_here`.

Now all that's missing is the owner token. 
After activating **developer mode** in discord under **settings**, 
rightclick yourself inside discord and copy the **ID** into the **login.py** file at `OWNER_ID = id_goes_here`.

### Ubuntu / Debian / Raspbian:

Install **pip** if it is not already installed to fetch some needed dependencies, 
and for audio playback we'll need **ffmpeg** and **opus-tools**:
    
    sudo apt install python3-pip ffmpeg opus-tools

Next the dependencies:

    python3 -m pip install -U aioconsole discord.py psutil pynacl requests simplejson tinytag yt-dlp

To run Maon you can use the following from Maon's directory:

    python3 Maon.py

### Windows:

Requires **Python 3.9+**, **pip**, and **ffmpeg** to be installed. 
Install instructions for these are on their respective websites.

To install the dependencies, open a new command prompt and enter:

    python -m pip install -U aioconsole discord.py psutil pynacl requests simplejson tinytag yt-dlp

Use the following in a command prompt from Maon's directory:

    python Maon.py
        

[issues-shield]: https://img.shields.io/github/issues-raw/raesoft/Maon.py?color=F8D386&style=flat-square
[issues-url]: https://github.com/raesoft/Maon.py/issues
[issues-closed-shield]: https://img.shields.io/github/issues-closed-raw/raesoft/Maon.py?color=AAF786&style=flat-square
[issues-closed-url]: https://github.com/raesoft/Maon.py/issues?q=is%3Aissue+is%3Aclosed
[discord-developer-url]: https://discord.com/developers/applications
