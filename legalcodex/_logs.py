import logging
from contextlib import contextmanager
from typing import Generator, Final
import logging.handlers

from ._cli._log_window import log_window

MEGABYTES :Final[int] = 1024 * 1024
FILE_NAME :Final[str] = "lc_server.log"

MAX_SIZE :Final[int] = 1 * MEGABYTES
BACKUP_COUNT :Final[int] = 5


@contextmanager
def init_log(verbose:bool, enable_log_window: bool)->Generator[None, None, None]:
    """
    Initialize the logging configuration.

    Args:
        verbose (bool): If True, set logging level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO

    format = "%(levelname)-8s - %(name)-20s - %(message)s"

    silence_loggers()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if enable_log_window:
        with log_window():
            yield
            input("Press Enter to exit...")
    else:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format))
        root_logger.addHandler(handler)
        try:
            logging.getLogger().info("Logging initialized. Level: %s", logging.getLevelName(level))
            yield
        finally:
            logging.getLogger().removeHandler(handler)



def silence_loggers()->None:
    silence = ["httpx",
               "openai._base_client",
               "google_genai.models",
               "httpcore"]

    for name in silence:
        logging.getLogger(name).setLevel(logging.WARNING)



def get_log_file_handler(verbose: bool)->logging.Handler:
    """
    return a file handler for logging to a file in the local directory
    The log file(s) will be rotated when they
    reach a certain size to prevent them from growing indefinitely.
    """
    level = logging.DEBUG if verbose else logging.INFO
    format = "%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s"

    handler = logging.handlers.RotatingFileHandler(FILE_NAME,
                                                   maxBytes=MAX_SIZE,
                                                   backupCount=BACKUP_COUNT)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format))
    return handler
