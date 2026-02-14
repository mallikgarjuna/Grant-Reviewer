# Phase 1.3 — Revise Spec + Bump Version

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-1-3-spec-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Apply review feedback.
Bump version.
Lock spec for PRD phase.

---

## Required Inputs

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md
- Phase 1.2 review output

---

## Versioning Rules

When revising:

- v0.1 → v0.2 (or next)
- Update Last Updated
- Append changelog entry

Example:

## Changelog

- v0.1 (date): Initial spec
- v0.2 (date): Applied review edits

When spec is considered stable:
Set Status: Ready for PRD
Keep version (e.g., v1.0 if finalized)

---

## docs/index.md Update

When spec becomes stable (Ready for PRD):
Update Status column to:
Phase 1

Do NOT advance to Phase 2 until you decide to generate PRD.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-1-3-spec-revise.md

Apply review edits to:

- @docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

Bump version.
Update changelog.
If stable, mark Status: Ready for PRD.
Stop.
