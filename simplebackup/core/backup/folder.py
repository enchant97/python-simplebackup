"""
functions related to modifying backup folders
"""

import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path

from ...core.const import BACKUP_DATESTAMP_UTC, ERROR_TYPES
from ...core.logging import logger


def copy_file(file_path: Path, backup_root: Path, callback_progress=None):
    """
    used in copy_files func to use map
    function of the ThreadPoolExecutor

        :param file_path: the path to the file to copy
        :param backup_root: folder to place the backup
        :param callback_progress: called when file has finised copying
    """
    # the root
    to_path = backup_root
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
    logger.debug("Generated to-path: \"%s\"", to_path)
    # make the directories
    to_path.mkdir(parents=True, exist_ok=True)
    # add filename to end of path
    to_path = to_path / file_parts[-1]
    # copy the file
    shutil.copy(file_path, to_path)
    logger.debug("Copied file from: \"%s\" to: \"%s\"", file_path, to_path)

    if callback_progress:
        # call progress callback to say file has been copied
        callback_progress()

def copy_files(backup_folder: Path, file_paths, callback_progress=None):
    """
    copies files to the backup folder location,
    note this will spawn threads

        :param backup_folder: the folder to place backup in
        :param file_paths: the files to copy
        :param callback_progress: func to call when a
                                  file has been copied,
                                  will be called from a thread
    """
    logger.debug("Starting files copy")
    with ThreadPoolExecutor(thread_name_prefix="copythread") as tpe:
        tpe.map(
            partial(copy_file, backup_root=backup_folder, callback_progress=callback_progress),
            file_paths
            )
    logger.debug("Finished files copy")

def create_backup_folder(root_backup_path: Path, error_callback=None):
    """
    creates the dated backup folder

        :param root_backup_path: the root backup path
        :param error_callback: the func to call when something
                               goes wrong, needs to accept
                               ERROR_TYPES as a param
        :return: the path a backup should be used for all backup files
    """
    backup_path = root_backup_path / datetime.utcnow().strftime(BACKUP_DATESTAMP_UTC)
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        logger.debug("Created backup folder: \"%s\"", backup_path)
        return backup_path
    except PermissionError:
        logger.exception(ERROR_TYPES.NO_BACKUP_WRITE_PERMISION.value)
        if error_callback:
            error_callback(ERROR_TYPES.NO_BACKUP_WRITE_PERMISION)
