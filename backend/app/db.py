"""
Database connection setup for Grant Reviewer.

Uses PostgreSQL via DATABASE_URL. No SQLite fallback.
"""

import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

# Local developer convenience: load `backend/.env` when present.
# In prod, prefer injecting env vars via the deployment environment.
_BACKEND_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if _BACKEND_ENV_PATH.is_file():
    load_dotenv(dotenv_path=_BACKEND_ENV_PATH, override=False)


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
    if not configured_url:
        raise RuntimeError(
            "DATABASE_URL is required. SQLite fallback has been removed; "
            "set DATABASE_URL to a PostgreSQL connection string."
        )
    return normalize_database_url(configured_url)


DATABASE_URL = _resolve_database_url()
engine = create_engine(
    DATABASE_URL,
    echo=False,
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
