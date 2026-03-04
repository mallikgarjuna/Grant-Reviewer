# WF-0053 — Contract Boundary Governance Enforcement PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-04

## 0. User Stories (MVP)

- US1: As a release owner, I want boundary-affecting changes to fail in CI unless required governance evidence is present, so that merge safety stays fail-closed.
- US2: As a contributor touching contract boundaries, I want deterministic failure messages that name missing evidence, so that remediation is objective and fast.
- US3: As a CI maintainer, I want strict-marker and contract-gate invariants preserved when policy expands, so that selector drift cannot silently bypass checks.
- US4: As a maintainer, I want one targeted compatibility matrix extension proving omitted-vs-explicit-default digest equivalence across `stage_gating`, `prompt_knobs`, and `reviewer_policy`, so that compatibility hardening remains bounded and auditable.

## Deferred Stories (Not in MVP)

- DS1: Runtime pipeline behavior or endpoint semantics changes.
- DS2: Broad producer realism expansion beyond one targeted equivalence case.
- DS3: Contract model redesign or snapshot version evolution.

## 1. In Scope

- Define canonical boundary-change trigger classes in governance policy and enforce required evidence coupling for those classes in CI/PR checks. (US1, US2)
- Keep enforcement fail-closed: missing required coupling must fail deterministically. (US1, US2)
- Preserve strict-marker and existing contract-gate baseline behavior as required invariants. (US3)
- Add one deterministic negative CI smoke proving policy fails when coupling is missing. (US1, US3)
- Add one targeted WF-0052 compatibility matrix case for omitted-vs-explicit-default digest equivalence across the three identified surfaces. (US4)
- Keep this workflow bounded to governance and compatibility hardening only. (US1-US4)

## 2. Out of Scope

- Changes to runtime review execution behavior, output semantics, or API product behavior.
- New frontend surfaces or user-facing product flows.
- Broad compatibility matrix expansion beyond one targeted case.
- Any relaxation of strict-marker enforcement.

## 3. User / System Flow

- Happy path:
1. Contributor changes an in-scope contract boundary file and opens a PR. (US1)
2. Boundary-trigger policy identifies the change class and computes required evidence bundle for that PR. (US1, US2)
3. PR contains required coupling evidence (contract-gate execution evidence and required workflow artifacts). (US1, US2)
4. CI executes strict-marker + contract-gate checks and governance coupling checks; all pass. (US1, US3)
5. PR is merge-eligible with auditable policy evidence preserved. (US1)

- Failure path A (missing required artifact coupling):
1. Contributor changes boundary file but omits one required artifact update/evidence item. (US1, US2)
2. Governance check fails with deterministic message naming missing item(s). (US2)
3. Merge remains blocked until missing evidence is added. (US1)

- Failure path B (marker/selector drift):
1. Boundary governance change introduces unregistered marker or invalid selector usage. (US3)
2. `--strict-markers` contract-gate path fails in CI as hard stop. (US3)

- Failure path C (negative smoke proof):
1. Negative smoke intentionally executes a missing-coupling scenario in CI validation path. (US1, US3)
2. Check fails deterministically, proving fail-closed governance behavior. (US1)

## 4. Functional Requirements

- FR1 (US1): The workflow shall define a canonical boundary-change trigger map for governance enforcement.
- FR1a (US1): The initial canonical trigger inventory is frozen to these classes: request-boundary contract models/validators, contract-gate selector/marker surfaces, CI contract-gate invocation wiring, and workflow traceability artifacts.
- FR2 (US1, US2): For each trigger class, the workflow shall define a mandatory evidence bundle that must be present in the same PR.
- FR2a (US1, US2): Mandatory evidence bundle IDs are frozen for MVP as `contract_gate_evidence`, `artifact_traceability_evidence`, and `negative_smoke_evidence`.
- FR3 (US1, US2): Governance checks shall fail closed when required evidence is missing for triggered classes.
- FR4 (US2): Governance check output shall provide deterministic, actionable missing-evidence diagnostics.
- FR5 (US3): Existing contract-gate strict-marker enforcement shall remain mandatory and unchanged in strictness.
- FR6 (US3): Contract-gate invocation wiring in CI shall remain explicit and covered by governance policy when boundary selector surfaces change.
- FR7 (US1, US3): CI shall include one deterministic negative smoke demonstrating missing-coupling failure semantics.
- FR8 (US4): Compatibility matrix shall include one omitted-vs-explicit-default digest-equivalence case spanning `stage_gating`, `prompt_knobs`, and `reviewer_policy`.
- FR9 (US4): The added compatibility case shall be deterministic and auditable in workflow artifacts.
- FR10 (US1-US4): Scope guard shall prevent introducing runtime behavior changes under this WF.

