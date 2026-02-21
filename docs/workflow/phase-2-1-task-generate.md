# Phase 2.1 — Generate Tasks (v0.1)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-2-1-task-generate.md.
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

Do NOT derive tasks from spec or brainstorm.

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

For each task include:

### Task 1 — <short title>

Goal:
Files to modify:
Acceptance Criteria:
Verification Steps:
Risks (if any):

Tasks must:

- Be sequential
- Respect dependencies
- Avoid scope expansion
- Be minimal for MVP

Max 5–15 tasks.

## Changelog

- v0.1 (<today>): Initial tasks from PRD

---

## docs/index.md Update

After generating tasks v0.1:
Update Status column to:
Phase 2

---

## How to Invoke in Codex Chat

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
2. If tasks are already crisp and minimal, proceed to Phase 4.1 (implementation): `@docs/workflow/phase-4-1-implement-tasks.md`
