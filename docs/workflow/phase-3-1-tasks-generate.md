# Phase 3.1 — Generate Tasks (v0.1)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-3-1-tasks-generate.md.
Do NOT modify this file during execution.

---

## Purpose

Convert an approved PRD into an ordered, implementation-ready task list (v0.1).

STOP after generating tasks v0.1.
No review in this step.

---

## Required Input

- docs/prd/prd-WF-XXXX-<slug>.md

PRD must have:
Status: Ready for Tasks

Do NOT derive tasks from spec or brainstorm.

---

## Output

- docs/tasks/tasks-WF-XXXX-<slug>.md

Only generate if Version = v0.0.

---

## Versioning Rules

Tasks file must include:

Artifact: tasks  
Version: v0.1  
Status: Draft  
Last Updated: YYYY-MM-DD

Include:

## Changelog

- v0.1 (YYYY-MM-DD): Initial task breakdown from PRD

---

## Required Tasks Structure

# WF-XXXX — <Title> Tasks

Artifact: tasks  
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
Phase 3

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-3-1-tasks-generate.md
- @docs/prd/prd-WF-XXXX-<slug>.md

Create:

- docs/tasks/tasks-WF-XXXX-<slug>.md

Stop after writing v0.1.
