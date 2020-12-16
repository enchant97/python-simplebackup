"""
functions related to finding folders
and finding files to backup
"""
import os
import re
import shutil
from pathlib import Path

from ..core.const import BACKUP_DATESTAMP_UTC_REG
from ..core.logging import logger


def search_included(paths_to_scan: tuple, paths_to_exclude: tuple, callback_progress=None) -> list:
    """
    walks the paths to scan using yield for each path

        :param paths_to_scan: tuple of Path obj of the
                              folder paths to walk
        :param paths_to_exclude: tuple of Path obj to
                                 skip scanning
        :param callback_progress: func to call when a
                                  file has been found,
                                  callback must accept one argument
                                  for whether it has finished search
        :return: list of each new filepath found as Path obj
    """
    found_paths = []
    for top in paths_to_scan:
        for root, sub_dirs, files in os.walk(top):
            # remove excluded paths by using a slice assignment
            sub_dirs[:] = [d for d in sub_dirs if Path(root).joinpath(d) not in paths_to_exclude]
            if files:
                for file in files:
                    full_path = Path(root).joinpath(file)
                    logger.debug("Searching found a file: \"%s\"", full_path)
                    found_paths.append(full_path)
                    if callback_progress:
                        # call progress callback to say file has been found
                        callback_progress()
    logger.debug("Finished finding files")
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
            logger.debug("Searching found a previous backup: \"%s\"", path)
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
        logger.debug("Sorted previous backups: \"%s\"", prev_backups)
        difference = (len(prev_backups) - versions_to_keep) + 1
        logger.debug("Difference of previous backups: \"%s\"", difference)
        for i in range(difference):
            try:
                curr_backup_path = prev_backups[i - 1]
                if curr_backup_path.is_dir():
                    logger.debug("Deleting a folder backup: \"%s\"", curr_backup_path)
                    # removes folder backups
                    shutil.rmtree(curr_backup_path)
                else:
                    logger.debug("Deleting a tar backup: \"%s\"", curr_backup_path)
                    # removes file backups
                    os.remove(curr_backup_path)
                backups_deleted += 1
            except FileNotFoundError:
                # we don't need to do anything as we were trying to delete anyway
                pass
    logger.debug("Finished deleting backups")
    return backups_deleted
