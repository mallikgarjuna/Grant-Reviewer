# Phase 1.2 — PRD Risk Audit (No Edits)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-1-2-prd-risk-audit.md.
Do NOT modify this file during execution.

---

## Purpose

Critically evaluate PRD before moving to Tasks.

This step MUST NOT edit any files.

---

## Required Input

- docs/prds/prd-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before running the risk audit, ensure the PRD draft being audited is **saved and committed** (so audit findings map to a specific PRD version).

---

## Phase Completion — Commit This Phase

Phase 1.2 produces audit output in chat only (no file edits). If you made no file changes, there is nothing to commit for this phase.

---

## Output (in chat only)

1. Use review range `main...HEAD` by default (unless the user explicitly requests a narrower range).
2. Execute `@docs/workflow/util-adversarial-diff-audit.md` with profile `planning`.
3. Fail-closed rule: do not consider this gate complete unless output includes all five required sections and explicit coverage of the six mandatory focus areas.
4. Keep PRD-specific rigor: include exact PRD edit guidance where findings exist.
5. Do NOT edit files.
