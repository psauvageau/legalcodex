from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional, Final, TypeVar, Callable, Iterator


from ..engine import Engine
from ..stream import Stream
from ..message import Message

from .chat_context import ChatContext

_logger = logging.getLogger(__name__)




T = TypeVar("T", bound="ChatBehaviour")



StreamCallback = Callable[[str], None]



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

    def send_message(self, user_message: str) -> Stream:
        """
        Send a user message to the engine and get the assistant's response.
         - The user message is appended to the context history.
        """
        prompt = user_message.strip()
        if not prompt:
            raise ValueError("user_message must not be empty")

        self.append_to_context(Message.User(prompt))
        response = self._engine.run_messages_stream(self.context)
        _logger.debug("Chat turn completed. History size=%d", len(self.context))

        return _ChatStream(response, self)

    def append_to_context(self, message: Message)->None:
        """
        Append a message to the context history without sending it to the engine.
        Useful for adding system messages or other information.
        """
        self.context.append(self._engine, message)

    #Used only for testing to inspect the message history
    @property
    def history(self) -> list[Message]:
        return list(self.context.get_messages())


class _ChatStream(Stream):
    def __init__(self, stream: Stream, chat_behaviour: ChatBehaviour):
        self._stream = stream
        self._chat_behaviour = chat_behaviour


    def __iter__(self)-> Iterator[str]:
        chunks:list[str] = []
        try:
            chunk:str
            for chunk in self._stream:
                chunks.append(chunk)
                yield chunk
        finally:
            content = "".join(chunks)
            msg= Message(role="assistant", content=content)
            self._chat_behaviour.append_to_context(msg)
            _logger.debug("Appended assistant message to context: %s", msg)
