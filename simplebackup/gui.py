from pathlib import Path
from threading import Thread
from tkinter import (BOTTOM, DISABLED, NORMAL, SUNKEN, BooleanVar, Tk, W, X,
                     filedialog, messagebox, simpledialog)
from tkinter.ttk import Button, Checkbutton, Label, Progressbar

from . import __version__
from .config import Config_Handler
from .const import APP_CONFIG_PATH
from .core.backup_search import search_included
from .core.copy_folder import copy_files, create_backup_folder
from .core.copy_tar import copy_tar_files


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
        files_to_backup = search_included(self.__included_folders, self.__search_callback)
        if self.__use_tar:
            copy_tar_files(files_to_backup, self.__backup_location, self.__copy_callback)
        else:
            backup_folder = create_backup_folder(self.__backup_location, self.__versions_to_keep)
            copy_files(backup_folder, files_to_backup, self.__copy_callback)


class TkApp(Tk):
    """
    The main Tk class for the gui of simplebackup
    """
    def __init__(self):
        super().__init__()
        title = "Simple Backup | V" + __version__
        self.wm_title(title)

        self.__thread = None
        self.__files_found = 0
        self.__files_copied = 0

        self.__app_config = Config_Handler(APP_CONFIG_PATH)
        self.__versions_to_keep = self.__app_config.get_versions_to_keep()
        self.__included_folders = self.__app_config.get_included_folders()
        self.__backup_location = self.__app_config.get_backup_path()

        self.__title_l = Label(self, text=title)
        self.__set_versions_to_keep = Button(self, text="Set Versions To Keep", command=self.update_versions_to_keep)
        self.__versions_to_keep_l = Label(self, text=self.__versions_to_keep)
        self.__inc_folder_bnt = Button(self, text="Add Folder", command=self.add_included_folder)
        self.__included_folders_l = Label(self)
        self.update_included_folders_label()
        self.__backup_to_bnt = Button(self, text="Backup Folder", command=self.set_backup_folder)
        self.__backup_folder_l = Label(self, text=str(self.__backup_location))
        self.__use_tar_l = Label(self, text="Use Tar")
        self.__use_tar_var = BooleanVar(self, False)
        self.__use_tar = Checkbutton(self, variable=self.__use_tar_var)
        self.__backup_start_bnt = Button(self, text="Start Backup", command=self.start_backup)
        self.__progress = Progressbar(self)
        self.__statusbar = Label(self, relief=SUNKEN, anchor=W)
        self._layout()

    def update_versions_to_keep(self):
        """
        update the number of versions to keep,
        asks the user for a integer
        """
        new_val = simpledialog.askinteger("Versions To Keep", "How many backups do you want to keep")
        if new_val != self.__versions_to_keep and new_val != None:
            self.__versions_to_keep = new_val
            self.__app_config.set_versions_to_keep(self.__versions_to_keep)
            self.__versions_to_keep_l.config(text=self.__versions_to_keep)

    def update_included_folders_label(self):
        """
        update the included folders label with new included folders
        """
        if self.__included_folders:
            self.__included_folders_l.config(text="; ".join(map(str, self.__included_folders)))
        else:
            self.__included_folders_l.config(text="None")

    def add_included_folder(self):
        """
        add a folder to include in the backup,
        will ask user for a directory
        """
        folder = filedialog.askdirectory(initialdir="/", title="Select Folder To Backup")
        if folder:
            folder_path = Path(folder)
            if folder_path != self.__backup_location:
                self.__included_folders.append(folder_path)
                self.update_included_folders_label()
                self.__app_config.set_included_folders(*self.__included_folders)
            else:
                messagebox.showwarning(
                    title="Folder Same As Backup Path",
                    message="You selected a folder that was the same as the backup path!")

    def set_backup_folder(self):
        """
        sets the backup folder by asking the user for a base directory
        """
        folder = filedialog.askdirectory(initialdir="/", title="Select Where To Backup To")
        if folder:
            self.__backup_location = Path(folder)
            self.__backup_folder_l.config(text=folder)
            self.__app_config.set_backup_path(self.__backup_location)

    def enable_gui(self):
        """
        enable the gui buttons, run when a backup has completed
        """
        self.__set_versions_to_keep.config(state=NORMAL)
        self.__inc_folder_bnt.config(state=NORMAL)
        self.__backup_to_bnt.config(state=NORMAL)
        self.__use_tar.config(state=NORMAL)
        self.__backup_start_bnt.config(state=NORMAL)

    def disable_gui(self):
        """
        disable the gui buttons, run when a backup is started
        """
        self.__set_versions_to_keep.config(state=DISABLED)
        self.__inc_folder_bnt.config(state=DISABLED)
        self.__backup_to_bnt.config(state=DISABLED)
        self.__use_tar.config(state=DISABLED)
        self.__backup_start_bnt.config(state=DISABLED)

    def progress_find_incr(self, finished=False):
        """
        increment the progress bar for finding
        files by 1 or mark as finished

            :param finished: mark the progressbar as finished
        """
        if finished:
            self.__progress.config(mode="determinate")
            self.__progress.config(value=0, maximum=self.__files_found)
            self.__statusbar.config(text=f"Found {self.__files_found} Files")
        else:
            self.__files_found += 1
            self.__progress.config(value=self.__files_found)
            self.__statusbar.config(text=f"Searching For Files, Found {self.__files_found} Files")

    def progress_copy_incr(self):
        """
        increment the progress bar for copying
        files by 1 or mark as finished
        """
        self.__files_copied += 1
        self.__progress.config(value=self.__files_copied)
        self.__statusbar.config(text=f"Copying Files {self.__files_copied} of {self.__files_found}")
        if self.__files_copied == self.__files_found:
            self.__statusbar.config(text=f"Finished Copying Files")
            messagebox.showinfo(title="Finished Copying Files", message="Finished copying all found files")
            # reset counters
            self.__files_found = 0
            self.__files_copied = 0
            self.__progress.config(value=0, maximum=100)
            self.enable_gui()

    def start_backup(self):
        """
        starts the backup
        """
        if not self.__backup_location:
            # no backup location was selected
            messagebox.showwarning(
                title="Backup Location Not Selected",
                message="You did not select a backup location!")
        elif not self.__included_folders:
            # no folders where found to backup
            messagebox.showwarning(
                title="No Folders To Backup",
                message="You did not add any folders to backup!")
        else:
            # basic checks passed
            self.disable_gui()
            # prep for search of files
            self.__progress.config(mode="indeterminate")
            self.__statusbar.config(text=f"Searching For Files")

            self.__thread = BackupThread(
                self.__included_folders, self.__backup_location,
                self.__versions_to_keep, self.progress_find_incr,
                self.progress_copy_incr, self.__use_tar_var.get()
                )
            # start the background backup thread so GUI wont appear frozen
            self.__thread.start()

    def _layout(self):
        self.__title_l.pack(fill=X)
        self.__set_versions_to_keep.pack(fill=X)
        self.__versions_to_keep_l.pack(fill=X)
        self.__inc_folder_bnt.pack(fill=X)
        self.__included_folders_l.pack(fill=X)
        self.__backup_to_bnt.pack(fill=X)
        self.__backup_folder_l.pack(fill=X)
        self.__use_tar_l.pack(fill=X)
        self.__use_tar.pack(fill=X)
        self.__backup_start_bnt.pack(fill=X)
        self.__progress.pack(fill=X)
        self.__statusbar.pack(side=BOTTOM, fill=X)
        self.wm_minsize(300, self.winfo_height())
        self.wm_resizable(True, False)
