# Engineering Standards

This guide contains the hard rules for boundaries, verification, testing, and systemic coordination failures to avoid.

## Setup & Commands

All commands should run from the repo root unless `cd backend` is specified.

- Backend setup: `cd backend && uv sync`
- Configure env: `cd backend && cp .env.example .env` (set `OPENAI_API_KEY`)
- Run review demo (calls OpenAI API): `cd backend && uv run python scripts/run_review.py`
- Validate call YAML (dry run): `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_cog_2026_full_official.yaml --dry-run`
- Ingest call YAML: `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_cog_2026_full_official.yaml`
- Reset local DB (Postgres): `cd backend && docker compose -f docker-compose.dev.yml down -v && docker compose -f docker-compose.dev.yml up -d`
- Lint: `cd backend && uv run ruff check .`
- Lint (autofix): `cd backend && uv run ruff check . --fix`
- Format: `cd backend && uv run ruff format .`

## Boundaries (Always / Ask First / Never)

### Always

- Make the smallest change that works; follow existing patterns.
- Verify with tests/build/lint or a reliable manual repro.
- **Git Hygiene**: Run `pre-commit run --all-files` before committing to ensure clean whitespace and valid config.
- Before starting a new WF phase, ensure the previous phase's primary artifact(s) are saved and committed (use `git status --short`).
- For Phase 3 implementation, run at least one targeted verification per completed subtask before committing that subtask, and log what was run.
- After writing code, explicitly list potential breakage risks and propose targeted tests that cover those risks.
- For bug fixes, follow test-first debugging: write or update a failing test that reproduces the bug first, then implement the fix until that test passes.
- Before any commit, confirm new/changed files are not accidentally ignored (`git status --ignored --short`). Prefer updating `.gitignore` with narrow allow/deny rules over `git add -f` (never force-add secrets).
- Update `docs/` as you go (decisions, Q&A, walkthroughs).
- Before pushing any branch to a remote, update `docs/` with all relevant work done on that branch.
- Be explicit about what you didn't verify and what to run next.

### Ask First

- Any ambiguous requirement or behavior change.
- Any change that touches >3 files (split into sub-tasks first).
- Anything that may incur cost or external side effects (e.g., running `scripts/run_review.py` hits the OpenAI API).
- Destructive actions (deleting data, resetting DBs, rewriting git history).
- Adding dependencies, changing the DB schema/migrations, or altering public APIs.

### Never

- Commit secrets or paste sensitive content into `docs/` (or anywhere in the repo).
- Claim verification you didn't run.
- Introduce large refactors unrelated to the requested change.

## Systemic Coordination Failures to Avoid

- **DB isolation for tests is mandatory**: Never run DB-backed backend tests against the dev/local app database. Tests must use a dedicated `DATABASE_URL` containing `test` (e.g., `grant_reviewer_test`) and a separate Docker compose stack (`backend/docker-compose.test.yml`).
- Don't start implementation when the user is still deciding; ask for an explicit "go ahead" when it's non-trivial.
- Don't block MVP progress on pre-existing repo-wide lint debt; enforce lint on changed files/touched modules and track full cleanup as a separate task.
- Never treat an external agent's `implementation_plan.md` as a substitute for WF artifacts (brainstorm/PRD/tasks/walkthrough).
- Always execute Part A, Part B, and Part C explicitly in every phase runner — even in self-directed mode.
- AGENTS.md is the SSOT for project rules and lessons. Any coding agent must update `AGENTS.md` (or the relevant guide in `docs/guides/`) — never agent-specific files like `GEMINI.md`.
- After promoting a parking lot item to a WF, **renumber** remaining items in that priority tier so `#1` is always the top item.
- **Before any manual local app QA after backend tests**: run `backend/scripts/reset_dev_db.sh` to restore canonical local data and avoid seeded-test data leaking into UI checks.
