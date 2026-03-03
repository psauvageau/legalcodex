from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from ..._schema import ChatContextSchema
from ..._user_access import User
from ...exceptions import LCException, ChatSessionNotFound
from ...ai.chat import chat_behaviour
from ...ai.chat._chat_types import ChatSessionId
from .._require_user import require_user

_logger = logging.getLogger(__name__)
router = APIRouter()


class CreateSessionRequest(BaseModel):
    session_id: str | None = None
    engine: str | None = None
    model: str | None = None
    max_messages: int | None = None


class MessageRequest(BaseModel):
    message: str


class SessionInfo(BaseModel):
    session_id: str
    description: str | None = None


class MessageResponse(BaseModel):
    response: str





@router.get("/chat/sessions", response_model=list[SessionInfo])
def list_sessions(user: User = Depends(require_user)) -> list[SessionInfo]:
    sessions = chat_behaviour.get_sessions(user)
    return [
        SessionInfo(
            session_id=str(session.session_id),
            description=getattr(session, "description", None),
        )
        for session in sessions
    ]


@router.post("/chat/sessions", status_code=status.HTTP_201_CREATED, response_model=SessionInfo)
def create_session(
    payload: CreateSessionRequest, response: Response, user: User = Depends(require_user)
) -> SessionInfo:
    try:
        if payload.session_id:
            session_id = ChatSessionId(payload.session_id)
            chat_behaviour.open_session(user, session_id)
            description = _find_session_description(session_id, user)
            response.status_code = status.HTTP_200_OK
            return SessionInfo(session_id=str(session_id), description=description)

        session_id = chat_behaviour.new_session(
            user=user,
            max_messages=payload.max_messages,
            engine_name=payload.engine,
            model=payload.model,
        )
        description = _find_session_description(session_id, user)
        response.status_code = status.HTTP_201_CREATED
        return SessionInfo(session_id=str(session_id), description=description)
    except ChatSessionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LCException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/chat/sessions/{session_id}/context", response_model=ChatContextSchema)
def get_context(session_id: str, user: User = Depends(require_user)) -> ChatContextSchema:
    try:
        return chat_behaviour.get_context(ChatSessionId(session_id))
    except LCException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/chat/sessions/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def send_message(
    session_id: str, payload: MessageRequest, user: User = Depends(require_user)
) -> MessageResponse:
    try:
        stream = chat_behaviour.send_message(ChatSessionId(session_id), payload.message)
        response_parts: list[str] = [chunk for chunk in stream]
        return MessageResponse(response="".join(response_parts))
    except LCException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/chat/sessions/{session_id}/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_context(session_id: str, user: User = Depends(require_user)) -> None:
    try:
        chat_behaviour.reset_context(ChatSessionId(session_id))
    except LCException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/chat/sessions/{session_id}/close", status_code=status.HTTP_204_NO_CONTENT)
def close_session(session_id: str, user: User = Depends(require_user)) -> None:
    try:
        chat_behaviour.close_session(ChatSessionId(session_id))
    except ChatSessionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LCException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _find_session_description(session_id: ChatSessionId, user: User) -> str | None:
    for session in chat_behaviour.get_sessions(user):
        if str(session.session_id) == str(session_id):
            return getattr(session, "description", None)
    return None