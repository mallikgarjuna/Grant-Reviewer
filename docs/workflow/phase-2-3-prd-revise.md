# Phase 2.3 — Revise PRD + Bump Version + Log Decisions

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-2-3-prd-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Apply Risk Audit edits.
Bump version.
Log decisions.
Stabilize PRD for Task phase.

---

## Required Inputs

- docs/prd/prd-WF-XXXX-<slug>.md
- Phase 2.2 review output

---

## Versioning Rules

When revising:

- v0.1 → v0.2 (or next)
- Update Last Updated
- Append to Changelog

Example:

## Changelog

- v0.1 (date): Initial PRD
- v0.2 (date): Applied risk audit edits

When PRD is stable:
Set:
Status: Ready for Tasks
Optionally bump to v1.0 if fully locked.

---

## Decision Logging

Update:

docs/logs/decisions.md

For each major decision:

- Date:
- WF ID:
- Context:
- Decision:
- Why:
- Tradeoff:

Log only decisions that affect:

- Architecture
- API contracts
- Scope
- Data model

---

## docs/index.md Update

When PRD becomes Ready for Tasks:
Update Status column to:
Phase 2 (Ready)

Do NOT advance to Phase 3 until you explicitly generate Tasks.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-2-3-prd-revise.md

Apply edits to:

- @docs/prd/prd-WF-XXXX-<slug>.md

Also update:

- @docs/logs/decisions.md

Bump version.
Append changelog.
If stable, mark Status: Ready for Tasks.
Stop.
