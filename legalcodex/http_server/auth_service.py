"""
JWT-based authentication service for stateless session management.

This module provides functions for creating and verifying JWT tokens
that encode user identity and roles with automatic expiration.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from .._environ import LC_JWT_SECRET

import jwt

_logger = logging.getLogger(__name__)

# Get JWT secret from environment; fallback to demo secret for development
JWT_SECRET_KEY = os.environ.get(LC_JWT_SECRET, "legalcodex-dev-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

@dataclass(frozen=True)
class TokenPayload:
    """Represents the data encoded in a JWT token."""
    username: str
    roles: list[str]


def create_access_token(
    token_payload :TokenPayload,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT token.

    Args:
        username: User identifier
        roles: List of security group names (e.g., ["user", "admin"])
        expires_delta: Token expiration time (default: 30 minutes)

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_EXPIRATION_MINUTES)

    now = datetime.utcnow()
    exp = now + expires_delta

    payload = {
        "sub": token_payload.username,  # Subject: the user identifier (username)
        "roles": token_payload.roles,   # Custom claim: list of security group names (e.g., ["user", "admin"])
        "exp": exp,       # Expiration Time: when the token becomes invalid (Unix timestamp)
        "iat": now,       # Issued At: when the token was created (Unix timestamp)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    _logger.debug("Created JWT token for user: %s with roles: %s", token_payload.username, token_payload.roles)
    return token


def verify_access_token(token: str) -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.

    Args:
        token: Encoded JWT token string

    Returns:
        TokenPayload if valid, None if invalid or expired

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid/malformed
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        roles = payload.get("roles", [])

        if not username:
            _logger.warning("Token missing 'sub' claim")
            return None

        return TokenPayload(username=username, roles=roles)

    except jwt.ExpiredSignatureError:
        _logger.debug("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        _logger.warning("Invalid token: %s", str(e))
        raise
