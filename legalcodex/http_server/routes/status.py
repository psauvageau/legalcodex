from __future__ import annotations

import logging
from datetime import datetime, timezone
import os

from fastapi import APIRouter

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
def get_status() -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _logger.debug("Received request for /status endpoint: %s", timestamp)
    return {
        "status": "ok",
        "message": "LegalCodex HTTP API server is running",
        "cwd": str(os.getcwd()),
        "timestamp_utc": timestamp,
    }
