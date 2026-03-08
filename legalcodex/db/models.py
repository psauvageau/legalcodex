"""
SQLAlchemy ORM models for LegalCodex persistence.

This module defines the database table structure for users, chat sessions, and
chat messages. In project architecture, it is the schema layer used by mapping
and data-access code, while business logic continues to work with domain objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Common ORM base class shared by all LegalCodex database models.

    It provides SQLAlchemy metadata used for table creation and migration tools,
    while model-specific fields are declared in concrete subclasses.
    """
    pass


class UserModel(Base):
    """Persistent representation of an authenticated LegalCodex user.

    This model stores login identity and security-group membership in the SQL
    database; authentication and authorization decisions are handled elsewhere.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    security_groups: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    sessions: Mapped[list[ChatSessionModel]] = relationship(back_populates="user")


class ChatSessionModel(Base):
    """Persistent metadata and context settings for one chat session.

    The row captures session ownership, engine configuration, and summarized
    context state; detailed message history is delegated to `ChatMessageModel`.
    """
    __tablename__ = "chat_sessions"

    uid: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    engine_name: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_model: Mapped[str] = mapped_column(String(128), nullable=False)
    engine_params: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    max_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    trim_length: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")

    user: Mapped[UserModel] = relationship(back_populates="sessions")
    messages: Mapped[list[ChatMessageModel]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessageModel.ordinal",
    )


class ChatMessageModel(Base):
    """Persistent message row belonging to a chat session.

    Each record stores one ordered message (role + content) linked to a session,
    allowing full conversation history reconstruction by mapper/repository code.
    """
    __tablename__ = "chat_messages"
    __table_args__ = (UniqueConstraint("session_uid", "ordinal", name="uq_chat_messages_session_ordinal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_uid: Mapped[str] = mapped_column(
        ForeignKey("chat_sessions.uid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    session: Mapped[ChatSessionModel] = relationship(back_populates="messages")
