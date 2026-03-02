# Backend Quirks

- **Script Paths:** When running backend scripts, use `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`.
- **Database variables:** `DATABASE_URL` is explicitly required; the backend no longer falls back to SQLite when unset.
- **2026-03-02 — Test/asset guardrails:** DB-backed tests fail-fast unless `DATABASE_URL` DB name contains `test` (local safe default used: `localhost:5433/grant_reviewer_test`); pre-commit blocks newly added files over 500KB.
