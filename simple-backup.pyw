"""
This is just a front for quickly
executing the GUI simplebackup module
"""
from simplebackup.gui import TkApp

root = TkApp(config_fn="app_config.json")
root.mainloop()
