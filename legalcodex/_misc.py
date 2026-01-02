import os
import json
from typing import Dict, Any, Generator
from contextlib import contextmanager
import cProfile
import pstats
import datetime

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



@contextmanager
def run_profiler(enable:bool=True)->Generator[None,None,None]:
    if not enable:
        yield
        return
    else:
        DATE_STAMP    = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        PROFILER_PATH = os.path.join(ROOT_PATH, ".work", f"profile_{DATE_STAMP}.stats")
        REPORT_PATH   = os.path.join(ROOT_PATH, ".work", f"profile_{DATE_STAMP}.txt")

        profiler = cProfile.Profile()
        profiler.enable()
        yield
        profiler.disable()
        profiler.dump_stats(PROFILER_PATH)
        # save as text
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            ps = pstats.Stats(profiler, stream=f)
            ps.sort_stats("tottime").print_stats()
