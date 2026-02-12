"""
Database connection setup for Grant Reviewer.

Uses SQLite file-based database. No migrations yet - tables are created
via SQLModel.metadata.create_all(). Easily swappable to PostgreSQL later.
"""

import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

DEFAULT_DB_DIR = Path(__file__).parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "grant_reviewer.db"
DEFAULT_SQLITE_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"


def normalize_database_url(raw_url: str) -> str:
    """Normalize DATABASE_URL into a SQLAlchemy-compatible connection URL."""
    parsed = urlparse(raw_url.strip())
    normalized_scheme = parsed.scheme
    if parsed.scheme == "postgres":
        normalized_scheme = "postgresql+psycopg"
    elif parsed.scheme == "postgresql":
        normalized_scheme = "postgresql+psycopg"

    if normalized_scheme != "postgresql+psycopg":
        return raw_url.strip()

    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query_map = dict(query_pairs)
    if "sslmode" not in query_map:
        query_pairs.append(("sslmode", "require"))
    if "connect_timeout" not in query_map:
        query_pairs.append(("connect_timeout", "3"))

    normalized_query = urlencode(query_pairs)
    return urlunparse(parsed._replace(scheme=normalized_scheme, query=normalized_query))


def _resolve_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if configured_url:
        return normalize_database_url(configured_url)

    DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_SQLITE_DATABASE_URL


def _build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


DATABASE_URL = _resolve_database_url()
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=_build_connect_args(DATABASE_URL),
)


def create_db_and_tables() -> None:
    """Create all tables defined in domain models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)


def ping_database() -> None:
    """Execute a minimal query to verify DB connectivity."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
