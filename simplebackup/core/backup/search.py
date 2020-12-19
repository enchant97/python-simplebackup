"""
functions related to finding folders
and finding files to backup
"""
import os
import re
import shutil
from pathlib import Path

from ...core.const import BACKUP_DATESTAMP_UTC_REG, ERROR_TYPES, SYSTEM_FILES
from ...core.logging import logger


def is_system_file(file_path: Path, system_files=SYSTEM_FILES) -> bool:
    """
    used to check whether the file is a system file

        :param file_path: a pathlib.Path to check
        :param system_files: the list/tuple that contains
                            the known systems files,
                            defaults to SYSTEM_FILES
        :return: whether it is a recognised system file
    """
    if file_path.name in system_files:
        return True
    return False

def search_included(paths_to_scan: tuple, paths_to_exclude: tuple, callback_progress=None) -> list:
    """
    walks the paths to scan using yield for each path,
    skips known system files

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
                    # combine filename and root path
                    full_path = Path(root).joinpath(file)
                    if is_system_file(full_path):
                        logger.debug("Skipping system file: \"%s\"", full_path)
                    else:
                        logger.debug("Searching found a file: \"%s\"", full_path)
                        found_paths.append(full_path)
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
            logger.debug("Searching found a previous backup: \"%s\"", path)
            yield path


def delete_prev_backups(root_backup_path: Path, versions_to_keep=2, error_callback=None) -> int:
    """
    deletes older backups keeping the amount of versions given

        :param root_backup_path: root path of all backups
        :param versions_to_keep: versions to keep, defaults to 2
        :param error_callback: the func to call when something
                               goes wrong, needs to accept
                               ERROR_TYPES as a param
        :return: the number of backups deleted, -1 if failed
    """
    if versions_to_keep < 0:
        # make sure we dont have negative numbers
        versions_to_keep = 0
    backups_deleted = 0
    try:
        prev_backups = [i for i in find_prev_backups(root_backup_path)]
    except PermissionError:
        backups_deleted = -1
        logger.exception(ERROR_TYPES.NO_BACKUP_READ_PERMISION.value)
        if error_callback:
            error_callback(ERROR_TYPES.NO_BACKUP_READ_PERMISION)
    except FileNotFoundError:
        backups_deleted = -1
        logger.exception(ERROR_TYPES.NO_BACKUP_PATH_FOUND.value)
        if error_callback:
            error_callback(ERROR_TYPES.NO_BACKUP_PATH_FOUND)
    else:
        if (versions_to_keep >= 0) and (len(prev_backups) >= versions_to_keep):
            prev_backups = sorted(prev_backups, reverse=True)
            logger.debug("Sorted previous backups: \"%s\"", prev_backups)
            difference = len(prev_backups) - versions_to_keep
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
                except PermissionError:
                    backups_deleted = -1
                    logger.exception(ERROR_TYPES.NO_BACKUP_WRITE_PERMISION.value)
                    if error_callback:
                        error_callback(ERROR_TYPES.NO_BACKUP_WRITE_PERMISION)
    return backups_deleted
