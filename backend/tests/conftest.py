"""Pytest safety guards for database isolation."""

from __future__ import annotations

import os
from urllib.parse import urlparse


def _database_name_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path


def _is_test_database_url(url: str) -> bool:
    database_name = _database_name_from_url(url).lower()
    return "test" in database_name


def pytest_runtest_setup(item) -> None:
    """Fail fast when DB tests point at a non-test database."""
    if "no_db" in item.keywords:
        return

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required for DB-backed tests. "
            "Set it to a dedicated test database URL."
        )

    if not _is_test_database_url(database_url):
        raise RuntimeError(
            "Unsafe DATABASE_URL for tests detected. "
            "Refusing to run because database name does not include 'test'. "
            f"Current URL: {database_url}"
        )
