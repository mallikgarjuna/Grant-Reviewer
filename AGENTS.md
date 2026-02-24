# Agent Instructions (AGENTS.md)

**Grant Reviewer** generates evaluation-criteria-grounded feedback on proposal snippets by ingesting funding call definitions and producing structured review cards traceable to evaluation criteria expectations.

## ⚠️ Core Directives for Agents

**Keep this file short and link elsewhere.** Only add rules here after an AI failure, using 1-3 lines of minimal context.
**Surprises:** If you encounter unexpected project behavior or think a new rule is needed here, **alert the developer** first.

## Quick Reference & Links

- **Tech Stack:** Python `3.12` (manager: `uv`), Node.js `22.17.0` (manager: `npm`).
- **Terminology:** Default to **"evaluation criteria"** or **"evaluation elements"** instead of "rubric" in all researcher-facing language (canonical definition: `backend/app/schemas/call_definitions_v2.py`).
- **Workflow / SSOT:** `docs/index.md` is the Source of Truth for task tracking. Tasks go in `docs/tasks/`.

**Deep-Dive Guides (Read these before coding):**
- [Workflow System (`docs/guides/workflow-system.md`)](docs/guides/workflow-system.md) - How WF phases work, branch naming, and artifact management.
- [Engineering Standards (`docs/guides/engineering-standards.md`)](docs/guides/engineering-standards.md) - Testing boundaries, DB isolation, setup commands, and pull request requirements.
- [Knowledge Base & Structure (`docs/guides/knowledge-base.md`)](docs/guides/knowledge-base.md) - Repository map and zero-latency logging rules.

## Project Gotchas

*(Added here because previous agents failed on them)*

- **Backend script paths:** Scripts importing `app/` need Python path setup. Example: `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`
- **SQLModel sessions:** Don't access ORM objects after session close; capture IDs/primitives first.
- **Database variables:** `DATABASE_URL` is required; backend no longer falls back to SQLite when unset.
- **DB Isolation (Tests):** DB isolation for tests is mandatory. Example: `cd backend && docker compose -f docker-compose.test.yml up -d && DATABASE_URL="postgresql://grant:grant@localhost:5433/grant_reviewer_test" uv run pytest`
- **Call YAML naming:** `{agency}_{program}_{year}_{stage}.yaml`.
- **Frontend Tools:** Frontend work requires Node tooling; prefer `nvm use v22.17.0` before running `npm`/`npx`. If `nvm` is not available, scaffold/build locally and commit the generated `frontend/` files.
