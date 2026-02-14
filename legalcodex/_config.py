from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from typing import Optional

from ._types import JSON_DICT
from ._misc import CONFIG_PATH

DEFAULT_FILE = CONFIG_PATH
DEFAULT_MODEL = "gpt-4.1-mini"





@dataclass(frozen=True)
class Config:
    api_keys: dict[str,str]= field(
        metadata={"help": "API keys for various services"}
    )

    model: str = field(
        default=DEFAULT_MODEL,
        metadata={"help": "LLM Model"}
    )

    @classmethod
    def load(cls, file_name :Optional[str] = None)->Config:
        """
        Load configuration from a JSON file.

        Args:
            file_name (str): Path to the configuration file.

        Returns:
            Config: Loaded configuration.
        """
        file_name = file_name or DEFAULT_FILE
        with open(file_name, "r") as f:
            data = json.load(f)

        return cls(**data)
