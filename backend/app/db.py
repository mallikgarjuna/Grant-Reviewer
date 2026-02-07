"""
Database connection setup for Grant Reviewer.

Uses SQLite file-based database. No migrations yet - tables are created
via SQLModel.metadata.create_all(). Easily swappable to PostgreSQL later.
"""

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

# SQLite file-based database (persists data between runs)
# Database file is stored in backend/data/grant_reviewer.db
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "grant_reviewer.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

# NOTE: check_same_thread=False is required for SQLite with FastAPI/async.
# SQLite by default only allows the thread that created it to use it.
# FastAPI endpoints may run on different threads, so we disable this check.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Create all tables defined in domain models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)
