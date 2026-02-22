"""
Authentication routes for the LegalCodex HTTP server.

    /auth/login
    /auth/logout
    /auth/session
"""
from __future__ import annotations

import logging
import datetime

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..._user_access import UsersAccess
from ..auth_service import create_access_token, verify_access_token, TokenPayload

_logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str




@router.post("/auth/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: LoginRequest, response: Response) -> None:

    user_access = UsersAccess.get_instance()
    user = user_access.authenticate(payload.username, payload.password)

    if user is None:
        _logger.info("Login failed for user: %s", payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Create JWT token with user's roles

    token = create_access_token(
        TokenPayload(user.username, [role for role in user.security_groups]),
        expires_delta = datetime.timedelta(days=1)
    )

    response.set_cookie(
        key="lc_access",
        value=token,
        httponly=True,
        samesite="lax",
        path="/api/v1",
        max_age=1800,  # 30 minutes
    )
    _logger.info("Login succeeded for user: %s with roles: %s", user.username, user.security_groups)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(
        key="lc_access",
        path="/api/v1",
    )
    _logger.info("Logout completed")


@router.get("/auth/session", response_model=None)
def session(request: Request) -> dict[str, bool | str | list[str]] | JSONResponse:
    """
    Check authentication status and return user info if authenticated.

    Returns:
        - 200 with authenticated=true and user details if token is valid
        - 401 with authenticated=false if token is missing or invalid
    """
    token = request.cookies.get("lc_access")

    if not token:
        _logger.debug("Session check: no token cookie")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"authenticated": False}
        )

    try:
        token_payload = verify_access_token(token)
        if token_payload is None:
            _logger.debug("Session check: token payload is None")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"authenticated": False}
            )

        return {
            "authenticated": True,
            "username": token_payload.username,
            "roles": token_payload.roles,
        }

    except jwt.ExpiredSignatureError:
        _logger.info("Session check: token has expired")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"authenticated": False}
        )
    except jwt.InvalidTokenError as e:
        _logger.warning("Session check: invalid token: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"authenticated": False}
        )
