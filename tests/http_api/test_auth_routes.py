import unittest

from fastapi.testclient import TestClient

from legalcodex.http_server.app import create_app


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
        self.assertEqual(session_response.json(), {"authenticated": True})

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
        self.assertIn("lc_access=GRANTED", set_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("SameSite=lax", set_cookie)
        self.assertIn("Path=/api/v1", set_cookie)

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
