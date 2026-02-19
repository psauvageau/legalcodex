"""
General types used across the codebase.
"""
from typing import Union, Protocol, TypeVar, Type

# JSON types used for representing configuration and other data structures.
_JSON_PRIM_VALUE = Union[str, int, float, bool, None]

JSON_LIST  = list["JSON_VALUE"]
JSON_DICT  = dict[str, "JSON_VALUE"]
JSON_VALUE = Union[_JSON_PRIM_VALUE, JSON_LIST, JSON_DICT]

SerType = TypeVar("SerType", bound="Serializable")

class Serializable(Protocol):
    """
    Protocol for objects that can be serialized to and deserialized from JSON-compatible dictionaries.
    """
    def serialize(self) -> JSON_DICT:
        ...

    @classmethod
    def deserialize(cls:Type[SerType], data: JSON_DICT) -> SerType:
        ...


