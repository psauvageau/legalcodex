from typing import Final
import logging




from ..engine import Engine


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


