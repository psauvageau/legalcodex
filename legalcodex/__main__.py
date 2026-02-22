import argparse
import logging
from typing import List, Type, Iterable, Optional, Generator, Final
from contextlib import contextmanager
from contextlib import contextmanager



from ._cli.cli_cmd import CliCmd
from ._cli.cmd_chat import CommandChat
from ._cli.cmd_serve import CommandServe
from ._cli.cmd_test import CommandTest



from .exceptions import LCException
from ._logs import init_log


COMMANDS :List[Type[CliCmd]] = [
    CommandChat,
    CommandServe,
    CommandTest,
    # Add new command classes here
]

_logger = logging.getLogger(__name__)

MEGABYTES :Final[int] = 1024 * 1024


def main()->None:
    """
    Main entry point for the LegalCodex CLI tool.
    """
    args: argparse.Namespace = _get_args(COMMANDS)


    if args.command:        # Execute the command
        try:
            with init_log(args.verbose, args.log_window):
                _logger.info("Starting LegalCodex")
                args.command.run(args)
                _logger.info("LegalCodex finished successfully")
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
    parser.add_argument('--verbose', '-v',action="store_true", help='Enable verbose output')
    parser.add_argument('--test',    '-t',action="store_true", help='Set Test Mode')
    parser.add_argument('--log-window',    '-l',action="store_true", help='Open the log window')


    subparsers :argparse.Action = parser.add_subparsers()
    parser.set_defaults(command=None)

    # Register the command classes
    for cmd in cmds:
        cmd().register(subparsers)

    return parser.parse_args()


if __name__ == "__main__":
    main()
