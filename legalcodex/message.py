from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, cast, TypeAlias, get_args

from ._types import JSON_DICT

Role            = Literal["system", "user", "assistant", "tool"]
_VALID_ROLES    = frozenset(get_args(Role))

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    def __str__(self) -> str:
        return f"{self.role:12}: {self.content[:60]}"

    def serialize(self) -> JSON_DICT:
        return {"role": self.role, "content": self.content}

    @classmethod
    def deserialize(cls, data: JSON_DICT) -> Message:

        role= data.get("role")
        content = data.get("content")

        if not role in _VALID_ROLES:
            raise ValueError(f"Invalid role in message: {role}")

        if not isinstance(content, str):
             raise ValueError(f"Invalid content type in message: expected str, got {type(content).__name__}")

        return cls(role=cast(Role, role),
            content=cast(str, content))


    @classmethod
    def User(cls, content:str)->Message:
        return Message("user", content)