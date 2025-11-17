import os
import json
from typing import Dict, Any, Generator

import openai

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT_PATH, "config.json")







def dbg_text_to_80_columns(text:str)->Generator[str,None,None]:
    """
    Split text into lines of max 80 columns for debugging output.
    """
    words = text.split()
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= 80:
            if current_line:
                current_line += " "
            current_line += word
        else:
            yield current_line
            current_line = word
    if current_line:
        yield current_line
