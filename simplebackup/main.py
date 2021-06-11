import logging
from argparse import ArgumentParser

from .cli import CLI
from .gui import TkApp


def get_sys_arguments():
    """
    parse the sys arguments provided to the program
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--cli",
        action='store_true',
        help="run the program in CLI mode rather than GUI",
    )
    parser.add_argument(
        "--level",
        choices=("debug", "info", "warning", "error", "critical"),
        default=logging.getLevelName(logging.ERROR),
        help="the log level for debugging",
    )
    return parser.parse_args()


def main():
    """
    run the program using any sys arguments provided
    """
    args = get_sys_arguments()
    log_level = logging.getLevelName(args.level.upper())
    logging.basicConfig(level=log_level)

    if args.cli:
        cli = CLI()
        cli.run()
    else:
        root = TkApp()
        root.mainloop()
