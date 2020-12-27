import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import (BOTTOM, DISABLED, END, NORMAL, SUNKEN, BooleanVar,
                     Listbox, Menu, Tk, W, X, filedialog, messagebox,
                     simpledialog)
from tkinter.ttk import Button, Checkbutton, Label, Progressbar

from .. import __version__
from ..core.config import Config_Handler
from ..core.const import APP_CONFIG_PATH, ERROR_TYPES, UPDATE_URL
from .backup_thread import BackupThread
from .simpledialog_extra import ask_combobox


class TkApp(Tk):
    """
    The main Tk class for the gui of simplebackup
    """
    def __init__(self, **kwargs):
        super().__init__()
        title = "Simple Backup | V" + __version__
        self.wm_title(title)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.__thread = None
        self.__files_found = 0
        self.__files_copied = 0

        config_fn = kwargs.get("config_fn", APP_CONFIG_PATH)
        self.__app_config = Config_Handler(config_fn)
        self.__curr_config = self.__app_config.default_config_i

        self.__menu = Menu(self)
        self.__menu_file = Menu(self.__menu, tearoff=0)
        self.__menu_file.add_command(label="Quit", command=self.quit)
        self.__menu_config = Menu(self.__menu, tearoff=0)
        self.__menu_config.add_command(label="New", command=self.new_config)
        self.__menu_config.add_command(label="Load", command=self.switch_config)
        self.__menu_config.add_command(label="Change Default", command=self.change_default_config)
        self.__menu_config.add_command(label="Rename Current", command=self.rename_curr_conf)
        self.__menu_config.add_separator()
        self.__menu_config.add_command(label="Delete Current", command=self.delete_current_config)
        self.__menu_config.add_command(label="Delete All", command=self.reset_config)
        self.__menu_help = Menu(self.__menu, tearoff=0)
        self.__menu_help.add_command(label="Check for Updates", command=self.show_update_popup)
        self.__menu_help.add_command(label="About", command=self.show_about_popup)
        self.__menu.add_cascade(label="File", menu=self.__menu_file)
        self.__menu.add_cascade(label="Config", menu=self.__menu_config)
        self.__menu.add_cascade(label="Help", menu=self.__menu_help)

        self.__title_l = Label(self, text=title, font=(16))
        self.__curr_config_name_l = Label(self)
        self.__last_backup_l = Label(self)
        self.__set_versions_to_keep = Button(self, text="Set Versions To Keep", command=self.update_versions_to_keep)
        self.__versions_to_keep_l = Label(self)
        self.__inc_folder_bnt = Button(self, text="Include Another Folder", command=self.add_included_folder)
        self.__included_folders_lb = Listbox(self, height=4)
        self.__included_folders_lb.bind("<<ListboxSelect>>", self.remove_selected_included_folder)
        self.__included_folders_lb.bind('<FocusOut>', self.deselect_included_folder)
        self.__excl_folder_bnt = Button(self, text="Exclude Another Folder", command=self.add_excluded_folder)
        self.__excluded_folders_lb = Listbox(self, height=4)
        self.__excluded_folders_lb.bind("<<ListboxSelect>>", self.remove_selected_excluded_folder)
        self.__excluded_folders_lb.bind('<FocusOut>', self.deselect_excluded_folder)
        self.__backup_to_bnt = Button(self, text="Backup Folder", command=self.set_backup_folder)
        self.__backup_folder_l = Label(self)
        self.__use_tar_l = Label(self, text="Use Tar")
        self.__use_tar_var = BooleanVar(self)
        self.__use_tar_var.trace_add("write", self.use_tar_changed)
        self.__use_tar = Checkbutton(self, variable=self.__use_tar_var)
        self.__backup_start_bnt = Button(self, text="Start Backup", command=self.start_backup)
        self.__progress = Progressbar(self)
        self.__statusbar = Label(self, text="ok", relief=SUNKEN, anchor=W)
        self._load_display()
        self._layout()

        if self.__app_config.show_help:
            self.show_help_popup()

    def on_closing(self):
        """
        called on window close
        """
        if self.__files_found != self.__files_copied:
            if messagebox.askyesno("Backup Running", "Do you want to stop the backup?"):
                self.destroy()
        else:
            self.destroy()

    def _load_display(self):
        """
        load the widgets with data from the current backup config,
        should be run after loading a config from file and at app launch
        """
        self.__versions_to_keep = self.__app_config.get_versions_to_keep(self.__curr_config)
        self.__included_folders = self.__app_config.get_included_folders(self.__curr_config)
        self.__excluded_folders = self.__app_config.get_excluded_folders(self.__curr_config)
        self.__backup_location = self.__app_config.get_backup_path(self.__curr_config)

        curr_conf_name = self.__app_config.get_config_name(self.__curr_config)
        self.__curr_config_name_l.config(text=f"Config Name: {curr_conf_name}")
        self.__last_backup_l.config(text=f"Last Known Backup: {self.__app_config.get_human_last_backup(self.__curr_config)}")
        self.__versions_to_keep_l.config(text=self.__versions_to_keep)
        self.__included_folders_lb.delete(0, END)
        self.__included_folders_lb.insert(0, *self.__included_folders)
        self.__excluded_folders_lb.delete(0, END)
        self.__excluded_folders_lb.insert(0, *self.__excluded_folders)
        self.__backup_folder_l.config(text=str(self.__backup_location))
        self.__use_tar_var.set(self.__app_config.get_use_tar(self.__curr_config))

    def switch_config(self):
        """
        switches what config to use for backup,
        asks the user for a config to load,
        then loads the display
        """
        next_combo = ask_combobox("Load Config", "Config Name", self.__app_config.get_config_names())
        if next_combo != None:
            self.__curr_config = next_combo
            self._load_display()

    def change_default_config(self):
        """
        switches what config to use for the default backup,
        asks the user for a config to load
        """
        next_combo = ask_combobox("Default Config", "Config Name", self.__app_config.get_config_names())
        if next_combo != None:
            self.__app_config.default_config_i = next_combo

    def rename_curr_conf(self):
        """
        rename a existing config,
        will ask the user in a popup string input
        """
        new_name = simpledialog.askstring("Rename Config", "New Name")
        if new_name:
            self.__app_config.rename_config(self.__curr_config, new_name)
            self._load_display()

    def new_config(self):
        """
        creates a new empty backup config,
        asks the user for config name
        """
        name = simpledialog.askstring("New Config", "Config Name")
        if name:
            self.__app_config.create_config(name)

    def delete_current_config(self):
        """
        deletes the current selected config, asks the user to confirm
        """
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the current config?"):
            self.__app_config.remove_config(self.__curr_config)
            self.__curr_config = self.__app_config.default_config_i
            self._load_display()

    def reset_config(self):
        """
        resets all the user configs, asks the user to confirm
        """
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the all configurations?"):
            self.__app_config.reset_config()
            self.__curr_config = self.__app_config.default_config_i
            self._load_display()

    def use_tar_changed(self, *args):
        """
        called each time the __use_tar_var is called
        """
        self.__app_config.set_use_tar(self.__curr_config, self.__use_tar_var.get())

    def update_versions_to_keep(self):
        """
        update the number of versions to keep,
        asks the user for a integer
        """
        new_val = simpledialog.askinteger("Versions To Keep", "How many backups do you want to keep", minvalue=0)
        if new_val != self.__versions_to_keep and new_val != None:
            self.__versions_to_keep = new_val
            self.__app_config.set_versions_to_keep(self.__curr_config, self.__versions_to_keep)
            self.__versions_to_keep_l.config(text=self.__versions_to_keep)

    def deselect_included_folder(self, *args):
        """
        deselects the selected element in included folder
        """
        self.__included_folders_lb.selection_clear(0, END)

    def deselect_excluded_folder(self, *args):
        """
        deselects the selected element in excluded folder
        """
        self.__excluded_folders_lb.selection_clear(0, END)

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
                self.__included_folders_lb.insert(END, folder_path)
                self.__app_config.set_included_folders(self.__curr_config, self.__included_folders)
            else:
                messagebox.showwarning(
                    title="Folder Same As Backup Path",
                    message="You selected a folder that was the same as the backup path!")

    def remove_selected_included_folder(self, *args):
        """
        remove the currently selected
        item in the included folders ListBox,
        will ask the user to confirm
        """
        curr_selection = self.__included_folders_lb.curselection()
        # check if there is a selection
        if curr_selection:
            if messagebox.askyesno("Confirm Delete", "Are you want to delete this folder?"):
                index_to_del = curr_selection[0]
                self.__included_folders.pop(index_to_del)
                self.__app_config.set_included_folders(self.__curr_config, self.__included_folders)
                self.__included_folders_lb.delete(index_to_del)
            self.deselect_included_folder()

    def add_excluded_folder(self):
        """
        add a folder to exclude in the backup,
        will ask user for a directory
        """
        folder = filedialog.askdirectory(initialdir="/", title="Select Folder To Exclude")
        if folder:
            folder_path = Path(folder)
            self.__excluded_folders.append(folder_path)
            self.__excluded_folders_lb.insert(END, folder_path)
            self.__app_config.set_excluded_folders(self.__curr_config, self.__excluded_folders)

    def remove_selected_excluded_folder(self, *args):
        """
        remove the currently selected
        item in the excluded folders ListBox,
        will ask the user to confirm
        """

        curr_selection = self.__excluded_folders_lb.curselection()
        # check if there is a selection
        if curr_selection:
            if messagebox.askyesno("Confirm Delete", "Are you want to delete this folder?"):
                index_to_del = curr_selection[0]
                self.__excluded_folders.pop(index_to_del)
                self.__app_config.set_excluded_folders(self.__curr_config, self.__excluded_folders)
                self.__excluded_folders_lb.delete(index_to_del)
            self.deselect_excluded_folder()

    def set_backup_folder(self):
        """
        sets the backup folder by asking the user for a base directory
        """
        folder = filedialog.askdirectory(initialdir="/", title="Select Where To Backup To")
        if folder:
            self.__backup_location = Path(folder)
            self.__backup_folder_l.config(text=folder)
            self.__app_config.set_backup_path(self.__curr_config, self.__backup_location)

    def enable_gui(self):
        """
        enable the gui buttons, run when a backup has completed
        """
        self.__set_versions_to_keep.config(state=NORMAL)
        self.__inc_folder_bnt.config(state=NORMAL)
        self.__included_folders_lb.config(state=NORMAL)
        self.__excl_folder_bnt.config(state=NORMAL)
        self.__excluded_folders_lb.config(state=NORMAL)
        self.__backup_to_bnt.config(state=NORMAL)
        self.__use_tar.config(state=NORMAL)
        self.__backup_start_bnt.config(state=NORMAL)

    def disable_gui(self):
        """
        disable the gui buttons, run when a backup is started
        """
        self.__set_versions_to_keep.config(state=DISABLED)
        self.__inc_folder_bnt.config(state=DISABLED)
        self.__included_folders_lb.config(state=DISABLED)
        self.__excl_folder_bnt.config(state=DISABLED)
        self.__excluded_folders_lb.config(state=DISABLED)
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
            self.__app_config.set_last_backup(self.__curr_config, datetime.utcnow())
            self.__last_backup_l.config(text=f"Last Known Backup: {self.__app_config.get_human_last_backup(self.__curr_config)}")
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
                self.__included_folders, self.__excluded_folders,
                self.__backup_location, self.__versions_to_keep,
                self.progress_find_incr, self.progress_copy_incr,
                self.handle_error_message, self.__use_tar_var.get()
                )
            # start the background backup thread so GUI wont appear frozen
            self.__thread.start()

    def show_about_popup(self):
        """
        show the about popup
        """
        messagebox.showinfo(
            "About",
            "simplebackup V" + __version__ + """ is cross-platform backup program written in python.
This app was made by enchant97/Leo Spratt.
It is licenced under GPL-3.0""")

    def show_update_popup(self):
        """
        open the default webbrowser to the update url
        """
        webbrowser.open(UPDATE_URL)

    def show_help_popup(self):
        messagebox.showinfo("Welcome", """Welcome to simplebackup, here is some help to get you started:
\nIncluding a folder to backup
    - Press the 'Include Folder' button to add a folder to backup
    - Remove a entry by clicking on the list below
\nExcluding a folder from the backup
    - Press the 'Exclude Folder' button to skip a folder to backup
    - Remove a entry by clicking on the list below
\nSetting where backups are stored
    - Click the 'Backup Folder' button to set where backups should be placed
\nMultiple backup configs
    Use the 'Config' button in the titlebar to change varius settings like creating a new config
\nVersions to keep
    This will be the number of backup to keep in the backup folder
""")
        self.__app_config.show_help = False

    def handle_error_message(self, error_type: ERROR_TYPES):
        self.__statusbar.config(text="Failed")
        if error_type is ERROR_TYPES.NO_BACKUP_WRITE_PERMISION:
            messagebox.showerror("No Write Permission", ERROR_TYPES.NO_BACKUP_WRITE_PERMISION.value)
        elif error_type is ERROR_TYPES.NO_BACKUP_READ_PERMISION:
            messagebox.showerror("No Read Permission", ERROR_TYPES.NO_BACKUP_READ_PERMISION.value)
        elif error_type is ERROR_TYPES.NO_FILES_FOUND_TO_BACKUP:
            messagebox.showerror("No Files Found", ERROR_TYPES.NO_FILES_FOUND_TO_BACKUP.value)
        elif error_type is ERROR_TYPES.NO_BACKUP_PATH_FOUND:
            messagebox.showerror("No Backup Path Found", ERROR_TYPES.NO_BACKUP_PATH_FOUND.value)
        self.__progress.config(mode="determinate")
        self.enable_gui()

    def _layout(self):
        self.config(menu=self.__menu)
        self.__title_l.pack(fill=X, pady=10, padx=5)
        self.__curr_config_name_l.pack(fill=X, padx=5)
        self.__last_backup_l.pack(fill=X, padx=5)
        self.__set_versions_to_keep.pack(fill=X, padx=5)
        self.__versions_to_keep_l.pack(fill=X, padx=5)
        self.__inc_folder_bnt.pack(fill=X, padx=5)
        self.__included_folders_lb.pack(fill=X, padx=5)
        self.__excl_folder_bnt.pack(fill=X, padx=5)
        self.__excluded_folders_lb.pack(fill=X, padx=5)
        self.__backup_to_bnt.pack(fill=X, padx=5)
        self.__backup_folder_l.pack(fill=X, padx=5)
        self.__use_tar_l.pack(fill=X, padx=5)
        self.__use_tar.pack(fill=X, padx=5)
        self.__backup_start_bnt.pack(fill=X, padx=5)
        self.__progress.pack(fill=X)
        self.__statusbar.pack(side=BOTTOM, fill=X)
        self.wm_minsize(300, self.winfo_height())
        self.wm_resizable(True, False)
