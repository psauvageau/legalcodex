from abc import ABC, abstractmethod
import logging
from typing import Iterable, Type, Iterator

from .._types import JSON_DICT, SerType
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


class SimpleContext(BaseContext):
    """
    Concrete implementation of Context that holds a list of messages.
    """
    _messages: list[Message]

    def __init__(self, messages: Iterable[Message]):
        self._messages = list(messages)

    def get_messages(self) -> Iterable[Message]:
        return self._messages
