# AGENTS.md

## About This Project (2-3 sentences: what it does, who it's for)

Grant Reviewer helps researchers improve grant proposals by generating rubric-grounded feedback on proposal snippets. It ingests funding call definitions (rubrics + proposal structure) and produces structured review cards that are traceable back to rubric expectations.

## Tech Stack (Be specific with versions; should be updated as the project evolves)

- Python: `3.12` (see `backend/.python-version`; backend requires `>=3.12`)
- Node.js: `22.17.0` (for `frontend/`; run `nvm use v22.17.0` before `npm`/`npx` when available)
- Package manager: `uv` (see `backend/uv.lock`)
- Backend deps (see `backend/pyproject.toml`):
  - `openai>=2.17.0`
  - `sqlmodel>=0.0.32`
  - `python-dotenv>=1.2.1`
  - `pyyaml>=6.0.3`
- Dev: `ruff>=0.15.0`
- Database: SQLite (file in `backend/data/`; Postgres-ready later)
- API (planned): FastAPI (see `docs/logs/qa_history.md` / `docs/logs/decisions.md`)

## Git Workflow

- Start each new (major) task in a new branch.
- Default to feature branches + PRs; keep diffs small; avoid drive-by refactors.
- Branch naming: `task-<id>-<short-slug>` (e.g., `task-6.0-llm-integration`).
- PR title/description and commits should reference the task/sub-task ID when applicable.
- Make a commit after each Phase (0–3) with a short descriptive message that includes both the **Task ID** and **what the artifact is about** (e.g., `docs: [8.0] Phase 0 brainstorming - frontend UI + launch architecture`, `docs: [8.0] Phase 1 PRD - frontend MVP scope`).
- During Phase 3 implementation, commit after each completed subtask (e.g., `7.1`, `7.2`, `7.3`) with a short descriptive message tied to that subtask ID.
- Commit messages: use conventional prefixes (`feat:`, `fix:`, `chore:`, `docs:`) and include the ID (e.g., `feat: [6.1.2] ...`).
- Do not commit secrets (`.env`, API keys). Keep `backend/data/*.db` gitignored.

## Key Directories

- `backend/`: application code and scripts
- `docs/`: documentation + task tracking (SSOT: `docs/index.md`)
- If missing, create at minimum: `docs/index.md`, `docs/maintenance.md`, `docs/lessons.md`, `docs/logs/qa_history.md`, `docs/logs/decisions.md`, `docs/logs/prompt_history.md`

## Knowledge Base Maintenance (Always-On)

Use repo-relative paths (don’t require machine-specific `file:///...` links).

- Q&A / clarifications: `docs/logs/qa_history.md` (log conceptual/clarification questions when asked)
- Architectural decisions: `docs/logs/decisions.md`
- Prompt history (datetimestamps): `docs/logs/prompt_history.md`
- Phase 0 brainstorming notes: `docs/brainstorms/brainstorming-[TaskID]-[slug].md`
- Walkthrough per major task (include verification results): `docs/walkthroughs/walkthrough_task_[ID]_[name].md`

Update these immediately after decisions/clarifications (“zero-latency logging”).

## Project Structure (map of the codebase)

```
.
├── backend/
│   ├── app/                 # models/schemas/repos/services
│   ├── scripts/             # seed/ingest/demo utilities
│   └── data/                # call YAML + sqlite db (gitignored)
└── docs/
    ├── index.md             # dashboard (SSOT)
    ├── maintenance.md       # small fixes
    ├── lessons.md           # gotchas
    ├── logs/                # qa_history/decisions/prompt_history
    ├── brainstorms/         # Phase 0 design notes
    ├── reference/           # durable reference docs (domain model, templates, etc.)
    ├── walkthroughs/        # per-task verification notes
    └── tasks/
        ├── active/          # in-flight PRDs + task plans
        └── completed/       # archived PRDs/tasks
```

## Commands (actual executable commands)

From repo root:

- Backend setup: `cd backend && uv sync`
- Configure env: `cd backend && cp .env.example .env` (set `OPENAI_API_KEY`)
- Run review demo (calls OpenAI API): `cd backend && uv run python scripts/run_review.py`
- Validate call YAML (dry run): `cd backend && uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run`
- Ingest call YAML: `cd backend && uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`
- Reset local DB: `cd backend && rm -f data/grant_reviewer.db`
- Lint: `cd backend && uv run ruff check .`
- Lint (autofix): `cd backend && uv run ruff check . --fix`
- Format: `cd backend && uv run ruff format .`

## Product Engineering Pipeline (Phase-Gated for Non‑Trivial Features)

Use for new functional areas, complex refactors, or significant UI/API changes. Skip for small fixes/docs.

