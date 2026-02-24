from __future__ import annotations

from typing import NewType, Optional, Final, cast
from dataclasses import dataclass, asdict, field

from ._types import JSON_DICT
from .exceptions import UserNotFound

from ._schema import UserSchema


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

    def serialize(self) -> UserSchema:
        return UserSchema(
            username=self.username,
            password_hash=self.password_hash,
            security_groups=[sgrp for sgrp in self.security_groups],
        )

    @classmethod
    def deserialize(cls, data: UserSchema) -> User:
        return cls(
            username=data.username,
            password_hash=data.password_hash,
            security_groups=[SGrp(sgrp) for sgrp in data.security_groups],
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, User):
            return NotImplemented
        return (self.username == value.username and
                self.password_hash == value.password_hash and
                self.security_groups == value.security_groups)




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