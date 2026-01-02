#type:ignore
import logging

from legalcodex._misc import run_profiler


PROFILER = False
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(levelname)-8s %(module)-15s : %(message)s"

_logger = logging.getLogger()

def main()->None:
    from legalcodex.loaders.tax_code import load_tax_code, TextBlock
    load_tax_code()

def _init_logging():
    format = "%(levelname)-8s %(module)-15s : %(message)s"
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

if __name__ == "__main__":
    _init_logging()
    with run_profiler(enable=PROFILER):
        main()
