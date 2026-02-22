import tempfile
import unittest
from datetime import datetime, timezone

from legalcodex.ai.chat.chat_context import ChatContext
from legalcodex.ai.chat.chat_session import ChatSession
from legalcodex.ai.engines.mock_engine import MockEngine
from legalcodex.ai.message import Message
from legalcodex.exceptions import LCValueError


class TestChatSession(unittest.TestCase):

    def test_serialize_and_deserialize_roundtrip(self) -> None:
        context = ChatContext(system_prompt="System prompt", max_messages=10)
        context.append(engine=MockEngine(), message=Message.User("hello"))

        created_at = datetime(2026, 2, 22, 10, 30, 0, tzinfo=timezone.utc)
        session = ChatSession(
            context=context,
            username="alice",
            engine_name="openai",
            engine_parameters={"model": "gpt-4.1-mini", "temperature": 0.2},
            created_at=created_at,
        )

        data = session.serialize()
        reloaded = ChatSession.deserialize(data)

        self.assertEqual(reloaded.username, "alice")
        self.assertEqual(reloaded.engine_name, "openai")
        self.assertEqual(reloaded.engine_parameters["model"], "gpt-4.1-mini")
        self.assertEqual(reloaded.created_at, created_at)
        self.assertEqual(reloaded.context, context)

    def test_serialize_contains_chat_context_entry(self) -> None:
        context = ChatContext(system_prompt="System prompt", max_messages=10)
        session = ChatSession(
            context=context,
            username="anonymous",
            engine_name="mock",
            engine_parameters={"model": "mock-model"},
        )

        data = session.serialize()

        self.assertIn("chat-context", data)
        self.assertIn("created_at", data)
        self.assertTrue(str(data["created_at"]).endswith("Z"))

    def test_save_and_load_file(self) -> None:
        context = ChatContext(system_prompt="System prompt", max_messages=10)
        context.append(engine=MockEngine(), message=Message.User("question"))

        session = ChatSession(
            context=context,
            username="anonymous",
            engine_name="mock",
            engine_parameters={"model": "mock-model"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/session.json"
            session.save(path)
            loaded = ChatSession.load(path)

        self.assertEqual(loaded.username, session.username)
        self.assertEqual(loaded.engine_name, session.engine_name)
        self.assertEqual(loaded.context, session.context)

    def test_deserialize_invalid_datetime_raises(self) -> None:
        context = ChatContext(system_prompt="System prompt", max_messages=10)
        payload = {
            "username": "anonymous",
            "engine_name": "mock",
            "engine_parameters": {"model": "mock-model"},
            "created_at": "not-a-date",
            "chat-context": context.serialize(),
        }

        with self.assertRaises(LCValueError):
            ChatSession.deserialize(payload)
