"""
functions related to modifying backup tar files
"""
import tarfile
from datetime import datetime
from pathlib import Path

from ..core.const import BACKUP_DATESTAMP_UTC
from ..core.logging import logger


def copy_tar_files(file_paths, backup_root: Path, callback_progress=None):
    """
    adds files into a tar backup file, is not threaded

        :param file_paths: paths to copy
        :param backup_root: folder to place the backup
        :param callback_progress: called when file has finised copying
    """
    logger.debug("Starting tar copy")
    backup_fn = backup_root / datetime.utcnow().strftime(BACKUP_DATESTAMP_UTC + ".tar")
    logger.debug("Generated tar backup filename: \"%s\"", backup_fn)
    with tarfile.open(backup_fn, "w") as backup_tar:
        logger.debug("Opened tarfile")
        for file_path in file_paths:
            logger.debug("Starting tar file copy: \"%s\"", file_path)
            # the root
            to_path = Path()
            # add drive letter to backup folder
            if file_path.drive.find(":"):
                # if drive has a letter add it to the backup folder
                to_path = to_path / file_path.drive.replace(":", "")
                logger.debug("Generated drive letter as folder: \"%s\"", to_path)

            # if the path has further folders
            file_parts = file_path.parts
            if len(file_parts) > 3:
                to_path = to_path.joinpath(*file_parts[1:-1])
            elif len(file_parts) == 3:
                to_path = to_path / file_parts[-2]
            to_path = to_path / file_parts[-1]
            backup_tar.add(file_path, arcname=to_path)
            logger.debug("Finish tar file copy: \"%s\"", file_path)

            if callback_progress:
                # call progress callback to say file has been copied
                callback_progress()
    logger.debug("Finished tar copy")
