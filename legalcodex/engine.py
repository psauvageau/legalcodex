"""
Represent an abstract AI Engine API
"""
import logging
from typing import Optional
from abc import ABC, abstractmethod

from ._config import Config


class Engine(ABC):

    _config : Config

    def __init__(self, config :Optional[Config] )->None:
        """
        Initialize the Engine with the given configuration.
        """
        self._config = config if config is not None else Config()

    @property
    def config(self)->Config:
        """
        Get the engine configuration.
        """
        return self._config




    @abstractmethod
    def run(self, prompt:str)->str:
        """
        Run the engine with the given prompt and return the response.
        """
        pass

