import argparse
import logging
from typing import List, Type, Iterable, Optional, Generator
from contextlib import contextmanager
from contextlib import contextmanager

from .exceptions import LCException

from ._cli.cli_cmd import CliCmd
from ._cli.cmd_chat import CommandChat
from ._cli.cmd_test import CommandTest

from ._cli._log_window import log_window


COMMANDS :List[Type[CliCmd]] = [
    CommandChat,
    CommandTest,
    # Add new command classes here
]

_logger = logging.getLogger(__name__)


def main()->None:
    """
    Main entry point for the LegalCodex CLI tool.
    """
    args: argparse.Namespace = _get_args(COMMANDS)


    if args.command:        # Execute the command
        try:
            with init_log(args.verbose, args.log_window):
                args.command.run(args)
        except LCException as e:
            logging.error("Error: %s", e)
            exit(1)
    else:
        print(f"No command specified. [{", ".join([cmd.title for cmd in COMMANDS])}]")
        exit(1)


def _get_args(cmds:List[Type[CliCmd]]) -> argparse.Namespace:
    """
    Create the main argument parser for the CLI
    """
    parser:argparse.ArgumentParser = argparse.ArgumentParser(
        description="LegalCodex CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--config', '-c',action="store", type=str, default=None, help='Path to the config file')
    parser.add_argument('--verbose', '-v',action="store_true", help='Enable verbose output')
    parser.add_argument('--test',    '-t',action="store_true", help='Set Test Mode')
    parser.add_argument('--log-window',    '-l',action="store_true", help='Open the log window')


    subparsers :argparse.Action = parser.add_subparsers()
    parser.set_defaults(command=None)

    # Register the command classes
    for cmd in cmds:
        cmd().register(subparsers)

    return parser.parse_args()

@contextmanager
def init_log(verbose:bool, enable_log_window: bool)->Generator[None, None, None]:
    """
    Initialize the logging configuration.

    Args:
        verbose (bool): If True, set logging level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO

    format = "%(levelname)-8s - %(name)-20s - %(message)s"

    #logging.basicConfig(level=level, format=format)



    silence = ["httpx",
               "openai._base_client",
               "google_genai.models",
               "httpcore"]

    for name in silence:
        logging.getLogger(name).setLevel(logging.WARNING)


    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if enable_log_window:
        with log_window():
            yield
            input("Press Enter to exit...")
    else:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format))
        root_logger.addHandler(handler)
        try:
            logging.getLogger().info("Logging initialized. Level: %s", logging.getLevelName(level))
            yield
        finally:
            logging.getLogger().removeHandler(handler)

if __name__ == "__main__":
    main()
