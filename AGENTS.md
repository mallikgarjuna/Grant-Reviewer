# AGENTS.md

## About This Project (2-3 sentences: what it does, who it's for)

Grant Reviewer helps researchers improve grant proposals by generating rubric-grounded feedback on proposal snippets. It ingests funding call definitions (rubrics + proposal structure) and produces structured review cards that are traceable back to rubric expectations.

## Terminology (researcher-friendly)

- Prefer **“evaluation criteria”** and **“evaluation elements”** over **“rubric”** when communicating with researchers/users (use “rubric” mainly for internal/dev shorthand where helpful).
- When it improves clarity, treat **evaluation** as a synonym for **assessment** or **review** in researcher-facing language (e.g., “assessment criteria”, “review criteria”).
- For consistency and to avoid user confusion, default to **“evaluation criteria”** / **“evaluation elements”** across *all* calls in product/UI copy (even if a specific funder uses “assessment”). Track per-funder wording variations for internal reference only.

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
- Database: PostgreSQL (local Docker + Neon in production)
- API (planned): FastAPI (see `docs/logs/qa_history.md` / `docs/logs/decisions.md`)

## Git Workflow

- For all *new* non-trivial initiatives, use the WF workflow system in `docs/workflow/README.md`.
- **Workflow & Docs Improvements**: For any changes or improvements to the documentation or workflow system itself, always use the dedicated persistent branch: `docs-workflow-changes-improvements`. Push changes to this branch, create a PR to merge into `main` (do NOT delete the branch upon merge), and then sync any active feature branches from `main`.
- Do not retroactively convert legacy task-based artifacts into WF artifacts unless explicitly requested.
- Never commit directly to `main`.
- WF IDs start after the legacy Task IDs (first WF is `WF-0009`; see `docs/index.md`).
- Branch naming (WF): `wf/<WF-ID>-<slug>` (example: `wf/WF-0009-landing-page`).
- Commit messages should start with the WF ID and include the workflow slug (example: `WF-0009: peerlens-landing-page - add landing hero CTA`).
- Keep diffs small; avoid drive-by refactors.
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
- WF brainstorming notes: `docs/brainstorms/brainstorm-<WF-ID>-<slug>.md`
- WF tasks list: `docs/tasks/task-<WF-ID>-<slug>.md`
- WF walkthrough: `docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md`
- Legacy (pre-WF) artifacts remain in `docs/brainstorms/`, `docs/walkthroughs/`, `docs/tasks/`, and `docs/prds/` with their existing Task ID naming.

Update these immediately after decisions/clarifications (“zero-latency logging”).

## Project Structure (map of the codebase)

```
.
├── backend/
│   ├── app/                 # models/schemas/repos/services
│   ├── scripts/             # seed/ingest/demo utilities
│   └── data/                # call YAML fixtures and local data files
└── docs/
    ├── index.md             # dashboard (SSOT)
    ├── maintenance.md       # small fixes
    ├── lessons.md           # gotchas
    ├── logs/                # qa_history/decisions/prompt_history
    ├── workflow/            # WF workflow instructions + prompt templates (SSOT)
    ├── templates/           # WF templates used by workflow phases
    ├── brainstorms/         # brainstorming notes (legacy + WF during migration)
    ├── specs/               # WF specs (pages/features)
    ├── prds/                # PRDs (legacy + WF during migration)
    ├── tasks/               # tasks (legacy + WF during migration)
    ├── walkthroughs/        # walkthrough notes (legacy + WF during migration)
    └── reference/           # durable reference docs (domain model, templates, etc.)
```

## Commands (actual executable commands)

From repo root:

- Backend setup: `cd backend && uv sync`
- Configure env: `cd backend && cp .env.example .env` (set `OPENAI_API_KEY`)
- Run review demo (calls OpenAI API): `cd backend && uv run python scripts/run_review.py`
- Validate call YAML (dry run): `cd backend && uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run`
- Ingest call YAML: `cd backend && uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`
- Reset local DB (Postgres): `cd backend && docker compose -f docker-compose.dev.yml down -v && docker compose -f docker-compose.dev.yml up -d`
- Lint: `cd backend && uv run ruff check .`
- Lint (autofix): `cd backend && uv run ruff check . --fix`
- Format: `cd backend && uv run ruff format .`

