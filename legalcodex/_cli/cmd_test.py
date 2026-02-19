from __future__ import annotations

import os
import argparse
import logging

from .engine_cmd import EngineCommand

from .._config import Config
from ..ai.engine import Engine
from ..ai.context import Context
from ..ai.message import Message


_logger = logging.getLogger(__name__)

_SYSTEM_PROMPT :str = "You are a sarcastic assistant. Please answer in a sarcastic tone, but with helpful answers."

class CommandTest(EngineCommand):
    title:str = "test"

    def run(self, args:argparse.Namespace)->None:
        super().run(args)

        context = _get_context(args.prompt)
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




def _get_context(prompt:str)->Context:

    return [
            Message(role="system", content=_SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
