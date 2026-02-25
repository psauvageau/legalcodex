"""
Chat session persistence model.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TypeVar, Type, Optional, Any, Final
from uuid import uuid4

from ...serialization import Serializable
from ...exceptions import LCValueError
from ..._user_access import User, UsersAccess
from ..._misc import serialize_datetime, parse_datetime
from ..._schema import ChatSessionSchema

from ..engine import Engine
from .._engine_selector import ENGINES, DEFAULT_ENGINE
from ..engines._models import MODELS, DEFAULT_MODEL

from .chat_context import ChatContext

_logger = logging.getLogger(__name__)

T = TypeVar("T", bound="ChatSession")

class ChatSession(Serializable[ChatSessionSchema]):
    """
    Represents a persisted chat session with context and engine metadata.
    """

    SCHEMA = ChatSessionSchema


    _uid : Final[str]
    _context: ChatContext
    _user : User
    _created_at: datetime
    _engine: Engine

    def __init__(
        self,
        uid: str,
        context: ChatContext,
        user : User,
        created_at :datetime,
        engine: Engine )->None:

        self._uid = uid
        self._context = context
        self._user = user
        self._created_at = created_at
        self._engine = engine


    @property
    def engine(self)->Engine:
        return self._engine

    @property
    def context(self) -> ChatContext:
        return self._context

    @property
    def username(self) -> str:
        return self._user.username



    def serialize(self) -> ChatSessionSchema:
        data = ChatSessionSchema(
            uid=         self._uid,
            username=    self._user.username,
            created_at = serialize_datetime(self._created_at),
            context = self._context.serialize(),
            engine=self._engine.serialize()
        )
        return data


    @classmethod
    def deserialize(cls: Type[T], data: ChatSessionSchema) -> T:
        user         = UsersAccess.get_instance().find(data.username)
        context      = ChatContext.deserialize(data.context)
        created_at   = parse_datetime(data.created_at)
        engine       = Engine.deserialize(data.engine)

        return cls(uid = data.uid,
                   user=user,
                   context=context,
                   created_at=created_at,
                   engine=engine)

    @classmethod
    def new_chat_session(cls: Type[T],
                         username:str,
                         system_prompt:str,
                         max_messages:int,
                         engine_name: str,
                         model:Optional[str] = None,
                         trim_length:Optional[int] = None) -> T:
        user = UsersAccess.get_instance().find(username)
        context = ChatContext(system_prompt=system_prompt, max_messages=max_messages, trim_length=trim_length)
        created_at = datetime.now(timezone.utc)

        engine = _get_engine(engine_name, model)

        return cls(
            uid=str(uuid4()),
            user=user,
            context=context,
            created_at=created_at,
            engine=engine
        )



def _get_engine(name:Optional[str],
                model:Optional[str])->Engine:

    model = model if model is not None else DEFAULT_MODEL
    engine_name = name if name is not None else DEFAULT_ENGINE

    engine_cls = ENGINES.get(engine_name, None)

    if engine_cls is None:
        raise LCValueError(f"Unknown engine name: {name}")

    if model not in MODELS:
        raise LCValueError(f"Model '{model}' is not available")
    return engine_cls(model=model)


