# Agent Instructions (AGENTS.md)

**Grant Reviewer**: evaluation-criteria-grounded feedback on proposal snippets; outputs review cards traceable to evaluation criteria expectations.

## ⚠️ Core Directives for Agents

**Keep this file tiny; link SSOT.** Add rules only after an AI failure (1-3 lines).
**Surprises:** unexpected behavior or new rule idea -> alert developer first.
**Style (this file):** extreme concision; sacrifice grammar.

## Quick Reference & Links

- **SSOT tasks:** use `docs/index.md`; add tasks under `docs/tasks/`. (Trigger: any work request.)
- **Terms:** say **evaluation criteria/elements** (not "rubric") in researcher-facing text; canonical: `backend/app/schemas/call_definitions_v2.py`. (Trigger: UI/docs/copy.)
- **Runtime:** Python `3.12` (see `backend/.python-version`, `uv`), Node `22.17.0` (see `.nvmrc`, `npm`). (Trigger: env/tooling issues.)
- **Code phrases:** `verify workflow` = run verification pass; `workflow preflight` = check WF closure readiness. (Trigger: user says phrase.)

**Read these only if needed:**
- WF phases/branches/artifacts -> `docs/guides/workflow-system.md`
- tests/DB/migrations/setup/PR rules -> `docs/guides/engineering-standards.md`
- repo map/KB/zero-latency logging -> `docs/guides/knowledge-base.md`

## Project Gotchas

*(Added here because previous agents failed on them)*

- **Backend script paths:** `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`
- **SQLModel sessions:** Don't access ORM objects after session close; capture IDs/primitives first.
- **Database variables:** `DATABASE_URL` is required; backend no longer falls back to SQLite when unset.
- **DB Isolation (Tests):** never run tests against dev DB. Example: `cd backend && docker compose -f docker-compose.test.yml up -d && export DATABASE_URL=...  # match backend/docker-compose.test.yml && uv run pytest`
- **Call YAML naming:** `{agency}_{program}_{year}_{stage}.yaml`.
- **Frontend Tools:** `nvm use` (uses `.nvmrc`) before `npm/npx`. No `nvm` -> scaffold/build locally; commit generated `frontend/`.
