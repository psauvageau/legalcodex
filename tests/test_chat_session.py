import tempfile
import unittest
from datetime import datetime, timezone
import os

from legalcodex.ai.chat.chat_context import ChatContext
from legalcodex.ai.chat.chat_session import ChatSession
from legalcodex.ai.chat import chat_behaviour

from legalcodex.ai.engines.mock_engine import MockEngine
from legalcodex.ai.message import Message
from legalcodex.exceptions import LCValueError
from legalcodex._user_access import User, UsersAccess
from legalcodex import serialization


MAX_MESSAGES = 10
SYSTEM_PROMPT = "Test System prompt"

class TestChatSession(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        context = ChatContext(system_prompt=SYSTEM_PROMPT, max_messages=MAX_MESSAGES)
        engine = MockEngine()
        user  = UsersAccess.get_instance().find("test")
        created_at = datetime(2026, 2, 22, 10, 30, 0, tzinfo=timezone.utc)

        self.session = ChatSession(
            uid="session-123",
            context=context,
            user=user,
            created_at=created_at,
            engine = engine)

        self.session.context.append(self.session.engine, Message.User("Hello"))


    def test_serialize_and_deserialize_roundtrip(self) -> None:
        data = self.session.serialize()
        reloaded = ChatSession.deserialize(data)
        self._compare(reloaded)

    def test_save_and_load_file(self) -> None:


        with tempfile.TemporaryDirectory(prefix="legalcodex_test_") as tmpdir:
            path = os.path.join(tmpdir, "session.json")
            serialization.save(self.session, path)
            reloaded = serialization.load(ChatSession, path)
        self._compare(reloaded)


    def _compare(self, reloaded: ChatSession) -> None:
        self.assertEqual(reloaded._uid,         self.session._uid)
        self.assertEqual(reloaded._user,        self.session._user)
        self.assertEqual(reloaded.engine.name,  self.session.engine.name)
        self.assertEqual(reloaded.engine.model, self.session.engine.model)
        self.assertEqual(reloaded.context,      self.session.context)
        self.assertEqual(reloaded._created_at,  self.session._created_at)


    def test_receive_user_message_appends_turn_and_returns_response(self) -> None:

        self.session.context.reset()

        stream = chat_behaviour.send_message(self.session, "User0")
        response :str = stream.all()

        self.assertEqual("0", response)

        history = list(self.session.context)


        self.assertEqual(len(history), 3)

        self.assertEqual(history[0].role, "system")
        self.assertEqual(history[0].content, SYSTEM_PROMPT)

        self.assertEqual(history[1].role, "user")
        self.assertEqual(history[1].content, "User0")

        self.assertEqual(history[2].role, "assistant")
        self.assertEqual(history[2].content, "0")


    def test_reset_keeps_only_system_message(self) -> None:

        self.assertEqual(len(list(self.session.context)), 2)

        self.session.context.reset()

        self.assertEqual(len(list(self.session.context)), 1)
        self.assertEqual(list(self.session.context)[0].role, "system")
        self.assertEqual(list(self.session.context)[0].content, SYSTEM_PROMPT)

    def test_rejects_empty_user_message(self) -> None:


        with self.assertRaises(LCValueError):
            chat_behaviour.send_message(self.session, "   ")

    def test_max_turns_trims_history(self) -> None:

        self.session.context.reset()


        self.assertEqual(self.session.context._summary, "")

        N = MAX_MESSAGES//2
        for i in range(N):
            chat_behaviour.send_message(self.session, str(i)).all()

        self.assertEqual(self.session.engine.count, N)
        self.assertEqual(len(list(self.session.context)), MAX_MESSAGES + 1) # N messages + system prompt



        # After MAX turns, the history should be trimmed to MAX messages
        chat_behaviour.send_message(self.session, "Extra message").all()

        self.assertEqual(self.session.engine.count, N + 2) # one for the extra message, one for the summary generation

        self.assertNotEqual(self.session.context._summary, "")




