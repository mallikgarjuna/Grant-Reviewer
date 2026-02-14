# Phase 1.2 — Spec Review Gate (No Edits)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-1-2-spec-review.md.
Do NOT modify this file during execution.

---

## Purpose

Critically evaluate spec before moving to PRD.

This step MUST NOT edit any files.

---

## Required Input

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before running the spec review gate, ensure the spec draft being reviewed is **saved and committed** (so review feedback maps cleanly to a specific spec version).

---

## Phase Completion — Commit This Phase

Phase 1.2 produces review output in chat only (no file edits). If you made no file changes, there is nothing to commit for this phase.

---

## Output (in chat only)

Return:

1. Top 5 clarity gaps
2. Scope creep risks
3. Missing definitions
4. Over-engineering warnings
5. Exact edits required (section + change)
6. Next 2 actions I should take (choose one)

Max 100 lines.
Be strict about MVP.

Do NOT edit files.
