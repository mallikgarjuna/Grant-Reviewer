"""
Database connection setup for Grant Reviewer.

Uses SQLite in-memory for prototype, easily swappable to PostgreSQL.
"""

from sqlmodel import Session, SQLModel, create_engine

# SQLite in-memory for prototype
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Create all tables defined in domain models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)
