from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional, Final, TypeVar, Callable, Iterator

from ..stream import Stream
from ..message import Message

from ...exceptions import LCValueError, LCException
from .chat_session import ChatSession


_logger = logging.getLogger(__name__)


def send_message(session:ChatSession, user_message: str) -> Stream:
    """
    Send a user message to the engine and get the assistant's response.
        - The user message is appended to the context history.
    """
    prompt = user_message.strip()
    if not prompt:
        raise LCValueError("user_message must not be empty")

    engine = session.engine
    context = session.context

    message = Message.User(prompt)
    context.append(session.engine, message)

    response = engine.run_messages_stream(context)

    _logger.debug("Chat turn completed. History size=%d", len(context))

    def on_end(content:str)->None:
        message= Message(role="assistant", content=content)
        context.append(engine, message)
        _logger.debug("Appended assistant message to context: %s", message)

    return _ChatStream(response, on_end)




_StreamEndCallback = Callable[[str], None]

class _ChatStream(Stream):
    """
    A wrapper around the engine's response stream with
    a callback for when the stream ends.
    """
    _stream:Optional[Stream]
    _callback: _StreamEndCallback

    def __init__(self, stream: Stream, callback:_StreamEndCallback):
        self._stream = stream
        self._callback = callback

    def __iter__(self)-> Iterator[str]:
        if self._stream is None:
            raise LCException("Stream has already ended")

        chunks:list[str] = []
        try:
            chunk:str
            for chunk in self._stream:
                chunks.append(chunk)
                yield chunk
        finally:
            content = "".join(chunks)
            self._callback(content)
            self._stream = None # Mark stream as ended to prevent further iteration
