"""Thread-safe singleton manager for chat sessions."""
from __future__ import annotations
import logging
import threading
from typing import Dict, cast


from ...exceptions import ChatSessionNotFound
from ..._singleton import Singleton
from ...serialization import Serializable
from ..._schema import ChatSessionManagerSchema
from .chat_session import ChatSession, ChatSessionId

_logger = logging.getLogger(__name__)


class ChatSessionManager(Singleton, Serializable[ChatSessionManagerSchema]):
    """Maintains chat sessions keyed by session id in a thread-safe map."""

    SCHEMA = ChatSessionManagerSchema
    _sessions: Dict[ChatSessionId, ChatSession]

    def __init__(self) -> None:
        self._sessions = {}
        self._lock = threading.RLock()

    def add_session(self, session: ChatSession) -> None:
        """Add or replace a session keyed by its uid."""
        session_id = session.uid

        with self._lock:
            assert session_id not in self._sessions, f"Session with id {session_id} already exists"
            self._sessions[session_id] = session
            _logger.debug("Registered chat session", extra={"session_id": session_id})

    def get_session(self, session_id:ChatSessionId) -> ChatSession:
        """Return the chat session for the given session id."""
        with self._lock:
            session = self._sessions.get(session_id)

        if session is None:
            raise ChatSessionNotFound(session_id)
        return session

    def serialize(self) -> ChatSessionManagerSchema:
        """Serialize all chat sessions keyed by id."""
        with self._lock:
            data = [ session.serialize() for session in self._sessions.values()]
        return self.SCHEMA(sessions=data)

    @classmethod
    def deserialize(cls, data: ChatSessionManagerSchema) -> ChatSessionManager:
        instance = cls()
        with instance._lock:
            assert len(instance._sessions) == 0, "Deserialization should only be called on a new instance"
            sessions = [ ChatSession.deserialize(session_data) for session_data in data.sessions]
            instance._sessions = { session.uid: session for session in sessions }
        return instance
