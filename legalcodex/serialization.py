import json
from typing import Protocol, Type, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar("T", bound="Serializable")


class Serializable(Protocol):
    """
    Protocol for objects that can be serialized to and deserialized from a Pydantic BaseModel.
     - SCHEMA: A Pydantic BaseModel class that defines the schema for serialization.
    """
    SCHEMA: Type[BaseModel]

    def serialize(self) -> BaseModel:
        """
        Serialize the object to a Pydantic BaseModel for JSON serialization.
        """
        ...

    @classmethod
    def deserialize(cls: Type[T], data: BaseModel) -> T:
        """
        Deserialize a Pydantic BaseModel back into an instance of the class.
        """
        ...


def save(obj:Serializable, filename:str)->None:
    """
    Save a Serializable object to a JSON file.
    """
    data = obj.serialize().model_dump()
    with open(filename, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)

def load(cls: Type[T], filename: str) -> T:
    """
    Load a Serializable object from a JSON file.
    """
    with open(filename, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    return cls.deserialize(cls.SCHEMA.model_validate(data))