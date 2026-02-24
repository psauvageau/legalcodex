from __future__ import annotations
from typing import Final, Optional, Iterator
import logging

from ..engine import Engine
from ..context import Context
from ..stream import Stream
from ._models import DEFAULT_MODEL


_logger = logging.getLogger(__name__)

class MockEngine(Engine):
    """
    A mock engine for testing purposes.
    """
    NAME : str  = "mock"

    _count:int = 0

    def __init__(self, model:str=DEFAULT_MODEL)->None:
        super().__init__(model=model)

    @property
    def count(self)->int:
        return self._count

    def run_messages_stream(self, context:Context)->Stream:
        """
        Return a deterministic response based
        on the latest user message in context.
        """
        ctx = list(context)
        _logger.debug("MockEngine received context with %d messages", len(ctx))
        response = str(self._count)
        self._count += 1
        return _TextStream(response)


class _TextStream(Stream):
    def __init__(self, text:str)->None:
        self._text = text

    def __iter__(self)->Iterator[str]:
        yield self._text

