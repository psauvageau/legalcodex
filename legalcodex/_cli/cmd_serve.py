from __future__ import annotations

import argparse
import logging
from typing import Final

import uvicorn

from ..exceptions import LCException
from .cli_cmd import CliCmd

_logger = logging.getLogger(__name__)

HOST:Final[str] = "127.0.0.1"
PORT:Final[int] = 8000

class CommandServe(CliCmd):
    title: str = "serve"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--host",
            type=str,
            default=HOST,
            help="Host interface to bind the HTTP server",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=PORT,
            help="Port to bind the HTTP server",
        )
        parser.add_argument(
            "--reload",
            action="store_true",
            help="Enable auto-reload for development",
        )

        parser.add_argument(
            "--workers",
            action="store",
            type=int,
            default=1,
            help="Number of worker processes for handling requests",
        )

    def run(self, args: argparse.Namespace) -> None:
        try:
            _logger.info("Starting HTTP server on %s:%s", args.host, args.port)
            uvicorn.run(
                "legalcodex.http_server.app:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                workers=args.workers,
            )
        except LCException:
            raise
        except Exception as ex:
            _logger.debug("Failed to start HTTP server", exc_info=ex)
            raise LCException("Failed to start HTTP server. Verify host/port and server configuration.") from ex
