from __future__ import annotations
import sys
import logging
from typing import Final
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from legalcodex.http_server.routes.status import router as status_router
from legalcodex.http_server.routes.auth import router as auth_router

_logger = logging.getLogger(__name__)

from .._logs import get_log_file_handler, silence_loggers


FRONTEND_DIR  : Final[Path] = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_INDEX: Final[Path] = FRONTEND_DIR / "index.html"


def create_app() -> FastAPI:
    _init_log(verbose=False)
    _logger.info("Initializing HTTP server application")
    app = FastAPI(title="legalcodex-http-server")



    @app.get("/")
    def get_frontend_index() -> FileResponse:
        _logger.debug("Serving frontend index from: %s", FRONTEND_INDEX)
        return FileResponse(FRONTEND_INDEX, media_type="text/html")

    app.include_router(status_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
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
