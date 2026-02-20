from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class Stream(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        pass

    def all(self) -> str:
        """
        Collect the entire stream into a single string.
        """
        return "".join(self)
