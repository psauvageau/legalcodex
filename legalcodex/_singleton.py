"""Singleton helpers."""

import threading
from typing import Any, Dict
from abc import ABCMeta


class SingletonMeta(ABCMeta):
    """Thread-safe singleton metaclass."""

    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Base class for singleton classes."""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        SingletonMeta._instances.pop(cls, None)
