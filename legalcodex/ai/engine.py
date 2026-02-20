"""
Represent an abstract AI Engine API
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Literal, Iterable, get_args, cast, Optional
from abc import ABC, abstractmethod


from .._types import JSON_DICT
from .._config import Config
from ..exceptions import ValueError

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
    _config : Final[Config]
    _model  : Final[str]

    def __init__(self, config: Config, model:Optional[str]=None)->None:
        """
        Initialize the Engine with the given configuration.
        """
        self._config = config
        self._model = _get_model(config, model)
        _logger.info(f"Engine: '{self.name}'")
        _logger.info(f"Model:  '{self._model}'")

    def close(self)->None:
        """
        Clean up any resources used by the engine.
        Override this method if your engine needs to do any cleanup.
        """
        pass

    @property
    def config(self)->Config:
        return self._config

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






def _get_model(config:Config, model:Optional[str])->str:
    """
    Get the model to use from the config,
    applying any necessary defaults or overrides.
    """
    val:str = DEFAULT_MODEL
    if model is not None:
        val = model
    elif config.model is not None:
        val = config.model

    if val not in MODELS:
        raise ValueError(f"Model '{val}' is not supported. Available models: {", ".join(MODELS)}")
    return val