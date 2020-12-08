from threading import Thread

from ..core.backup_search import delete_prev_backups, search_included
from ..core.copy_folder import copy_files, create_backup_folder
from ..core.copy_tar import copy_tar_files


class BackupThread(Thread):
    """
    A thread to run the backup and
    update progressbar without freezing the gui
    """
    def __init__(self, included_folders, backup_location, versions_to_keep, search_callback, copy_callback, use_tar=False):
        super().__init__(name="backup")
        self.__included_folders = included_folders
        self.__backup_location = backup_location
        self.__versions_to_keep = versions_to_keep
        self.__search_callback = search_callback
        self.__copy_callback = copy_callback
        self.__use_tar = use_tar

    def run(self):
        # delete prev backups, find files to backup, then do backup
        delete_prev_backups(self.__backup_location, self.__versions_to_keep)
        files_to_backup = search_included(self.__included_folders, self.__search_callback)
        if self.__use_tar:
            copy_tar_files(files_to_backup, self.__backup_location, self.__copy_callback)
        else:
            backup_folder = create_backup_folder(self.__backup_location)
            copy_files(backup_folder, files_to_backup, self.__copy_callback)
