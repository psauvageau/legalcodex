from __future__ import annotations

import argparse

from .cli_cmd import CliCmd


class CommandChat(CliCmd):
    title: str = "chat"

    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """



    def run(self, args: argparse.Namespace) -> None:
        pass
