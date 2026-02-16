from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional, Final

from ..engine import Engine, Message

from .chat_context import ChatContext

_logger = logging.getLogger(__name__)






class ChatBehaviour:
    """
    ChatBehaviour manages the conversation flow with an Engine,
    maintaining context and history.
    """

    DEFAULT_MAX_TURN: int = 99
    _engine: Final[Engine]
    _system_prompt: Final[str]
    _max_turns: Final[int]
    _max_overflow = 20

    _context : ChatContext

    def __init__(
        self,
        engine: Engine,
        system_prompt: str,
        max_turns: Optional[int] = None,
    ) -> None:
        self._engine = engine
        self._system_prompt = system_prompt.strip()
        self._max_turns = self.DEFAULT_MAX_TURN if max_turns is None else max_turns

        self.reset()

    def reset(self) -> None:
        self._context = ChatContext(engine = self._engine,
                                    system_prompt = self._system_prompt,
                                    max_messages = self._max_turns)


    def send_message(self, user_message: str) -> str:
        """
        Send a user message to the engine and get the assistant's response.
         - The user message is appended to the context history.
        """
        prompt = user_message.strip()
        if not prompt:
            raise ValueError("user_message must not be empty")

        self._context.append(Message(role="user", content=prompt))
        response = self._engine.run_messages(self._context)
        self._context.append(Message(role="assistant", content=response))

        _logger.debug("Chat turn completed. History size=%d", len(self._context))

        return response


    #Used only for testing to inspect the message history
    @property
    def history(self) -> list[Message]:
        return list(self._context.get_messages())

