# Maon Discord Bot
[![Issues][issues-shield]][issues-url]
[![Issues-Closed][issues-closed-shield]][issues-closed-url]

Maon is a little hobby project, as well as a project to get to know the Git workflow.
Maon is written in `Python3.8+` and tested on `Ubuntu 20.04+`, `Ubuntu Server 20.04`, `Windows 10`, 
and `Raspbian Buster`. Maon should run on most UNIX platforms, if you can install the required libraries 
below. The most notable functionality of Maon is its chat integrated media browser to browse media files
and play them by navigating the browser with emojis that have been added to the media browser embed message. 

# Table of Contents:
- [List of Commands](#list-of-commands)
    - [Admin](#admin)
    - [Basic](#basic)
    - [Music](#music)
- [Installation](#installation)
    - [Discord Tokens & IDs](#discord-tokens-&-ids)
    - [Ubuntu / Debian / Raspbian](#ubuntu-/-debian-/-raspbian)
    - [Windows](#windows)
- [Running Maon](#running-maon)
    - [Ubuntu / Debian / Raspbian](#ubuntu-/-debian-/-raspbian)
    - [Windows](#windows)

# List of Commands
## Admin
- `shutdown` (alias: `kill`)

Shuts down Maon gracefully.

- `restart`
    
Restarts Maon.

- `reload <extension name / all>` 

Reloads an extension module like audio or filebrowser or all of them.

- `disable <extension name / all>`

Disables an extension module or all of them.

- `enable <extension name / all>`

Enables an extension module or all of them.

- `remove <number>` (alias: `clear`, `delete`)

Remove `number` of messages.

- `status <playing / watching / listening> <text>`

Sets a status for Maon.

- `status cancel`

Disables the hourly status text cycle.

- `scrub`

Deletes the music cache folder.

- `emojiname <emoji>`

Returns the ascii encoded name of an emoji.

## Basic
- `help` (alias: `info`, `infocard`)

Lists all commands.

- `version`

Shows the current version of Maon.

- `ping`

Shows the websocket ping in milliseconds.

- `flip` (alias: `coin`, `toss`)

Flip a coin.

- `rng <number>` (alias: `dice`, `roll`)

Roll the dice for a random number from 1 to `number`.

- `rng <number> x<number>`

Roll the dice multiple times for x`number` times. Example: `m roll 20 x5` or `m roll 20*5` to roll 20 times 5.

- `eightball` (alias: `am`, `is`, `are`, `can`, `do`, `does`, `will`...)

Maon will reply to a closed question or the `eightball` command. For example: `Maon is pineapple pizza the best 
in the world?` will have Maon reply with some form of yes, no, maybe... I don't knoooow, can you repeat the question~

- `poll` (alias: `umfrage`)

Generate a quick poll. Example command:
`maon poll What's your favorite ice cream flavor? -o banana -o strawberry -o chocolate`

- `mal <search term>` (alias: `anime`, `animu`, `manga`)

Maon will look up the requested search term and return the closest anime title linking to MyAnimeList. 
The alias `manga` will look for a manga title instead.

## Music
- `play <url / path / filename>` (alias: `p`, `stream`, `yt`)

Play a local sound file from the music folder or a Youtube link in a voice channel.

- `sfx <path / filename>` (alias: `s`, `effects`, `effect`)

Play a local sound file from the sfx folder. Once Maon has joined a voice channel, the prefix and sfx 
command can be removed and sound effects can be played by writing the sound effects title only into 
the chat. Example: `m s oof` becomes `oof` for ease of- and speedy access to sound effects.

- `browse <music / sfx>` (alias: `b`, `browser`)

Opens the chat embedded file browser to browse through either the music or sfx folder. The browser 
can be navigated with emojis to change pages, enter a folder or go back, or to choose and play a song 
or sound effect.

- `volume <number between 0 and 100>` (alias: `v`, `vol`)

Changes the volume of Maon. Default volume is set in the configuration file.

- `join` (alias: `j`)

Maon joins the voice channel and generates the audioplayer.

- `skip` (alias: `next`, `n`, `ne`, `nxt`, `sk`, `skp`)

Skips the currently playing song or sound effect.

- `loop <song / playlist / queue / q / off>`

Loops the currently playing song, or the whole playlist or turns the looping function off.

- `shuffle <off>`

Shuffles the current playlist after every song.

- `pause`

Pauses the currently playing song or sound effect.

- `resume` (alias: `res`, `cont`, `continue`, `re`, `co`)

Resumes the paused song or sound effect.

- `stop` (alias: `leave`, `l`)

Stops Maon's audioplayer and makes Maon leave the voice channel.

- `playlist` (alias: `q`, `queue`)

Shows the current playlist and the entry numbers of the songs.

- `playlist <number, number, ...>` 

Puts songs in the playlist of entry number `number` to the front of the playlist.

- `playlist clear <number, number, ...>`

Removes songs from the playlist of entry number `number`. Aliases for `clear` include `delete`, `del`,
 `d`, `remove`, `rm`, `r`

- `playlist copy <number, number, ...>`

Copies songs from the playlist of entry number `number` to the front of the playlist.

# Installation:
## Discord Tokens & IDs:
Maon needs a bot token, Maon's ID and the ID of the bot owner for a successful login. The first step 
to get all of these is to create a new application on the discord developer page. 
https://discord.com/developers/applications

There select `New Application` and give Maon her name. Once created, head over to the `Bot` page and 
click `Add Bot`. From there, click `copy` underneath the token to receive your bot token and put it 
into the `login.py` file at `token = "token goes here"`.

Once Maon has a token, go back to `General Information` and copy the `Client ID` to the `login.py` 
file at `MAON_ID = id_goes_here`.

Now all that's missing is the owner token. After activating developer mode in discord under settings, 
rightclick yourself inside discord and copy the ID into the `login.py` file at `OWNER_ID = id_goes_here`.

## Ubuntu / Debian / Raspbian:
Install `pip` if it is not already installed to fetch some needed dependencies, and for audio playback 
we'll need `ffmpeg` and `opus-tools`:
    
    sudo apt install python3-pip ffmpeg opus-tools

Next the dependencies:

    python3 -m pip install -U aioconsole discord.py psutil pynacl simplejson tinytag==1.7.0 yt-dlp

## Windows:
Requires `Python 3.8+`, `pip`, and `ffmpeg` to be installed. Install instructions for
these are on their respective websites.

To install the dependencies, open a new command prompt and enter:

    python -m pip install -U aioconsole discord.py psutil pynacl simplejson tinytag==1.7.0 yt-dlp
        
# Running Maon:
## Ubuntu / Debian / Raspbian:
To run Maon you can use the following from Maon's directory:

    python3 Maon.py
    
## Windows:
Use the following in a command prompt from Maon's main directory:

    python Maon.py
	
[issues-shield]: https://img.shields.io/github/issues-raw/raesoft/Maon.py?color=F8D386&style=flat-square
[issues-url]: https://github.com/raesoft/Maon.py/issues
[issues-closed-shield]: https://img.shields.io/github/issues-closed-raw/raesoft/Maon.py?color=AAF786&style=flat-square
[issues-closed-url]: https://github.com/raesoft/Maon.py/issues?q=is%3Aissue+is%3Aclosed
