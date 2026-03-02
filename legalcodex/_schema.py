from datetime import datetime, timezone
from typing import Any, Type, TypeVar, Optional, Final, Protocol, Literal

from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    """
    Schema for user data, including username, password hash, and security groups.
    """
    username: str = Field(..., description="The unique username of the user.")
    password_hash: str = Field(..., description="The hashed password of the user.")
    security_groups: list[str] = Field(..., description="A list of security groups the user belongs to.")

class EngineSchema(BaseModel):
    """
    Configuration schema for an AI engine, including model and other parameters.
    """
    name: str = Field(..., description="The name of the engine to use.")
    model: str = Field(..., description="The name of the model to use for the engine.")
    parameters: Optional[dict[str, str]] = Field(default=None, description="Additional parameters for the engine.")

MessageRole = Literal["system", "user", "assistant", "tool"]

class MessageSchema(BaseModel):
    """
    Schema for a single message in the chat history, including role and content.
    """
    role:    MessageRole = Field(..., description="The role of the message sender (e.g., 'user', 'assistant').")
    content: str  = Field(..., description="The content of the message.")

class ChatContextSchema(BaseModel):
    """
    Schema for the conversational context
    """
    system_prompt : str = Field(..., description="The system prompt that sets the context for the conversation.")
    max_messages  : int = Field(..., description="The maximum number of messages to keep in the history before trimming.")
    trim_length   : int = Field(..., description="The number of messages to remove when trimming the history.")
    summary       : str = Field(..., description="A summary of the messages that were removed from the history due to trimming.")
    history       : list[MessageSchema] = Field(..., description="The main conversation history, excluding the system prompt and summary.")


class ChatSessionSchema(BaseModel):
    """
    Serialization schema for ChatSession using Pydantic.
    """
    uid         : str
    username    : str
    created_at  : str
    context     : ChatContextSchema
    engine      : EngineSchema

    class Config:
        extra = "forbid"


class ChatSessionManagerSchema(BaseModel):
    """Serialization schema for a collection of chat sessions keyed by id."""

    sessions: list[ChatSessionSchema]

    class Config:
        extra = "forbid"
