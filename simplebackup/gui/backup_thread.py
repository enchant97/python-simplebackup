from threading import Thread

from ..core.backup_search import delete_prev_backups, search_included
from ..core.copy_folder import copy_files, create_backup_folder
from ..core.copy_tar import copy_tar_files
from ..core.logging import logger
from ..core.const import ERROR_TYPES

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
        :param error_callback: the func to call when something
                               goes wrong, needs to accept
                               ERROR_TYPES as a param
        :param use_tar: whether to use tar backups, defaults to False
    """
    def __init__(self, included_folders, excluded_folders, backup_location, versions_to_keep, search_callback, copy_callback, error_callback, use_tar=False):
        super().__init__(name="backup")
        self.__included_folders = included_folders
        self.__excluded_folders = excluded_folders
        self.__backup_location = backup_location
        self.__versions_to_keep = versions_to_keep
        self.__search_callback = search_callback
        self.__copy_callback = copy_callback
        self.__error_callback = error_callback
        self.__use_tar = use_tar

    def run(self):
        logger.debug("Starting backup thread")
        # delete prev backups, find files to backup, then do backup
        deleted = delete_prev_backups(self.__backup_location, self.__versions_to_keep, self.__error_callback)
        if deleted != -1:
            logger.debug("Finished deleting previous backups")
            logger.debug("Searching for files to backup")
            files_to_backup = search_included(self.__included_folders, self.__excluded_folders, self.__search_callback)
            if files_to_backup:
                logger.debug("Finished searching for files to backup")
                if self.__use_tar:
                    logger.debug("Running tar type backup")
                    copy_tar_files(files_to_backup, self.__backup_location, self.__copy_callback, self.__error_callback)
                else:
                    logger.debug("Creating backup folder")
                    backup_folder = create_backup_folder(self.__backup_location, self.__error_callback)
                    if backup_folder:
                        logger.debug("Running folder type backup")
                        copy_files(backup_folder, files_to_backup, self.__copy_callback)
            else:
                logger.error("No files found to backup!")
                self.__error_callback(ERROR_TYPES.NO_FILES_FOUND_TO_BACKUP)
        logger.debug("Stopping backup thread")
