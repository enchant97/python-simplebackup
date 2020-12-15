from pathlib import Path

HUMAN_READABLE_TIMESTAMP = "%Y-%m-%d %H.%M.%S"
UTC_TIMESTAMP = "%Y-%m-%dT%H.%M.%SZ"
BACKUP_DATESTAMP_UTC = f"BACKUP {UTC_TIMESTAMP}"
BACKUP_DATESTAMP_UTC_REG = r"^BACKUP ([0-9]{4})(-)?(1[0-2]|0[1-9])(?(2)-)(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[01]?[0-9]).?([0-5]?[0-9]).?([0-5]?[0-9])Z"
APP_CONFIG_PATH = Path(__file__).parent.absolute() / "app_config.json"
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
    "configs": [BASE_CONF]
}
