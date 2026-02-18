from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional, Final, TypeVar


from ..engine import Engine
from ..message import Message

from .chat_context import ChatContext

_logger = logging.getLogger(__name__)




T = TypeVar("T", bound="ChatBehaviour")

class ChatBehaviour:
    """
    ChatBehaviour manages the conversation flow with an Engine,
    maintaining context and history.
    """
    DEFAULT_MAX_TURN: int = 99

    context : Final[ChatContext]

    def __init__(self,engine: Engine, context : ChatContext)-> None:
        self._engine  = engine
        self.context = context

    def send_message(self, user_message: str) -> str:
        """
        Send a user message to the engine and get the assistant's response.
         - The user message is appended to the context history.
        """
        prompt = user_message.strip()
        if not prompt:
            raise ValueError("user_message must not be empty")

        self.context.append(self._engine, Message.User(prompt))
        response = self._engine.run_messages(self.context)
        self.context.append(self._engine, Message(role="assistant", content=response))

        _logger.debug("Chat turn completed. History size=%d", len(self.context))

        return response


    #Used only for testing to inspect the message history
    @property
    def history(self) -> list[Message]:
        return list(self.context.get_messages())


