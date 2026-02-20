from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
def get_status() -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "status": "ok",
        "timestamp_utc": timestamp,
    }
