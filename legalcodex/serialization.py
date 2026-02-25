from __future__ import annotations
import json
from typing import Protocol, TypeVar
from typing_extensions import Self

from pydantic import BaseModel

from ._types import JSON_DICT


# Type variable for the Pydantic schema used by a Serializable implementation.
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class Serializable(Protocol[SchemaT]):
    """Objects that can round-trip through a Pydantic schema."""

    SCHEMA: type[SchemaT]

    def serialize(self) -> SchemaT:
        ...

    @classmethod
    def deserialize(cls: type[Self], data: SchemaT) -> Self:
        ...


# Concrete Serializable class type.
C = TypeVar("C", bound="Serializable[BaseModel]")


def to_dict(obj: Serializable[SchemaT]) -> JSON_DICT:
    """
    Convert a Serializable object to a JSON-serializable dictionary using its schema.
    """
    return obj.serialize().model_dump()

def save(obj: Serializable[SchemaT], filename: str) -> None:
    """
    Save a Serializable object to a JSON file.
    """
    data = to_dict(obj)
    with open(filename, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)




def from_dict(cls: type[C], data: JSON_DICT) -> C:
    """
    Create an instance of a Serializable class from a JSON dictionary using its schema.
    """
    return cls.deserialize(cls.SCHEMA.model_validate(data))


def load(cls: type[C], filename: str) -> C:
    """
    Load a Serializable object from a JSON file.
    """
    with open(filename, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    return from_dict(cls, data)
