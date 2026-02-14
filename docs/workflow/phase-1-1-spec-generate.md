# Phase 1.1 — Generate Spec (v0.1)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-1-1-spec-generate.md.
Do NOT modify this file during execution.

---

## Purpose

Convert brainstorm into a structured Spec (v0.1).

STOP after writing spec v0.1.
No review in this step.

---

## Required Inputs

- docs/brainstorm/brainstorm-WF-XXXX-<slug>.md
- docs/index.md (to confirm WF ID and paths)

---

## Output

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

Do NOT create new spec file if it already exists.
Update it only if Version = v0.0.

---

## Versioning Rules

Spec must include:

Version: v0.1  
Status: Draft  
Last Updated: YYYY-MM-DD

Changelog:

## Changelog

- v0.1 (YYYY-MM-DD): Initial spec from brainstorm

---

## Spec Structure

# WF-XXXX — <Title> Spec

Artifact: spec  
Version: v0.1  
Status: Draft  
Last Updated: <today>

## 1. Purpose

What this initiative enables.

## 2. User / System Context

Who interacts with this and in what situation.

## 3. Core Behavior

Primary action or capability.

## 4. In Scope

Explicit list.

## 5. Out of Scope

Strict exclusions.

## 6. Data & Dependencies

APIs, models, permissions (if known).

## 7. Edge Considerations

Known constraints or complexities.

(If page-type spec, include Desktop ASCII wireframe section.)

## Changelog

- v0.1 (<today>): Initial spec from brainstorm

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-1-1-spec-generate.md
- @docs/brainstorm/brainstorm-WF-XXXX-<slug>.md

Create or update:

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

Stop after writing v0.1.
