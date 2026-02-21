# WF-0023 — Tier 2 Phase 4 Runner

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-21

## 1. Context
Create the strict Phase 4 orchestrator, add safety warnings to lifecycles, and document the missing code phrases (Tier 2 scope).

## 2. Tasks

### [x] Task 1.0: Create Phase 4 Runner (`docs/workflow/phase-4-run-implement.md`)
- [x] Create `docs/workflow/phase-4-run-implement.md`.
- [x] Define Part A (Execution Loop) using the existing `phase-4-1-implement-tasks.md`.
- [x] Define Part B (Verification Gate) requiring the agent to stop, run tests/checks, and ask user for a UI manual test signal if applicable.
- [x] Define Part C (Walkthrough Gate) requiring the agent to write the walkthrough only *after* Part B is approved.
- [x] Add the standard `How to Invoke in Chat` section with the prompt template.
- [x] Add this new runner to the `how-to-use-workflow-actions.md` cheat-sheet.

### [x] Task 2.0: Update Lifecycle Runners
- [x] Edit `docs/workflow/run-lifecycle-auto.md`:
  - Enforce `(Parts A, B, C)` on Phases 1, 2, 3, and 4.
  - Add bold warning: **Context Limit Warning**: If context feels heavy after Phase 3, stop and advise user to start a new chat for Phase 4.
- [x] Edit `docs/workflow/run-lifecycle-interactive.md`:
  - Enforce `(Parts A, B, C)` on Phases 1, 2, 3, and 4.
  - Add the same bold **Context Limit Warning**.

### [ ] Task 3.0: Document Code Phrases in `AGENTS.md` and `README.md`
- [ ] In `AGENTS.md` section `Code phrases`, ensure `workflow preflight` and `verify workflow` are mentioned (done in base).
- [ ] In `docs/workflow/README.md`, under a new `## Glossary / Code Phrases` section (or equivalent), explicitly define:
  - `verify workflow`: status, diff, lint/build checks, pass/fail summary.
  - `workflow preflight`: review of closure state, artifact bounds, readiness for next WF.

## Traceability Statement
- Derived directly from `prd-WF-0023-tier2-phase4.md` v1.0.
