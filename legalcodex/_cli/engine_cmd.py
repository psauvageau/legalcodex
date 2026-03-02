from __future__ import annotations
from typing import Final, Optional
import argparse
import logging
import os
import json


from ..exceptions import LCException
from .._environ import LC_API_KEY

from ..ai.engine import Engine
from ..ai.engines._models import DEFAULT_MODEL
from ..ai._engine_selector import ENGINES, DEFAULT_ENGINE
from ..ai.stream import Stream

from .cli_cmd import CliCmd

_logger = logging.getLogger(__name__)

class EngineCommand(CliCmd):
    CONFIG_FILE_NAME : Final[str] = "config.json"

    _engine : Optional[Engine] = None

    def run(self, args:argparse.Namespace)->None:
        """
        Run the command logic using the engine.
        """
        assert self._engine is None, "Engine already initialized"
        self._engine  :Engine = ENGINES[args.engine](args.model)
        _logger.info("Initialized engine: %s", self.engine.name)



    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        parser.add_argument('--engine',    '-e',action="store", type=str, default=DEFAULT_ENGINE, choices=ENGINES.keys(), help='Specify the engine to use')
        parser.add_argument('--model',    '-m',action="store", type=str, default=None,  help=f'Specify the model to use; default: {DEFAULT_MODEL}')

    @property
    def engine(self)->Engine:
        """
        Get the initialized engine instance.
        """
        assert self._engine is not None, "Engine not initialized"
        return self._engine


    @classmethod
    def stream_handler(cls, stream:Stream)->None:
        chunks :list[str] = []
        print("AI > ", end="", flush=True)
        for chunk in stream:
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        print()
        _logger.info("Stream complete. Full response: %s", "".join(chunks))

    @classmethod
    def set_api_key(cls)->None:
        try:
            with open("config.json", "r") as file_handle:
                config = json.load(file_handle)
            key = config["openai_key"]
            os.environ[LC_API_KEY] = key
        except Exception as e:
            raise LCException(f"Error loading OpenAI key: {e}") from None
