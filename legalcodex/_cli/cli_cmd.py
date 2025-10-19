"""
Multi-Command Argument Parser

Example Usage:

    class ExampleCmd(CommandArg):
        title = "example"

        def execute(self, args:Namespace)->None:
            print(f"Command: {self.title}: {args.foo}:{args.bar}")

        def add_arguments(self, parser):
            parser.add_argument('--bar', type=int, help='bar help') # Local Argument

    parser = CommandParser(command_args.build_commands(globals()))
    parser.add_argument('--foo', type=int, help='foo help')         # Global arguments
    args = parser.get_args()

    if args.command:
        args.command.execute(args)

"""
from __future__ import annotations
import typing
import argparse
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any


#===========================================
class CliCmd(ABC):
    """
    Base class for command arguments
    """
    title:str #Must be redefined

    @abstractmethod
    def run(self, args:argparse.Namespace)->None:
        pass

    def __str__(self) -> str:
        return f"Command({self.title})"

    def register(self, subparsers:Any)->None:
        """
        Add command specific arguments to the parser
        """
        parser = subparsers.add_parser(self.title, help=f'{self.title} Help')
        self.add_arguments(parser)
        parser.set_defaults(command=self)

    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        pass
