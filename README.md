# Maon Discord Bot
Maon Discord Bot was written in Python3 and tested on both Ubuntu 18.04
and Raspian stretch 9.8.
Maon should run on most UNIX platforms if you can install all the libraries
listed below.

# Manual Installation Instructions:
Before doing anything:

	sudo apt-get update
	sudo apt-get upgrade

Install pip:

	sudo apt install python3-pip

Install discord:

	python3 -m pip install -U discord.py

Install mp3_tagger:

	python3 -m pip install mp3_tagger

Install youtube-dl:

	python3 -m pip install --upgrade youtube-dl

Install PyNaCl:

	python3 -m pip install pynacl
	
Install FFmpeg and Opus audio library:

	sudo apt-get install ffmpeg
	sudo apt-get install libopus0 opus-tools
