# Backend

Python backend for Grant Reviewer using SQLModel and FastAPI.

## Tech Stack

- **Python 3.12+**
- **SQLModel** - ORM with Pydantic validation
- **SQLite** - File-based database (PostgreSQL-ready)
- **FastAPI** - REST API (coming soon)
- **UV** - Package manager

## Structure

```
backend/
├── app/
│   ├── models/domain.py     # 11 SQLModel tables
│   ├── schemas/             # Pydantic validation
│   │   └── call_definitions.py  # YAML ingestion schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   │   └── reviewer_service.py  # Core review logic
│   └── db.py                # Database connection
├── scripts/
│   ├── seed.py              # Sample data seeding
│   ├── ingest_call.py       # YAML call ingestion CLI
│   └── run_review.py        # Review demo
├── data/
│   ├── calls/               # YAML call definitions
│   └── grant_reviewer.db    # SQLite database (gitignored)
└── tests/
```

## Setup

```bash
# Install dependencies
uv sync

# Create database tables
uv run python -c "from app.db import create_db_and_tables; create_db_and_tables()"
```

## Scripts

### Ingestion (Admin)

```bash
# Validate a call definition (dry run)
uv run python scripts/ingest_call.py data/calls/sample_erc_call.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/sample_erc_call.yaml
```

### Demo

```bash
# Seed sample data and run review demo
uv run python scripts/seed.py
uv run python scripts/run_review.py
```

## Database

- **Location**: `data/grant_reviewer.db`
- **Type**: SQLite (file-based, persists between runs)
- **Migrations**: Not yet implemented (uses `create_all()`)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required for reviews |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | Optional |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | Optional |

Create a `.env` file (gitignored) for local development.
