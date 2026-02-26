"""Thread-safe singleton manager for chat sessions."""

import logging
import threading
from typing import Dict


from ...exceptions import ChatSessionNotFound
from ..._singleton import Singleton
from .chat_session import ChatSession, ChatSessionId

_logger = logging.getLogger(__name__)


class ChatSessionManager(Singleton):
    """Maintains chat sessions keyed by session id in a thread-safe map."""

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
