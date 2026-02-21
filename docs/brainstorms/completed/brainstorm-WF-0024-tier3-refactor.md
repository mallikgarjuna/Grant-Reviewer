# WF-0024 — Tier 3: Phase 1-3 Runner Refactor

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-21

## 1. Problem Statement
The current workflow orchestrators for Phase 1 (Spec), Phase 2 (PRD), and Phase 3 (Tasks) are nearly identical (~160 lines each). They maintain the exact same Part A (Generate), Part B (Review), and Part C (Revise) structure but duplicate boilerplate code.

When establishing new workflow rules (e.g., changing the verification checklist), we must manually edit 3+ files. This duplication violates DRY principles, bloats the context window during execution, and fragments the single source of truth for planning phases.

## 2. Desired Outcome
- Coalesce `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` into ONE parametric runner called `phase-123-run-planning.md` (or similar).
- Delete the old individual phase runner files.
- Update `how-to-use-workflow-actions.md` and the lifecycle runners (`run-lifecycle-auto.md`, `run-lifecycle-interactive.md`) to point to the new single wrapper.
- Update `docs/workflow/README.md` to reflect the new file naming and structure.
- Add an `archive` folder strategy for deprecated documentation (if needed) or simply delete.

## 3. Target User / Actor
- AI Coding Agents traversing the planning phases (Phases 1-3).
- Project Maintainers updating workflow procedures.

## 4. MVP Definition & Rough Idea
This is explicitly scoped as the final **Tier 3 (The Refactoring & Archival)** step of the Workflow System Upgrade.
We will create a single markdown document that reads: "If you are in Phase 1, the Input is X and Output is Y. If Phase 2... If Phase 3... But the Execution Rules (Part A/B/C) are universal."

## 5. Constraints & Non-Goals
- **Non-Goal**: Refactoring Phase 4 (already hardened in WF-0023) or Phase 0 (special initial state).
- **Non-Goal**: Altering the actual Part A/B/C logic itself; we are strictly *consolidating* existing logic, not reinventing it.

## Traceability Statement
- Derived from the explicit user directive to isolate Tier 3 (The Refactoring & Consolidating of Phase 1-3 runner orchestrators) into its own PR.
