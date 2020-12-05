"""
functions related to modifying backup tar files
"""
import tarfile
from datetime import datetime
from pathlib import Path

from ..const import BACKUP_DATESTAMP_UTC


def copy_tar_files(file_paths, backup_root: Path, callback_progress=None):
    backup_fn = backup_root / datetime.utcnow().strftime(BACKUP_DATESTAMP_UTC + ".tar")
    with tarfile.open(backup_fn, "w") as backup_tar:
        for file_path in file_paths:
            backup_tar.add(file_path)
            if callback_progress:
                # call progress callback to say file has been copied
                callback_progress()
