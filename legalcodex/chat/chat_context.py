"""
Conversation Context.
"""
import logging
from typing import Final, Optional, Iterable, Type, TypeVar

from .._types import JSON_DICT
from ..engine import Engine
from ..message import Message
from ..context import BaseContext
import json
from ..exceptions import ValueError

from .chat_summarizer import summarize_overflow

_logger = logging.getLogger(__name__)

T = TypeVar("T", bound="ChatContext")

class ChatContext(BaseContext):
    """
    ChatContext manages the conversation history and system prompt for a chat session.
    It provides methods to get the full message history, append new messages, and trim the history to
    """
    _system_prompt: Final[Message]  # The system prompt that is always included at the beginning of the message history
    _max_messages: Final[int]       # maximum number of messages to keep in the history before trimming
    _trim_length: Final[int]        # number of messages to remove when trimming the history

    _history: list[Message]         # The main conversation history, excluding the system prompt and summary
    _summary: str                   # A summary of the messages that were removed from the history due to trimming

    def __init__(self,  system_prompt: str,
                        max_messages: int,
                        trim_length:Optional[int]=None) -> None:

        if max_messages <= 4:
            raise ValueError("max_messages must be greater than 4 to allow for trimming")

        self._system_prompt = Message("system", system_prompt.strip())
        self._max_messages = max_messages
        self._trim_length = max(trim_length if trim_length is not None else int(max_messages/2), 1)

        self._history = []
        self._summary = ""

    def reset(self)-> None:
        """
        Reset the conversation context, clearing the history and summary but keeping the system prompt.
        """
        self._history = []
        self._summary = ""


    def get_messages(self) -> Iterable[Message]:
        """
        Return the full message history including the system prompt.
        """
        yield self._system_prompt

        if self._summary:
            yield Message("system", "Summary: " + self._summary)

        yield from self._history

    def append(self, engine: Engine, message: Message) -> None:
        """
        Append a message to the history.
        """
        _logger.debug("Appending message to history: %s", message)
        self._history.append(message)

        if len(self._history) > self._max_messages:
            self._trim(engine)

    def save(self, filename: str) -> None:
        """
        Save the current conversation context to a file.
        """
        _logger.info("Saving chat context to file: %s", filename)
        content = self.serialize()
        as_str = json.dumps(content, indent=2)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(as_str)

    @classmethod
    def load(cls:type[T], filename: str) -> T:
        """
        Load a conversation context from a file.
        """


        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.deserialize(data)


    @classmethod
    def deserialize(cls: Type[T], data: JSON_DICT) -> T:
        """
        Deserialize a conversation context from a JSON dictionary.
        """
        try:
            #TODO: More validation

            system_prompt = Message.deserialize(data["system_prompt"]).content #type: ignore[arg-type]
            max_messages = int(data["max_messages"])                           #type: ignore[arg-type]
            trim_length = int(data["trim_length"])                             #type: ignore[arg-type]
            instance = cls(
                           system_prompt=system_prompt,
                           max_messages=max_messages,
                           trim_length=trim_length)

            instance._summary = str(data["summary"])
            instance._history = [Message.deserialize(msg) for msg in data["history"]] #type: ignore[arg-type, union-attr]

            return instance

        except Exception as err:
            _logger.error("Failed to deserialize context from data: %s", data)
            _logger.exception(err)
            raise ValueError("Failed to deserialize context from data") from err



    def serialize(self) -> JSON_DICT:
        """
        Serialize the context to a JSON-serializable dictionary.
        """
        return {
            "system_prompt" : self._system_prompt.serialize(),
            "max_messages"  : int(self._max_messages),
            "trim_length"     : int(self._trim_length),
            "summary"       : self._summary,
            "history"       : [ msg.serialize() for msg in self._history ]
        }

    def _trim(self, engine:Engine) -> None:
        """
        Trim the message history to the specified maximum number of turns.
        """
        _logger.info("Trimming chat history. Current length=%d, max=%d", len(self._history), self._max_messages)
        try:
            #split the history into the part to keep and the overflow
            overflow = self._history[:self._trim_length]
            keep     = self._history[self._trim_length:]

            assert len(keep) + len(overflow) == len(self._history)
            assert len(keep) >=0 and len(overflow) >= 0

            new_summary = summarize_overflow(engine, self._summary, overflow)

            _logger.debug("History trimmed. Kept %d messages, summarized %d messages into %d chars",
                          len(keep), len(overflow), len(new_summary) if new_summary else 0)

            _logger.debug("New summary content: %s", new_summary)

            self._history = keep
            self._summary = new_summary if new_summary else self._summary



        except Exception as err:
            _logger.error("Failed to summarize overflow; keeping full history")
            _logger.exception(err)
            _logger.warning("Trimming History without summarization. This may lead to loss of important context.")
            self._history = self._history[self._trim_length:]


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChatContext):
            return False

        return (self._system_prompt == other._system_prompt and
                self._max_messages == other._max_messages and
                self._trim_length == other._trim_length and
                self._history == other._history and
                self._summary == other._summary)


    def __len__(self) -> int:
        """
        Return the number of messages in the history (excluding system prompt).
        """
        return len(self._history)