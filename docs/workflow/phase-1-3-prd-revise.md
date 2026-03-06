# Phase 1.3 — Revise PRD + Bump Version + Log Decisions

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-1-3-prd-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Apply Risk Audit edits.
Bump version.
Log decisions.
Stabilize PRD for Task phase.

---

## Required Inputs

- docs/prds/prd-WF-XXXX-<slug>.md
- Phase 1.2 review output

---

## Phase Gate — Commit Previous Phase

Before revising the PRD, ensure the Phase 1.2 audit output has been captured in chat and the current PRD is **saved**. After revisions, commit the updated PRD (and any logged decisions) before moving to Phase 2.

---

## Phase Completion — Commit This Phase

After revising the PRD, bumping version, and logging decisions, ensure all updated files are **saved and committed** before starting Phase 3.

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

Stability checklist (must be true before Ready for Tasks):

- User Stories (MVP) exist and map to flows/requirements
- US# traceability exists in flows/reqs/contracts (no orphan requirements)
- Design tree + deep modules are plausible (no hand-wavy “magic modules”)
- Testing Decisions exist (TDD seams + boundary mocking rules)

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
Phase 1 (Ready)

Do NOT advance to Phase 3 until you explicitly generate Tasks.

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-1-3-prd-revise.md

Apply edits to:

- @docs/prds/prd-WF-XXXX-<slug>.md

Also update:

- @docs/logs/decisions.md

Bump version.
Append changelog.
If stable, mark Status: Ready for Tasks.
Stop.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 2.1 (generate tasks v0.1): `@docs/workflow/phase-2-1-task-generate.md`
   - **Provide an explicit, copy-pasteable prompt block** for the user to start this phase.
2. Re-run Phase 1.2 (PRD risk audit) to validate the revised PRD: `@docs/workflow/phase-1-2-prd-risk-audit.md`
