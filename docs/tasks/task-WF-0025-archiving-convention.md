# WF-0025 — Completed Workflow Archival Strategy

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-21

## 1. Context
Create a formal archival mechanism to maintain a clean workspace. All workflows marked `Done` in `docs/index.md` will have their artifacts retroactively moved into `completed/` subdirectories, and the Phase 4 runner will be updated to enforce this behavior for all future workflows.

## 2. Tasks

### [x] Task 1.0: Create Archive Directories
- [x] Create `completed/` inside `docs/brainstorms/`.
- [x] Create `completed/` inside `docs/specs/features/`.
- [x] Create `completed/` inside `docs/specs/pages/`.
- [x] Create `completed/` inside `docs/prds/`.
- [x] Create `completed/` inside `docs/tasks/`.
- [x] Create `completed/` inside `docs/walkthroughs/`.
- [x] Add an empty `.gitkeep` implicitly to ensure empty directories are tracked if needed (optional if folders immediately populated).

### [ ] Task 2.0: Update Workflow System Rules
- [ ] Edit `docs/workflow/phase-4-run-implement.md`. Add a new bullet in `PART C` commanding the AI to `git mv` the 5 artifacts into their respective `completed/` folders after drafting the walkthrough and before ending the Phase.
- [ ] Edit `docs/workflow/README.md`. Add a new section under "Artifacts" documenting the `completed/` directory archival convention.

### [ ] Task 3.0: Retroactive Cleanup Execution
- [ ] Identify all workflows in `docs/index.md` marked explicitly as `| Done |`.
- [ ] Extract the list of markdown file paths mapped to those Done workflows.
- [ ] Execute `git mv` to shift each of those physical files into its respective `completed/` subdirectory.
- [ ] In the same commit, run a search/replace over `docs/index.md` to update all the links for those artifacts to include the `completed/` subpath.
- [ ] Verify `docs/index.md` syntax and link integrity.

## Traceability Statement
- Derived directly from `prd-WF-0025-archiving-convention.md` v1.0.
