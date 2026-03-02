import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from legalcodex.http_server.app import create_app
from legalcodex.ai.chat.chat_session_manager import ChatSessionManager, get_path


class TestChatRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())
        self._clear_sessions()
        self._login()

    def _login(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "test", "password": "hello"},
        )
        self.assertEqual(response.status_code, 204)

    def _clear_sessions(self) -> None:
        manager = ChatSessionManager()
        with manager._lock:
            manager._sessions.clear()

        sessions_path = Path(get_path())
        sessions_path.mkdir(parents=True, exist_ok=True)
        for file in sessions_path.glob("*.json"):
            file.unlink()

    def test_create_session_creates_and_lists_session(self) -> None:
        create_response = self.client.post("/api/v1/chat/sessions", json={})
        self.assertEqual(create_response.status_code, 201)
        session_id = create_response.json()["session_id"]
        self.assertTrue(session_id)

        list_response = self.client.get("/api/v1/chat/sessions")
        self.assertEqual(list_response.status_code, 200)
        session_ids = [item["session_id"] for item in list_response.json()]
        self.assertIn(session_id, session_ids)

    def test_create_session_opens_existing(self) -> None:
        first_response = self.client.post("/api/v1/chat/sessions", json={})
        self.assertEqual(first_response.status_code, 201)
        session_id = first_response.json()["session_id"]

        second_response = self.client.post(
            "/api/v1/chat/sessions", json={"session_id": session_id}
        )
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.json()["session_id"], session_id)

    def test_create_session_missing_returns_404(self) -> None:
        missing_id = str(uuid4())
        response = self.client.post(
            "/api/v1/chat/sessions", json={"session_id": missing_id}
        )
        self.assertEqual(response.status_code, 404)




if __name__ == "__main__":
    unittest.main()
