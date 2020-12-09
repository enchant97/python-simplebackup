from datetime import datetime
from pathlib import Path

from . import __version__
from .config import Config_Handler
from .const import APP_CONFIG_PATH
from .core.backup_search import delete_prev_backups, search_included
from .core.copy_folder import copy_files, create_backup_folder
from .core.copy_tar import copy_tar_files


class CLI:
    def __init__(self):
        self.__files_found = 0
        self.__files_backed_up = 0

        self.__app_config = Config_Handler(APP_CONFIG_PATH)
        self.__versions_to_keep = self.__app_config.get_versions_to_keep()
        self.__paths_to_backup = self.__app_config.get_included_folders()
        self.__excluded_paths = self.__app_config.get_excluded_folders()
        self.__backup_path = self.__app_config.get_backup_path()
        self.__use_tar = self.__app_config.get_use_tar()

    def show_welcome(self):
        print("Simple Backup CLI Mode | V" + __version__)
        print("Written By Leo Spratt - GPL-3.0")
        print(f"Last Known Backup: {self.__app_config.human_last_backup}")

    def add_path_to_backup(self):
        while True:
            try:
                path = input("Enter Path (or leave blank to go back): ")
                if not path:
                    break
                else:
                    path = Path(path).resolve(strict=True)
                    self.__paths_to_backup.append(path)
                    self.__app_config.set_included_folders(self.__paths_to_backup)
            except FileNotFoundError:
                print("That path does not seem to exit!")

    def change_backup_path(self):
        while True:
            try:
                path = input("Enter New Backup Path (or leave blank to go back): ")
                if not path:
                    break
                path = Path(path).resolve(strict=True)
                self.__backup_path = path
                self.__app_config.set_backup_path(self.__backup_path)
            except FileNotFoundError:
                print("That path does not seem to exit!")

    def change_versions_to_keep(self):
        while True:
            try:
                self.__versions_to_keep = int(input("Enter Number Of Versions To Keep: "))
                self.__app_config.set_versions_to_keep(self.__versions_to_keep)
                break
            except ValueError:
                print("Invalid Input!")

    def incr_search_prog(self, finished=False):
        if finished:
            print(f"Found Files, Found: {self.__files_found}", end='\r', flush=True)
        else:
            self.__files_found += 1
            print(f"Finding Files, Found: {self.__files_found}", end='\r', flush=True)

    def incr_backed_up_prog(self):
        self.__files_backed_up += 1
        print(f"Copied {self.__files_backed_up} out of {self.__files_found}", end='\r', flush=True)

        if self.__files_backed_up == self.__files_found:
            print(f"Finished Copying: {self.__files_backed_up} Files", end='\r', flush=True)
            print("\nPress A Key To Quit")

    def backup(self):
        if self.__backup_path:
            if self.__paths_to_backup:
                delete_prev_backups(self.__backup_path, self.__versions_to_keep)
                files_to_backup = search_included(
                    self.__paths_to_backup,
                    self.__excluded_paths,
                    self.incr_search_prog
                    )
                if self.__use_tar:
                    copy_tar_files(files_to_backup, self.__backup_path, self.incr_backed_up_prog)
                else:
                    backup_folder = create_backup_folder(self.__backup_path)
                    copy_files(backup_folder, files_to_backup, self.incr_backed_up_prog)

                # wait for files to finish copying then return to menu
                while True:
                    input()
                    if self.__files_backed_up == self.__files_found:
                        self.__app_config.set_last_backup(datetime.utcnow())
                        break
                return True
            else:
                print("No folders added to backup!")
        else:
            print("Backup path not set!")
        return False

    def show_menu(self):
        while True:
            print("\nMenu:")
            print("1. change backup path")
            print("2. add a folder to backup")
            print(f"3. change versions to keep ({self.__versions_to_keep})")
            print("4. start folder backup")
            if self.__use_tar:
                print("5. switch to folder type")
            else:
                print("5. switch to tar type")
            print("q. quit")
            choice = input("Enter Your Choice: ")
            if choice == "q":
                break
            elif choice == "5":
                self.__use_tar = not self.__use_tar
                self.__app_config.set_use_tar(self.__use_tar)
            elif choice == "4":
                if self.backup():
                    break
                else:
                    print("Failed To Copy")
            elif choice == "3":
                self.change_versions_to_keep()
            elif choice == "2":
                self.add_path_to_backup()
            elif choice == "1":
                self.change_backup_path()
            else:
                print("Unknown Input!")

    def run(self):
        """
        blocking function to run the CLI
        """
        self.show_welcome()
        self.show_menu()
