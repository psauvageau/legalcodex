import unittest

from legalcodex._config import Config
from legalcodex.chat.chat_behaviour import ChatBehaviour
from legalcodex.engines.mock_engine import MockEngine


class TestChatBehaviour(unittest.TestCase):
    def setUp(self) -> None:
        config = Config(api_keys={"mock": "unused"})
        self.engine = MockEngine(config)

    def test_initializes_with_system_message(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")

        self.assertEqual(len(behaviour.history), 1)
        self.assertEqual(behaviour.history[0].role, "system")
        self.assertEqual(behaviour.history[0].content, "System prompt")

    def test_receive_user_message_appends_turn_and_returns_response(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")

        response = behaviour.receive_user_message("Hello")

        self.assertIn("MockEngine response #0", response)
        self.assertEqual(len(behaviour.history), 3)
        self.assertEqual(behaviour.history[1].role, "user")
        self.assertEqual(behaviour.history[1].content, "Hello")
        self.assertEqual(behaviour.history[2].role, "assistant")

    def test_reset_keeps_only_system_message(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")
        behaviour.receive_user_message("Hello")

        behaviour.reset()

        self.assertEqual(len(behaviour.history), 1)
        self.assertEqual(behaviour.history[0].role, "system")

    def test_rejects_empty_user_message(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")

        with self.assertRaises(ValueError):
            behaviour.receive_user_message("   ")

    @unittest.skip("Test for history trimming when max_turns is exceeded")
    def test_max_turns_trims_history(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt", max_turns=1)

        behaviour.receive_user_message("first")
        behaviour.receive_user_message("second")

        self.assertEqual(len(behaviour.history), 4)
        self.assertEqual(behaviour.history[0].role, "system")
        self.assertEqual(behaviour.history[1].role, "system")
        self.assertTrue(behaviour.history[1].content.startswith("Conversation summary:"))
        self.assertEqual(behaviour.history[2].content, "second")



if __name__ == "__main__":
    unittest.main()
