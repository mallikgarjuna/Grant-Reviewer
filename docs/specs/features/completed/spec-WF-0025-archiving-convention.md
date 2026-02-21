# WF-0025 — Completed Workflow Archival Strategy

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Goal
Implement a robust archival clean-up strategy that isolates completed (`Done`) workflows from active ones by moving their artifacts into `completed/` subdirectories within their respective root folders, and update the workflow runners to enforce this going forward.

## 2. User Stories
- **As a Project Maintainer**, I want my active `docs/brainstorms/`, `docs/specs/`, `docs/prds/`, etc., folders to only contain files for initiatives currently in progress, so I can easily see what the team is working on.
- **As an AI Coding Agent**, I want historical context neatly tucked into `/completed/` folders so I don't accidentally pull in stale context from old files when I run blanket directory searches.

## 3. Functional Requirements
### Directory Structure Additions
- **FR1**: Create a `completed/` directory inside `docs/brainstorms/`.
- **FR2**: Create a `completed/` directory inside `docs/specs/features/`.
- **FR3**: Create a `completed/` directory inside `docs/specs/pages/`.
- **FR4**: Create a `completed/` directory inside `docs/prds/`.
- **FR5**: Create `docs/tasks/completed/` (actually, this already exists conceptually per `GEMINI.md`, but ensure it is strictly utilized).
- **FR6**: Create a `completed/` directory inside `docs/walkthroughs/`.

### Workflow Enforcement Updates
- **FR7**: Update `docs/workflow/phase-4-run-implement.md`. In Part C (Walkthrough + Ship), add explicit instructions commanding the agent to move the 5 artifacts (Brainstorm, Spec, PRD, Tasks, Walkthrough) into their respective `completed/` folders immediately *after* the walkthrough is written but *before* the branch is merged.
- **FR8**: Update `docs/workflow/README.md` to document this `completed/` directory archival convention.

### Retroactive Cleanup Scripting
- **FR9**: Execute the cleanup process on all legacy workflows currently marked as `Done` in `docs/index.md` (e.g., WF-0009 through WF-0024).
- **FR10**: Ensure that `docs/index.md` is updated so all links for `Done` workflows correctly point to the `completed/` paths.

## 4. Non-Functional Requirements
- **Safety**: Do not delete any artifact content. Only move files and update `index.md` pointers.

## Traceability Statement
- Derived directly from `brainstorm-WF-0025-archiving-convention.md` v1.0.
