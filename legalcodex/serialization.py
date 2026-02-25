from __future__ import annotations
import json
from typing import Protocol, TypeVar, Generic
from typing_extensions import Self
from abc import ABC, abstractmethod

from pydantic import BaseModel

from ._types import JSON_DICT


# Type variable for the Pydantic schema used by a Serializable implementation.
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class Serializable(Generic[SchemaT], ABC):
    """Objects that can round-trip through a Pydantic schema."""

    SCHEMA: type[SchemaT]

    @abstractmethod
    def serialize(self) -> SchemaT:
        ...

    @classmethod
    @abstractmethod
    def deserialize(cls: type[Self], data: SchemaT) -> Self:
        ...


    def to_dict(self) -> JSON_DICT:
        """
        Convert a Serializable object to a JSON-serializable dictionary using its schema.
        """
        return self.serialize().model_dump()

    def save(self, filename: str) -> None:
        """
        Save a Serializable object to a JSON file.
        """
        data = self.to_dict()
        with open(filename, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=2)

    @classmethod
    def from_dict(cls: type[Self], data: JSON_DICT) -> Self:
        """
        Create an instance of a Serializable class from a JSON dictionary using its schema.
        """
        return cls.deserialize(cls.SCHEMA.model_validate(data))


    @classmethod
    def load(cls: type[Self], filename: str) -> Self:
        """
        Load a Serializable object from a JSON file.
        """
        with open(filename, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return cls.from_dict(data)
