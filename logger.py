import discord
from datetime import datetime
from time import time
from time import monotonic

def log_messages(message):
    log = "({}) (gid: {}) {}#{}: {}".format(
        datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S"),
        message.guild.id,
        message.author.name,
        message.author.discriminator,
        message.content)
    print(log)
    with open("log.txt", "a+") as log_file:
        print(log, file = log_file)

def log_info(text: str):
    log = "[INFO] ({}) {}".format(datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S"), text)
    print (log)
    with open("log.txt", "a+") as log_file:
        print(log, file = log_file)

def log_error(text: str):
    log = "[ERROR] ({}) {}".format(datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S"), text)
    print(log)
    with open("log.txt", "a+") as log_file:
        print(log, file = log_file)
