# WF-0024 — Tier 3: Phase 1-3 Runner Refactor

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-21

## 1. Context
Create the singular Phase 1-3 orchestrator (`phase-123-run-planning.md`), update all calling documentation to point to it, and securely delete the three legacy phase runners.

## 2. Tasks

### [x] Task 1.0: Create the Unified Runner (`docs/workflow/phase-123-run-planning.md`)
- [x] Create `docs/workflow/phase-123-run-planning.md`.
- [x] Add the Phase/Input/Output parameter matrix.
- [x] Define the universal Part A (Generate), Part B (Review/Audit), and Part C (Revise & Bump) gates using variables instead of hardcoded paths.
- [x] Add the standard `How to Invoke in Chat` section with the parameterized prompt template.

### [x] Task 2.0: Update Caller Documentation
- [x] **`how-to-use-workflow-actions.md`**: Update the Phase 1, Phase 2, and Phase 3 "End-to-End" cheat sheet blocks to invoke `phase-123-run-planning.md` instead of the legacy individual files.
- [x] **`run-lifecycle-auto.md`**: Update steps 3, 4, and 5 to point to `phase-123-run-planning.md`.
- [x] **`run-lifecycle-interactive.md`**: Update steps 3, 4, and 5 to point to `phase-123-run-planning.md`.
- [x] **`docs/workflow/README.md`**: Update the `Runner shortcuts:` list to point to `phase-123-run-planning.md`.

### [ ] Task 3.0: Excise Legacy Runners (The Deletion)
- [ ] Delete `docs/workflow/phase-1-run-spec.md`.
- [ ] Delete `docs/workflow/phase-2-run-prd.md`.
- [ ] Delete `docs/workflow/phase-3-run-task.md`.
- [ ] Run `git diff` and search for any dangling references to the deleted files.

## Traceability Statement
- Derived directly from `prd-WF-0024-tier3-refactor.md` v1.0.
