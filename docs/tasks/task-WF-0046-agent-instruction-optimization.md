# WF-0046 — Agent Instruction Optimization Tasks

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Centralize project-specific rules in AGENTS.md
Goal: Extract unique global rules from `~/.gemini/GEMINI.md` into `AGENTS.md` and ensure length constraints.
Slice: rule-consolidation
User Stories: US1, US2
PRD Requirements: FR1
Depends on: none
Enables: 3
Parallelizable: no
Files to modify:
- AGENTS.md
Acceptance Criteria: `AGENTS.md` contains the ~10 unique project-specific rules missing from `docs/guides/` and is <= 45 lines.
TDD Plan: N/A
Verification Steps:
- Run `wc -l AGENTS.md` and verify output is <= 45.

### [ ] Task 2 — Delete duplicate repo GEMINI.md
Goal: Remove the redundant repo-level `GEMINI.md` file.
Slice: cleanup
User Stories: US2
PRD Requirements: FR2
Depends on: none
Enables: none
Parallelizable: yes
Files to modify:
- GEMINI.md
Acceptance Criteria: `GEMINI.md` no longer exists in the repository root.
TDD Plan: N/A
Verification Steps:
- Run `ls GEMINI.md` and verify it fails.

### [ ] Task 3 — Backup and trim global GEMINI.md
Goal: Backup the user-global file to `/tmp/` and trim it to safety nets only.
Slice: global-safety-trim
User Stories: US2, US3
PRD Requirements: FR3, FR4, FR6
Depends on: 1
Enables: none
Parallelizable: no
Files to modify:
- ~/.gemini/GEMINI.md
- /tmp/GEMINI.md.bak
Acceptance Criteria: `~/.gemini/GEMINI.md` is backed up to `/tmp/GEMINI.md.bak` and is trimmed to <= 15 lines.
TDD Plan: N/A
Verification Steps:
- Run `ls /tmp/GEMINI.md.bak` to ensure backup exists.
- Run `wc -l ~/.gemini/GEMINI.md` and verify output is <= 15.

### [ ] Task 4 — Append deferred improvements to Parking Lot
Goal: Document deferred architectural stories.
Slice: documentation
User Stories: US3
PRD Requirements: FR5
Depends on: none
Enables: none
Parallelizable: yes
Files to modify:
- docs/parking_lot.md
Acceptance Criteria: Stories D (code-based enforcement) and G (loop-style Phase 3) from the brainstorm are added to `docs/parking_lot.md`.
TDD Plan: N/A
Verification Steps:
- Run `cat docs/parking_lot.md` to verify the new items are listed.

## Changelog

- v0.1 (2026-03-04): Initial task breakdown from PRD
