import asyncio
import json
import logbook
from defaults import DEFAULT_CUSTOMIZATION
from defaults import DEFAULT_SETTINGS
from discord import __version__
from discord import Intents
from discord.ext.commands import Bot
from logging import Logger
from os import environ
from os import mkdir
from os.path import exists

from aiohttp.client_exceptions import ClientConnectorError
from discord import ConnectionClosed
from discord import LoginFailure
from discord import HTTPException

logbook.getLogger("discord")
log: Logger = logbook.getLogger("maon")
__maon_version__ = "23.2.22"


class Maon(Bot):
    def __init__(self) -> None:
        log.info(f"Maon v{__maon_version__}")
        log.info(f"Discord.py v{__version__}")
        log.info("Starting Maon...")
        self.extensions_list: list[str] = ["admin", "audio", "console", "error_manager", "misc"]
        self.custom: dict[str, str | list[str]] = self._load_customization()
        self.settings: dict[str, str | int | float] = self._load_settings()
        super().__init__(
            command_prefix=self._set_prefix(),
            help_command=None, 
            intents=self._set_intents(), 
            options=self._set_options()
        )

    
    async def setup_hook(self) -> None:
        for ext in self.extensions_list:
            log.info(f"Loading {ext} extension...")
            await self.load_extension(f"{ext}")
        log.info("Synchronizing application (slash) commands to discord...")
        await self.tree.sync()


    async def _get_prefix(self) -> str:
        """Returns a single prefix string. \n
        The discord.py built-in `get_prefix(ctx)` returns all the prefixes instead."""
        prefix: str | list[str] | None = self.custom.get("prefix")
        if prefix and isinstance(prefix, list):
            return prefix[0]
        elif prefix and isinstance(prefix, str):
            return prefix
        else:
            return "m "


    def _load_customization(self) -> dict[str, str | list[str]]:
        log.info("Loading customizations...")
        if not exists(f"./configs/"):
            mkdir("./configs/")
        # Check if custom file exists
        custom: dict[str, str | list[str]] = {}
        if exists(f"./configs/custom.json"):
            # Check if custom file is actually valid json
            try:
                with open("./configs/custom.json", "r") as cjson:
                    # If yes, load from file 
                    custom = json.load(cjson)
                # Add new defaults if missing
                changed: bool = False
                for k, v in DEFAULT_CUSTOMIZATION.items():
                    if k not in custom:
                        custom[k] = v
                        changed = True
                if changed:
                    with open("./configs/custom.json", "w") as cjson:
                        json.dump(custom, cjson, sort_keys=True, indent=4)
                return custom
            except json.JSONDecodeError:    
                pass    # File is corrupted, overwrite it with the defaults
        # If no or corrupted, create a new one with the default settings and save it
        with open("./configs/custom.json", "w") as cjson:
            json.dump(DEFAULT_CUSTOMIZATION, cjson, sort_keys=True, indent=4)
            return DEFAULT_CUSTOMIZATION


    async def reload_customization(self) -> None:
        if not exists(f"./configs/custom.json"):
            return log.error("My custom.json file got deleted.")
        custom: dict[str, str | list[str]] = {}
        try:
            with open("./configs/custom.json", "r") as cjson:
                custom = json.load(cjson)
            # Add new defaults if missing
            changed: bool = False
            for k, v in DEFAULT_CUSTOMIZATION.items():
                if k not in custom:
                    custom[k] = v
                    changed = True
            if changed:
                with open("./configs/custom.json", "w") as cjson:
                    json.dump(custom, cjson, sort_keys=True, indent=4)
            self.custom = custom
            log.info("Customizations reloaded.")
        except json.JSONDecodeError:    
            log.error("My custom.json file is corrupted.")


    async def save_customization(self) -> None:
        with open("./configs/custom.json", "w") as cjson:
            json.dump(self.custom, cjson, sort_keys=True, indent=4)
            log.info("Customizations saved.")


    def _load_settings(self) -> dict[str, str | int | float]:
        log.info("Loading settings...")
        if not exists(f"./configs/"):
            mkdir("./configs/")
        # Check if settings file exists
        settings: dict[str, str | int | float] = {}
        if exists(f"./configs/settings.json"):
            # Check if settings file is actually valid json
            try:
                with open("./configs/settings.json", "r") as cjson:
                    # If yes, load from file 
                    settings = json.load(cjson)
                # Add new defaults if missing
                changed: bool = False
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in settings:
                        settings[k] = v
                        changed = True
                if changed:
                    with open("./configs/settings.json", "w") as cjson:
                        json.dump(settings, cjson, sort_keys=True, ident=4)
                return settings
            except json.JSONDecodeError:    
                pass    # File is corrupted, overwrite it with the defaults
        # If no or corrupted, create a new one with the default settings and save it
        with open("./configs/settings.json", "w") as cjson:
            json.dump(DEFAULT_SETTINGS, cjson, sort_keys=True, indent=4)
            return DEFAULT_SETTINGS


    async def reload_settings(self) -> None:
        if not exists(f"./configs/settings.json"):
            return log.error("My settings.json file got deleted.")
        settings: dict[str, str | int | float] = {}
        try:
            with open("./configs/settings.json", "r") as cjson:
                settings = json.load(cjson)
            # Add new defaults if missing
            changed: bool = False
            for k, v in DEFAULT_SETTINGS.items():
                if k not in settings:
                    settings[k] = v
                    changed = True
            if changed:
                with open("./configs/settings.json", "w") as cjson:
                    json.dump(settings, cjson, sort_keys=True, indent=4)
            self.settings = settings
            log.info("Settings reloaded.")
        except json.JSONDecodeError:    
            log.error("My settings.json file is corrupted.")


    async def save_settings(self) -> None:
        with open(f"./configs/settings.json", "w") as cjson:
            json.dump(self.settings, cjson, sort_keys=True, indent=4)
            log.info("Settings saved.")


    def _set_prefix(self) -> str | list[str]:
        log.info("Setting prefix...")
        prefix: str | list[str] | None = self.custom.get("prefix")
        if isinstance(prefix, str) and prefix:
            return prefix
        elif isinstance(prefix, list) and prefix and not (len(prefix) == 1 and prefix[0]):
            return prefix
        else:
            log.warning("My command prefixes are missing, please set them in the custom.json file. Using 'm ' as prefix in the meantime.")
            return "m "


    def _set_intents(self) -> Intents:
        log.info("Setting intents...")
        intents = Intents.none()
        intents.dm_messages = True
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_reactions = True
        intents.members = True
        intents.message_content = True
        intents.voice_states = True
        return intents

    
    def _set_options(self) -> dict[str, int | bool]:
        log.info("Setting options...")
        options: dict[str, int | bool] = {}
        try:
            options["owner_id"] = self._env_get_owner_id()
        except (TypeError, ValueError):
            log.error(f"Your owner_id looks to be faulty. You can set it again with: \n\n    ./run setup\n")
            exit(1)
        options["case_insensitive"] = True
        return options


    def _env_get_owner_id(self) -> int:
        oid: str | None = environ.get("MAON_OWNER_ID")
        if oid is None:
            raise TypeError
        try:
            return int(oid)
        except ValueError:
            raise

    
    def _env_get_token(self) -> str:
        token: str | None = environ.get("MAON_TOKEN")
        if token is None:
            raise TypeError
        return token


if __name__ == "__main__":
    try:
        maon = Maon()
        asyncio.run(maon.start(maon._env_get_token()))
        log.log(logbook.RAW, "\nMaybe I'll take over the world some other time.\n")
    except KeyboardInterrupt:
        log.info("Shutting down...\n")
    except TypeError:
        log.error("I need a discord API token to log in. You can change it by starting me with\n\n   ./run setup\n")
        exit(1)
    except LoginFailure:
        log.error("It looks like my API token is faulty, make sure you have entered it correctly or re-paste it with:\n\n   ./run setup\n")
        exit(1)
    except (ClientConnectorError, HTTPException, ConnectionClosed):
        log.error("It looks like my connection to Discord has issues.")
        exit(1)
