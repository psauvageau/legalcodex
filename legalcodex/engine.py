"""
Represent an abstract AI Engine API
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Literal, Iterable, get_args, cast
from abc import ABC, abstractmethod


from ._types import JSON_DICT
from ._config import Config
from .exceptions import ValueError
from .message import Message
from .context import Context

_logger = logging.getLogger(__name__)













class Engine(ABC):
    """
    An abstract AI engine interface.

    All specific engine implementations should inherit from this class and implement the run() method.
    They must also have a class attribute NAME which is used to identify the engine type.
    """
    _config : Final[Config]

    def __init__(self, config: Config)->None:
        """
        Initialize the Engine with the given configuration.
        """
        self._config = config


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



    @abstractmethod
    def run_messages(self, context:Context)->str:
        """
        Run the engine with a full conversational context and return the response.
        """
        pass
