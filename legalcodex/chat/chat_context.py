"""
Conversation Context.
"""
import logging

from typing import Final, Optional
from ..engine import Context, Message, Engine

from .chat_summarizer import summarize_overflow


_logger = logging.getLogger(__name__)




class ChatContext(Context):
    """
    ChatContext manages the conversation history and system prompt for a chat session.
    It provides methods to get the full message history, append new messages, and trim the history to
    """
    _system_prompt: Final[Message]  # The system prompt that is always included at the beginning of the message history
    _history: list[Message]         # The main conversation history, excluding the system prompt and summary

    _summary: str                   # A summary of the messages that were removed from the history due to trimming
    _max_messages: Final[int]       # maximum number of messages to keep in the history before trimming
    _to_remove: Final[int]          # number of messages to remove when trimming the history

    def __init__(self, engine:Engine,
                 system_prompt: str,
                 max_messages: int,
                 trim_length:Optional[int]=None) -> None:
        self._summary = ""
        self._engine = engine
        self._system_prompt = Message("system", system_prompt.strip())
        self._max_messages = max_messages
        self._to_remove = trim_length if trim_length is not None else int(max_messages/2)

        self._history = []


    def get_messages(self) -> list[Message]:
        """
        Return the full message history including the system prompt.
        """
        messages = [self._system_prompt]

        if self._summary:
            messages.append(Message("system", "Summary: " + self._summary))

        messages.extend(self._history)
        return messages

    def append(self, message: Message) -> None:
        """
        Append a message to the history.
        """
        self._history.append(message)

        if len(self._history) > self._max_messages:
            self._trim()

    def _trim(self) -> None:
        """
        Trim the message history to the specified maximum number of turns.
        """
        try:
            #split the history into the part to keep and the overflow
            overflow = self._history[:self._to_remove]
            keep     = self._history[self._to_remove:]

            assert len(keep) + len(overflow) == len(self._history)
            assert len(keep) >=0 and len(overflow) >= 0

            new_summary = summarize_overflow(self._engine, self._summary, overflow)

            self._history = keep
            self._summary = new_summary if new_summary else self._summary

        except Exception as err:
            _logger.exception("Failed to summarize overflow; keeping full history")
            return

    def __len__(self) -> int:
        """
        Return the number of messages in the history (excluding system prompt).
        """
        return len(self._history)