"""
This is just a front for quickly
executing the GUI simplebackup module
"""
import logging

from simplebackup.gui import TkApp

logging.basicConfig(filename="simplebackup.log", level=logging.WARNING)
root = TkApp(config_fn="app_config.json")
root.mainloop()
