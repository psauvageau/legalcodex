from __future__ import annotations
from typing import Final, Optional
import argparse
import logging


from ..ai.engine import Engine
from ..ai._engine_selector import ENGINES, DEFAULT_ENGINE
from .._config import Config

from .cli_cmd import CliCmd



_logger = logging.getLogger(__name__)

class EngineCommand(CliCmd):


    _engine : Optional[Engine] = None

    def run(self, args:argparse.Namespace)->None:
        """
        Run the command logic using the engine.
        """
        assert self._engine is None, "Engine already initialized"
        config = Config.load(args.config)

        self._engine  :Engine = ENGINES[args.engine](config, args.model)

        _logger.info("Initialized engine: %s", self.engine.name)



    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        parser.add_argument('--engine',    '-e',action="store", type=str, default=DEFAULT_ENGINE, choices=ENGINES.keys(), help='Specify the engine to use')
        parser.add_argument('--model',    '-m',action="store", type=str, default=None,  help='Open the log window')

    @property
    def engine(self)->Engine:
        """
        Get the initialized engine instance.
        """
        assert self._engine is not None, "Engine not initialized"
        return self._engine

