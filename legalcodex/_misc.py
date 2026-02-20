import os
import json
from typing import Dict, Any, Generator
import time
import logging

from contextlib import contextmanager


import openai



ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT_PATH, "config.json")



@contextmanager
def log_timer(name: str)->Generator[None, None, None]:

    start = time.time()
    yield
    end = time.time()

    logger = logging.getLogger("timer")
    logger.debug(f"{name} took {end - start:.2f} seconds")
