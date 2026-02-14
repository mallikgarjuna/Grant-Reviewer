# Task 8.1: Lint Baseline Cleanup (Phase 2 Plan)

**Date**: 2026-02-13  
**Task ID**: 8.1  
**Pipeline Phase**: Phase 2 (Task breakdown)  
**Status**: Draft (v0.1 - Parked for later)  
**PRD**: `docs/prds/prd-8.1-lint-baseline-cleanup.md`  

---

## Scope Guardrails

- Prefer Ruff configuration and small, mechanical fixes.
- Avoid changing runtime behavior unless absolutely required for correctness.
- Keep diffs reviewable; if changes expand beyond expectations, split into follow-up tasks.

---

## Subtasks

### 8.1.1 Choose baseline ruleset

- [ ] Decide Ruff rule scope for backend:
  - [ ] Which rule families are “must fix” now vs deferred
  - [ ] What per-file ignores are acceptable for `backend/tests/`

### 8.1.2 Add Ruff configuration

- [ ] Add `[tool.ruff]` configuration (likely in `backend/pyproject.toml`)
- [ ] Add per-file ignores for `backend/tests/` as needed (pytest `assert`, etc.)
- [ ] Ensure configuration is documented briefly in this task file

### 8.1.3 Fix autofixable findings first

- [ ] Run `cd backend && uv run ruff check . --fix`
- [ ] Run `cd backend && uv run ruff format .`
- [ ] Re-run `cd backend && uv run ruff check .` and capture remaining categories

### 8.1.4 Fix remaining high-signal findings

- [ ] Address remaining import sorting, formatting, and correctness issues
- [ ] Avoid large refactors; prefer localized edits

### 8.1.5 Verification (required)

- [ ] `cd backend && uv run ruff check .`
- [ ] `cd backend && uv run ruff format .`
- [ ] `cd backend && uv run pytest -q`

---

## Notes (Parking Context)

As of 2026-02-13:

- Backend tests pass (`22 passed`).
- Backend Ruff check is failing with a large number of findings; expect meaningful benefit from a ruleset decision plus per-file ignores for tests.

---

## Revision History

- **v0.1** (2026-02-13): Parked task plan created to resume later.
