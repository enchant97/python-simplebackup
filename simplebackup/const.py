from pathlib import Path

BACKUP_DATESTAMP_UTC = "BACKUP %Y-%m-%dT%H.%M.%SZ"
BACKUP_DATESTAMP_UTC_REG = r"^BACKUP ([0-9]{4})(-)?(1[0-2]|0[1-9])(?(2)-)(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[01]?[0-9]).?([0-5]?[0-9]).?([0-5]?[0-9])Z"
APP_CONFIG_PATH = Path(__file__).parent.absolute() / "app_config.json"
