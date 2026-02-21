from __future__ import annotations
import sys
import os
import logging
import mimetypes
from typing import Final
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles



_logger = logging.getLogger(__name__)

from .._logs import get_log_file_handler, silence_loggers
from .._environ import LC_FRONTEND_PATH


def create_app() -> FastAPI:

    from legalcodex.http_server.routes.status import router as status_router
    from legalcodex.http_server.routes.auth import router as auth_router

    _init_log(verbose=False)
    _configure_static_mime_types()
    _logger.info("Initializing HTTP server application")
    app = FastAPI(title="legalcodex-http-server")



    @app.get("/")
    def get_frontend_index() -> FileResponse:
        index_path = get_frontend_path() / "index.html"
        _logger.debug("Serving frontend index from: %s", index_path)
        return FileResponse(index_path, media_type="text/html")

    app.include_router(status_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.mount("/", StaticFiles(directory=get_frontend_path()), name="frontend")
    return app


def _configure_static_mime_types() -> None:
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("application/javascript", ".mjs")



def _init_log(verbose:bool=False)->None:
    level = logging.DEBUG if verbose else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level=level)
    handler = get_log_file_handler(verbose)
    root_logger.addHandler(handler)
    root_logger.addHandler(logging.StreamHandler(sys.stderr))

    silence_loggers()



def get_frontend_path() -> Path:
    env_path = os.environ.get(LC_FRONTEND_PATH)
    if env_path:
        path =  Path(env_path)
    else:
        path = Path.cwd() / "frontend"

    if not path.exists():
        _logger.warning("Frontend path does not exist: %s", path)
    return path

app = create_app()
