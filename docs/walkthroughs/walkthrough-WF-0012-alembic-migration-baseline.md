# WF-0012 — Alembic Migration Baseline

Artifact: walkthrough  
Version: v0.1  
Status: Complete  
Last Updated: 2026-02-16

## Summary

WF-0012 established a Postgres-only Alembic migration baseline for the backend, including:
- Alembic dependency + scaffold under `backend/migrations/`
- Alembic metadata wiring to SQLModel models
- Root baseline migration revision
- Baseline lifecycle validation (`upgrade`, `downgrade`, re-`upgrade`)
- Backend runbook updates for migration operations and local drift handling

## Files Implemented

- `backend/pyproject.toml`
- `backend/uv.lock`
- `backend/alembic.ini`
- `backend/migrations/env.py`
- `backend/migrations/script.py.mako`
- `backend/migrations/README`
- `backend/migrations/versions/abf608dc18b6_baseline_schema.py`
- `backend/README.md`

## How To Run

From repo root:

```bash
cd backend
uv run alembic current
uv run alembic history --verbose
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
```

Notes:
- `DATABASE_URL` must target PostgreSQL.
- For local verification, Docker Compose Postgres is the canonical path (`backend/docker-compose.dev.yml`).

## Verification Executed

Task-level verification run during implementation:

1. `cd backend && uv run alembic --help`
2. `cd backend && uv run alembic current`
3. `cd backend && uv run alembic history --verbose`
4. `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_mig_baseline?sslmode=disable' uv run alembic revision --autogenerate -m "baseline schema"`
5. `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_mig_verify2?sslmode=disable' uv run alembic upgrade head`
6. `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_mig_verify2?sslmode=disable' uv run alembic downgrade -1`
7. `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_mig_verify2?sslmode=disable' uv run alembic upgrade head`
8. `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_mig_verify2?sslmode=disable' uv run alembic current`

Observed result:
- Baseline revision `abf608dc18b6` is the single head and is reversible on a fresh Postgres DB.

## Known Limitations

- This WF does not include production migration deployment automation.
- Existing local DBs with drift may need either local reset or `alembic stamp head` (when schema equivalence is confirmed).
- Baseline migration is immutable; follow-up schema changes must use new migration revisions.