## 5. Data & API Contracts

- C1 (US1, FR1, FR1a, FR2): Governance trigger contract:
  - Input: changed file paths in PR diff.
  - Trigger classes (frozen for MVP):
    - `request_boundary_contract_surface`: files under request-boundary model/validator surfaces (for example `backend/app/engine/contracts.py`, `backend/app/engine/review_request_validator.py`).
    - `contract_gate_selector_surface`: contract-gate test selector/marker surfaces (for example `backend/tests/engine/test_review_request_contracts.py`, `backend/pytest.ini`).
    - `ci_contract_gate_wiring_surface`: CI invocation wiring (for example `.github/workflows/ci.yml`).
    - `workflow_traceability_surface`: WF task and walkthrough artifact files for WF-0053.
  - Output: list of triggered classes + required evidence bundle IDs.
  - Behavior: deterministic map by explicit path rules only; no heuristic-only fallback.

- C2 (US1, US2, FR2, FR2a, FR3, FR4): Required evidence bundle contract:
  - `contract_gate_evidence`: CI execution evidence for contract-gate path including strict-marker behavior.
  - `artifact_traceability_evidence`: required workflow artifact updates for the triggered boundary class (`docs/tasks/task-WF-0053-...` and `docs/walkthroughs/walkthrough-WF-0053-...` when governance surfaces are changed).
  - `negative_smoke_evidence`: deterministic proof artifact from one missing-coupling failure scenario.
  - Missing any required bundle item -> deterministic fail status with explicit missing bundle IDs.

- C3 (US3, FR5, FR6): Marker/selector guard contract:
  - Contract-gate test execution uses strict marker validation.
  - Unregistered marker usage is hard-fail.
  - Selector or marker namespace updates on boundary surfaces are governed by coupling policy.

- C4 (US1, US3, FR7): Negative smoke contract:
  - Simulate/validate one missing-coupling scenario by intentionally withholding one required evidence bundle in a controlled check path.
  - Expected outcome: deterministic failure verdict with explicit reason code/message.
  - Safety: smoke check is assertion-style so successful CI run requires proving the negative case fails as expected.

- C5 (US4, FR8, FR9): Compatibility extension contract:
  - One new matrix case verifies digest equivalence between omitted optional defaults and explicit defaults across `stage_gating`, `prompt_knobs`, `reviewer_policy`.
  - Case has stable identifier, expected outcome, and artifact traceability.

State transitions:
- `pr_opened` -> `trigger_evaluated` -> `evidence_validated` -> `merge_eligible`
- failure terminals:
  - `failed_missing_evidence`
  - `failed_marker_guard`
  - `failed_negative_smoke_expected` (for proof lane)

## 6. Components / Modules

- CI workflow policy layer (`.github/workflows/ci.yml`)
  - Enforce contract-gate + governance coupling checks and negative smoke integration. (FR3, FR5-FR7)
- Boundary governance check module/script (existing or new bounded utility)
  - Resolve triggers and required evidence bundles with deterministic diagnostics. (FR1-FR4)
- Contract/compatibility test surfaces (`backend/tests/engine/test_review_request_contracts.py` and associated fixtures)
  - Preserve strict-marker invariants and add one targeted compatibility matrix case. (FR5, FR8, FR9)
