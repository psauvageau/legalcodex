from __future__ import annotations
from dataclasses import dataclass


from typing import NewType


ChatSessionId = NewType("ChatSessionId", str)



@dataclass(frozen=True)
class ChatSessionInfo:
    session_id: ChatSessionId
    description:str