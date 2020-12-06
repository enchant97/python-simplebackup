"""
functions related to modifying backup folders
"""

import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path

from ..const import BACKUP_DATESTAMP_UTC
from .backup_search import find_prev_backups


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
    # if the path has further folders
    file_parts = file_path.parts
    if len(file_parts) > 3:
        to_path = to_path.joinpath(*file_parts[1:-1])
    elif len(file_parts) == 3:
        to_path = to_path / file_parts[-2]
    # make the directories
    to_path.mkdir(parents=True, exist_ok=True)
    # add filename to end of path
    to_path = to_path / file_parts[-1]
    # copy the file
    shutil.copy(file_path, to_path)

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
    with ThreadPoolExecutor(thread_name_prefix="copythread") as tpe:
        tpe.map(
            partial(copy_file, backup_root=backup_folder, callback_progress=callback_progress),
            file_paths
            )

def create_backup_folder(root_backup_path: Path, versions_to_keep=2):
    """
    creates the dated backup folder and removes
    old ones if versions have reached limit

        :param root_backup_path: the root backup path
        :param versions_to_keep: the number of backups to keep if -1 will keep all
        :return: the path a backup should be used for all backup files
    """
    prev_backups = [i for i in find_prev_backups(root_backup_path)]
    if (versions_to_keep > 0) and (len(prev_backups) >= versions_to_keep):
        prev_backups = sorted(prev_backups, reverse=True)
        difference = (len(prev_backups) - versions_to_keep) + 1
        for i in range(difference):
            shutil.rmtree(prev_backups[i - 1])

    backup_path = root_backup_path / datetime.utcnow().strftime(BACKUP_DATESTAMP_UTC)
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path
