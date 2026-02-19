import unittest

from legalcodex.ai.engine import Engine
from legalcodex.ai.message import Message
from legalcodex.ai.chat.chat_context import ChatContext
from legalcodex.ai.engines.mock_engine import MockEngine




class TestChatContext(unittest.TestCase):




    def test_initializes_with_system_message(self) -> None:


        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)


        messages = list(chat_context.get_messages())

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, "system")
        self.assertEqual(messages[0].content, "System prompt")


    def test_reset_keeps_only_system_message(self) -> None:


        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        chat_context.append(engine=MockEngine(), message=Message(role="user", content="Hello"))

        chat_context.reset()

        messages = list(chat_context.get_messages())

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, "system")

    def test_get_messages_includes_system_prompt(self) -> None:


        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        chat_context.append(engine=MockEngine(), message=Message(role="user", content="Hello"))

        messages = list(chat_context.get_messages())

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "system")
        self.assertEqual(messages[0].content, "System prompt")
        self.assertEqual(messages[1].role, "user")
        self.assertEqual(messages[1].content, "Hello")

    def test_append_trims_history_when_exceeding_max_messages(self) -> None:
        engine = MockEngine()
        N = 10
        T = 7
        chat_context = ChatContext(system_prompt="System prompt",
                                   max_messages=N,
                                   trim_length=T)

        for i in range(N):
            chat_context.append(engine, Message.User(f"Message {i}"))
        self.assertEqual(len(chat_context._history), N)
        self.assertEqual(engine.count, 0)
        self.assertEqual(chat_context._summary,"")

        chat_context.append(engine, Message.User(f"Message {i}"))

        self.assertEqual(engine.count, 1)
        self.assertNotEqual(chat_context._summary,"")
        self.assertEqual(len(chat_context._history), N - T + 1)



        a=0


        #self.assertEqual(len(chat_context._history), N * 2 - N + 1)




    def test_serialize_and_deserialize(self) -> None:

        engine = MockEngine()


        chat_context = ChatContext(system_prompt="System prompt", max_messages=10)
        for i in range(5):
            chat_context.append(engine=engine, message=Message.User(str(i)))

        data = chat_context.serialize()
        new_context = ChatContext.deserialize(data)

        self.assertEqual(chat_context, new_context)
