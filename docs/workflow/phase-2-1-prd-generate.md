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

## Output

- docs/prd/prd-WF-XXXX-<slug>.md

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

- docs/prd/prd-WF-XXXX-<slug>.md

Stop after writing v0.1.
