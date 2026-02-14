from typing import Final
import logging




from ..engine import Context, Engine


_logger = logging.getLogger(__name__)



class MockEngine(Engine):
    """
    A mock engine for testing purposes.
    """
    NAME : Final[str]  = "mock"

    _count:int = 0


    def run(self, prompt:str)->str:
        """
        Return a fixed response for testing.
        """
        _logger.debug("MockEngine received prompt: %s", prompt)
        message = f"MockEngine response #{self._count} to prompt: {prompt}"
        self._count += 1
        return message

    def run_messages(self, context:Context)->str:
        """
        Return a deterministic response based on the latest user message in context.
        """
        messages = context.get_messages()
        latest_user_prompt = ""

        for message in reversed(messages):
            if message.role == "user":
                latest_user_prompt = message.content
                break

        return self.run(latest_user_prompt)


