# Brainstorming 8.1: Lint Baseline Cleanup

**Date**: 2026-02-09  
**Task ID**: 8.1  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.1)  
**Last Updated**: 2026-02-09  

## Goal

Establish a practical lint baseline so new work can be verified reliably without blocking delivery on historical lint debt.

## Problem Snapshot

- `cd backend && uv run ruff check .` currently reports many existing violations across legacy files.
- This makes "lint pass" ambiguous for scoped feature work.
- Fixing all violations in one pass is high-risk and slows MVP delivery.

## MVP Direction (Phase 0 proposal)

1. Define a **narrow baseline strategy**:
   - enforce strict linting on changed/new files first
   - reduce existing debt incrementally in scoped batches
2. Split cleanup into safe execution slices:
   - auto-fixable issues first (`ruff --fix` + format)
   - manual/high-signal issues next
3. Avoid behavior changes:
   - no refactors beyond style/lint correctness
   - no API contract changes

## Success Criteria (for upcoming PRD)

- Team can run a documented lint command that is meaningful for active development.
- Existing lint debt has an explicit backlog and prioritized remediation sequence.
- Cleanup changes are test-validated and low-risk.

## Risks

- Large lint sweeps can create noisy diffs and accidental behavior changes.
- Some ruff rules may conflict with established testing patterns (e.g., assert usage in tests) and need policy decisions.

## Non-Scope Ideas (deferred)

- Global style-guide overhaul.
- Adopting additional linters/type checkers in this task.
- Rewriting legacy modules for architecture improvements under the lint umbrella.

## Revision History

- **v0.1** (2026-02-09): Initial Phase 0 draft for lint baseline cleanup workflow.
