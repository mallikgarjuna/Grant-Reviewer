# WF-0025 — Completed Workflow Archival Strategy

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. Context & Purpose
The workflow system currently lacks an explicit garbage collection/archival strategy for completed Phase 0-4 artifacts. `docs/index.md` marks items as `Done` and the `GEMINI.md` instructs agents to move completed tasks to a `completed/` folder, but this is not strictly enforced across all artifact types nor clearly orchestrated inside Phase 4. We need a formalized, retrospective cleanup of old files.

## 2. Acceptance Criteria (AC)
- **AC1**: Inside the following 6 directories, a `completed/` subdirectory exists: `docs/brainstorms/`, `docs/specs/features/`, `docs/specs/pages/`, `docs/prds/`, `docs/tasks/`, `docs/walkthroughs/`.
- **AC2**: All artifact markdown files belonging to a workflow row marked exactly `Done` in `docs/index.md` are moved into their respective `completed/` subdirectories. (Active workflows like `Phase 0`, `Phase 1`, etc. remain at their root level).
- **AC3**: The markdown links in `docs/index.md` for these `Done` workflows are updated to point to the new `completed/` paths.
- **AC4**: `docs/workflow/phase-4-run-implement.md` contains explicit instructions in `PART C` commanding the agent to move the WF's artifacts into the respective `completed/` folders after creating the walkthrough.
- **AC5**: `docs/workflow/README.md` is updated to define this standard archival behavior.

## 3. Scope Boundaries
- **In Scope**: Creating folders, moving legacy files mapped to `Done` status, updating the index, updating Phase 4 orchestrator.
- **Out of Scope**: Archiving old design logs (`decisions.md` etc.), archiving generic Markdown that doesn't belong to a specific WF, or altering the actual file *contents* of any `Done` artifact.

## 4. Technical Approach / Risks
- **Risk**: Moving files will break the link references in `docs/index.md` and the user experience will degrade.
- **Mitigation**: An explicit sed/replace or manual update step must be taken to rewrite the paths in `docs/index.md` alongside the file moves via git in exactly the same commit.
- **Risk**: Deleting or misplacing active WF artifacts.
- **Mitigation**: We must manually query `docs/index.md` for `| Done |` and only move artifacts that belong to those explicit `WF-XXXX` ID targets.

## Traceability Statement
- Derived directly from `spec-WF-0025-archiving-convention.md` v1.0.
