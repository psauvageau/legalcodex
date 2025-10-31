from __future__ import annotations

import os
import argparse
import logging

from .cli_cmd import CliCmd

from .._config import Config
from ..engine import Engine, OpenAIEngine

_logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o",  # or "gpt-4", "gpt-3.5-turbo"

class CommandTest(CliCmd):
    title:str = "test"

    def run(self, args:argparse.Namespace)->None:
        config = Config.load(args.config)
        engine  :Engine = OpenAIEngine(config)
        response = engine.run(args.prompt)
        print("Response:")
        print(response)


    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        parser.add_argument('--path', '-p',action="store", type=str, default=None, help='Path to the directory')
        parser.add_argument('prompt', type=str, help='Prompt to send to the model')

