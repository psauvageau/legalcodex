
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel


from ..exceptions import UserNotFound
from .._user_access import UsersAccess, User

from .auth_service import verify_access_token


ACCESS_COOKIE_NAME = "lc_access"




def require_user(request: Request) -> User:
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token_payload = verify_access_token(token)
    if token_payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_access = UsersAccess.get_instance()
    try:
        user = user_access.find(token_payload.username)
        return user
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
