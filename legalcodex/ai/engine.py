"""
Represent an abstract AI Engine API
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Literal, Iterable, get_args, cast, Optional
from abc import ABC, abstractmethod


from .._types import JSON_DICT
from ..exceptions import LCValueError

from .message import Message
from .context import Context
from .stream import Stream
from .engines._models import MODELS, DEFAULT_MODEL

_logger = logging.getLogger(__name__)

class Engine(ABC):
    """
    An abstract AI engine interface.

    All specific engine implementations should inherit from this class and implement the run() method.
    They must also have a class attribute NAME which is used to identify the engine type.
    """
    _model  : Final[str]

    def __init__(self, model:Optional[str]=None)->None:
        """
        Initialize the Engine with the given configuration.
        """
        self._model = model or DEFAULT_MODEL
        _logger.info(f"Engine: '{self.name}'")
        _logger.info(f"Model:  '{self._model}'")

    @property
    def name(self)->str:
        """
        Get the name of the engine.
        """
        assert hasattr(self, "NAME"), "Engine subclass must have a NAME class attribute"
        return self.NAME # type: ignore

    @property
    def model(self)->str:
        return self._model

    @abstractmethod
    def run_messages_stream(self, context:Context)->Stream:
        """
        Run the engine with a full conversational context and return a response stream.
        """
        pass
