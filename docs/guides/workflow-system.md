# Workflow System

This guide outlines the standard workflow for all non-trivial initiatives in the Grant Reviewer project.

## WF Workflow (Idea → Shipped Code)

Use the WF workflow system for non-trivial work:

- **Workflow definition (SSOT):** `docs/workflow/README.md`
- **Chat prompt templates (cheat sheet):** `docs/workflow/how-to-use-workflow-actions.md`
- **WF artifact filename convention** (note singular *task* prefix):
  - `docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`
  - `docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md` (detailed brainstorm Q&A transcript)
  - `docs/prds/prd-WF-XXXX-<slug>.md`
  - `docs/tasks/task-WF-XXXX-<slug>.md`
  - `docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md`

During migration, legacy task-based artifacts remain in place unless explicitly mapped to a WF ID.

### Workflow Execution Rules

- **Runners are Routers:** When executing a workflow runner (e.g., `lifecycle-run-auto.md`), you **MUST** read and follow the specific steps in the referenced phase file (e.g., `phase-0-0-start-workflow.md`).
- Before starting a new WF phase (or phase runner), ensure the previous phase’s primary artifact(s) are saved and committed (use `git status --short` to confirm a clean boundary).
- After completing a WF phase, ensure any artifacts edited/created in that phase are saved and committed before starting the next phase.
- During phase runners, commit at each part boundary: after Part A outputs, after Part C revisions, and after any Part B edits when applicable.
- **Self-Directed Mode:** When explicitly granted self-directed execution for small-scope WFs, proceed through all phases using your best recommendations without pausing for a signal at each boundary. **However**, you must *still* execute and print the headers/traceability statements for Part A (generate), Part B (review/no edits), and Part C (revise) in every phase runner. Do not compress them into a single step.

## Task Lifecycle & Tracking

- `docs/index.md` is the dashboard/registry (SSOT) with two tables: legacy Task IDs and WF IDs.
- Minor work: append to `docs/maintenance.md`.
- Decisions: `docs/logs/decisions.md`.
- During Phase 2 task planning, enforce atomic tasks (prefer `<=3` files touched per task) and split aggressively for independent testability.

## Git Workflow

- For all new non-trivial initiatives, use the WF workflow system.
- Branch naming (WF): `wf/<WF-ID>-<slug>` (example: `wf/WF-0009-landing-page`).
- Commit messages should start with the WF ID and include the workflow slug (example: `WF-0009: peerlens-landing-page - add landing hero CTA`).
- **Docs/Workflow Improvements:** Treat documentation or workflow system changes as standard workflows (e.g., `wf/WF-XXXX-update-docs`).
- **No Local Merges:** Local merges are discouraged. Never push, merge, or delete remote branches autonomously. Wait for the user's explicit `ship it` command or permission.
- **Ship It = PR -> Merge**:
  1. Push feature branch to `origin`.
  2. Create a PR via `gh pr create` with a descriptive title and body summarizing what changed, why, and verification results.
  3. Merge via `gh pr merge --auto --merge --delete-branch` (or wait for approval if required).
  4. Sync local `main` via `git checkout main && git pull`.
- Do not commit secrets (`.env`, API keys). Keep `backend/data/*.db` gitignored.

## Skills & Collaboration

- If a matching skill exists (a `SKILL.md`), follow it for that phase.
- **Check skills first**: before starting a new type of task, check `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`.
- Skill index (portable): `docs/reference/skills_index.md`.
- **Code Phrases:** Review `docs/reference/code_phrases.md` for standard phrases like `park this`, `pick P[x] #[n]`, etc. which carry specific semantic meaning in the project.
