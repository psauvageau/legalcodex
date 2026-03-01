"""Thread-safe singleton manager for chat sessions."""
from __future__ import annotations
import logging
import threading
from typing import Dict, cast
import os

from ..._misc import get_root_path
from ...exceptions import ChatSessionNotFound
from ..._singleton import Singleton
from .chat_session import ChatSession, ChatSessionId

_logger = logging.getLogger(__name__)




class ChatSessionManager(Singleton):
    """Maintains chat sessions keyed by session id in a thread-safe map."""


    _sessions: Dict[ChatSessionId, ChatSession]

    def __init__(self) -> None:
        _logger.debug("Initializing ChatSessionManager:%s", id(self))
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
        """
        Return the chat session for the given session id.
        raises ChatSessionNotFound if no session exists for the given id.
        """
        session : ChatSession | None = None

        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                _logger.debug("Found chat session in memory", extra={"session_id": session_id})
            else:
                session = _load_session(session_id)
                if session is not None:
                    self._sessions[session_id] = session
                    _logger.debug("Loaded chat session from disk and added to memory", extra={"session_id": session_id})


        if session is None:
            raise ChatSessionNotFound(session_id)
        return session

    def save(self) -> None:
        """Persist all chat sessions to disk under their uid."""

        with self._lock:
            for session in self._sessions.values():
                _save_session(session)
        _logger.debug("Saved chat sessions")

def _save_session(session: ChatSession) -> None:
    """Save a single chat session to disk under its uid."""
    path = get_path()
    os.makedirs(path, exist_ok=True)

    filename = os.path.join(path, f"{session.uid}.json")
    try:
        session.save(filename)
        _logger.debug("Saved chat session to disk", extra={"session_id": session.uid, "path": filename})
    except Exception as err:
        _logger.error(
            "Failed to save chat session",
            extra={"session_id": session.uid, "path": filename, "error": str(err)},
        )

def _load_session(session_id: ChatSessionId) -> ChatSession | None:
    """Load a single chat session from disk by its session id."""
    path = get_path()
    filename = os.path.join(path, f"{session_id}.json")

    if not os.path.isfile(filename):
        return None

    try:
        session = ChatSession.load(filename)
        _logger.debug("Loaded chat session from disk", extra={"session_id": session_id, "path": filename})
        return session

    except Exception as err:
        _logger.error(
            "Failed to load chat session",
            extra={"session_id": session_id, "path": filename, "error": str(err)},
        )
        return None


def get_path() -> str:
    """
    Return the directory where the sessions are stored.
    """
    root_path = get_root_path()
    return os.path.join(root_path, ".chat_sessions")
