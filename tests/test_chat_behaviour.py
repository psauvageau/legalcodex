import unittest

from legalcodex._config import Config
from legalcodex.chat.chat_behaviour import ChatBehaviour
from legalcodex.engines.mock_engine import MockEngine
from legalcodex.engine import Engine, Context, Message


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

        response = behaviour.send_message("Hello")

        self.assertIn("MockEngine response #0", response)
        self.assertEqual(len(behaviour.history), 3)
        self.assertEqual(behaviour.history[1].role, "user")
        self.assertEqual(behaviour.history[1].content, "Hello")
        self.assertEqual(behaviour.history[2].role, "assistant")

    def test_reset_keeps_only_system_message(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")
        behaviour.send_message("Hello")

        behaviour.reset()

        self.assertEqual(len(behaviour.history), 1)
        self.assertEqual(behaviour.history[0].role, "system")

    def test_rejects_empty_user_message(self) -> None:
        behaviour = ChatBehaviour(self.engine, system_prompt="System prompt")

        with self.assertRaises(ValueError):
            behaviour.send_message("   ")


    def test_max_turns_trims_history(self) -> None:

        engine = TestEngine(config=None) #type: ignore[arg-type]

        N = 20

        behaviour = ChatBehaviour(engine,
                                  system_prompt="System prompt",
                                  max_turns=N * 2,
                                  )

        self.assertEqual(behaviour._context._summary, "")

        for i in range(N):
            behaviour.send_message(str(i))
        self.assertEqual(engine.count, N)

        # After MAX turns, the history should be trimmed to MAX messages
        behaviour.send_message("Extra message")
        self.assertEqual(engine.count, N + 2) # one for the extra message, one for the summary generation

        self.assertNotEqual(behaviour._context._summary, "")



class TestEngine(Engine):
    NAME = "test"
    count:int = 0
    def run_messages(self, context:Context)->str:
        """
        Return a deterministic response based on the latest user message in context.
        """
        value=  str(self.count)
        self.count += 1
        return value




