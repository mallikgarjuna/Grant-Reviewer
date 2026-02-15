# WF-0011 — Local Postgres Dev DB Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-15

## Task Breakdown (Sequential Order)

### Task 1 — Add blessed local Postgres compose file

Goal:
- Provide a single repository-managed local Postgres startup contract.

Files to modify:
- `backend/docker-compose.dev.yml`

Acceptance Criteria:
- Compose file defines `postgres` service on `localhost:5432`.
- Uses a named volume for local persistence.
- Service is runnable with standard `docker compose` commands.

Verification Steps:
- `cd backend && docker compose -f docker-compose.dev.yml up -d`
- `cd backend && docker compose -f docker-compose.dev.yml ps`

Risks (if any):
- Port `5432` conflicts on some machines.

### Task 2 — Align local env contract with Postgres-first dev

Goal:
- Make local localhost Postgres the documented default and keep Neon opt-in only.

Files to modify:
- `backend/.env.example`

Acceptance Criteria:
- Example `DATABASE_URL` points to localhost Postgres and includes `sslmode=disable`.
- Explicit note states local defaults must not target Neon hosts.
- SQLite fallback behavior is documented as explicit fallback only.

Verification Steps:
- Open `backend/.env.example` and confirm contract text and sample URL.

Risks (if any):
- Confusion if local `.env` still contains stale Neon URL.

### Task 3 — Document canonical local runbook (startup, bootstrap, reset, verify)

Goal:
- Provide one authoritative local setup and recovery flow for contributors.

Files to modify:
- `backend/README.md`

Acceptance Criteria:
- README includes start/stop/reset commands for compose service.
- Reset command is clearly labeled destructive and local-only.
- Reset guidance includes warning to verify `DATABASE_URL` host is local before running.
- README includes bootstrap commands using existing scripts.
- README includes minimum readiness thresholds (`prompt_templates`, `funding_calls`, `proposal_nodes` >= 1).
- README includes one Postgres-backed stub review verification path with expected terminal status behavior.
- README includes brief no-Docker fallback note (secondary path only).

Verification Steps:
- Manually follow runbook steps from clean local DB state.
- Run reset flow, rerun bootstrap, and reconfirm readiness thresholds.

Risks (if any):
- Documentation drift if commands are not validated during task execution.

### Task 4 — Capture Postgres-backed verification evidence in walkthrough

Goal:
- Prove local readiness on Postgres with concrete command/result evidence.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0011-local-postgres-dev-db.md`

Acceptance Criteria:
- Walkthrough records exact commands and outcomes for:
  - local Postgres startup check,
  - bootstrap scripts,
  - readiness count checks,
  - one stub review flow reaching terminal status.
- Walkthrough records deviations and fixes observed during execution.

Verification Steps:
- Confirm walkthrough contains timestamped command/result evidence for each required check.

Risks (if any):
- Incomplete evidence may reduce confidence in reproducibility.

### Task 5 — Final consistency and implementation handoff gate

Goal:
- Ensure WF-0011 artifacts are implementation-ready and phase status is consistent.

Files to modify:
- `docs/index.md`
- `docs/tasks/task-WF-0011-local-postgres-dev-db.md`

Acceptance Criteria:
- Task file remains `Status: Ready for Implementation`.
- `docs/index.md` WF-0011 row status is `Phase 3 (Ready)`.
- Task changelog reflects review-driven revision.

Verification Steps:
- `rg -n "WF-0011|Phase 3 \(Ready\)|Ready for Implementation" docs/index.md docs/tasks/task-WF-0011-local-postgres-dev-db.md`

Risks (if any):
- Workflow state drift if status updates are skipped.

## Changelog

- v0.1 (2026-02-15): Initial task breakdown from PRD
- v0.2 (2026-02-15): Applied review edits (sequencing cleanup, merged redundant README tasks, and tightened handoff criteria)