## WF Workflow (Idea → Shipped Code)

Use the WF workflow system for non-trivial work:

- Workflow definition (SSOT): `docs/workflow/README.md`
- Chat prompt templates (cheat sheet): `docs/workflow/how-to-use-workflow-actions.md`
- WF artifact filename convention (note singular *task* prefix):
  - `docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`
  - `docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md`
  - `docs/prds/prd-WF-XXXX-<slug>.md`
  - `docs/tasks/task-WF-XXXX-<slug>.md`
  - `docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md`

During migration, legacy task-based artifacts remain in place unless explicitly mapped to a WF ID.

### Skills & Collaboration (Optional)

- If a matching skill exists (a `SKILL.md`), follow it for that phase.
- **Check skills first**: before starting a new type of task, check `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`.
- Preferred pipeline skills: `brainstorming` → `spec` → `prd` → `tasks`.
- Skill index (portable): `docs/reference/skills_index.md`.
- Multi-Agent Collaboration: For the recommended approach to splitting the workflow across Antigravity and VSCode Codex, see `docs/reference/agent_collaboration_strategy.md`.

## Task Lifecycle & Tracking (Source of Truth: `docs/index.md`)

- `docs/index.md` is the dashboard/registry (migration in progress) with two tables: legacy Task IDs and WF IDs.
- Minor work: append to `docs/maintenance.md`.
- Decisions: `docs/logs/decisions.md`.
- When using the WF workflow, follow `docs/workflow/README.md` for artifact paths and status updates.

## Boundaries (subheadings: ### Always; ### Ask first; ### Never)

### Always

- Make the smallest change that works; follow existing patterns.
- Verify with tests/build/lint or a reliable manual repro.
- **Git Hygiene**: Run `pre-commit run --all-files` before committing to ensure clean whitespace and valid config.
- Before starting a new WF phase (or phase runner), ensure the previous phase’s primary artifact(s) are saved and committed (use `git status --short` to confirm a clean boundary).
- After completing a WF phase, ensure any artifacts edited/created in that phase are saved and committed before starting the next phase.
- During phase runners, commit at each part boundary: after Part A outputs, after Part C revisions, and after any Part B edits when applicable (if Part B is no-edit by design, explicitly state no commit needed).
- For Phase 3 implementation, run at least one targeted verification per completed subtask before committing that subtask, and log what was run.
- After writing code, explicitly list potential breakage risks and propose targeted tests that cover those risks.
- For bug fixes, follow test-first debugging: write or update a failing test that reproduces the bug first, then implement the fix until that test passes.
- Before any commit, confirm new/changed files are not accidentally ignored: run `git status --ignored --short`. Prefer updating `.gitignore` with narrow allow/deny rules over `git add -f` (never force-add secrets).
- Update `docs/` as you go (decisions, Q&A, walkthroughs).
- Before pushing any branch to a remote, update `docs/` with all relevant work done on that branch (status/index, decisions, Q&A, prompt history, walkthrough/task artifacts as applicable).
- After each successful push to remote, explicitly print a confirmation that docs/WF artifacts were updated before that push (or explicitly state if none were required).
- **Ship It = PR -> Merge**: To follow industry standards, `ship it` means:
  1. Push feature branch to `origin`.
  2. Create a PR via `gh pr create` with a **descriptive title and body** summarizing what changed, why, and verification results. Do NOT use `--fill` alone — always provide a meaningful PR description.
  3. Merge via `gh pr merge --auto --merge --delete-branch` (or wait for approval if required).
  4. Sync local `main` via `git checkout main && git pull`.
  Local merges are discouraged. **CRITICAL**: Never push, merge, or delete remote branches autonomously. You *must* wait for the user's explicit `ship it` command or permission.
