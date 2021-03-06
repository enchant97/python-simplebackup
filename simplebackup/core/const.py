from enum import Enum
from pathlib import Path

USER_HOME_PATH = Path.home()
SYSTEM_FILES = ("Thumbs.db", "thumbs.db", ".DS_Store")
HUMAN_READABLE_TIMESTAMP = "%Y-%m-%d %H.%M.%S"
UTC_TIMESTAMP = "%Y-%m-%dT%H.%M.%SZ"
BACKUP_DATESTAMP_UTC = f"BACKUP {UTC_TIMESTAMP}"
BACKUP_DATESTAMP_UTC_REG = r"^BACKUP ([0-9]{4})(-)?(1[0-2]|0[1-9])(?(2)-)(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[01]?[0-9]).?([0-5]?[0-9]).?([0-5]?[0-9])Z"
UPDATE_URL = "https://github.com/enchant97/python-simplebackup/releases"
# what each backup config uses as a base
BASE_CONF = {
    "name": "default",
    "backup-path": None,
    "included-folders": [],
    "excluded-folders": [],
    "versions-to-keep": 2,
    "use-tar": False,
    "last-backup": None
}
# the base for the config file that contains all the backup configs
BASE_CONF_FILE = {
    "default-conf-i": 0,
    "show-help": True,
    "configs": []
}


class ERROR_TYPES(str, Enum):
    """
    contains error types for
    use in a error_callback
    """
    NO_BACKUP_WRITE_PERMISION = "Backup location has no write permissions!"
    NO_BACKUP_READ_PERMISION = "Backup location has no read permissions!"
    NO_FILES_FOUND_TO_BACKUP = "No files were found to backup!"
    NO_BACKUP_PATH_FOUND = "Backup location does not seem to exist!"
