from __future__ import annotations

import logging
import argparse
import json
import os
from contextlib import closing, contextmanager
from typing import Optional, Generator, Final, cast, Any

from .._user_access import UsersAccess, User

from ..ai.chat._chat_types import ChatSessionId
from ..ai.chat.chat_session_manager import ChatSessionManager
from ..ai.chat import chat_behaviour
from ..ai.stream import Stream
from ..exceptions import LCException, ChatSessionNotFound

from .engine_cmd import EngineCommand


_logger = logging.getLogger(__name__)



DEFAULT_MAX_TURN = 40

CLI_SESSION_ID :Final[ChatSessionId] = ChatSessionId("cli-session")


class CommandChat(EngineCommand):
    title: str = "chat"

    def run(self, args: argparse.Namespace) -> None:
        self.set_api_key()
        session_id = get_session_id(args)
        commands_processor = ChatCommandProcessor(session_id)
        write("Starting interactive chat session. Type 'help' for commands.")
        try:
            while True:
                try:
                    print("=============================")
                    prompt = input("You> ").strip()
                    if not prompt:
                        write("Please enter a message or type 'help'.")
                        continue
                    print()
                    commands_processor.execute(prompt)
                    stream :Stream = chat_behaviour.send_message(session_id, prompt)
                    self.stream_handler(stream)

                except CommandExecutedException:
                    continue

                except LCException as e:
                    write(f"Error: {e}")

                except (KeyboardInterrupt, ExitException):
                        write("Exiting chat session.")
                        break
        finally:
            chat_behaviour.close_session(session_id)


def get_session_id(args:argparse.Namespace)->ChatSessionId:
    user = _get_user()

    # Return the first available session for the user
    for session_info in chat_behaviour.get_sessions(user):
        return session_info.session_id

    # If no session exists, create a new one with the CLI_SESSION_ID
    return chat_behaviour.new_session(user=user,
                               engine_name=args.engine,
                               model=args.model)


def write(msg:str)->None:
    """
    Handler for the chat response stream.
    Writes the message to the console.
    """
    _logger.info(msg)
    print(msg)
    print()



class ChatCommandProcessor:
    """
    A wrapper for chat-related commands, providing common utilities and shared state.
    """
    _session_id : Final[ChatSessionId]

    def __init__(self, chat:ChatSessionId)->None:
        self._session_id = chat

        def exit()->None:
            raise ExitException()

        def help()->None:
            cmds = ", ".join(self._commands.keys())
            write(f"Commands: {cmds}")

        def history()->None:
            data = chat_behaviour.get_context(self._session_id)
            for msg in data.history:
                write(f"{msg.role}: {msg.content}")
            print()

        def reset()->None:
            chat_behaviour.reset_context(self._session_id)
            write("Chat context reset.")

        self._commands = {      "exit": exit,
                                "quit": exit,
                                "help": help,
                                "history": history,
                                "reset": reset,
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


def _get_user()->User:
    return UsersAccess.get_instance().find("test")