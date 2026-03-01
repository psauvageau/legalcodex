from __future__ import annotations

import logging
import argparse
import json
import os
from contextlib import closing, contextmanager
from typing import Optional, Generator, Final, cast, Any

from ..ai.chat.chat_session import ChatSession, ChatSessionId
from ..ai.chat.chat_session_manager import ChatSessionManager
from ..ai.chat import chat_behaviour
from ..ai.stream import Stream
from ..exceptions import LCException, ChatSessionNotFound

from .engine_cmd import EngineCommand


_logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TURN = 40

CLI_SESSION_ID :Final[ChatSessionId] = ChatSessionId("cli-session")


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
        cm = ChatSessionManager()
        session = get_session(args)
        commands_processor = ChatCommandProcessor(session.uid)
        write("Starting interactive chat session. Type 'help' for commands.")
        try:
            while True:
                try:
                    prompt = input("You> ").strip()
                    if not prompt:
                        write("Please enter a message or type 'help'.")
                        continue

                    commands_processor.execute(prompt)
                    stream :Stream = chat_behaviour.send_message(session, prompt)
                    self.stream_handler(stream)
                    print()

                except CommandExecutedException:
                    continue

                except LCException as e:
                    write(f"Error: {e}")

                except (KeyboardInterrupt, ExitException):
                        write("Exiting chat session.")
                        break
        finally:
            cm.save()


def get_session(args:argparse.Namespace)->ChatSession:

    manager = ChatSessionManager()
    try:
        session = manager.get_session(CLI_SESSION_ID)

        return session

    except ChatSessionNotFound:
        pass

    session = _CliChatSession.new_chat_session(
            username="test",
            system_prompt=args.system,
            max_messages=args.max_turns,
            engine_name=args.engine,
            model=args.model,
            trim_length=0
        )
    ChatSessionManager().add_session(session)
    if session.uid != CLI_SESSION_ID:
        raise LCException("CLI session should have a fixed session id")

    return session

def write(msg:str)->None:
    _logger.info(msg)
    print(msg)
    print()

class _CliChatSession(ChatSession):
    """
    A wrapper around ChatSession that automatically saves after each message.
    """

    @classmethod
    def _new_session_id(cls) -> ChatSessionId:
        return CLI_SESSION_ID



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
            messages = self.chat_session.context.get_messages()

            for msg in messages:
                write(f"{msg.role}: {msg.content}")

        self._commands = {      "exit": exit,
                                "quit": exit,
                                "help": help,
                                "history": history,
                                "reset": self.chat_session.context.reset,
                }

    @property
    def chat_session(self) -> ChatSession:
        cm = ChatSessionManager()

        session = cm.get_session(self._session_id)
        return session

    def execute(self, prompt:str)->None:
        command = prompt.lower()
        if command in self._commands:
            self._commands[command]()
            raise CommandExecutedException()


class CommandExecutedException(LCException):
    pass

class ExitException(Exception):
    pass