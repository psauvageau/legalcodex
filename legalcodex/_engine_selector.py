"""
Engine selector module to manage different engine implementations.
"""

from .engine import Engine
from .engines.openai_engine import OpenAIEngine
from .engines.mock_engine import MockEngine


ENGINES : dict[str, type[Engine]] = {
    OpenAIEngine.NAME: OpenAIEngine,
    MockEngine.NAME: MockEngine,
}


DEFAULT_ENGINE = MockEngine.NAME