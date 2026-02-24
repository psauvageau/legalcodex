"""
Represent an abstract AI Engine API
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Literal, Iterable, get_args, cast, Optional, TypeVar, cast
from abc import ABC, abstractmethod


from .._types import JSON_DICT
from ..exceptions import LCValueError
from .._schema import EngineSchema

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
    DEFAULT : Final[str] = "openai"


    NAME :str # Each subclass must define a unique NAME class attribute to identify the engine type.

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
        return self.NAME

    @property
    def model(self)->str:
        return self._model

    @abstractmethod
    def run_messages_stream(self, context:Context)->Stream:
        """
        Run the engine with a full conversational context and return a response stream.
        """
        pass

    def serialize(self) -> EngineSchema:
        """
        Serialize the Engine instance to a JSON dictionary.
        """
        return EngineSchema(name=self.name, model=self.model, parameters=None)

    @staticmethod
    def deserialize(data: EngineSchema) -> Engine:
        """
        Deserialize an Engine instance from a JSON dictionary.
        """
        try:
            from .engines.mock_engine import MockEngine
            from .engines.openai_engine import OpenAIEngine
            engine_dict :dict[str, type[Engine]] = {
                MockEngine.NAME: MockEngine,
                OpenAIEngine.NAME: OpenAIEngine
            }
            engine_cls = engine_dict[data.name]
            return engine_cls(model=data.model)


        except Exception as e:
            raise LCValueError(f"Failed to deserialize Engine: {e}") from e


