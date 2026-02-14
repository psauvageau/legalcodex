from __future__ import annotations

import logging

import argparse

from .engine_cmd import EngineCommand


_logger = logging.getLogger(__name__)


class CommandChat(EngineCommand):
    title: str = "chat"

    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        super().add_arguments(parser)



    def run(self, args: argparse.Namespace) -> None:
        super().run(args)

        print("Starting interactive chat session. Type 'exit' to quit.")
        while True:
            prompt = input("You: ")
            if prompt.lower() in ['exit', 'quit']:
                print("Exiting chat session.")
                break

            response = self.engine.run(prompt)
            print(f"Model: {response}")
