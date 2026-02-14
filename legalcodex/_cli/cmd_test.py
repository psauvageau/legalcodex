from __future__ import annotations

import os
import argparse
import logging

from .engine_cmd import EngineCommand

from .._config import Config
from ..engine import Engine, Context, Message
from .._engine_selector import ENGINES, DEFAULT_ENGINE

_logger = logging.getLogger(__name__)

_SYSTEM_PROMPT :str = "You are a sarcastic assistant. Please answer in a sarcastic tone, but with helpful answers."

class CommandTest(EngineCommand):
    title:str = "test"

    def run(self, args:argparse.Namespace)->None:
        super().run(args)

        context = ContextTest(args.prompt)
        response = self.engine.run_messages(context)
        print("Response:")
        print(response)


    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        super().add_arguments(parser)
        parser.add_argument('prompt', type=str, help='Prompt to send to the model')



class ContextTest(Context):


    def __init__(self, prompt: str):
        self._messages = [
            Message(role="system", content=_SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]





    def get_messages(self)->list[Message]:
        return self._messages