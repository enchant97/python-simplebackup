import logging
import sys

from .cli import CLI
from .const import LOGGING_PATH
from .gui import TkApp

if __name__ == "__main__":
    logging.basicConfig(filename=LOGGING_PATH, level=logging.WARNING)
    if len(sys.argv) > 1:
        if sys.argv[1] == "gui":
            root = TkApp()
            root.mainloop()
    else:
        cli = CLI()
        cli.run()
