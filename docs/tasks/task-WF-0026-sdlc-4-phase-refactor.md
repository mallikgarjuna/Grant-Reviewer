# Tasks: WF-0026 — SDLC 4-Phase Refactor

**Version:** v0.1
**Last Updated:** 2026-02-21
**Status:** Draft

---

## Task 1.0: Delete Deprecated Spec Phase Files
- [ ] 1.1: `git rm docs/workflow/phase-1-1-spec-generate.md`
- [ ] 1.2: `git rm docs/workflow/phase-1-2-spec-review.md`
- [ ] 1.3: `git rm docs/workflow/phase-1-3-spec-revise.md`
- [ ] 1.4: Create `docs/specs/DEPRECATED.md` explaining the Spec phase was merged into the unified PRD as of WF-0026
- [ ] 1.5: Commit: `WF-0026: [1.0] delete deprecated spec phase files`

## Task 2.0: Rename Phase 0 Runner
- [ ] 2.1: `git mv docs/workflow/phase-0-run-start-and-brainstorm.md docs/workflow/phase-0-run-start-and-brainstorm-ideation.md`
- [ ] 2.2: Update internal content: change recommended next action from `phase-1-run-spec.md` to `phase-1-run-prd-definition.md`
- [ ] 2.3: Commit: `WF-0026: [2.0] rename Phase 0 runner`

## Task 3.0: Rename and Renumber Phase 1 (Definition) Files
- [ ] 3.1: `git mv docs/workflow/phase-2-1-prd-generate.md docs/workflow/phase-1-1-prd-generate.md`
- [ ] 3.2: `git mv docs/workflow/phase-2-2-prd-risk-audit.md docs/workflow/phase-1-2-prd-risk-audit.md`
- [ ] 3.3: `git mv docs/workflow/phase-2-3-prd-revise.md docs/workflow/phase-1-3-prd-revise.md`
- [ ] 3.4: Update content inside each file: change any "Phase 2" references to "Phase 1" and any references to adjacent phase files
- [ ] 3.5: Commit: `WF-0026: [3.0] rename PRD sub-phase files to Phase 1`

## Task 4.0: Rename and Renumber Phase 2 (Planning) Files
- [ ] 4.1: `git mv docs/workflow/phase-3-1-task-generate.md docs/workflow/phase-2-1-task-generate.md`
- [ ] 4.2: `git mv docs/workflow/phase-3-2-task-review.md docs/workflow/phase-2-2-task-review.md`
- [ ] 4.3: `git mv docs/workflow/phase-3-3-task-revise.md docs/workflow/phase-2-3-task-revise.md`
- [ ] 4.4: Update content inside each file: change any "Phase 3" references to "Phase 2" and any references to adjacent phase files
- [ ] 4.5: Commit: `WF-0026: [4.0] rename Task sub-phase files to Phase 2`

## Task 5.0: Rename Phase 3 (Execution) Runner and Sub-Phases
- [ ] 5.1: `git mv docs/workflow/phase-4-run-implement.md docs/workflow/phase-3-run-implement-execution.md`
- [ ] 5.2: `git mv docs/workflow/phase-4-1-implement-tasks.md docs/workflow/phase-3-1-implement-tasks.md`
- [ ] 5.3: `git mv docs/workflow/phase-4-2-verify-and-ship.md docs/workflow/phase-3-2-verify-and-ship.md`
- [ ] 5.4: Update content inside each file: change any "Phase 4" references to "Phase 3" and any references to adjacent phase files
- [ ] 5.5: Commit: `WF-0026: [5.0] rename Implement files to Phase 3`

## Task 6.0: Rewrite the Unified Planning Runner
- [ ] 6.1: `git mv docs/workflow/phase-123-run-planning.md docs/workflow/phase-12-run-planning.md`
- [ ] 6.2: Remove the entire Phase 1 (Spec) row from the routing matrix
- [ ] 6.3: Renumber the matrix: Phase 2 (PRD) → Phase 1 (Definition), Phase 3 (Tasks) → Phase 2 (Planning)
- [ ] 6.4: Update all inner-loop file references to point to the new filenames
- [ ] 6.5: Commit: `WF-0026: [6.0] rewrite unified planning runner`

## Task 7.0: Update Lifecycle Runners
- [ ] 7.1: Rewrite `run-lifecycle-auto.md`: remove Spec step, renumber all phases, update runner filenames
- [ ] 7.2: Rewrite `run-lifecycle-interactive.md`: same changes
- [ ] 7.3: Commit: `WF-0026: [7.0] update lifecycle runners`

## Task 8.0: Update Cheat Sheet and Documentation
- [ ] 8.1: Rewrite `how-to-use-workflow-actions.md` with new runner filenames and prompt templates
- [ ] 8.2: Rewrite `docs/workflow/README.md`: update phase list, runner shortcuts, status values, artifact hierarchy
- [ ] 8.3: Update `AGENTS.md`: update WF Workflow section with new phase names, runner references
- [ ] 8.4: Commit: `WF-0026: [8.0] update cheat sheet and documentation`

## Task 9.0: Verify
- [ ] 9.1: Run `rg "phase-1-run-spec" docs/` — expect 0 results
- [ ] 9.2: Run `rg "phase-2-run-prd" docs/` — expect 0 results
- [ ] 9.3: Run `rg "phase-3-run-task" docs/` — expect 0 results
- [ ] 9.4: Run `rg "phase-4-run-implement" docs/` — expect 0 results
- [ ] 9.5: Run `rg "Phase 4" docs/workflow/` — expect 0 results in workflow instruction files
- [ ] 9.6: Run `pre-commit run --all-files`
- [ ] 9.7: Verify `how-to-use-workflow-actions.md` contains valid prompts referencing only new filenames

---

## Changelog

- v0.1 (2026-02-21): Initial draft.
