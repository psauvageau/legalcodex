from __future__ import annotations

import os
import argparse
import logging

from .cli_cmd import CliCmd

_logger = logging.getLogger(__name__)

class CommandTest(CliCmd):    
    title:str = "test"

    def run(self, args:argparse.Namespace)->None:
        print("Running test command")
                
    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        parser.add_argument('--path', '-p',action="store", type=str, default=None, help='Path to the directory')

        
        
        

