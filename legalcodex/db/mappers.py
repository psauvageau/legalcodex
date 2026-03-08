"""
Domain/ORM mapping helpers for LegalCodex persistence.

This module translates between SQLAlchemy database rows and the project's core
chat/user domain objects so the rest of the application can stay database-agnostic.
It is responsible for shape conversion (including message ordering and engine metadata)
while connection management and table definitions are delegated to
`legalcodex.db.connection` and `legalcodex.db.models`.
"""

from __future__ import annotations

from typing import cast

from .._schema import MessageRole
from .._misc import parse_datetime
from .._user_access import SGrp, User, UsersAccess
from ..ai._engine_selector import ENGINES
from ..ai.chat._chat_types import ChatSessionId
from ..ai.chat.chat_context import ChatContext
from ..ai.chat.chat_session import ChatSession
from ..ai.message import Message

from .models import ChatMessageModel, ChatSessionModel, UserModel


def user_model_to_domain(model: UserModel) -> User:
    """Convert a persisted user row into the LegalCodex `User` domain object.

    This mapper keeps SQL storage details out of authentication and service code,
    which consume only project-level domain types.
    """
    return User(
        username=model.username,
        password_hash=model.password_hash,
        security_groups=[SGrp(value) for value in model.security_groups],
    )


def user_domain_to_model(user: User) -> UserModel:
    """Convert a domain `User` object into the ORM model used for database writes.

    This function limits SQL schema coupling to the mapper layer so higher-level
    modules can keep using stable domain representations.
    """
    return UserModel(
        username=user.username,
        password_hash=user.password_hash,
        security_groups=[str(value) for value in user.security_groups],
    )


def message_model_to_domain(model: ChatMessageModel) -> Message:
    """Translate one stored chat message row into a domain `Message`.

    It normalizes role/content fields so chat logic can operate without direct
    knowledge of SQL table column types.
    """
    return Message(role=MessageRole(model.role), content=model.content)


def message_domain_to_model(session_uid: str, ordinal: int, message: Message) -> ChatMessageModel:
    """Create an ORM chat-message row from a domain `Message`.

    The mapper assigns session linkage and message order, while calling code
    decides transaction scope and persistence timing.
    """
    return ChatMessageModel(
        session_uid=session_uid,
        ordinal=ordinal,
        role=message.role,
        content=message.content,
    )


def session_model_to_domain(model: ChatSessionModel, user: User | None = None) -> ChatSession:
    """Rebuild a full `ChatSession` domain object from persisted session data.

    This includes restoring chat context, ordered history, and engine metadata,
    while user lookup/selection remains delegated to `UsersAccess` when needed.
    """
    domain_user = user if user is not None else UsersAccess.get_instance().find(model.username)

    history = [message_model_to_domain(msg) for msg in sorted(model.messages, key=lambda item: item.ordinal)]
    context = ChatContext(
        system_prompt=model.system_prompt,
        max_messages=model.max_messages,
        trim_length=model.trim_length,
        summary=model.summary,
        history=history,
    )

    engine_cls = ENGINES.get(model.engine_name)
    if engine_cls is None:
        raise ValueError(f"Unknown engine name in DB: {model.engine_name}")

    engine = engine_cls(model=model.engine_model)
    return ChatSession(
        uid=cast(ChatSessionId, model.uid),
        context=context,
        user=domain_user,
        created_at=model.created_at,
        engine=engine,
    )


def session_domain_to_model(session: ChatSession) -> tuple[ChatSessionModel, list[ChatMessageModel]]:
    """Flatten a domain `ChatSession` into ORM session/message models.

    The returned tuple is ready for repository-level upsert logic; this mapper
    handles structure conversion, while DB transaction policy stays elsewhere.
    """
    data = session.serialize()
    context_data = data.context
    engine_data = data.engine

    session_model = ChatSessionModel(
        uid=data.uid,
        username=data.username,
        created_at=parse_datetime(data.created_at),
        engine_name=engine_data.name,
        engine_model=engine_data.model,
        engine_params=engine_data.parameters,
        system_prompt=context_data.system_prompt,
        max_messages=context_data.max_messages,
        trim_length=context_data.trim_length,
        summary=context_data.summary,
    )

    message_models = [
        message_domain_to_model(data.uid, ordinal, Message.deserialize(message))
        for ordinal, message in enumerate(context_data.history)
    ]

    return session_model, message_models
