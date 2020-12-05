"""
functions related to finding folders
and finding files to backup
"""
import os
import re
from pathlib import Path

from ..const import BACKUP_DATESTAMP_UTC_REG


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
