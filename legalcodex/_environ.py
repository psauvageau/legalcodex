"""
Contains all the environment variables

"""

from typing import Final


# API key
LC_API_KEY :Final[str] = "LC_API_KEY"

LC_ROOT_PATH :Final[str] = "LC_ROOT_PATH"
LC_FRONTEND_PATH :Final[str] = "LC_FRONTEND_PATH"

# JWT secret key for token signing (development fallback in auth_service.py)
LC_JWT_SECRET :Final[str] = "LC_JWT_SECRET"