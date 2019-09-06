# Maon Discord Bot
Maon Discord Bot is written in Python3 and tested on both Ubuntu 18.04 and Raspian stretch 9.8.
Maon should run on most UNIX platforms if you can install all the libraries listed below.

# Manual Installation Instructions:
Before doing anything:

	sudo apt-get update
	sudo apt-get upgrade

Install pip:

	sudo apt-get install python3-pip

Install discord API wrapper:

	python3 -m pip install discord.py

Install tinytag:

	python3 -m pip install tinytag

Install youtube-dl:

	python3 -m pip install youtube-dl

Install lxml for python3:

	sudo apt-get install python3-lxml

Install PyNaCl:

	python3 -m pip install pynacl

Install FFmpeg and Opus audio library:

	sudo apt-get install ffmpeg
	sudo apt-get install libopus0 opus-tools
