import unittest
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient

from legalcodex.http_server.app import create_app
from legalcodex.http_server.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM


class TestAuthRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_session_returns_unauthorized_without_cookie(self) -> None:
        response = self.client.get("/api/v1/auth/session")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"authenticated": False})

    def test_session_returns_authenticated_after_login(self) -> None:
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "sauvp", "password": "hello"},
        )
        self.assertEqual(login_response.status_code, 204)

        session_response = self.client.get("/api/v1/auth/session")

        self.assertEqual(session_response.status_code, 200)
        data = session_response.json()
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["username"], "sauvp")
        self.assertIsInstance(data["roles"], list)
        self.assertIn("user", data["roles"])

    def test_root_serves_frontend_index(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("LegalCodex", response.text)

    def test_stylesheet_is_served(self) -> None:
        response = self.client.get("/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.headers.get("content-type", ""))
        self.assertIn("font-family", response.text)

    def test_auth_app_script_is_served_with_javascript_mime_type(self) -> None:
        response = self.client.get("/js/auth-app.js")

        self.assertEqual(response.status_code, 200)
        content_type = response.headers.get("content-type", "")
        self.assertIn("javascript", content_type)
        self.assertIn("createApp", response.text)

    def test_login_success_sets_cookie(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "sauvp", "password": "hello"},
        )

        self.assertEqual(response.status_code, 204)
        set_cookie = response.headers.get("set-cookie", "")
        # JWT token is set (contains dots for header.payload.signature)
        self.assertIn("lc_access=", set_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("SameSite=lax", set_cookie)
        self.assertIn("Path=/api/v1", set_cookie)
        self.assertIn("Max-Age=1800", set_cookie)

        # Extract and verify token is valid JWT
        cookie_value = response.cookies.get("lc_access")
        self.assertIsNotNone(cookie_value)
        # JWT tokens have 3 parts separated by dots
        self.assertEqual(cookie_value.count("."), 2) # type: ignore[union-attr]

    def test_login_failure_returns_unauthorized(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "wrong", "password": "nope"},
        )

        self.assertEqual(response.status_code, 401)

    def test_logout_clears_cookie(self) -> None:
        response = self.client.post("/api/v1/auth/logout")

        self.assertEqual(response.status_code, 204)
        set_cookie = response.headers.get("set-cookie", "")
        self.assertIn("lc_access=", set_cookie)
        self.assertIn("Max-Age=0", set_cookie)
        self.assertIn("Path=/api/v1", set_cookie)
    def test_session_rejects_expired_token(self) -> None:
        """Test that expired tokens are rejected."""
        from datetime import datetime, timedelta

        # Create an expired token
        expired_payload = {
            "sub": "sauvp",
            "roles": ["user"],
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Test with expired token
        response = self.client.get(
            "/api/v1/auth/session",
            cookies={"lc_access": expired_token}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"authenticated": False})

    def test_session_rejects_invalid_token(self) -> None:
        """Test that invalid/tampered tokens are rejected."""
        response = self.client.get(
            "/api/v1/auth/session",
            cookies={"lc_access": "invalid.token.signature"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"authenticated": False})

    def test_session_includes_user_roles(self) -> None:
        """Test that session response includes user roles."""
        # Login first
        self.client.post(
            "/api/v1/auth/login",
            json={"username": "sauvp", "password": "hello"},
        )

        # Check session includes roles
        response = self.client.get("/api/v1/auth/session")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["authenticated"])
        self.assertIn("roles", data)
        self.assertIsInstance(data["roles"], list)