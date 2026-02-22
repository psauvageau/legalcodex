"""
Engine selector module to manage different engine implementations.
"""
from typing import Type

from .engine import Engine
from .engines.openai_engine import OpenAIEngine
from .engines.mock_engine import MockEngine


ENGINES : dict[str, Type[Engine]] = {
    OpenAIEngine.NAME:  OpenAIEngine,
    MockEngine.NAME:    MockEngine,
}

def get_engine(name: str, model: str) -> Engine:
    """
    Factory function to create an Engine instance based on the given name and model.
    """
    if name not in ENGINES:
        raise ValueError(f"Unknown engine name: {name}")

    engine_cls = ENGINES[name]
    return engine_cls(model=model)

DEFAULT_ENGINE = OpenAIEngine.NAME
