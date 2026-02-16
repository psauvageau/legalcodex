from abc import ABC, abstractmethod
import logging
from typing import Iterable, Type, Iterator

from ._types import JSON_DICT, SerType
from .message import Message

_logger = logging.getLogger(__name__)



Context = Iterable[Message]


class BaseContext(ABC):
    """
    Abstract conversation context passed to engine implementations.
    """

    @abstractmethod
    def get_messages(self)->Iterable[Message]:
        """
        Return provider-agnostic chat messages for the current context.
        """
        pass

    def __iter__(self)->Iterator[Message]:
        """
        Iterate over messages in the context.
        """
        return iter(self.get_messages())


    def serialize(self) -> JSON_DICT:
        """
        Serialize the context to a JSON-serializable dictionary.
        """
        return {"messages": [message.serialize() for message in self.get_messages()]}

    @classmethod
    def deserialize(cls:Type[SerType], data: JSON_DICT) -> SerType:
        """
        Deserialize a context from a JSON dictionary.
        """
        messages_data = data.get("messages")
        if not isinstance(messages_data, list):
            raise ValueError("Invalid context data: 'messages' must be a list")

        messages = []
        for message_data in messages_data:
            if not isinstance(message_data, dict):
                raise ValueError("Invalid context data: each message must be a dict")
            messages.append(Message.deserialize(message_data))

        return cls(messages) # type: ignore


class SimpleContext(BaseContext):
    """
    Concrete implementation of Context that holds a list of messages.
    """
    _messages: list[Message]

    def __init__(self, messages: Iterable[Message]):
        self._messages = list(messages)

    def get_messages(self) -> Iterable[Message]:
        return self._messages
