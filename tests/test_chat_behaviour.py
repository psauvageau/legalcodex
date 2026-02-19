import unittest

from legalcodex._config import Config

from legalcodex.ai.chat.chat_context import ChatContext
from legalcodex.ai.chat.chat_behaviour import ChatBehaviour
from legalcodex.ai.engines.mock_engine import MockEngine
from legalcodex.ai.engine import Engine
from legalcodex.ai.context import Context
from legalcodex.ai.message import Message


class TestChatBehaviour(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MockEngine()

    def test_initializes_with_system_message(self) -> None:
        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        behaviour = ChatBehaviour(self.engine, chat_context)

        self.assertEqual(len(behaviour.history), 1)
        self.assertEqual(behaviour.history[0].role, "system")
        self.assertEqual(behaviour.history[0].content, "System prompt")

    def test_receive_user_message_appends_turn_and_returns_response(self) -> None:
        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        behaviour = ChatBehaviour(self.engine, chat_context)

        response = behaviour.send_message("Hello")

        self.assertEqual("0", response)
        self.assertEqual(len(behaviour.history), 3)
        self.assertEqual(behaviour.history[1].role, "user")
        self.assertEqual(behaviour.history[1].content, "Hello")
        self.assertEqual(behaviour.history[2].role, "assistant")

    def test_reset_keeps_only_system_message(self) -> None:
        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        behaviour = ChatBehaviour(self.engine, chat_context)
        behaviour.send_message("Hello")

        chat_context.reset()

        self.assertEqual(len(behaviour.history), 1)
        self.assertEqual(behaviour.history[0].role, "system")

    def test_rejects_empty_user_message(self) -> None:
        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        behaviour = ChatBehaviour(self.engine, chat_context)

        with self.assertRaises(ValueError):
            behaviour.send_message("   ")


    def test_max_turns_trims_history(self) -> None:

        engine = MockEngine()

        N = 20

        chat_context = ChatContext(system_prompt="System prompt",
                                   max_messages=N * 2,
                                   trim_length=N)

        behaviour = ChatBehaviour(engine, chat_context)

        self.assertEqual(behaviour.context._summary, "")

        for i in range(N):
            behaviour.send_message(str(i))
        self.assertEqual(engine.count, N)

        # After MAX turns, the history should be trimmed to MAX messages
        behaviour.send_message("Extra message")
        self.assertEqual(engine.count, N + 2) # one for the extra message, one for the summary generation

        self.assertNotEqual(behaviour.context._summary, "")



