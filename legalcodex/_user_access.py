from __future__ import annotations

from typing import NewType, Optional, Final, cast
from dataclasses import dataclass, asdict, field

from ._types import JSON_DICT
from .exceptions import UserNotFound


SGrp = NewType("SGrp", str) # Security Group

PWHash = NewType("PWHash", str) # Password Hash

AdminSGrp : Final[SGrp] = SGrp("admin")
UserSGrp  : Final[SGrp] = SGrp("user")
ChatSGrp  : Final[SGrp] = SGrp("chat")


@dataclass(frozen=True)
class User:
    username: str
    password_hash: str
    security_groups: list[SGrp]

    def serialize(self) -> JSON_DICT:
        return cast(JSON_DICT, asdict(self))

    @classmethod
    def deserialize(cls, data: JSON_DICT) -> User:
        return cls(
            username=data["username"], # type: ignore[arg-type]
            password_hash=data["password_hash"],# type: ignore[arg-type]
            security_groups=[SGrp(sgrp) for sgrp in data["security_groups"]],# type: ignore[union-attr, arg-type]
        )



class UsersAccess:

    _instance = None

    def __init__(self) -> None:
        pass

    @classmethod
    def get_instance(cls) -> UsersAccess:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def find(self, username: str) -> User:
        user = _MOCK_USER_DB.get(username)
        if user is None:
            raise UserNotFound(username)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:

        user = _MOCK_USER_DB.get(username)
        if user and user.password_hash == _hash_password(password):
            return user
        return None




def _hash_password(password:str)->PWHash:
    # Placeholder for password hashing logic
    return PWHash(password)


_USERS :Final[list[User]] = [
    User("test",_hash_password("hello"),[UserSGrp, ChatSGrp]),
    User("sauvp",_hash_password("hello"),[AdminSGrp, UserSGrp, ChatSGrp]),
    User("dan",_hash_password("ninja"),[UserSGrp]),
]

_MOCK_USER_DB : Final[dict[str, User]] = {user.username: user for user in _USERS}