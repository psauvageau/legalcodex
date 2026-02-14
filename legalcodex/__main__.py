import argparse
import logging
from typing import List, Type, Iterable, Optional, Generator

from .exceptions import LCException

from ._cli.cli_cmd import CliCmd
from ._cli.cmd_chat import CommandChat
from ._cli.cmd_test import CommandTest


COMMANDS :List[Type[CliCmd]] = [
    CommandChat,
    CommandTest,
    # Add new command classes here
]


def main()->None:
    """
    Main entry point for the LegalCodex CLI tool.
    """
    args: argparse.Namespace = _get_args(COMMANDS)

    init_log(args.verbose)

    if args.command:        # Execute the command
        try:
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

    subparsers :argparse.Action = parser.add_subparsers()
    parser.set_defaults(command=None)

    # Register the command classes
    for cmd in cmds:
        cmd().register(subparsers)

    return parser.parse_args()



def init_log(verbose:bool)->None:
    """
    Initialize the logging configuration.

    Args:
        verbose (bool): If True, set logging level to DEBUG, otherwise INFO.
    """
    if verbose:
        level = logging.DEBUG

    else:
        level = logging.INFO

    format = "%(levelname)-8s - %(name)-20s - %(message)s"

    logging.basicConfig(level=level, format=format)

    silence = ["httpx",
               "google_genai.models",
               "httpcore"]

    for name in silence:
        logging.getLogger(name).setLevel(logging.WARNING)

if __name__ == "__main__":
    main()
