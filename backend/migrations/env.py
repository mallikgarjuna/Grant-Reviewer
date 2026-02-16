import os
from logging.config import fileConfig
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.engine import engine_from_config

from alembic import context
from sqlmodel import SQLModel

# Import model module so SQLModel metadata is populated.
from app.models import domain  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def _normalize_database_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.strip())
    if parsed.scheme not in {"postgres", "postgresql", "postgresql+psycopg"}:
        return raw_url.strip()

    normalized_scheme = "postgresql+psycopg"
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query_map = dict(query_pairs)
    if "sslmode" not in query_map:
        query_pairs.append(("sslmode", "require"))
    if "connect_timeout" not in query_map:
        query_pairs.append(("connect_timeout", "3"))

    return urlunparse(
        parsed._replace(
            scheme=normalized_scheme,
            query=urlencode(query_pairs),
        )
    )


configured_url = os.getenv("DATABASE_URL", "").strip()
if configured_url:
    config.set_main_option("sqlalchemy.url", _normalize_database_url(configured_url))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
