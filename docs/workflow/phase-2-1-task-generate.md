# Phase 2.1 — Generate Tasks (v0.1)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-2-1-task-generate.md.
Do NOT modify this file during execution.

---

## Purpose

Convert an approved PRD into an ordered, implementation-ready task list (v0.1).

STOP after generating tasks v0.1.
No review in this step.

---

## Required Input

- docs/prds/prd-WF-XXXX-<slug>.md

PRD must have:
Status: Ready for Tasks

Do NOT derive tasks directly from brainstorm.

---

## Phase Gate — Commit Previous Phase

Before generating the task file, ensure the PRD you are converting is **saved and committed** (so the plan is traceable to a stable PRD input).

---

## Phase Completion — Commit This Phase

After generating task v0.1, **save and commit** the updated task file before proceeding to Phase 2.2 review.

---

## Output

- docs/tasks/task-WF-XXXX-<slug>.md

Only generate if Version = v0.0.

---

## Versioning Rules

Tasks file must include:

Artifact: task
Version: v0.1
Status: Draft
Last Updated: YYYY-MM-DD

Include:

## Changelog

- v0.1 (YYYY-MM-DD): Initial task breakdown from PRD

---

## Required Tasks Structure

# WF-XXXX — <Title> Tasks

Artifact: task
Version: v0.1
Status: Draft
Last Updated: <today>

## Task Breakdown (Sequential Order)

Task planning rules:

- Prefer thin vertical slices (end-to-end tracer bullet early).
- Keep tasks atomic (<=3 files preferred) but maintain slice coherence using `Slice:`.
- Every behavior change/bug fix MUST be implemented with TDD (red/green/refactor).
- Avoid horizontal slicing (do not plan "all tests first, all code later"). Prefer `RED->GREEN` per slice increment.
- Tasks MUST be written so Phase 3 can execute and *log* a recognizable TDD loop per task (labels: `RED`, `GREEN`, `REFACTOR`).
- Add explicit dependency metadata per task (`Depends on`, `Enables`, `Parallelizable`) to make ordering assumptions reviewable.
- Dependency metadata is planning-only and MUST NOT be interpreted as permission to parallelize Phase 3 execution.
- Treat `task` as the canonical planning and commit unit. Do NOT invent a second execution-unit format.
- Add only deterministic execution hints. Do NOT add free-form "agent decides" language.
- `Session boundary after` is planning guidance for Phase 3 chat hygiene, not an automatic stop signal by itself.

For each task include:

### [ ] Task 1 — <short title>

Goal:
Slice: <tracer-bullet|slice-name>
User Stories: <US1, US2> (from PRD) or `N/A`
PRD Requirements: <FR1, FR2> (from PRD) or `N/A`
Depends on: <Task #s or `none`>
Enables: <Task #s or `none`>
Parallelizable: <yes|no> (planning-only signal)
Files to modify:
Must touch files: <project-relative paths or `none`>
May touch files: <project-relative paths or `none`>
Out of scope: <explicit exclusions or `none`>
Stop if: <hard boundary conditions that require pausing Phase 3 and reassessing, or `none`>
Session boundary after: <yes|no>
Acceptance Criteria:
TDD Plan: <required: `N/A` or explicit `RED/GREEN/REFACTOR` plan>
Verification Steps:
Risks (if any):

Tasks must:

- Be sequential
- Respect dependencies
- Avoid scope expansion
- Be minimal for MVP
- Form a DAG-valid dependency structure:
  - No cycles.
  - `Depends on` references must point to earlier tasks only.
  - Prefer topological ordering in the listed sequence.
- Be atomic and implementation-ready:
  - Prefer each task to touch no more than 3 files.
  - If a task would exceed ~3 files, split it into smaller dependent tasks.
  - Use as many tasks as needed to keep each task testable, verifiable, and easy to implement.
  - Each task must have concrete acceptance criteria and explicit verification steps tied only to that task.
  - `Must touch files` should name the minimum expected surface; `May touch files` captures tightly bounded spillover only.
  - `Out of scope` must explicitly name tempting adjacent edits that are forbidden for this task.
  - `Stop if` must encode hard execution boundaries such as task-plan mismatch, cross-stack spillover, repeated verification failure, or missing prerequisite evidence.
  - Set `Session boundary after: yes` when the next task would be safer in a fresh Phase 3 session/chat, but remember this remains advisory and does not force an automatic stop.
  - If the task changes behavior or fixes a bug, `TDD Plan` MUST:
    - name the intended failing test (or test location) for **RED**
    - name the minimal implementation change for **GREEN**
    - name any cleanup target for **REFACTOR** (or `skip` if none)
  - `Verification Steps` MUST include at least one concrete automated command (test/lint/typecheck/etc.) that proves the acceptance criteria for that task.

No fixed task-count cap: optimize for atomicity and clarity over brevity.

Tracer bullet requirement:

- Task 1 (or Task 2) should be a tracer bullet that proves the end-to-end path for at least one MVP story.

## Changelog

- v0.1 (<today>): Initial tasks from PRD

---

## docs/index.md Update

After generating tasks v0.1:
Update Status column to:
Phase 2

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-2-1-task-generate.md
- @docs/prds/prd-WF-XXXX-<slug>.md

Create:

- docs/tasks/task-WF-XXXX-<slug>.md

Stop after writing v0.1.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 2.2 (tasks review gate): `@docs/workflow/phase-2-2-task-review.md`
2. If tasks are already crisp and minimal, proceed to Phase 3.1 (implementation): `@docs/workflow/phase-3-1-implement-tasks.md`