- Workflow artifacts (`docs/tasks/...`, `docs/walkthroughs/...`)
  - Maintain explicit traceability evidence for boundary-affecting changes. (FR2, FR9)

Design tree (dependencies + ordering):
1. Freeze trigger map and required evidence bundle definitions. (FR1, FR2)
2. Implement fail-closed governance check and deterministic diagnostics. (FR3, FR4)
3. Integrate with CI while preserving strict-marker contract-gate invariants. (FR5, FR6)
4. Add deterministic negative smoke proof. (FR7)
5. Add one bounded compatibility matrix extension and traceability evidence. (FR8, FR9)
6. Verify scope guard (no runtime behavior changes). (FR10)

Deep modules:
- Trigger/evidence policy is a small public surface with hidden mapping logic.
- CI invocation is explicit and stable; policy internals remain encapsulated.
- Compatibility evidence remains fixture-driven and deterministic.

Suggested file paths (coarse):
- `.github/workflows/ci.yml`
- `backend/tests/engine/test_review_request_contracts.py`
- `backend/tests/engine/fixtures/` (if required by targeted case)
- `docs/tasks/task-WF-0053-contract-boundary-governance-enforcement.md`
- `docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md`

## 7. Edge Cases

- E1 (US1, US2): PR touches both boundary and non-boundary files; policy still enforces only boundary-triggered evidence requirements.
- E2 (US2, US3): Boundary changes update selectors but miss marker registration updates; strict-marker fail path catches drift.
- E3 (US1): Trigger map too broad causes false positives; diagnostics must identify exact trigger class.
- E4 (US1): Trigger map too narrow misses real boundary changes; governance audit must include explicit trigger inventory.
- E5 (US4): Digest-equivalence case passes for two surfaces but fails on one; matrix evidence must isolate failing surface deterministically.

## 8. Testing Decisions (TDD)

- TDD rule: behavior changes start with failing tests/checks (RED), then minimal implementation (GREEN), then refactor.
- Seam S1 (US1, US2; FR1-FR4): Governance trigger/evidence mapping tests.
  - Validate trigger class detection and missing-evidence failures.
  - Include positive and negative cases for each frozen trigger class.
  - Boundary-only mocks; no mocking of CI runner semantics.
- Seam S2 (US3; FR5, FR6): Marker/selector guard tests.
  - Prove strict-marker hard-fail on unregistered marker usage.
  - Prove selector-wiring governance check fails when coupling requirements are unmet.
- Seam S3 (US1, US3; FR7): Negative smoke proof.
  - Deterministic CI-path test/check that intentionally omits required coupling and must fail.
  - Assert expected failure reason code/message to prove fail-closed semantics, not generic failure.
- Seam S4 (US4; FR8, FR9): Compatibility extension test.
  - Add one deterministic omitted-vs-explicit-default digest-equivalence case across all three surfaces.
  - Include a no-trigger-path prove-it test showing non-boundary-only PR changes do not require governance bundles.

Minimal test types per story:
- US1: integration-ish governance policy tests + CI wiring smoke.
- US2: unit tests for deterministic missing-evidence diagnostics.
- US3: integration-ish strict-marker/selector guard tests.
- US4: integration-ish compatibility fixture test for three-surface digest equivalence.

## 9. Telemetry (Minimal)

- Count governance check failures by trigger class and missing-evidence type.
- Count strict-marker failure incidents in contract-gate lane.
- Track negative smoke execution status as policy health signal.

## 10. Deferred / Not in MVP

- Expansion of boundary trigger map beyond current contract boundary surfaces.
- Multiple compatibility classes beyond the one targeted equivalence case.
- Any changes to runtime validation order or endpoint response semantics.

## 11. Open Questions (if any)

- None blocking for Phase 2 task generation.

## 12. Changelog

- v0.1 (2026-03-04): Initial PRD from brainstorm.
- v0.2 (2026-03-04): Applied risk-audit edits: frozen trigger inventory, explicit required evidence bundle IDs, assertion-safe negative smoke contract, expanded TDD prove-it coverage, and marked Ready for Tasks.
