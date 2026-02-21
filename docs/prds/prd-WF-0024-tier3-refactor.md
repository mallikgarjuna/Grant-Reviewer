# WF-0024 — Tier 3: Phase 1-3 Runner Refactor

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. Context & Purpose
The workflow system currently uses three separate runner files (`phase-1-run-spec.md`, `phase-2-run-prd.md`, `phase-3-run-task.md`) to handle the planning phases. These files are functionally identical in their Part A/B/C gating structure, leading to unnecessary maintenance overhead and bloated context windows. We need to replace them with a single parametric runner.

## 2. Acceptance Criteria (AC)
- **AC1**: `docs/workflow/phase-123-run-planning.md` acts as the single entry point for Phases 1, 2, and 3.
- **AC2**: The new runner clearly defines the Input/Output matrix based on the invoked Phase ID.
- **AC3**: The new runner successfully maps to the preexisting sub-phase files (e.g., `phase-1-1-spec-generate.md`, etc.).
- **AC4**: `how-to-use-workflow-actions.md` is updated to invoke the new runner for Phases 1, 2, and 3.
- **AC5**: `run-lifecycle-auto.md` and `run-lifecycle-interactive.md` invoke the new runner.
- **AC6**: `docs/workflow/README.md` reflects the unified runner in its shortcut list.
- **AC7**: The legacy `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` files are completely deleted from the repository.

## 3. Scope Boundaries
- **In Scope**: Creating `phase-123-run-planning.md`, updating callers, deleting legacy files.
- **Out of Scope**: Editing the underlying Part A (Generate), Part B (Review), or Part C (Revise) sub-phase logic files.

## 4. Technical Approach / Risks
- **Risk**: Deleting the old runner files before all incoming links are updated could break workflow navigation.
- **Mitigation**: Update all calling files (Lifecycles, Cheat Sheets, README) *before* deleting the old runner files in the atomic commit sequence.
- **Risk**: Agents might get confused by the parameterization if it's too abstract.
- **Mitigation**: Use a dead-simple Markdown table in `phase-123-run-planning.md` to map `Phase N` to `Input Artifact`, `Target Output Artifact`, and `Part A/B/C Sub-files`.

## Traceability Statement
- Derived directly from `spec-WF-0024-tier3-refactor.md` v1.0.
