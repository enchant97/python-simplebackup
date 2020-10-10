from pathlib import Path
from threading import Thread
from tkinter import (DISABLED, NORMAL, SUNKEN, Button, Label, Tk, W, X,
                     filedialog, messagebox, BOTTOM)
from tkinter.ttk import Progressbar

from . import __version__
from .core import copy_files, create_backup_folder, search_included


class BackupThread(Thread):
    def __init__(self, included_folders, backup_location, versions_to_keep, search_callback, copy_callback):
        super().__init__()
        self.__included_folders = included_folders
        self.__backup_location = backup_location
        self.__versions_to_keep = versions_to_keep
        self.__search_callback = search_callback
        self.__copy_callback = copy_callback

    def run(self):
        files_to_backup = search_included(self.__included_folders, self.__search_callback)
        backup_folder = create_backup_folder(self.__backup_location, self.__versions_to_keep)
        copy_files(backup_folder, files_to_backup, self.__copy_callback)

class TkApp(Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("Simple Backup | V" + __version__)

        self.__thread = None
        self.__files_found = 0
        self.__files_copied = 0

        self.__versions_to_keep = 2
        self.__included_folders = []
        self.__backup_location = None

        self.__inc_folder_bnt = Button(self, text="Add Folder", command=self.add_included_folder)
        self.__included_folders_l = Label(self)
        self.__backup_to_bnt = Button(self, text="Backup Folder", command=self.set_backup_folder)
        self.__backup_folder_l = Label(self)
        self.__backup_start_bnt = Button(self, text="Start Backup", command=self.start_backup)
        self.__progress = Progressbar(self)
        self.__statusbar = Label(self, relief=SUNKEN, anchor=W)
        self.layout()

    def add_included_folder(self):
        folder = filedialog.askdirectory(initialdir="/", title="Select Folder To Backup")
        if folder:
            folder_path = Path(folder)
            if folder_path != self.__backup_location:
                self.__included_folders.append(folder_path)
                self.__included_folders_l.config(text="; ".join(map(str, self.__included_folders)))
            else:
                messagebox.showwarning(title="Folder Same As Backup Path", message="You selected a folder that was the same as the backup path!")

    def set_backup_folder(self):
        folder = filedialog.askdirectory(initialdir="/", title="Select Where To Backup To")
        if folder:
            self.__backup_location = Path(folder)
            self.__backup_folder_l.config(text=folder)

    def enable_gui(self):
        """
        enable the gui buttons, run when a backup has completed
        """
        self.__inc_folder_bnt.config(state=NORMAL)
        self.__backup_to_bnt.config(state=NORMAL)
        self.__backup_start_bnt.config(state=NORMAL)

    def progress_find_incr(self, finished=False):
        if finished:
            self.__progress.config(mode="determinate")
            self.__progress.config(value=0, maximum=self.__files_found)
            self.__statusbar.config(text=f"Found {self.__files_found} Files")
        else:
            self.__files_found += 1
            self.__progress.config(value=self.__files_found)
            self.__statusbar.config(text=f"Searching For Files, Found {self.__files_found} Files")

    def progress_copy_incr(self):
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
        if not self.__backup_location:
            # no backup location was selected
            messagebox.showwarning(title="Backup Location Not Selected", message="You did not select a backup location!")
        elif not self.__included_folders:
            # no folders where found to backup
            messagebox.showwarning(title="No Folders To Backup", message="You did not add any folders to backup!")
        else:
            # basic checks passed
            self.__inc_folder_bnt.config(state=DISABLED)
            self.__backup_to_bnt.config(state=DISABLED)
            self.__backup_start_bnt.config(state=DISABLED)
            # prep for search of files
            self.__progress.config(mode="indeterminate")
            self.__statusbar.config(text=f"Searching For Files")

            self.__thread = BackupThread(
                self.__included_folders, self.__backup_location,
                self.__versions_to_keep, self.progress_find_incr,
                self.progress_copy_incr
                )
            # start the background backup thread so GUI wont appear frozen
            self.__thread.start()

    def layout(self):
        self.__inc_folder_bnt.pack(fill=X)
        self.__included_folders_l.pack(fill=X)
        self.__backup_to_bnt.pack(fill=X)
        self.__backup_folder_l.pack(fill=X)
        self.__backup_start_bnt.pack(fill=X)
        self.__progress.pack(fill=X)
        self.__statusbar.pack(side=BOTTOM, fill=X)
