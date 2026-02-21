from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from typing import Optional, Final

from ._types import JSON_DICT
from ._misc import CONFIG_PATH
from .ai.engines._models import DEFAULT_MODEL


# Name of the environment variable for the API key
LC_API_KEY :Final[str] = "LC_API_KEY"

DEFAULT_FILE = CONFIG_PATH







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
    def load(cls, file_name :Optional[str])->Config:
        """
        Load configuration from a JSON file.

        Args:
            file_name (str): Path to the configuration file.

        Returns:
            Config: Loaded configuration.
        """

        file_name = file_name or DEFAULT_FILE

        data = get_from_file(file_name)
        if data is None:
            data = get_config()
        assert isinstance(data, dict), "Configuration data must be a dictionary"
        return cls(**data) #type: ignore


class MockConfig(Config):
    """
    A mock configuration for testing purposes.
    """
    def __init__(self) -> None:
        super().__init__(api_keys={"mock": "mock_api_key"})


def get_from_file(file_name: Optional[str]) -> Optional[JSON_DICT]:
    """
    Get the configuration from a file
    """
    file_name = file_name or DEFAULT_FILE

    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f) #type: ignore

    return None


def get_config() -> JSON_DICT:
    """
    Get the configuration from the environment
    """
    api_keys = os.environ[LC_API_KEY]

    data :JSON_DICT =  {
        "api_keys": {
            "openai": api_keys
        },
        "model": "gpt-5-nano"
    }
    return data
