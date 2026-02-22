import os
import json
from typing import Dict, Any, Generator
import time
import logging

from contextlib import contextmanager

from datetime import datetime, timezone




@contextmanager
def log_timer(name: str)->Generator[None, None, None]:

    start = time.time()
    yield
    end = time.time()

    logger = logging.getLogger("timer")
    logger.debug(f"{name} took {end - start:.2f} seconds")




def serialize_datetime(value: datetime) -> str:
    as_utc = value.astimezone(timezone.utc)
    return as_utc.isoformat().replace("+00:00", "Z")


def parse_datetime(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    value = datetime.fromisoformat(raw)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

