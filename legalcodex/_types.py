"""
General types used across the codebase.
"""
from __future__ import annotations

from typing import Union, Protocol, TypeVar, Type, Protocol

from pydantic import BaseModel

# JSON types used for representing configuration and other data structures.
_JSON_PRIM_VALUE = Union[str, int, float, bool, None]

JSON_LIST  = list["JSON_VALUE"]
JSON_DICT  = dict[str, "JSON_VALUE"]
JSON_VALUE = Union[_JSON_PRIM_VALUE, JSON_LIST, JSON_DICT]




