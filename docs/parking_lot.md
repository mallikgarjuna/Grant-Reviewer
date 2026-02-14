# Parking Lot / Backlog

**Purpose**: A dedicated place to park “not now” items (tech debt, ideas, risks, follow-ups) so they don’t get lost. When something becomes a priority, promote it into a real task/PRD under `docs/tasks/active/` and link it from `docs/index.md`.

## Guidelines

### Parking (adding non-priority items)

Add items under **Parked Items** when they are valuable but **not the next thing** to do.

Each parked item should include:
- **Date**: when it was parked (helps prune stale items).
- **One-line title**: specific and searchable (start with a verb).
- **Type**: idea / tech debt / risk / ops / product.
- **Why it matters**: 1–2 lines max.
- **Promote when…**: a trigger (e.g., “before launch”, “after first timeout”, “next schema change”).
- **Owner** (optional): who will likely pick it up.
- **Links** (optional): to relevant files, walkthroughs, or incidents.

Where to park it:
- **Minor, opportunistic fixes** → `docs/maintenance.md`
- **Not-now but important** → this file (`docs/parking_lot.md`)
- **Active work** → promote to `docs/tasks/active/` and track in `docs/index.md`

Maintenance hygiene:
- Prefer fewer, higher-signal items; merge duplicates instead of adding variants.
- When an item is promoted, don’t delete it—mark it as promoted and link the new artifacts.

### Unparking (promoting into the workflow)

Promote an item when it becomes “next” or when its **Promote when…** trigger fires.

Promotion checklist (Brainstorm → PRD → Task Plan):
1) **Phase 0 (Brainstorming)**: create `docs/brainstorms/brainstorming-<TaskID>-<slug>.md` with scope/options/risks.
2) **Phase 1 (PRD)**: create `docs/prd/prd-<TaskID>-<slug>.md` with goals, non-goals, success criteria.
3) **Phase 2 (Task breakdown)**: create `docs/tasks/active/task-<TaskID>-<slug>.md` with subtasks + verification.
4) **Update dashboard**: add the new task row + links in `docs/index.md`.
5) **Mark promoted here**: update the parked item to include:
   - `Promoted to: <TaskID>` and links to the brainstorm/PRD/task files.
6) **Phase gates**: before Phase 3 implementation, explicitly decide “go ahead” on scope and verification approach.

---

## Critical Snapshot (2026-02-13)

- MVP is end-to-end: FastAPI + Next.js BFF + Clerk; production Postgres path exists; backend API tests pass (`cd backend && uv run pytest -q`).
- Guardrails are weak: no repo CI workflows found; backend lint is currently failing at repo scale (`cd backend && uv run ruff check .` reports ~275 findings).
- Some planning/doc drift exists (example: 8.0C is marked complete in `docs/index.md` while the 8.0C task file reports “In Progress”).

---

## Next Priority Options (recommended order as of 2026-02-13)

1) **Guardrails (CI + lint baseline)**  
   - Why: protects main from regressions and makes iteration cheaper.  
   - Parked next step: complete Task 8.1 (`docs/tasks/active/task-8.1-lint-baseline-cleanup.md`).

2) **Production data safety (Alembic migrations)**  
   - Why: Postgres is real; relying on `create_all()` is risky for schema evolution.  
   - Promote when: next time we need a schema change or before public launch.

3) **Async review execution (scaling path)**  
   - Why: improves timeout/retry behavior and supports longer model latencies.  
   - Promote when: we see timeouts, want background jobs, or need better UX for long-running reviews.

---

## Parked Items

- [ ] (2026-02-13) Add CI workflows for backend (`pytest`, `ruff`) and frontend (`npm run lint`, `npm run check:*`).  
  - Why: enforce “green main”.  
  - Promote when: before starting the next multi-day feature.

- [ ] (2026-02-13) Create Task/PRD for Alembic migration baseline.  
  - Why: safe schema changes in Postgres.  
  - Promote when: first new table/column beyond MVP.

- [ ] (2026-02-13) Create Task/PRD for async review pipeline (queue + poll).  
  - Why: resilience and UX improvements for long-running model calls.  
  - Promote when: we introduce retries, background processing, or higher traffic.

---

## Revision History

- **v0.1** (2026-02-13): Created as a dedicated parking place for snapshot + priorities + non-urgent TODOs.
