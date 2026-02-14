from __future__ import annotations

import logging
from typing import Optional, Final

from .engine import Context, Engine, Message

_logger = logging.getLogger(__name__)



class _ChatContext(Context):
    _history: list[Message]
    _system_prompt: Final[Message]

    def __init__(self, system_prompt: str) -> None:

        self._system_prompt = Message(
            role="system",
            content=system_prompt.strip(),
        )

        self._history = []

    def get_messages(self) -> list[Message]:
        """
        Return the full message history including the system prompt.
        """
        messages = [self._system_prompt]
        messages.extend(self._history)
        return messages

    def append(self, message: Message) -> None:
        """
        Append a message to the history.
        """
        self._history.append(message)

    def trim(self, max_turns: int) -> None:
        """
        Trim the message history to the specified maximum number of turns.
        """
        if max_turns is None:
            return

        max_messages = max_turns * 2
        if len(self._history) <= max_messages:
            return
        self._history = self._history[-max_messages:]

    def __len__(self) -> int:
        """
        Return the number of messages in the history (excluding system prompt).
        """
        return len(self._history)


class ChatBehaviour:

    DEFAULT_MAX_TURN: int = 99
    _engine: Final[Engine]
    _system_prompt: Final[str]
    _max_turns: Final[int]

    _context : _ChatContext

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
        self._context = _ChatContext(self._system_prompt)

    def receive_user_message(self, user_message: str) -> str:
        prompt = user_message.strip()
        if not prompt:
            raise ValueError("user_message must not be empty")

        self._context.append(Message(role="user", content=prompt))
        response = self._engine.run_messages(self._context)
        self._context.append(Message(role="assistant", content=response))

        self._context.trim(self._max_turns)

        _logger.debug("Chat turn completed. History size=%d", len(self._context))

        return response

    @property
    def history(self) -> list[Message]:
        return self._context.get_messages()
