from __future__ import annotations
from typing import Final
import logging

from ..engine import Engine
from ..context import Context
from .._config import Config, MockConfig

_logger = logging.getLogger(__name__)

class MockEngine(Engine):
    """
    A mock engine for testing purposes.
    """
    NAME : Final[str]  = "mock"

    _count:int = 0

    def __init__(self, config:Config=None, model:Optional[str]=None)->None: #type: ignore
        self._count:int = 0
        if config is None:
            config = MockConfig()
        super().__init__(config=config, model=model)

    @property
    def count(self)->int:
        return self._count


    def run_messages(self, context:Context)->str:
        """
        Return a deterministic response based
        on the latest user message in context.
        """
        ctx = list(context)
        _logger.debug("MockEngine received context with %d messages", len(ctx))
        response = str(self._count)
        self._count += 1
        return response

