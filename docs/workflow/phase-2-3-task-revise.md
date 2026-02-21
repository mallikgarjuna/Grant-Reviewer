# Phase 2.3 — Revise Tasks + Bump Version

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-2-3-task-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Apply review edits.
Bump version.
Finalize task list for implementation.

---

## Required Inputs

- docs/tasks/task-WF-XXXX-<slug>.md
- Phase 2.2 review output

---

## Phase Gate — Commit Previous Phase

Before revising the task plan, ensure the Phase 2.2 review output has been captured in chat and the current task file is **saved**. After revisions, commit the updated task file before starting Phase 3.

---

## Phase Completion — Commit This Phase

After revising the task file, bumping version, and marking it ready, ensure the updated task file is **saved and committed** before starting Phase 3.

---

## Versioning Rules

When revising:

- v0.1 → v0.2 (or next)
- Update Last Updated
- Append changelog entry

Example:

## Changelog

- v0.1 (date): Initial tasks
- v0.2 (date): Applied review edits

When stable:
Set:
Status: Ready for Implementation
Optionally bump to v1.0.

---

## docs/index.md Update

When tasks are Ready for Implementation:
Update Status column to:
Phase 2 (Ready)

Do NOT mark Done yet.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-2-3-task-revise.md

Apply edits to:

- @docs/tasks/task-WF-XXXX-<slug>.md

Bump version.
Append changelog.
If stable, mark Status: Ready for Implementation.
Stop.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 3.1 (implement tasks): `@docs/workflow/phase-3-1-implement-tasks.md`
   - **Provide an explicit, copy-pasteable prompt block** for the user to start this phase.
2. Re-run Phase 2.2 (tasks review gate) to validate the revised task list: `@docs/workflow/phase-2-2-task-review.md`
