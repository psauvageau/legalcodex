from __future__ import annotations

import os
import argparse
import logging

from .engine_cmd import EngineCommand

from .._config import Config
from ..engine import Engine
from .._engine_selector import ENGINES, DEFAULT_ENGINE

_logger = logging.getLogger(__name__)

class CommandTest(EngineCommand):
    title:str = "test"

    def run(self, args:argparse.Namespace)->None:
        super().run(args)

        response = self.engine.run(args.prompt)
        print("Response:")
        print(response)


    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        super().add_arguments(parser)
        parser.add_argument('prompt', type=str, help='Prompt to send to the model')
