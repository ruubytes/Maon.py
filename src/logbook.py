import logging
from logging.handlers import TimedRotatingFileHandler
from configs import settings


__all__ = [ "getLogger" ]


RAW = 60


class ColoredFormatter(logging.Formatter):
    C_DEBUG = '\033[96m'    # cyan
    C_INFO = '\033[94m'     # blue
    C_WARN = '\033[93m'     # yellow
    C_ERROR = '\033[91m'    # red
    END_COLOR = '\033[0m'   # stop coloring
    DATEFMT = "%H:%M:%S"
    FORMAT_HEAD = "%(levelname).1s|%(asctime)s|%(name)s: "
    FORMAT_MESSAGE = "%(message)s"
    FORMATS = {
        logging.DEBUG: f"{C_DEBUG}{FORMAT_HEAD}{END_COLOR}{FORMAT_MESSAGE}",
        logging.INFO: f"{C_INFO}{FORMAT_HEAD}{END_COLOR}{FORMAT_MESSAGE}",
        logging.WARN: f"{C_WARN}{FORMAT_HEAD}{END_COLOR}{FORMAT_MESSAGE}",
        logging.ERROR: f"{C_ERROR}{FORMAT_HEAD}{END_COLOR}{FORMAT_MESSAGE}",
        logging.CRITICAL: f"{C_ERROR}{FORMAT_HEAD}{END_COLOR}{FORMAT_MESSAGE}",
        RAW: f"{FORMAT_MESSAGE}"
    }

    def format(self, record):
        return logging.Formatter(self.FORMATS.get(record.levelno), self.DATEFMT).format(record)


def getLogger(name: str = None):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    if len(log.handlers) > 1:   # ignore if the NullHandler is in the list
        return log

    filehandler = TimedRotatingFileHandler(
        filename=f"{settings.LOGGING_DISCORD_PATH_FILE}",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(logging.Formatter(
        fmt="%(levelname).1s|%(asctime)s|%(name)s: %(message)s", 
        datefmt="%H:%M:%S"
    ))

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.INFO)
    streamhandler.setFormatter(ColoredFormatter())

    log.addHandler(filehandler)
    log.addHandler(streamhandler)

    return log


def removeLogger(name: str = None):
    return 