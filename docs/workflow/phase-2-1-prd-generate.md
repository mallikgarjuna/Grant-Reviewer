# Phase 2.1 — Generate PRD (v0.1)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-2-1-prd-generate.md.
Do NOT modify this file during execution.

---

## Purpose

Convert an approved Spec into a structured PRD (v0.1).

STOP after writing PRD v0.1.
No review in this step.

---

## Required Input

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

Spec must have:
Status: Ready for PRD

Do NOT use brainstorm files.

---

## Phase Gate — Commit Previous Phase

Before generating the PRD, ensure the spec you are converting is **saved and committed** (so PRD v0.1 is traceable to a stable spec input).

---

## Phase Completion — Commit This Phase

After generating PRD v0.1, **save and commit** the updated PRD file before proceeding to Phase 2.2 risk audit.

---

## Output

- docs/prds/prd-WF-XXXX-<slug>.md

Do NOT create a new PRD file if it exists.
Only generate if Version = v0.0.

---

## Versioning Rules

PRD must include:

Artifact: prd  
Version: v0.1  
Status: Draft  
Last Updated: YYYY-MM-DD

Include:

## Changelog

- v0.1 (YYYY-MM-DD): Initial PRD from spec

---

## Required PRD Structure

# WF-XXXX — <Title> PRD

Artifact: prd  
Version: v0.1  
Status: Draft  
Last Updated: <today>

## 1. In Scope

## 2. Out of Scope

## 3. User / System Flow

- Happy path
- 2–3 failure paths

## 4. Functional Requirements

## 5. Data & API Contracts

- request/response shapes
- validation rules
- state transitions

## 6. Components / Modules

- boundaries
- responsibilities
- suggested file paths

## 7. Edge Cases

## 8. Telemetry (Minimal)

## Deferred / Not in MVP

## Open Questions (if any)

## Changelog

- v0.1 (<today>): Initial PRD from spec

---

## docs/index.md Update

After generating PRD v0.1:
Update Status column to:
Phase 2

Do NOT mark Done.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-2-1-prd-generate.md
- @docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

Create:

- docs/prds/prd-WF-XXXX-<slug>.md

Stop after writing v0.1.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 2.2 (PRD risk audit): `@docs/workflow/phase-2-2-prd-risk-audit.md`
2. Do a quick PRD self-review for scope creep and missing flows, then revise PRD v0.1 before running the audit.
