from __future__ import annotations

import logging
import argparse
import json
import os
from contextlib import closing, contextmanager
from typing import Optional, Generator

from ..ai.chat.chat_session import ChatSession
from ..ai.chat import chat_behaviour
from ..ai.stream import Stream
from ..exceptions import LCException
from .._environ import LC_API_KEY

from .engine_cmd import EngineCommand


_logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TURN = 40


FILE_NAME = "chat_session.json"

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

    def run(self, args: argparse.Namespace) -> None:
        self.set_api_key()

        with self.get_session(args) as session:
            commands = ChatCommands(session)
            write("Starting interactive chat session. Type 'help' for commands.")
            while True:
                try:
                    prompt = input("You> ").strip()
                    if not prompt:
                        write("Please enter a message or type 'help'.")
                        continue

                    commands.execute(prompt)

                    stream :Stream = chat_behaviour.send_message(session, prompt)
                    self.stream_handler(stream)

                except CommandExecutedException:
                    continue

                except LCException as e:
                    write(f"Error: {e}")

                except (KeyboardInterrupt, ExitException):
                        write("Exiting chat session.")
                        session.context.save(FILE_NAME)
                        break

    @contextmanager
    def get_session(self, args:argparse.Namespace)->Generator[ChatSession,None,None]:
        if os.path.isfile(FILE_NAME):
            session = ChatSession.load(FILE_NAME)
        else:
            session = ChatSession.new_chat_session(
                    username="test",
                    system_prompt=args.system,
                    max_messages=args.max_turns,
                    engine_name=args.engine,
                    model=args.model,
                    trim_length=0
                )
        try:
            yield session
        finally:
            session.save(FILE_NAME)


def write(msg:str)->None:
    _logger.info(msg)
    print(msg)
    print()









class ChatCommands:
    """
    A wrapper for chat-related commands, providing common utilities and shared state.
    """
    def __init__(self, chat:ChatSession)->None:
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