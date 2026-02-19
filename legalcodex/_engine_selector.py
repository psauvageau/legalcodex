"""
Engine selector module to manage different engine implementations.
"""
from typing import Type

from .engine import Engine
from .engines.openai_engine import OpenAIEngine
from .engines.mock_engine import MockEngine


ENGINES : dict[str, Type[Engine]] = {
    OpenAIEngine.NAME: OpenAIEngine,
    MockEngine.NAME: MockEngine,
}


DEFAULT_ENGINE = OpenAIEngine.NAME