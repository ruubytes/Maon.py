# Maon Discord Bot
Maon Discord Bot is written in Python3 and tested on both Ubuntu 18.04 and Raspian stretch 9.8.
Maon should run on most UNIX platforms if you can install all the libraries listed below.

# Manual installation of required libraries:
Before doing anything:

	sudo apt-get update
	sudo apt-get upgrade

Install pip, lxml, ffmpeg and opus:

	sudo apt-get install python3-pip python3-lxml ffmpeg libopus0 opus-tools

Install discord API wrapper, tinytag, youtube-dl and PyNaCl:

	python3 -m pip install discord.py tinytag youtube-dl pynacl

# Running it:
If the requirements are met and the login.py has all the required tokens and IDs,
start the bot by using

	python3 maon.py
