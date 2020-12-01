"""
Used for handling the configuration of the app
"""

import json
from pathlib import Path

DEFAULT_CONF = {
    "backup-path": None,
    "included-folders": [],
    "versions-to-keep": 2
}


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
        self.__config = DEFAULT_CONF
        self.__write()

    def set_included_folders(self, *locations):
        self.__config["included-folders"] = [str(i) for i in locations]
        self.__write()

    def set_backup_path(self, new_path: Path):
        self.__config["backup-path"] = str(new_path)
        self.__write()

    def set_versions_to_keep(self, new_val: int):
        self.__config["versions-to-keep"] = new_val
        self.__write()

    def get_included_folders(self) -> list:
        return [Path(i) for i in self.__config["included-folders"]]

    def get_backup_path(self) -> Path:
        if self.__config["backup-path"]:
            return Path(self.__config["backup-path"])
        return None

    def get_versions_to_keep(self) -> int:
        return self.__config["versions-to-keep"]
