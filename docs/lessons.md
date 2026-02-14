# Project Lessons

## Stage 3 Learnings

### L1: sys.path for Script Imports
**Issue**: `ModuleNotFoundError` when running scripts from `/backend/scripts/`.
**Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent))` at top of scripts.
**Prevention**: Always add path manipulation in scripts that import from `app/`.

### L2: SQLModel Session Lifecycle
**Issue**: `DetachedInstanceError` when accessing entity attributes after `session.close()`.
**Fix**: Capture IDs into a dict before closing session.
**Prevention**: Never access model attributes after session is closed.

### L3: In-Memory DB Persistence
**Issue**: SQLite in-memory DB resets when new session is created, causing UNIQUE constraint errors on re-seed.
**Fix**: Don't re-seed; reuse existing session for related tests.
**Prevention**: Design tests to share one seeded database instance.

### L4: Call Definition Filename Convention
**Convention**: `{agency}_{program}_{year}_{stage}.yaml`
**Example**: `erc_cog_2026_full.yaml`, `nwo_vici_2026_pre.yaml`
**Reference**: See `backend/data/calls/README.md` for full documentation.

### L5: Task File Updates During Execution
**Issue**: Updated internal artifact `task.md` but forgot to update the project task file `docs/tasks/task-X.0-*.md`.
**Fix**: After each subtask completion, update the project task file (not just internal artifacts).
**Prevention**: Always update `docs/tasks/task-X.0-*.md` with `[x]` checkmarks as subtasks complete. Also update `docs/index.md` when task status changes.

### L6: Brainstorming Log Naming Convention
**Issue**: Brainstorming logs were created without a task ID in the filename.
**Fix**: Rename brainstorming log files to include the task ID.
**Prevention**: For each major task, name Phase 0 brainstorming logs like `docs/brainstorms/brainstorming-[TaskID]-[slug].md`.

### L7: Phase 3 Commit Granularity
**Issue**: Phase 3 implementation progressed without commits at each completed subtask boundary (e.g., `7.1`, `7.2`).
**Fix**: Commit after each completed Phase 3 subtask with a short, scoped message that includes the subtask ID.
**Prevention**: Treat each subtask as a commit checkpoint during implementation; avoid batching multiple completed subtasks into one commit.

### L8: Commit After Each Pipeline Phase (with Task ID)
**Issue**: Work crossed Phase boundaries (Phase 0 → 1 → 2 → 3) without a clear commit checkpoint tied to the Task ID.
**Fix**: Create one commit after each Phase artifact is completed (Phase 0 brainstorming log, Phase 1 PRD, Phase 2 task plan, Phase 3 implementation + walkthrough).
**Prevention**: Use commit messages that include the Task ID (and subtask ID when relevant) plus a brief description of what the phase artifact covers, e.g. `docs: [8.0] Phase 0 brainstorming - frontend UI + launch architecture`, `docs: [8.0] Phase 1 PRD - frontend MVP scope`, `docs: [8.0] Phase 2 plan - implementation tasks`, `feat: [8.0] Phase 3 - implement frontend MVP`.

### L9: Don’t Let Legacy Lint Debt Block MVP
**Issue**: Repo-wide lint checks include large pre-existing debt and can stall feature delivery.
**Fix**: For MVP-focused work, enforce lint on changed files/touched modules and keep full debt cleanup in a dedicated follow-up task.
**Prevention**: Treat repo-wide lint remediation as planned maintenance (separate task/phase), not as a blocker for unrelated MVP feature slices.

### L10: Wrap Up Locally Before Next Major Task (No Remote)
**Issue**: Multiple local task branches can drift without a clear integration checkpoint when no GitHub remote/PR flow exists.
**Fix**: Create a local milestone branch from `main`, merge completed task branches, add a milestone tag, and create a `git bundle` backup.
**Prevention**: Before starting each new major task, complete a local wrap-up checkpoint so rollback and task handoff remain predictable.

### L11: Keep IDE Workspace File Local
**Issue**: `Grant-Reviewer.code-workspace` changes are local-user preferences and create noisy branch status.
**Fix**: Mark it as local-only with `git update-index --skip-worktree Grant-Reviewer.code-workspace`.
**Prevention**: Use `skip-worktree` for tracked, machine-local workspace config files unless an intentional shared update is required.

### L12: Local Runtime Verification vs Codex Sandbox Verification
**Issue**: Static checks passed in Codex, but runtime browser/server flows (`/app` auth redirects, end-to-end submit flow) could not be reliably validated inside sandbox constraints.
**Fix**: Add a single local verification entrypoint (`scripts/verify_local_8_0A.sh`) that runs automated checks first and then prints a required manual browser checklist.
**Prevention**: For frontend runtime features, explicitly separate "sandbox/static verification" from "local runtime verification" in task + walkthrough artifacts.

### L13: Next.js 16 Clerk Route Protection Convention
**Issue**: Using deprecated/misplaced middleware conventions caused auth-related runtime failures and confusion around route protection.
**Fix**: Use `frontend/src/proxy.ts` with `clerkMiddleware` and explicit route matchers for `/app/*` and `/api/bff/*`.
**Prevention**: For new Next.js versions, follow current framework conventions (`proxy.ts`) and avoid stale middleware patterns from older examples.

### L14: Backend `.env` Loading for Local Uvicorn
**Issue**: Running `uvicorn main:app --reload` did not automatically load `backend/.env`, causing missing secret/config errors (notably `BFF_SHARED_SECRET`).
**Fix**: Load `backend/.env` from `backend/main.py` using `load_dotenv(..., override=False)`.
**Prevention**: Ensure local entrypoints load expected env files safely, while preserving production precedence for injected environment variables.

### L15: Shared Secret Alignment Across Frontend and Backend
**Issue**: `Generate Review` failed with signature verification errors when frontend and backend had mismatched or missing `BFF_SHARED_SECRET`.
**Fix**: Document and enforce a single shared secret value in both `frontend/.env.local` and `backend/.env`.
**Prevention**: Treat cross-service secrets as paired configuration and verify alignment early in local setup.

### L16: Merge-and-Tag Milestone Before New Major Task
**Issue**: Starting a new major task from an unmerged feature branch increases drift, complicates rollback, and weakens task boundaries.
**Fix**: Merge completed task branch into `main`, tag milestone, then branch the next major task from updated `main`.
**Prevention**: Use a consistent "finish -> merge -> tag -> new branch" lifecycle for every major task (especially with a remote repo).

### L17: Pre-Commit Ignore Safety Check
**Issue**: Secret-bearing files (`.env`, local caches, generated output) can be accidentally staged during fast iteration.
**Fix**: Run `git status --ignored --short` before each commit and adjust `.gitignore` with narrow rules if needed.
**Prevention**: Make ignored-file review a mandatory pre-commit gate, and never force-add secrets.

### L18: Don’t `source .env` When Values Contain `&`
**Issue**: `source backend/.env` failed with `parse error near '&'` because the `DATABASE_URL` contained query params like `...&channel_binding=...`.
**Fix**: Prefer `python-dotenv` for local dev entrypoints, or set env vars explicitly in your shell (e.g., `export DATABASE_URL='postgresql://...'`).
**Prevention**: Treat `.env` files as dotenv-format (not shell scripts). If you must load them in a shell, ensure values are safely quoted.

### L19: Neon Connection Strings — Prefer Direct for Render
**Issue**: Using Neon pooler (`-pooler`) plus `channel_binding=require` caused intermittent `psycopg.OperationalError` failures (`SSL connection has been closed unexpectedly`) on real queries from Render.
**Fix**: Use Neon **direct** connection strings (pooling OFF) and remove `channel_binding=require` for this deployment path; keep `sslmode=require`.
**Prevention**: For server-side deployments, start with direct connections; only introduce pooling/extra SSL parameters after verifying stability under real request traffic.

### L20: Production Bootstrap Without Render Shell (Free Tier)
**Issue**: Render free instances do not support interactive shell, so you can’t run bootstrap scripts inside the service.
**Fix**: Run bootstrap scripts locally against the same production Neon DB used by Render (export `DATABASE_URL` and run `uv run python ...`).
**Prevention**: Always document bootstrap as an explicit “run from dev machine” step and verify via the deployed API (`/calls`, `/health/db`) afterward.
