from __future__ import annotations
import sys
import logging
from fastapi import FastAPI

from legalcodex.http_server.routes.status import router as status_router

_logger = logging.getLogger(__name__)

from .._logs import get_log_file_handler, silence_loggers





def create_app() -> FastAPI:
    _init_log(verbose=False)
    _logger.info("Initializing HTTP server application")
    app = FastAPI(title="legalcodex-http-server")
    app.include_router(status_router, prefix="/api/v1")
    return app



def _init_log(verbose:bool=False)->None:
    level = logging.DEBUG if verbose else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    handler = get_log_file_handler(verbose)
    root_logger.addHandler(handler)
    root_logger.addHandler(logging.StreamHandler(sys.stderr))

    silence_loggers()



app = create_app()
