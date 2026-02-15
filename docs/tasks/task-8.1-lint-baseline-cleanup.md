# Task 8.1: Lint Baseline Cleanup (Phase 2 Plan)

**Date**: 2026-02-13  
**Task ID**: 8.1  
**Pipeline Phase**: Phase 2 (Task breakdown)  
**Status**: Complete (v0.2)  
**PRD**: `docs/prds/prd-8.1-lint-baseline-cleanup.md`  

---

## Scope Guardrails

- Prefer Ruff configuration and small, mechanical fixes.
- Avoid changing runtime behavior unless absolutely required for correctness.
- Keep diffs reviewable; if changes expand beyond expectations, split into follow-up tasks.

---

## Subtasks

### 8.1.1 Choose baseline ruleset

- [x] Decide Ruff rule scope for backend:
  - [x] Must-fix now: `E4,E7,E9,F,I,B,UP`
  - [x] Deferred: docstring/type-annotation/pylint-style strictness families
  - [x] Per-file ignore accepted: `scripts/run_review.py:E402` (intentional `sys.path` setup)

### 8.1.2 Add Ruff configuration

- [x] Add `[tool.ruff]` configuration in `backend/pyproject.toml`
- [x] Add targeted per-file ignore for `backend/scripts/run_review.py` (`E402`)
- [x] Document configuration in this task file

### 8.1.3 Fix autofixable findings first

- [x] Run `cd backend && uv run ruff check . --fix`
- [ ] Run `cd backend && uv run ruff format .` (deferred; not required for selected baseline)
- [x] Re-run `cd backend && uv run ruff check .` and capture remaining categories
  - Remaining after autofix: one `B007` in `app/schemas/call_definitions.py`

### 8.1.4 Fix remaining high-signal findings

- [x] Address remaining import sorting, formatting, and correctness issues
- [x] Avoid large refactors; prefer localized edits

### 8.1.5 Verification (required)

- [x] `cd backend && uv run ruff check .`
- [ ] `cd backend && uv run ruff format .` (deferred; baseline does not require full formatting pass)
- [x] `cd backend && uv run pytest -q`

---

## Notes (Parking Context)

As of 2026-02-13:

- Backend tests pass (`22 passed`).
- Backend Ruff check is failing with a large number of findings; expect meaningful benefit from a ruleset decision plus per-file ignores for tests.

---

## Revision History

- **v0.1** (2026-02-13): Parked task plan created to resume later.
- **v0.2** (2026-02-15): Implemented safe baseline via Ruff config + autofix and localized cleanup; `ruff check` and `pytest` both pass.