**Phase definitions (use these labels everywhere):**
- **Phase 0 = Brainstorming** (ideation/design note in `docs/brainstorms/`)
- **Phase 1 = PRD** (definition in `docs/tasks/active/prd-[TaskID]-*.md`)
- **Phase 2 = Task breakdown** (plan in `docs/tasks/active/task-[TaskID]-*.md`)
- **Phase 3 = Implementation** (execute plan + verify + walkthrough in `docs/walkthroughs/`)

1. Phase 0 (Ideation): brief design note in `docs/brainstorms/`
2. Phase 1 (PRD): `docs/tasks/active/prd-[TaskID]-[feature-name].md`
3. Phase 2 (Plan): `docs/tasks/active/task-[TaskID]-[name].md` + link in `docs/index.md`
4. Phase 3 (Execute/Verify): implement checklist + walkthrough in `docs/walkthroughs/`

Approval gates: ask for an explicit “go ahead” at each phase boundary in interactive work.

Artifact convention:
- Phase artifacts (brainstorming/PRD/task plan/walkthrough) should include a `Status` line with a lightweight version (e.g., `Draft (v0.2 - Revised)` → `Approved (v1.0)`), plus a short `Revision History` section when revised.

### Skills (Optional)

- If a matching skill exists (a `SKILL.md`), follow it for that phase.
- Preferred pipeline skills: `brainstorming` → `prd` → `prd-to-tasks`.
- Skill index (portable): `docs/reference/skills_index.md`.

## Task Lifecycle & Tracking (Source of Truth: `docs/index.md`)

- `docs/index.md` is the SSOT (dashboard linking PRDs, task files, walkthroughs).
- Major tasks: `docs/tasks/active/task-[ID]-[name].md`; PRDs: `docs/tasks/active/prd-[ID]-[name].md`.
- Minor work: append to `docs/maintenance.md`.
- Keep checklists current (`[/]` in-progress, `[x]` done) as you execute.
- Verification: every major task ends with a **Verify** subtask that exercises the full flow.
- Archive completed PRDs/tasks to `docs/tasks/completed/` and immediately fix links in `docs/index.md`.

## Boundaries (subheadings: ### Always; ### Ask first; ### Never)

### Always

- Make the smallest change that works; follow existing patterns.
- Verify with tests/build/lint or a reliable manual repro.
- For Phase 3 implementation, run at least one targeted verification per completed subtask before committing that subtask, and log what was run.
- Before any commit, confirm new/changed files are not accidentally ignored: run `git status --ignored --short`. Prefer updating `.gitignore` with narrow allow/deny rules over `git add -f` (never force-add secrets).
- Update `docs/` as you go (decisions, Q&A, walkthroughs).
- Be explicit about what you didn’t verify and what to run next.
- At the end of every response, explicitly tell/ask the user what to do or prompt next.

### Ask first

- Any ambiguous requirement or behavior change.
- Any change that touches >3 files (split into sub-tasks first).
- Anything that may incur cost or external side effects (e.g., running `scripts/run_review.py` hits the OpenAI API).
- Destructive actions (deleting data, resetting DBs, rewriting git history).
- Adding dependencies, changing the DB schema/migrations, or altering public APIs.

### Never

- Commit secrets or paste sensitive content into `docs/` (or anywhere in the repo).
- Claim verification you didn’t run.
- Introduce large refactors unrelated to the requested change.

## Known Gotchas (### Project-specific gotchas; ### Systemic coordination failures)

Add lessons learned here as you encounter them. Every time the agent does something wrong, add one line to prevent it next time.

Guideline:
- Keep **always-on workflow rules** in this `AGENTS.md`.
- Put **detailed incident writeups + prevention steps** in `docs/lessons.md`, and reference them from here when useful.

### Project-specific gotchas

- Backend scripts importing `app/` may need path setup when run from `backend/scripts/` (see `docs/lessons.md`).
- SQLModel: don’t access ORM objects after session close; capture IDs/primitives first (see `docs/lessons.md`).
- SQLite in-memory DB resets across sessions; design tests to reuse one seeded instance (see `docs/lessons.md`).
- Call YAML naming: `{agency}_{program}_{year}_{stage}.yaml` (see `backend/data/calls/README.md`).
- Don’t forget to update the real project task files (`docs/tasks/active/task-*.md`) and `docs/index.md` while executing (see `docs/lessons.md`).
- Frontend work requires Node tooling; prefer `nvm use v22.17.0` before running `npm`/`npx`. If `nvm` is not available in the current environment, scaffold/build locally and commit the generated `frontend/` files.

### Systemic coordination failures

- Don’t start implementation when the user is still deciding; ask for an explicit “go ahead” when it’s non-trivial.
- Don’t skip phase gates for non-trivial features; keep artifacts (PRD/task/walkthrough) in sync with `docs/index.md`.
- Don’t block MVP progress on pre-existing repo-wide lint debt; enforce lint on changed files/touched modules and track full cleanup as a separate task.
- Before starting the next major task (especially without a remote), create a local integration milestone: merge completed task branches into one branch, tag it, and create a `git bundle` backup.
