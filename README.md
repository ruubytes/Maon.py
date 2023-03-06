# Maon Discord Bot

[![Issues][issues-shield]][issues-url]
[![Issues-Closed][issues-closed-shield]][issues-closed-url]

Maon is a hobby project, a highly personalized discord bot, and a project to get to know the Git workflow.
Maon is written in **Python3.9+** and tested on **Ubuntu 22.04 Server / WSL Ubuntu 22**, but should run on most UNIX platforms, 
if you can install the required libraries below. 

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

### 🇰🇵 Owner

```
tba
```

### 🏳️‍🌈 Moderators

```
tba
```

### 🎶 Music

```
tba
```

### 🔰 Misc

```
tba
```

### ⌨️ Console

```
tba
```

## Installation:

### Discord Tokens & IDs:

Maon needs a **discord API token**, your **discord ID**, and some **intents** enabled.

### Linux:

Required packages for maon to function are `python3-pip`, `ffmpeg` and `opus-tools`. These can be installed with:

    sudo apt-get install python3-pip ffmpeg opus-tools -y

Next, simply execute the `run` script in the main directory of Maon and let it install the required python dependencies.
Afterwards, Maon will ask for the **discord API token** and your **discord ID**.

Additional run arguments are `./run noupdate` to skip the update check, and `./run setup` to re-setup the **discord API token** and **discord ID**.

My preferred way to run Maon is with a terminal multiplexer like tmux:

    tmux new -d -s "maon" /home/user/Maon.py/run

## Troubleshooting:

- ClientException when trying to play audio.

ffmpeg needs to be in the system path, because the audio_player creates a subprocess with ffmpeg to stream audio.


[issues-shield]: https://img.shields.io/github/issues-raw/raesoft/Maon.py?color=F8D386&style=flat-square
[issues-url]: https://github.com/raesoft/Maon.py/issues
[issues-closed-shield]: https://img.shields.io/github/issues-closed-raw/raesoft/Maon.py?color=AAF786&style=flat-square
[issues-closed-url]: https://github.com/raesoft/Maon.py/issues?q=is%3Aissue+is%3Aclosed
[discord-developer-url]: https://discord.com/developers/applications
