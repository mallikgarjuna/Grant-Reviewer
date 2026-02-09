# Brainstorming 8.1: Lint Baseline Cleanup

**Date**: 2026-02-09  
**Task ID**: 8.1  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.2 - Revised)  
**Last Updated**: 2026-02-09  

## Goal

Establish a practical lint baseline so new work can be verified reliably without blocking delivery on historical lint debt.

## Problem Snapshot

- `cd backend && uv run ruff check .` currently reports many existing violations across legacy files.
- This makes "lint pass" ambiguous for scoped feature work.
- Fixing all violations in one pass is high-risk and slows MVP delivery.
- Current repo state has no committed CI workflow under `.github/workflows/`, so lint enforcement is not yet centralized.

## MVP Decisions (Locked for PRD 8.1)

### 1) Baseline mechanism
- Use **diff-based lint gating** for backend Python files in PRs.
- Gate only changed files first (not whole repo) to stop new debt while avoiding legacy-blocking failures.
- Keep full-repo lint as non-gating visibility signal for now (optional local check).

### 2) Baseline ownership
- Task owner (current implementer) proposes lint policy changes.
- Repo maintainer/reviewer approves rule changes and any new ignores.
- Every ignore entry must include a short reason in config comments and a follow-up cleanup reference.

### 3) CI gating decision
- Add a minimal CI workflow in Task 8.1 that runs the same canonical lint command used locally.
- CI fail condition: lint errors on changed backend Python files.
- Keep unit tests in CI as-is (or add if missing) but do not block 8.1 on broad CI redesign.

### 4) Formatter policy
- Standardize on **Ruff only** for MVP:
  - `ruff check`
  - `ruff format`
- Do not introduce Black/isort in parallel to avoid style churn and tool conflicts.

### 5) Rule-category policy (MVP)
- Enforce high-signal correctness/import hygiene first.
- Defer or relax noisy/test-hostile categories where needed (e.g., test asserts, certain docstring strictness, per-file exceptions) with explicit rationale.
- Track relaxed categories for later tightening (Task 8.3).

### 6) Behavior-change guardrails
- Allowed in 8.1:
  - formatting/import order/trailing commas
  - safe, semantics-preserving lint fixes
- Not allowed in 8.1 without explicit review note:
  - edits that alter exception flow/return behavior
  - removal of imports used for side effects/registration
  - non-trivial logical rewrites justified as "lint cleanup"

### 7) Canonical command parity
- Define one canonical lint command and use it both locally and in CI.
- MVP candidate: `cd backend && uv run ruff check` (scoped to changed files in CI wrapper).

### 8) Diff-noise control
- Apply autofix only to selected file sets (changed files or explicitly chosen module batch).
- Do not run repo-wide `--fix` during baseline setup.

## MVP Direction (Phase 0 proposal)

1. Implement baseline and gating in Task 8.1:
   - lint policy + formatter policy + CI diff gate + canonical command docs
2. Defer debt paydown to follow-up task batches (8.2):
   - module-by-module cleanup with tight diffs and tests
3. Defer rule tightening to a separate hardening task (8.3):
   - progressively increase strictness after MVP surface stabilizes

## Success Criteria (for upcoming PRD)

- `8.1` has a documented and working lint baseline mechanism (local + CI parity).
- PRs fail on newly introduced lint issues in changed backend Python files.
- Formatter strategy is explicit and singular (Ruff-only).
- Deferred debt and rule-tightening backlog is explicitly captured (`8.2`, `8.3`).
- At least one small validation batch confirms the mechanism works end-to-end.

## Risks

- Large lint sweeps can create noisy diffs and accidental behavior changes.
- Rule strictness may still conflict with established test/script patterns and require targeted per-file policy.
- Local-vs-CI command drift can undermine enforcement if command parity is not locked.

## Non-Scope Ideas (deferred)

- Global style-guide overhaul.
- Adopting additional linters/type checkers in this task.
- Rewriting legacy modules for architecture improvements under the lint umbrella.
- Full-repo lint cleanup in one PR.
- CI platform redesign beyond minimal lint-gating workflow.

## Deferred Task Backlog (proposed)

- **Task 8.2**: Lint debt paydown in micro-batches (module-by-module).
- **Task 8.3**: Progressive rule tightening and cleanup of temporary ignores.

## Revision History

- **v0.1** (2026-02-09): Initial Phase 0 draft for lint baseline cleanup workflow.
- **v0.2** (2026-02-09): Added explicit baseline mechanism, CI gating plan, ownership, rule/formatter policy, behavior guardrails, done definition, and deferred task split (8.2/8.3).
