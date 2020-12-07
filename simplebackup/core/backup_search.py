"""
functions related to finding folders
and finding files to backup
"""
import os
import re
import shutil
from pathlib import Path

from ..const import BACKUP_DATESTAMP_UTC_REG


def search_included(paths_to_scan: tuple, callback_progress=None) -> list:
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
    found_paths = []
    for top in paths_to_scan:
        for root, _dirs, files in os.walk(top):
            if files:
                for file in files:
                    found_paths.append(Path(root).joinpath(file))
                    if callback_progress:
                        # call progress callback to say file has been found
                        callback_progress()
    if callback_progress:
        callback_progress(True)
    return found_paths

def find_prev_backups(root_backup_path: Path, name_re=BACKUP_DATESTAMP_UTC_REG):
    """
    finds all backup folders in a backup folder and yields each one

        :param root_backup_path: the root backup folder
                                 where all backups
                                 are contained
        :param name_re: the regular expression to
                        match a backup to
        :return: each path that is a valid backup
    """
    for path in root_backup_path.iterdir():
        if re.match(name_re, path.name):
            yield path

def delete_prev_backups(root_backup_path: Path, versions_to_keep=2) -> int:
    """
    deletes older backups keeping the amount of versions given

        :param root_backup_path: root path of all backups
        :param versions_to_keep: versions to keep
        :return: the number of backups deleted
    """
    backups_deleted = 0
    prev_backups = [i for i in find_prev_backups(root_backup_path)]
    if (versions_to_keep >= 0) and (len(prev_backups) >= versions_to_keep):
        prev_backups = sorted(prev_backups, reverse=True)
        difference = (len(prev_backups) - versions_to_keep) + 1
        for i in range(difference):
            try:
                curr_backup_path = prev_backups[i - 1]
                if curr_backup_path.is_dir():
                    # removes folder backups
                    shutil.rmtree(curr_backup_path)
                else:
                    # removes file backups
                    os.remove(curr_backup_path)
                backups_deleted += 1
            except FileNotFoundError:
                # we don't need to do anything as we were trying to delete anyway
                pass
    return backups_deleted
