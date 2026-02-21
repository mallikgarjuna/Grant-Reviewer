# WF-0025 — Completed Workflow Archival Strategy

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-21

## 1. Problem Statement
The current Workflow System Upgrade (WF-0022 through WF-0024) successfully hardened phase execution but neglected artifact lifecycle management (Finding 9 of the Workflow Review). After an initiative enters the `Done` state, its brainstorming, specification, PRD, task, and walkthrough artifacts remain lingering in their respective root directories. Over time, this leads to significant file bloat, making it difficult to distinguish context between active WFs and historical completed WFs.

## 2. Desired Outcome
- Establish a "Per-Artifact `completed/` Strategy" by creating a `completed/` subdirectory inside each of the main artifact folders (`docs/brainstorms/`, `docs/specs/features/`, `docs/specs/pages/`, `docs/prds/`, `docs/tasks/`, `docs/walkthroughs/`).
- Forcefully define this archival mechanism as part of the Phase 4 gate in `docs/workflow/phase-4-run-implement.md`.
- Ensure all relevant documentation linking to `.md` files (specifically `docs/index.md`) points to the new `completed/` subdirectories for finished initiatives.
- Retroactively groom legacy "Done" items into this new structure.

## 3. Target User / Actor
- AI Coding Agents concluding Phase 4.
- Project Maintainers exploring historical artifacts.

## 4. MVP Definition & Rough Idea
Instead of building complex chronological or WF-specific archive folders (e.g. `docs/archive/WF-0020/`), we will keep the current horizontal segregation but nest a single `completed/` inbox inside each category folder. This maintains the explicit separation of concerns (all specs together, all tasks together) while dramatically clearing the active working space.

## 5. Constraints & Non-Goals
- **Non-Goal**: We are not altering the underlying contents of any files, only their physical paths and the links referencing them.

## Traceability Statement
- Derived from Finding 9 of `workflow_review.md.resolved` and explicit user affirmation to isolate this as WF-0025.
