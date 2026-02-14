# PRD: Task 8.1 Lint Baseline Cleanup

**Date**: 2026-02-13  
**Task ID**: 8.1  
**Pipeline Phase**: Phase 1 (PRD)  
**Status**: Draft (v0.1 - Parked for later)  
**Owner**: -  

---

## Context / Problem

We have working backend tests and a deployed MVP flow, but backend lint is currently failing at repo scale. This makes iterative development slower and increases the chance of “accidental breakage” as we change code.

Observed today:

- `cd backend && uv run pytest -q` passes (`22 passed`).
- `cd backend && uv run ruff check .` fails with ~275 findings (including many in `tests/` and import/formatting issues).

---

## Goals

- Establish a **repeatable lint baseline** for backend code using Ruff.
- Make `cd backend && uv run ruff check .` a reliable signal (i.e., it passes under an agreed ruleset).
- Keep rules pragmatic for an MVP codebase (avoid spending cycles on low-value style churn).

---

## Non-Goals

- No drive-by refactors unrelated to lint correctness.
- No behavioral changes to the API or domain model to satisfy style rules.
- No frontend lint cleanup in this task (separate task if needed).

---

## Proposed Approach (High Level)

- Add a Ruff configuration (likely in `backend/pyproject.toml`) that:
  - Enforces import sorting/formatting consistency.
  - Uses targeted per-file ignores for legitimate test patterns (e.g., `assert` in pytest).
  - Focuses on correctness and maintainability rules first.
- Fix the fastest/highest-signal findings first (format/import/order, trivial simplifications).
- Explicitly document any rules we intentionally defer (and why).

---

## Success Criteria

- `cd backend && uv run ruff format .` produces a clean tree (no diffs after formatting).
- `cd backend && uv run ruff check .` passes.
- `cd backend && uv run pytest -q` still passes.

---

## Risks / Tradeoffs

- Lint cleanup can balloon in scope; we should prefer configuration + targeted fixes over mass rewrites.
- Some rules may be counterproductive for tests; per-file ignores should be used sparingly but pragmatically.

---

## Revision History

- **v0.1** (2026-02-13): Parked PRD created to resume later with clear exit criteria.

