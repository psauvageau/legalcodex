"""
Database connection utilities for LegalCodex.

This module creates and reuses the SQLAlchemy engine and session factory used by
the data-access layer. In project architecture, it is the low-level boundary
between application code and the SQL database connection/pooling details.
It is responsible for engine/session lifecycle and transaction handling via
`get_session()`, while table definitions and record mapping are delegated to
`legalcodex.db.models` and `legalcodex.db.mappers`.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .._environ import LC_DATABASE_URL

_logger = logging.getLogger(__name__)


_DEFAULT_DATABASE_URL = "sqlite:///legalcodex_dev.db"


@lru_cache(maxsize=1)
def get_database_url() -> str:
    """Resolve the database URL from environment with a local-dev fallback.

    This keeps deployment-specific connection details outside application logic
    and centralizes configuration for all DB access in the project.
    """
    return os.getenv(LC_DATABASE_URL, _DEFAULT_DATABASE_URL)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache the shared SQLAlchemy engine.

    In LegalCodex architecture, this is the single entry point for low-level
    database connectivity (connection pool + SQL transport), while queries and
    record shaping are handled by repositories/mappers in other modules.
    """
    database_url = get_database_url()
    _logger.info("Initialising database engine for URL scheme: %s", database_url.split(":", 1)[0])
    return create_engine(database_url, future=True, pool_pre_ping=True)


SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create database tables from ORM metadata when they do not exist.

    This helper is for initialization/bootstrap flows only; schema evolution in
    deployed environments is expected to be managed by migration tooling.
    """
    from .models import Base

    Base.metadata.create_all(bind=get_engine())


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional database session with automatic cleanup.

    Callers use this as a context manager to run DB operations; commit/rollback
    mechanics stay here so service and route code can remain focused on domain
    behavior rather than SQL transaction details.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
