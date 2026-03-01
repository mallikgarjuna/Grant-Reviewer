# Testing Isolation & Practice

- **DB Isolation (Tests):** Never run tests against the dev DB. Always isolate them. Tests must run only when `DATABASE_URL` points to a test database whose name includes `test`.
  - Example: `cd backend && docker compose -f docker-compose.test.yml up -d && export DATABASE_URL=...  # match backend/docker-compose.test.yml && uv run pytest`
- **Reset Scripts:** Use `backend/scripts/reset_dev_db.sh` and `backend/scripts/reset_test_db.sh` to get deterministic local state. This is mandatory preflight before QA/testing.
- **Linting vs Legacy:** Enforce strict linting (`ruff`, `mypy`) on *new* code, but use per-file ignores or excludes for legacy code to avoid blocking progress. "Changed-files lint now, full debt cleanup as separate task."
- **Verification Before Commit:** Always require at least one targeted verification (test, lint, build, or manual check) per Phase 3 subtask *before* committing.
- **2026-03-01 — Matrix-driven contracts:** When using a shared fixture matrix across test surfaces, avoid global row-count assertions in one module. Enforce coverage and schema by surface, and ensure PROMPT_ONLY policy tests assert prompt-influence (not just non-blocking behavior).
