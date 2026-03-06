# Phase 1.1 — Generate PRD (v0.1)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-1-1-prd-generate.md.
Do NOT modify this file during execution.

---

## Purpose

Convert an approved Brainstorm into a structured PRD (v0.1).

STOP after writing PRD v0.1.
No review in this step.

---

## Required Input

- docs/brainstorms/brainstorm-WF-XXXX-<slug>.md

Brainstorm must have:
Status: Draft Complete

Repo grounding note:
- If the PRD will rely on assumptions about the *current repo state* (existing endpoints, hardcoded flows, available exemplars, etc.), the brainstorm should already include a short `## Repo Reality Snapshot (Read-Only)` section produced during Phase 0.1 preflight.
- If that snapshot is missing *and* repo grounding is needed, STOP and route back to Phase 0.1 to add it to the brainstorm (then commit) before generating PRD v0.1. Do not “sneak in” new repo-derived facts directly into the PRD without capturing them upstream in the brainstorm.

Optional input (Type: page):
- If the brainstorm contains `## Appendix — Page Spec (MVP)`, incorporate it into the PRD flow/states/edge cases (do not expand scope beyond it).

---

## Phase Gate — Commit Previous Phase

Before generating the PRD, ensure the brainstorm you are converting is **saved and committed** (so PRD v0.1 is traceable to a stable brainstorm input).

---

## Phase Completion — Commit This Phase

After generating PRD v0.1, **save and commit** the updated PRD file before proceeding to Phase 1.2 risk audit.

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

- v0.1 (YYYY-MM-DD): Initial PRD from brainstorm

---

## Required PRD Structure

# WF-XXXX — <Title> PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: <today>

## 0. User Stories (MVP)

MVP only. Keep short but complete.

Format:
- US1: As a <user>, I want <capability>, so that <outcome>.

Also include:

## Deferred Stories (Not in MVP)

## 1. In Scope

## 2. Out of Scope

## 3. User / System Flow

- Happy path
- 2–3 failure paths

Traceability rule:

- Every flow step should reference at least one story: `(US1)` / `(US2)` etc.

## 4. Functional Requirements

Traceability rule:

- Every requirement must reference the story(ies) it serves: `(US1)` / `(US2)` etc.
- Every requirement must have a stable ID: `FR1`, `FR2`, ...

Format:

- FR1 (US1): <requirement>

## 5. Data & API Contracts

- request/response shapes
- validation rules
- state transitions

Traceability rule:

- Contracts should reference the story(ies) that require them: `(US1)` / `(US2)` etc.
- Contracts should reference the requirement IDs they implement when feasible: `(FR1)` / `(FR2)` etc.

## 6. Components / Modules

- boundaries
- responsibilities
- design tree (dependencies + ordering)
- deep modules (small interface, lots hidden; stable public seams + responsibilities)
- suggested file paths (coarse; avoid per-line detail)

## 7. Edge Cases

Traceability rule:

- Edge cases should reference the impacted story/flow step when feasible: `(US1)` etc.

## 8. Testing Decisions (TDD)

TDD is required for behavior changes/bug fixes:

- test seams (public interfaces)
- what to mock (boundaries only)
- minimal test types per story/requirement (unit vs integration-ish)

## 9. Telemetry (Minimal)

## 10. Deferred / Not in MVP

## 11. Open Questions (if any)

## 12. Changelog

- v0.1 (<today>): Initial PRD from brainstorm

---

## docs/index.md Update

After generating PRD v0.1:
Update Status column to:
Phase 1

Do NOT mark Done.

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-1-1-prd-generate.md
- @docs/brainstorms/brainstorm-WF-XXXX-<slug>.md

Create:

- docs/prds/prd-WF-XXXX-<slug>.md

Stop after writing v0.1.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 1.2 (PRD risk audit): `@docs/workflow/phase-1-2-prd-risk-audit.md`
2. Do a quick PRD self-review for scope creep and missing flows, then revise PRD v0.1 before running the audit.
