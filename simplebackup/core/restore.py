"""
code to restore a backup
"""
import os
import shutil
import tarfile
from pathlib import Path

from ..core.logging import logger
from .const import USE_DRIVE_LETTERS
from .exceptions import UnknownBackupType


def restore_folder(backup_path: Path):
    if USE_DRIVE_LETTERS:
        #TODO windows restore folder
        pass
    else:
        #TODO linux/unix restore folder
        pass

def restore_tar(backup_path: Path):
    if USE_DRIVE_LETTERS:
        #TODO windows restore tar
        pass
    else:
        with tarfile.open(backup_path) as tar_obj:
            tar_obj.extractall(path="/")

def restore_any(backup_path: Path):
    """
    will try to restore any known formats,
    calling the correct restore function

        :param backup_path: the path to the backup
    """
    if backup_path.is_dir():
        # backup is folder type
        restore_folder(backup_path)
    elif backup_path.name.endswith(".tar"):
        # backup is tar type
        restore_tar(backup_path)
    else:
        raise UnknownBackupType(f"Cannot restore unknown backup file: {backup_path.name}")