- Be explicit about what you didn’t verify and what to run next.
- At the end of every response, explicitly tell/ask the user what to do or prompt next.
- **Workflow chat hygiene**: Before starting a new WF, explicitly state whether to start a new chat or continue in the current chat; if recommending a new chat, provide a ready-to-paste starting prompt that includes the `pick P[x] #[n]` (or WF ID/slug) and the intended workflow runner/action.
- **Code phrases**: The user has shortcut phrases for frequent actions (see `docs/reference/code_phrases.md`). Key ones: **`park this`** (add to parking lot), **`pick P[x] #[n]`** (promote to WF), **`remember this`** (codify rule in `AGENTS.md` or `docs/lessons.md`), **`log this`** (record in `docs/logs/`), **`status`** / **`what's next`** / **`diff`** / **`verify workflow`** / **`critical review`** / **`workflow preflight`** / **`run phase [N]`** / **`go ahead`** / **`update docs`** / **`docs cleanup`** / **`wrap up`** / **`ship it`**. Recognize and act on these immediately.
- **Composed phrases**: when a phrase overlaps existing ones, execute it as a composition of existing phrase behaviors first (then add only minimal extra checks/reporting).
- When reporting completion of a phase/part/action, explicitly list the files and skills/instructions used for that step.
- For workflow guidance in responses: before Phase 3 completion, present “Next 2 actions” as end-to-end phase runner options (`phase-1-run-prd-definition`, `phase-2-run-tasks-planning`) rather than split part files.
- After Phase 3 is completed, replace “Next 2 actions” with “Next 2 WF ideas/features” phrased as candidate follow-up workflows (with suggested Phase 0.0 starts).

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
- `DATABASE_URL` is required; backend no longer falls back to SQLite when unset.
- Call YAML naming: `{agency}_{program}_{year}_{stage}.yaml` (see `backend/data/calls/README.md`).
- Don’t forget to update the real project task files (`docs/tasks/task-*.md`) and `docs/index.md` while executing (see `docs/lessons.md`).
- Frontend work requires Node tooling; prefer `nvm use v22.17.0` before running `npm`/`npx`. If `nvm` is not available in the current environment, scaffold/build locally and commit the generated `frontend/` files.

### Systemic coordination failures

- Don’t start implementation when the user is still deciding; ask for an explicit “go ahead” when it’s non-trivial.
- Don’t skip phase gates for non-trivial features; keep artifacts (PRD/task/walkthrough) in sync with `docs/index.md`.
- Don’t block MVP progress on pre-existing repo-wide lint debt; enforce lint on changed files/touched modules and track full cleanup as a separate task.
- Before starting the next major task (especially without a remote), create a local integration milestone: merge completed task branches into one branch, tag it, and create a `git bundle` backup.
- Never treat an external agent's `implementation_plan.md` (e.g. Antigravity) as a substitute for WF artifacts (brainstorm/spec/PRD/tasks). Always create and commit proper WF artifacts before writing code.
- When the user explicitly grants self-directed execution for small-scope WFs, proceed through all phases using own best recommendations without waiting for signals. Default: wait for signals at each phase gate.
- Always execute Part A (generate), Part B (review, no edits), and Part C (revise) explicitly in every phase runner — even in self-directed mode. Print PART headers, document findings, and output the traceability statement. No compression into a single step (see `docs/lessons.md` L23).
- **AGENTS.md is the SSOT for project rules and lessons.** Any coding agent (Antigravity, Codex, etc.) must update `AGENTS.md` — never agent-specific files like `GEMINI.md` — for project-level rules. Agent-specific files should reference `AGENTS.md`.
- After promoting a parking lot item to a WF, **renumber** remaining items in that priority tier so `#1` is always the top item. The Promoted Items section preserves the original identity via its WF ID link.
- **Runners are Routers**: When executing a workflow runner (e.g., `run-lifecycle-auto.md`), you **MUST** read and follow the specific steps in the referenced phase file (e.g., `phase-0-0-start-workflow.md`). Do not guess sub-steps from the runner's summary. Using the runner without opening the referenced phase file is a critical failure.
