# Maon Discord Bot
[![Issues][issues-shield]][issues-url]
[![Issues-Closed][issues-closed-shield]][issues-closed-url]

Maon is a little hobby project, as well as a project to get to know the Git workflow.
Maon is written in `Python3.6+` and tested on `Ubuntu 18.04+`, `Windows 10`, and `Raspbian Buster`.
Maon should run on most UNIX platforms, if you can install the required libraries below. The most notable
functionality of Maon is its chat integrated media browser to browse media files and play them by navigating
the browser with emojis that have been added to the media browser embed message. 

# Table of Contents:
- [Installation](#installation)
    - [Ubuntu / Debian / Raspbian](#ubuntu-/-debian-/-raspbian)
    - [Windows](#windows)
- [Running Maon](#running-maon)
    - [Ubuntu / Debian / Raspbian](#ubuntu-/-debian-/-raspbian)
    - [Windows](#windows)

# Installation:
## Ubuntu / Debian / Raspbian:
Before doing anything, the usual:
    
    sudo apt update

If you don't already have `pip` installed:
    
    sudo apt install python3-pip
    
For audio playback we'll need `ffmpeg` and `opus-tools`:

    sudo apt install ffmpeg
    sudo apt install opus-tools

Next the dependencies:

    python3 -m pip install -U psutil discord.py youtube-dl pynacl tinytag

## Windows:
Requires `Python 3.6+`, `pip`, and `ffmpeg` to be installed. Install instructions for
these are on their respective websites.

To install the dependencies, open a new command prompt and enter:

    python -m pip install -U psutil discord.py youtube-dl pynacl tinytag
        
# Running Maon:
## Ubuntu / Debian / Raspbian:
To run Maon you can use the following from Maon's directory:

    python3 Maon.py
    
## Windows:
Use the following in a command prompt from Maon's main directory:

    python Maon.py
	
[issues-shield]: https://img.shields.io/github/issues/RaeNon/Maon.py?style=flat-square
[issues-url]: https://github.com/RaeNon/Maon.py/issues
[issues-closed-shield]: https://img.shields.io/github/issues-closed/RaeNon/Maon.py?style=flat-square
[issues-closed-url]: https://github.com/RaeNon/Maon.py/issues?q=is%3Aissue+is%3Aclosed
