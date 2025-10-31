from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from typing import Optional



from ._misc import CONFIG_PATH

DEFAULT_FILE = CONFIG_PATH
DEFAULT_MODEL = "gpt-4.1-mini"





@dataclass(frozen=True)
class Config:
    api_key: str = field(
        default="",
        metadata={"help": "API key for OpenAI"}
    )

    model: str = field(
        default=DEFAULT_MODEL,
        metadata={"help": "Model to use for OpenAI"}
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


        api_key = data["api_keys"]["openai"]
        model   = data.get("model", DEFAULT_MODEL)

        return cls(api_key, model)


