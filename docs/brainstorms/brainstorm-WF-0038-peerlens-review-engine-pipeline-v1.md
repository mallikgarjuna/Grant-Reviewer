# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: brainstorm
Version: v0.1
Status: In progress
Last Updated: 2026-02-28

## Objective

Design a universal, call-agnostic Grant Review Engine Pipeline that works across NWO / ERC / MSCA with **no funder-specific branching** in the engine. All variability lives in declarative call configuration. The engine produces `DiagnosticFinding v1` as its atomic output.

## Inputs / Current Truth

- Source of truth (architecture snapshot): `docs/reference/architecture_chat.md`
- Evaluation terminology: use “evaluation criteria/elements” (not “rubric”)

## Locked Decisions (Snapshot)

- Product identity: surgical pre-submission diagnostic tool; optimized for researcher trust.
- v1 scope: section-level diagnostics first (no full-proposal engine yet).
- Output philosophy: analytical-only findings (problem + why + fix direction), no rewriting; traceable to expectations; precision/traceability > performance/flash.
- Qualitative evaluation is primary; numerical scoring is optional/secondary and isolated (must not contaminate core logic).
- One canonical, call-agnostic engine: calls define WHAT; engine defines HOW; modes define WHICH components are activated; extend via configuration, not mutation; atomic output is `DiagnosticFinding v1`.

## Decisions Approved (This Chat, 2026-02-28)

1. `DiagnosticFinding v1` is **trace-first** (required traceability/determinism fields).
2. Interactive Q&A format is standardized: each question includes explicit options + assistant recommendation.
3. WF-tagging discipline: all architecture decisions + Q&A entries are tagged with the WF id.
4. Adversarial critique standard: 3 risks must cover (a) config authoring, (b) runtime execution, (c) downstream consumption/governance; each risk must include a recommended mitigation/guardrail.
5. Call-agnostic pipeline v1: **two-pass** model (Pass 1 normalized observations; Pass 2 maps observations → `DiagnosticFinding v1`).

## Exit Criteria (Status)

Already satisfied (principle-level):
- WHAT vs HOW separation is stated and treated as a core design constraint.
- Scoring is explicitly isolated/optional (no contamination of core evaluation).

Missing / not yet frozen:
- `DiagnosticFinding v1` schema is frozen (constraints specified precisely enough to implement without further architecture decisions).
- Call-agnostic pipeline v1 is fully defined (stage contracts + required artifacts across both passes).
- Adversarial stress test finds no structural contradictions (for at least NWO / ERC / MSCA configurations).
- Implementation blueprint can be described without new architecture decisions.

## Next Architectural Decisions (Queue)

- Freeze `DiagnosticFinding v1` field-level constraints (required vs optional, enums, referential integrity expectations).
- Define “Observation” contract/vocabulary and its determinism/trace guarantees (Pass 1 output).
- Specify how call configuration declares expectations, constraints, and evaluation criteria/elements (WHAT) without encoding funder-specific semantics.
- Define execution profiles (modes) as activation sets over the two-pass pipeline.
- Map `DiagnosticFinding v1` to the existing `ReviewCard` surface (downstream compatibility contract).
