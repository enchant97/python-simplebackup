from threading import Thread

from ..core.backup_search import delete_prev_backups, search_included
from ..core.copy_folder import copy_files, create_backup_folder
from ..core.copy_tar import copy_tar_files
from ..core.logging import logger


class BackupThread(Thread):
    """
    A thread to run the backup and
    update progressbar without freezing the gui

        :param included_folders: the included folders
        :param excluded_folders: the excluded folders
        :param backup_location: where backups are stored
        :param versions_to_keep: the number of backups to keep
        :param search_callback: func to call each time a file is found
        :param copy_callback: func to call each time copy has finished
        :param use_tar: whether to use tar backups, defaults to False
    """
    def __init__(self, included_folders, excluded_folders, backup_location, versions_to_keep, search_callback, copy_callback, use_tar=False):
        super().__init__(name="backup")
        self.__included_folders = included_folders
        self.__excluded_folders = excluded_folders
        self.__backup_location = backup_location
        self.__versions_to_keep = versions_to_keep
        self.__search_callback = search_callback
        self.__copy_callback = copy_callback
        self.__use_tar = use_tar

    def run(self):
        logger.debug("Starting backup thread")
        # delete prev backups, find files to backup, then do backup
        delete_prev_backups(self.__backup_location, self.__versions_to_keep)
        logger.debug("Finished deleting previous backups")
        files_to_backup = search_included(self.__included_folders, self.__excluded_folders, self.__search_callback)
        logger.debug("Finished searching for files to backup")
        if self.__use_tar:
            logger.debug("Running tar type backup")
            copy_tar_files(files_to_backup, self.__backup_location, self.__copy_callback)
        else:
            logger.debug("Creating backup folder")
            backup_folder = create_backup_folder(self.__backup_location)
            logger.debug("Running folder type backup")
            copy_files(backup_folder, files_to_backup, self.__copy_callback)
        logger.debug("Stopping backup thread")
