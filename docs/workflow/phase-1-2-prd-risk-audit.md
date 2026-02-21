# Phase 1.2 — PRD Risk Audit (No Edits)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-1-2-prd-risk-audit.md.
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

Return:

1. Top 5 MVP risks (ranked)
2. Missing decisions (recommend defaults)
3. Scope creep warnings
4. Implementation landmines
5. Exact edits required (section + change)
6. Next 2 actions I should take (choose one)

Max 120 lines.
Be strict about MVP and fast shipping.

Do NOT edit files.
