from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

_logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str




@router.post("/auth/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: LoginRequest, response: Response) -> None:
    if payload.username != "sauvp" or payload.password != "hello":
        _logger.info("Login failed for user: %s", payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    response.set_cookie(
        key="lc_access",
        value="GRANTED",
        httponly=True,
        samesite="lax",
        path="/api/v1",
    )
    _logger.info("Login succeeded for user: %s", payload.username)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(
        key="lc_access",
        path="/api/v1",
    )
    _logger.info("Logout completed")


@router.get("/auth/session", response_model=None)
def session(request: Request) -> dict[str, bool] | JSONResponse:
    access = request.cookies.get("lc_access")
    if access == "GRANTED":
        return {"authenticated": True}

    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"authenticated": False})
