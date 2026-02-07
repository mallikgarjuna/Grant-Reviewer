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

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Create all tables defined in domain models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)
