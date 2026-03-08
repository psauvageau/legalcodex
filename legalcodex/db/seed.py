"""Seed utilities for initializing LegalCodex demo users in the SQL database.

This module provides a small bootstrap path used during local setup and first
deployment initialization. In project architecture, it prepares baseline user
records, while authentication behavior and user lookup remain in higher-level
access/service modules.
"""

from __future__ import annotations

import logging

from sqlalchemy import select

from .._user_access import AdminSGrp, ChatSGrp, UserSGrp, _hash_password
from .connection import get_session, init_db
from .models import UserModel

_logger = logging.getLogger(__name__)


_DEMO_USERS = [
    {
        "username": "test",
        "password_hash": _hash_password("hello"),
        "security_groups": [str(UserSGrp), str(ChatSGrp)],
    },
    {
        "username": "sauvp",
        "password_hash": _hash_password("hello"),
        "security_groups": [str(AdminSGrp), str(UserSGrp), str(ChatSGrp)],
    },
    {
        "username": "dan",
        "password_hash": _hash_password("ninja"),
        "security_groups": [str(UserSGrp)],
    },
]


def seed_demo_users() -> None:
    """Insert default demo users if they are not already present.

    This function is idempotent: it checks for existing usernames before insert,
    so repeated runs safely maintain seed state without duplicating records.
    """
    init_db()

    with get_session() as session:
        for user_data in _DEMO_USERS:
            username = user_data["username"]
            existing = session.execute(select(UserModel).where(UserModel.username == username)).scalar_one_or_none()
            if existing is not None:
                continue

            session.add(
                UserModel(
                    username=username,
                    password_hash=str(user_data["password_hash"]),
                    security_groups=user_data["security_groups"],
                )
            )
            _logger.info("Seeded demo user: %s", username)


def main() -> None:
    """Run the seeding entrypoint for CLI/module execution.

    This sets logging for operator visibility, executes user seeding, and emits
    a completion message for deployment or local bootstrap workflows.
    """
    logging.basicConfig(level=logging.INFO)
    seed_demo_users()
    _logger.info("Database seeding completed")


if __name__ == "__main__":
    main()
