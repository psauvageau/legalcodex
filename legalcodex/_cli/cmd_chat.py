from __future__ import annotations

import logging
import argparse
import os

from ..chat.chat_behaviour import ChatBehaviour
from ..chat.chat_context import ChatContext
from ..exceptions import LCException

from .engine_cmd import EngineCommand


_logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TURN = 40


FILE_NAME = "chat_context.json"

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

        parser.add_argument("--no-load", action="store_true", help="Do not load chat history from a file")

    def _get_chat_context(self, args: argparse.Namespace) -> ChatContext:

        load = not args.no_load

        if load:
            if os.path.exists(FILE_NAME):
                return ChatContext.load(FILE_NAME)
            else:
                _logger.warning("No existing chat context found, starting new session.")

        chat = ChatContext( system_prompt=args.system,
                            max_messages=args.max_turns)
        return chat


    def run(self, args: argparse.Namespace) -> None:
        super().run(args)

        chat_context = self._get_chat_context(args)

        chat = ChatBehaviour(self.engine, chat_context)

        commands = ChatCommands(chat)

        write("Starting interactive chat session. Type 'help' for commands.")
        while True:
            try:
                prompt = input("You> ").strip()
                if not prompt:
                    write("Please enter a message or type 'help'.")
                    continue

                commands.execute(prompt)

                response = chat.send_message(prompt)
                write(f"AI > {response}")

            except CommandExecutedException:
                continue

            except LCException as e:
                write(f"Error: {e}")

            except (KeyboardInterrupt, ExitException):
                    write("Exiting chat session.")
                    chat.context.save(FILE_NAME)
                    break

def write(msg:str)->None:
    _logger.info(msg)
    print(msg)
    print()


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
            write(f"Commands: {cmds}")

        def history()->None:
            messages = self._chat.context.get_messages()
            for msg in messages:
                write(f"{msg.role}: {msg.content}")

        self._commands = {      "exit": exit,
                                "quit": exit,
                                "help": help,
                                "history": history,
                                "reset": self._chat.context.reset,
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