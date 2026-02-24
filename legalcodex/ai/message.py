from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, cast, TypeAlias, get_args

from .._schema import MessageSchema, MessageRole




@dataclass(frozen=True)
class Message:
    """
    Represents a single message in the chat
    history, including role and content.
    """
    role: MessageRole
    content: str
    def __str__(self) -> str:
        return f"{self.role:12}: {self.content[:60]}"

    def serialize(self) -> MessageSchema:
        return MessageSchema(   role = self.role,
                                content = self.content )

    @classmethod
    def deserialize(cls, data: MessageSchema) -> Message:
        return cls( data.role, data.content)

    @classmethod
    def User(cls, content:str)->Message:
        return Message("user", content)