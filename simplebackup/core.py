import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path

from .const import BACKUP_DATESTAMP_UTC, BACKUP_DATESTAMP_UTC_REG


def search_included(paths_to_scan: tuple, callback_progress=None):
    """
    walks the paths to scan using yield for each path

        :param paths_to_scan: tuple of Path obj of the
                              folder paths to walk
        :param callback_progress: func to call when a
                                  file has been found,
                                  callback must accept one argument
                                  for whether it has finished search
        :return: yields each new filepath found as Path obj
    """
    for top in paths_to_scan:
        for root, _dirs, files in os.walk(top):
            if files:
                for file in files:
                    if callback_progress:
                        # call progress callback to say file has been found
                        callback_progress()
                    yield Path(root).joinpath(file)
    if callback_progress:
        callback_progress(True)

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
    # if the path has further folders
    file_parts = file_path.parts
    if len(file_parts) > 3:
        for i in range(1, len(file_parts) -1):
            to_path = to_path / file_parts[i]
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
    if backup_folder.drive.find(":"):
        # if drive has a letter add it to the backup folder
        backup_folder = backup_folder / backup_folder.drive.replace(":", "")

    with ThreadPoolExecutor(thread_name_prefix="copythread") as tpe:
        tpe.map(
            partial(copy_file, backup_root=backup_folder, callback_progress=callback_progress),
            file_paths
            )

def find_prev_backups(root_backup_path: Path, name_re=BACKUP_DATESTAMP_UTC_REG):
    """
    finds all backup folders in a backup folder

        :param root_backup_path: the root backup folder
                                 where all backups
                                 are contained
        :param name_re: the regular expression to
                        match a backup to
        :return: each path that is a valid backup
    """
    for path in root_backup_path.iterdir():
        if path.is_dir():
            if re.fullmatch(name_re, path.name):
                yield path

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
