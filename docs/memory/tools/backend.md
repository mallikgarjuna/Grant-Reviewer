# Backend Quirks

- **Script Paths:** When running backend scripts, use `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`.
- **Database variables:** `DATABASE_URL` is explicitly required; the backend no longer falls back to SQLite when unset.
