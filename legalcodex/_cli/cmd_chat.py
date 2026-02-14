from __future__ import annotations

import logging

import argparse

from .engine_cmd import EngineCommand
from ..chat_behaviour import ChatBehaviour
from ..exceptions import LCException


_logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TURN = 99

class CommandChat(EngineCommand):
    title: str = "chat"

    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        super().add_arguments(parser)
        parser.add_argument(
            "--system",
            type=str,
            default=DEFAULT_SYSTEM_PROMPT,
            help="Override the system prompt for this chat session",
        )
        parser.add_argument(
            "--max-turns",
            type=int,
            default=DEFAULT_MAX_TURN,
            help="Maximum number of user/assistant turns to keep in memory",
        )



    def run(self, args: argparse.Namespace) -> None:
        super().run(args)

        chat = ChatBehaviour(
            engine=self.engine,
            system_prompt=args.system,
            max_turns=args.max_turns,
        )
        commands = ChatCommands(chat)

        _logger.info("Starting interactive chat session. Type 'help' for commands.")
        while True:
            try:
                prompt = input("You> ").strip()
                if not prompt:
                    _logger.info("Please enter a message or type 'help'.")
                    continue

                commands.execute(prompt)

                response = chat.receive_user_message(prompt)
                _logger.info("AI > %s", response)

            except CommandExecutedException:
                continue

            except LCException as e:
                _logger.info("Error: %s", e)

            except (KeyboardInterrupt, ExitException):
                    _logger.info("\nExiting chat session.")
                    break



class ChatCommands:
    """
    A wrapper for chat-related commands, providing common utilities and shared state.
    """
    def __init__(self, chat:ChatBehaviour)->None:
        self._chat = chat

        def exit()->None:
            raise ExitException()

        def help()->None:
            cmds = ", ".join(self._commands.keys())
            _logger.info("Commands: %s", cmds)

        self._commands = {      "exit": exit,
                                "quit": exit,
                                "help": help,
                                "reset": self._chat.reset,
                }

    def execute(self, prompt:str)->None:
        command = prompt.lower()
        if command in self._commands:
            self._commands[command]()
            raise CommandExecutedException()


class CommandExecutedException(LCException):
    pass

class ExitException(Exception):
    pass