from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional, Final, TypeVar, Callable, Iterator


from ..._schema import ChatContextSchema
from ..._types import JSON_DICT
from ..._prompts import CHAT_SYSTEM_PROMPT
from ..._user_access import User

from ..stream import Stream
from ..message import Message

from ...ai.engines._models import DEFAULT_MODEL
from ...ai._engine_selector import ENGINES, DEFAULT_ENGINE

from ...exceptions import LCValueError, LCException
from .chat_session import ChatSession
from .chat_session_manager import ChatSessionManager
from ._chat_types import ChatSessionInfo, ChatSessionId


_DEFAULT_MAX_MESSAGES :Final[int] = 20

_logger = logging.getLogger(__name__)

def get_sessions(user:User) -> list[ChatSessionInfo]:
    """
    Get a list of available chat sessions with their descriptions.
    """
    return list(ChatSessionManager().get_sessions(user))


def open_session(user:User, session_id: ChatSessionId) -> None:
    """
    Open a chat session with the given session id or create a new one if no id is provided.
    """
    _logger.debug("Opening chat session: %s", session_id)

    # just try to get the session to ensure it exists, otherwise an exception will be raised
    ChatSessionManager().get_session(session_id)


def close_session(session_id:ChatSessionId)->None:
    """
    Close the chat session with the given session id.
    """
    _logger.debug("Closing chat session: %s", session_id)
    ChatSessionManager().close_session(session_id)


def new_session(user:User,
                max_messages:Optional[int]=None,
                engine_name :Optional[str]=None,
                model       :Optional[str]=None
                )->ChatSessionId:
    """
    Create a new chat session for the given user and return its session id.
    """
    engine_name = engine_name or DEFAULT_ENGINE
    model = model or DEFAULT_MODEL

    _logger.debug("Creating new chat session for user: %s with engine: %s and model: %s", user.username, engine_name, model)

    session:ChatSession = ChatSession.new_chat_session(
            username=user.username,
            system_prompt=CHAT_SYSTEM_PROMPT,
            max_messages=max_messages if max_messages is not None else _DEFAULT_MAX_MESSAGES,
            engine_name=engine_name,
            model=model,
            trim_length=None
        )
    ChatSessionManager().add_session(session)
    return session.uid


def send_message(session_id:ChatSessionId,
                 user_message: str) -> Stream:
    """
    Send a user message to the char and get the assistant's response.
        - The user message is appended to the context history.
    """
    session = ChatSessionManager().get_session(session_id)
    return session.send_message(user_message)



def get_context(session_id:ChatSessionId) -> ChatContextSchema:
    """
    Get the current chat context for the given session id.
    """
    cm :ChatSessionManager = ChatSessionManager()
    session = cm.get_session(session_id)
    return session.context.serialize()


def reset_context(session_id:ChatSessionId) -> None:
    """
    Reset the chat context for the given session id, clearing the history and summary but keeping the system prompt.
    """
    cm :ChatSessionManager = ChatSessionManager()
    session = cm.get_session(session_id)
    return session.context.reset()
