import os
import atexit
import asyncio
import datetime
from io import TextIOWrapper


__all__ = [ 'getLogger', 'removeLogger', 'CColors' ]

_instance: 'Minfo' = None


class CColors:
    C_DEBUG = '\033[96m'    # cyan
    C_INFO = '\033[94m'     # blue
    C_WARN = '\033[93m'     # yellow
    C_ERROR = '\033[91m'    # red
    END_COLOR = '\033[0m'   # stop coloring


class Minfo():
    def __init__(self, file_dir: str = "./logs/"):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.file_dir: str = file_dir
        self.file_name: str = ""
        self.f: TextIOWrapper = None
        self.dispatchers: list['Minstance'] = []
        self.log_q: asyncio.Queue = asyncio.Queue()
        self.logging_task: asyncio.Task = self.loop.create_task(self.logging_loop(), name="logging_task")
        

    async def logging_loop(self):
        try:    
            while True:
                message = await self.log_q.get()
                if f"minfo-{datetime.date.today().strftime('%y%m%d')}.log" != self.file_name:
                    if self.f:
                        self.f.close()
                    self.file_name = f"minfo-{datetime.date.today().strftime('%y%m%d')}.log"
                    self.f = open(self.file_dir + self.file_name, 'a+')

                if len(message.get("term_text")) > 0:
                    print(message.get("term_text"))
                try:
                    self.f.write(f"{message.get('file_text')}\n")
                    self.f.flush()
                except ValueError:
                    pass

        except asyncio.CancelledError:
            pass

        finally:
            for disp in self.dispatchers:
                del disp


class Minstance():
    def __init__(self, name: str, level: int = 1):
        global _instance
        self._master: 'Minfo' = _instance
        self._name: str = name
        self._level: int = level

    
    def raw(self, text: str = None, term: bool = True):
        message = {"term_text": f"{text}", "file_text": f"{text}"} if term else {"term_text": "", "file_text": f"{text}"}
        asyncio.ensure_future(self._master.log_q.put(message))


    def debug(self, text: str = None):
        if self._level <= 0:
            message = {
                "term_text": f'{CColors.C_DEBUG}D|{datetime.datetime.now().strftime("%X")}|{self._name}:{CColors.END_COLOR} {text}',
                "file_text": f'D|{datetime.datetime.now().strftime("%X")}|{self._name}: {text}'
            }
            asyncio.ensure_future(self._master.log_q.put(message))


    def info(self, text: str = None):
        if self._level <= 1:
            message = {
                "term_text": f'{CColors.C_INFO}I|{datetime.datetime.now().strftime("%X")}|{self._name}:{CColors.END_COLOR} {text}',
                "file_text": f'I|{datetime.datetime.now().strftime("%X")}|{self._name}: {text}'
            }
            asyncio.ensure_future(self._master.log_q.put(message))


    def warn(self, text: str = None):
        if self._level <= 2:
            message = {
                "term_text": f'{CColors.C_WARN}W|{datetime.datetime.now().strftime("%X")}|{self._name}:{CColors.END_COLOR} {text}',
                "file_text": f'W|{datetime.datetime.now().strftime("%X")}|{self._name}: {text}'
            }
            asyncio.ensure_future(self._master.log_q.put(message))


    def error(self, text: str = None):
        if self._level <= 3:
            message = {
                "term_text": f'{CColors.C_ERROR}E|{datetime.datetime.now().strftime("%X")}|{self._name}:{CColors.END_COLOR} {text}',
                "file_text": f'E|{datetime.datetime.now().strftime("%X")}|{self._name}: {text}'
            }
            asyncio.ensure_future(self._master.log_q.put(message))


def getLogger(name: str, level: int = 1, file_dir: str = "./logs/"):
    """Get a logging object.\n
    Level determines what will be written to file and / or console.\n
    0 logs from DEBUG to ERR, 1 logs INFO - ERR, 2 logs WARN - ERR, 3 logs ERR only.\n
    Set the logs directory with `file_dir`. It should be set with the first getLogger call,
    subsequent file_dir changes will be ignored for now."""
    global _instance
    if _instance is None:
        if not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        _instance = Minfo(file_dir)

    logger = Minstance(name, level)
    _instance.dispatchers.append(logger)
    return logger


def removeLogger(minstance: Minstance):
    global _instance
    if _instance:
        try:
            _instance.dispatchers.remove(minstance)
        except ValueError:
            pass
