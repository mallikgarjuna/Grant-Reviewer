# WF-0023 — Tier 2 Phase 4 Runner

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. Context & Purpose
Phase 4 (Implementation) lacks the strict Part A/B/C verification gates that protect Phases 1-3. We need to introduce `phase-4-run-implement.md` to force execution, verification, and walkthrough generation into distinct gated steps. We also need to document key code phrases and warn agents about context exhaustion.

## 2. Acceptance Criteria (AC)
- **AC1**: `docs/workflow/phase-4-run-implement.md` exists and requires execute -> verify -> walkthrough.
- **AC2**: The Phase 4 runner explicitly references `docs/workflow/phase-4-1-implement-tasks.md` for the underlying Task implementation loop.
- **AC3**: The Phase 4 runner explicitly instructs the agent to report verification evidence before creating the walkthrough.
- **AC4**: `docs/workflow/run-lifecycle-auto.md` explicitly lists `(Parts A, B, C)` for Phases 1-4.
- **AC5**: `docs/workflow/run-lifecycle-interactive.md` explicitly lists `(Parts A, B, C)` for Phases 1-4.
- **AC6**: Both lifecycle runners include a bold context-exhaustion warning and a recommendation to pause.
- **AC7**: `docs/workflow/README.md` natively defines `workflow preflight` and `verify workflow`.

## 3. Scope Boundaries
- **In Scope**: Creating `phase-4-run-implement.md`, editing `run-lifecycle-auto.md`, `run-lifecycle-interactive.md`, and `README.md`.
- **Out of Scope**: Editing the core implementation orchestrator `phase-4-1-implement-tasks.md`. Refactoring the spec/prd/task runners (this is deferred to WF-0024).

## 4. Technical Approach / Risks
- **Risk**: The Phase 4 runner might conflict with `phase-4-1-implement-tasks.md`.
- **Mitigation**: `phase-4-run-implement.md` will essentially be a "wrapper." Part A says "Do the work described in `phase-4-1-implement-tasks.md`". Part B says "Now stop, run tests, and ask the user if they'd like to do UI verification." Part C says "Now write the walkthrough." This separates the loop from the closure gates.

## Traceability Statement
- Derived directly from `spec-WF-0023-tier2-phase4.md` v1.0.
