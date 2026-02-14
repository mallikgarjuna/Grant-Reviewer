# Phase 3.3 — Revise Tasks + Bump Version

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-3-3-tasks-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Apply review edits.
Bump version.
Finalize task list for implementation.

---

## Required Inputs

- docs/tasks/tasks-WF-XXXX-<slug>.md
- Phase 3.2 review output

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
Phase 3 (Ready)

Do NOT mark Done yet.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-3-3-tasks-revise.md

Apply edits to:

- @docs/tasks/tasks-WF-XXXX-<slug>.md

Bump version.
Append changelog.
If stable, mark Status: Ready for Implementation.
Stop.
