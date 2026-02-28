from __future__ import annotations

from typing import NewType, Optional, Final
from dataclasses import dataclass



SGrp = NewType("SGrp", str) # Security Group

PWHash = NewType("PWHash", str) # Password Hash

AdminSGrp : Final[SGrp] = SGrp("admin")
UserSGrp : Final[SGrp] = SGrp("user")


@dataclass(frozen=True)
class User:
    username: str
    password_hash: str
    security_groups: list[SGrp]





class UsersAccess:

    _instance = None

    def __init__(self) -> None:
        pass

    @classmethod
    def get_instance(cls) -> UsersAccess:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def authenticate(self, username: str, password: str) -> Optional[User]:

        user = _MOCK_USER_DB.get(username)
        if user and user.password_hash == _hash_password(password):
            return user
        return None




def _hash_password(password:str)->PWHash:
    # Placeholder for password hashing logic
    return PWHash(password)


_USERS :Final[list[User]] = [
    User("sauvp",_hash_password("hello"),[AdminSGrp, UserSGrp]),
    User("dan",_hash_password("ninja"),[UserSGrp]),
]

_MOCK_USER_DB : Final[dict[str, User]] = {user.username: user for user in _USERS}