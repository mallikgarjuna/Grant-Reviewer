# WF-0012 — Alembic Migration Baseline Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-16

## Task Breakdown (Sequential Order)

### Task 1 — Add Alembic dependency and scaffold

Goal:
- Enable Alembic tooling in backend and create baseline scaffold files.

Files to modify:
- `backend/pyproject.toml`
- `backend/uv.lock`
- `backend/alembic.ini`
- `backend/migrations/env.py`
- `backend/migrations/script.py.mako`

Acceptance Criteria:
- Alembic command is available via `uv run alembic`.
- Scaffold files are present under `backend/migrations/`.
- No app runtime behavior outside migration tooling is changed.

Verification Steps:
- `cd backend && uv run alembic --help`
- `cd backend && uv run alembic current`

Risks (if any):
- Version mismatch between lockfile and pyproject may break command execution.

### Task 2 — Wire Alembic env to Postgres and SQLModel metadata

Goal:
- Configure Alembic runtime to use project `DATABASE_URL` and load SQLModel metadata.

Files to modify:
- `backend/migrations/env.py`
- `backend/alembic.ini`

Acceptance Criteria:
- `env.py` imports/targets the application metadata.
- Alembic reads Postgres URL contract without SQLite fallback assumptions.
- Task starts only after Task 1 scaffold exists.

Verification Steps:
- `cd backend && uv run alembic current`
- `cd backend && uv run alembic history --verbose`

Risks (if any):
- Import path setup could fail if env is not aligned with backend module layout.

### Task 3 — Generate and review baseline migration revision

Goal:
- Create the first root revision from current schema and ensure migration content is reviewed before apply.

Files to modify:
- `backend/migrations/versions/<revision>_baseline.py`

Acceptance Criteria:
- Baseline revision exists with `down_revision = None`.
- Migration file accurately reflects current schema intent and has working upgrade/downgrade.
- Revision message clearly indicates baseline intent.

Verification Steps:
- `cd backend && uv run alembic revision --autogenerate -m "baseline schema"`
- Manually inspect generated revision file for correctness and reversibility.

Risks (if any):
- Autogenerate may require manual cleanup for ordering/defaults.

### Task 4 — Validate upgrade/downgrade baseline lifecycle on local Postgres

Goal:
- Prove baseline migration lifecycle works end-to-end on local Postgres.

Files to modify:
- `backend/migrations/versions/<revision>_baseline.py` (if fixes needed)

Acceptance Criteria:
- Baseline applies and rolls back cleanly.
- Final state returns to baseline head.
- Validation is executed on local Postgres only (no production DB operations).

Verification Steps:
- `cd backend && uv run alembic upgrade head`
- `cd backend && uv run alembic downgrade -1`
- `cd backend && uv run alembic upgrade head`
- `cd backend && uv run alembic current`

Risks (if any):
- Existing local DB drift may require local reset/stamp workflow before success.

### Task 5 — Update backend runbook/docs for migration operations

Goal:
- Document exact Postgres-only migration commands and recovery guidance.

Files to modify:
- `backend/README.md` (or existing backend runbook location)

Acceptance Criteria:
- Docs include setup assumptions, baseline command sequence, and troubleshooting for invalid URL/import/drift issues.
- Docs state baseline immutability and no production rollout automation in this WF.
- Commands documented here match commands validated in Task 4.

Verification Steps:
- Review docs for command accuracy against implemented flow.
- Execute documented command sequence once to confirm docs and behavior match.

Risks (if any):
- Documentation drift if command examples diverge from actual config.

### Task 6 — Final verification and WF artifact sync

Goal:
- Close Phase 4-ready planning by capturing final verification checklist and synchronizing WF documentation state.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0012-alembic-migration-baseline.md`
- `docs/logs/decisions.md` (only if new implementation-time decisions are made)

Acceptance Criteria:
- Walkthrough records executed verification commands and outcomes.
- Any implementation decisions discovered during execution are logged in `docs/logs/decisions.md`.
- No new migrations beyond baseline are introduced in this workflow.

Verification Steps:
- `cd backend && uv run alembic history --verbose`
- `cd backend && uv run alembic current`

Risks (if any):
- Skipping logs/walkthrough updates can break WF traceability.

## Changelog

- v0.1 (2026-02-16): Initial task breakdown from PRD
- v0.2 (2026-02-16): Applied task review edits for sequencing clarity and implementation readiness
