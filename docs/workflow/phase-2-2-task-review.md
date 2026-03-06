# Phase 2.2 — Tasks Review (No Edits)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-2-2-task-review.md.
Do NOT modify this file during execution.

---

## Purpose

Critically evaluate task breakdown before implementation.

This step MUST NOT modify any files.

---

## Required Input

- docs/tasks/task-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before running the task review gate, ensure the task file being reviewed is **saved and committed** (so review feedback maps to a specific task version).

---

## Phase Completion — Commit This Phase

Phase 2.2 produces review output in chat only (no file edits). If you made no file changes, there is nothing to commit for this phase.

---

## Output (in chat only)

Return:

1. Task sequencing issues (including dependency graph issues: cycles, missing prerequisites, invalid references)
2. Atomicity violations (tasks too large; >3 files changed; unclear boundaries)
3. Missing integration/glue tasks
4. Over-engineering warnings
5. Redundant or mergeable tasks
6. Exact edits required (task number + change)
7. Missing traceability (tasks missing Slice/User Stories; tracer bullet missing/late; missing dependency metadata `Depends on`/`Enables`/`Parallelizable`)
8. Testing gaps (tasks missing explicit `RED/GREEN/REFACTOR` TDD Plan where required; verification steps missing concrete automated commands; verification steps not proving acceptance criteria)
9. PRD alignment gaps (tasks reference non-existent US#; tasks missing US# where PRD says MVP)
10. PRD requirement alignment gaps (tasks reference non-existent FR#; tasks missing FR# where PRD defines requirements)
11. Next 2 actions I should take (choose one)

Max 100 lines.
Be strict about MVP.
Be strict about atomic tasks: prefer tasks that are independently testable/verifiable and touch <=3 files when feasible.
Be strict about dependency ordering: task list should be topologically valid and easy to execute sequentially in Phase 3.
`Parallelizable` is planning metadata only; do NOT recommend parallel task execution for Phase 3.

Do NOT edit files.
