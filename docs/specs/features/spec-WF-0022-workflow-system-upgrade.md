# WF-0022 — Workflow System Upgrade

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Goal
Refactor the Project Workflow System (`docs/workflow/`) to reduce file sprawl, enforce verification in Phase 4, and eliminate documentation maintenance debt, explicitly targeting issues discovered during WF-0009 through WF-0021 execution.

## 2. User Stories
- **As an AI Coding Agent**, I need shorter, non-repetitive instruction files so I don't exhaust my context window and miss critical instructions.
- **As a Project Maintainer**, I need a single unified phase runner so I don't have to update boilerplate Part A/B/C logic in 3 different files.
- **As an AI Coding Agent**, I need a Phase 4 runner that explicitly forces me to verify my implementation before completing a task.
- **As a Project Maintainer**, I want an archival convention to keep the active `docs/` directories uncluttered.

## 3. Functional Requirements
### Tier 1: Quick Wins & Cheat-Sheet Reduction
- **FR1.1**: Fix numbering gaps in existing phase runners (e.g., duplicate `2.` bullets).
- **FR1.2**: Correct typos in `run-lifecycle-interactive.md`.
- **FR1.3**: Standardize agent terminology ("Codex or Antigravity or any coding agent") across all runners.
- **FR1.4**: Remove duplicate line 139 in `AGENTS.md`.
- **FR1.5**: Truncate `how-to-use-workflow-actions.md` to contain *only* phase-runner prompts and lifecycle runners. Delete individual sub-phase prompts to enforce "Runners are Routers".

### Tier 2: Risk Mitigation (Phase 4 & Lifecycles)
- **FR2.1**: Create `docs/workflow/phase-4-run-implement.md` with Part A (Execute), Part B (Verify/Integrate), Part C (Walkthrough + Ship).
- **FR2.2**: Update `run-lifecycle-auto.md` and `run-lifecycle-interactive.md` to include explicit context-reset warnings and commit boundaries.
- **FR2.3**: Document `workflow preflight` and `verify workflow` checklist stubs in `docs/workflow/README.md`.

### Tier 3: Refactoring & Archival
- **FR3.1**: Create `docs/workflow/universal-phase-runner.md` that uses YAML/markdown variables to represent Phase 1, 2, and 3 logic in a single file. (Note: May require testing agent behavior with parametric markdown).
- **FR3.2**: Delete the old explicitly split Phase 1/2/3 runner files to reduce sprawl, updating references in `README.md` and lifecycle files.
- **FR3.3**: Define an archival protocol in `README.md` advising to move "Done" artifacts into `docs/archive/WF-XXXX/`.

## 4. Non-Functional Requirements
- **Backward Compatibility**: Existing active branches (`WF-0021`) must remain operational after syncing `main`.
- **Clarity**: All edits must maintain the existing strict, imperative tone.

## Traceability Statement
- Derived from `brainstorm-WF-0022-workflow-system-upgrade.md` v1.0.
