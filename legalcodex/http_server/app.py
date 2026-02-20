from __future__ import annotations

import logging
from fastapi import FastAPI

from legalcodex.http_server.routes.status import router as status_router

_logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="legalcodex-http-server")
    app.include_router(status_router, prefix="/api/v1")
    return app


app = create_app()
