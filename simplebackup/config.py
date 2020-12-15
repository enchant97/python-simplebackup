"""
Used for handling the configuration of the app
"""

import json
from datetime import datetime
from pathlib import Path

from .const import (BASE_CONF, BASE_CONF_FILE, HUMAN_READABLE_TIMESTAMP,
                    UTC_TIMESTAMP)


class Config_Handler:
    """
    Stores the configation for the app

        :param fn: the filename for the json config file
    """
    def __init__(self, fn: str):
        self.__fn = fn
        self.__config = None
        self.__load()

    def __load(self):
        """
        loads the config from file
        """
        try:
            with open(self.__fn, "rt") as fo:
                self.__config = json.load(fo)
        except FileNotFoundError:
            self.reset_config()

    def __write(self):
        """
        writes the config to file
        """
        with open(self.__fn, "wt") as fo:
            json.dump(self.__config, fo)

    def reset_config(self):
        """
        resets the config file,
        or initialise a new file
        """
        self.__config = dict(BASE_CONF_FILE)
        self.__write()

    def create_config(self, name: str):
        """
        adds a new config at the end of the configs list

            :param name: the name of the config
        """
        config = dict(BASE_CONF)
        config["name"] = name
        self.__config["configs"].append(config)
        self.__write()

    def get_config_names(self) -> tuple:
        """
        will return all the config names,
        with the specific index they are
        """
        names = []
        for i in range(len(self.__config["configs"])):
            names.append(self.__config["configs"][i]["name"])
        return tuple(names)

    def get_config_name(self, config_i: int) -> str:
        """
        returns the config name for the specific index given

            :param config_i: the config index
        """
        return self.__config["configs"][config_i]["name"]

    def rename_config(self, config_i: int, new_name: str):
        """
        rename an existing backup config

        :param config_i: the config index
        :param new_name: the new config name
        """
        self.__config["configs"][config_i]["name"] = new_name
        self.__write()

    def remove_config(self, config_i: int):
        """
        removes a specific backup config,
        will create a default if deleting the last config

            :param config_i: the config index
        """
        if config_i == self.default_config_i:
            # if the config to delete is the current change current index to 0
            self.default_config_i = 0
        del self.__config["configs"][config_i]
        if len(self.__config["configs"]) == 0:
            # create a default config if none exists now
            self.create_config("default")
        self.__write()

    @property
    def default_config_i(self) -> int:
        return self.__config["default-conf-i"]

    @default_config_i.setter
    def default_config_i(self, new_val: int):
        # make sure new_val is a int
        new_val = int(new_val)
        if new_val >= 0 and new_val < len(self.__config["configs"]):
            # make sure the index is valid
            self.__config["default-conf-i"] = new_val
            self.__write()
        else:
            raise ValueError("Invalid config index")

    def set_included_folders(self, config_i: int, locations: list):
        self.__config["configs"][config_i]["included-folders"] = [str(i) for i in locations]
        self.__write()

    def set_excluded_folders(self, config_i: int, locations: list):
        self.__config["configs"][config_i]["excluded-folders"] = [str(i) for i in locations]
        self.__write()

    def set_backup_path(self, config_i: int, new_path: Path):
        self.__config["configs"][config_i]["backup-path"] = str(new_path)
        self.__write()

    def set_versions_to_keep(self, config_i: int, new_val: int):
        self.__config["configs"][config_i]["versions-to-keep"] = int(new_val)
        self.__write()

    def set_use_tar(self, config_i: int, new_val: bool):
        self.__config["configs"][config_i]["use-tar"] = bool(new_val)
        self.__write()

    def set_last_backup(self, config_i: int, new_val: datetime):
        if isinstance(new_val, datetime):
            self.__config["configs"][config_i]["last-backup"] = new_val.strftime(UTC_TIMESTAMP)
        else:
            self.__config["configs"][config_i]["last-backup"] = None
        self.__write()

    def get_included_folders(self, config_i: int) -> list:
        return [Path(i) for i in self.__config["configs"][config_i]["included-folders"]]

    def get_excluded_folders(self, config_i: int) -> list:
        return [Path(i) for i in self.__config["configs"][config_i]["excluded-folders"]]

    def get_backup_path(self, config_i: int) -> Path:
        if self.__config["configs"][config_i]["backup-path"]:
            return Path(self.__config["configs"][config_i]["backup-path"])
        return None

    def get_versions_to_keep(self, config_i: int) -> int:
        return self.__config["configs"][config_i]["versions-to-keep"]

    def get_use_tar(self, config_i: int) -> bool:
        return self.__config["configs"][config_i]["use-tar"]

    def get_last_backup(self, config_i: int) -> datetime:
        last_backup = self.__config["configs"][config_i]["last-backup"]
        if not last_backup:
            return None
        return datetime.strptime(last_backup, UTC_TIMESTAMP)

    def get_human_last_backup(self, config_i: int) -> str:
        last_backup = self.__config["configs"][config_i]["last-backup"]
        if not last_backup:
            return "never"
        return datetime.strptime(
            last_backup, UTC_TIMESTAMP
            ).strftime(HUMAN_READABLE_TIMESTAMP)
