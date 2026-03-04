# WF-0053 — Contract Boundary Governance Enforcement Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-04

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: fail-closed governance gate for one boundary trigger

Goal:
Prove end-to-end governance coupling for one boundary trigger class by failing deterministically when required evidence is missing.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
- `backend/scripts/check_contract_boundary_governance.py`
- `backend/tests/scripts/test_check_contract_boundary_governance.py`
- `.github/workflows/ci.yml`
Acceptance Criteria:
- Governance checker detects at least one trigger class (`request_boundary_contract_surface`) from changed paths.
- Missing required evidence bundle causes deterministic hard failure with explicit missing bundle IDs.
- CI runs the governance checker in backend lane and fails closed on checker failure.
TDD Plan:
- RED: Add failing tests in `backend/tests/scripts/test_check_contract_boundary_governance.py` for missing required evidence under a triggered change.
- GREEN: Implement minimal trigger detection + required-bundle enforcement and wire checker invocation in CI.
- REFACTOR: Extract reusable constants for trigger and bundle IDs.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_tracer_missing_evidence_fails"`
- `rg -n "check_contract_boundary_governance|wf0053" .github/workflows/ci.yml`
Risks (if any): CI wiring differences across jobs may require lane-specific command normalization.

### [x] Task 2 — Freeze full trigger inventory and deterministic path mapping

Goal:
Expand governance checker from tracer scope to full PRD trigger inventory with explicit path-mapped classes.
Slice: trigger-inventory-hardening
User Stories: US1
PRD Requirements: FR1, FR1a
Depends on: 1
Enables: 4
Parallelizable: no
Files to modify:
- `backend/scripts/check_contract_boundary_governance.py`
- `backend/tests/scripts/test_check_contract_boundary_governance.py`
Acceptance Criteria:
- Checker supports all frozen classes: `request_boundary_contract_surface`, `contract_gate_selector_surface`, `ci_contract_gate_wiring_surface`, `workflow_traceability_surface`.
- Trigger detection uses explicit path rules only and is deterministic.
- Untriggered diffs produce deterministic no-trigger result.
TDD Plan:
- RED: Add failing per-class trigger tests plus a no-trigger case in `test_check_contract_boundary_governance.py`.
- GREEN: Implement explicit path-map logic for each trigger class.
- REFACTOR: Normalize path-rule table and matching helpers.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_trigger_inventory"`
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_no_trigger_path"`
Risks (if any): Over-broad path patterns can create false positives if not tightly scoped.

### [x] Task 3 — Enforce mandatory evidence bundle IDs with deterministic diagnostics

Goal:
Lock bundle contract IDs and ensure deterministic error messaging for missing evidence.
Slice: evidence-contract-hardening
User Stories: US1, US2
PRD Requirements: FR2, FR2a, FR3, FR4
Depends on: 1
Enables: 4
Parallelizable: no
Files to modify:
- `backend/scripts/check_contract_boundary_governance.py`
- `backend/tests/scripts/test_check_contract_boundary_governance.py`
Acceptance Criteria:
- Required bundle IDs are exactly `contract_gate_evidence`, `artifact_traceability_evidence`, `negative_smoke_evidence`.
- Missing bundle failures include stable reason code/message plus explicit missing bundle IDs.
- Diagnostics remain deterministic for multiple missing bundles.
TDD Plan:
- RED: Add failing tests for single/multiple missing bundles and stable diagnostic formatting.
- GREEN: Implement fixed bundle-ID validation and deterministic diagnostic rendering.
- REFACTOR: Isolate diagnostic formatting helper for stable ordering.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_missing_bundle_diagnostics"`
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_required_bundle_ids"`
Risks (if any): Non-deterministic set ordering could leak into diagnostics without explicit sorting.

### [ ] Task 4 — Marker/selector governance coupling and strict-marker guard

Goal:
Ensure governance gate covers marker/selector drift surfaces and preserves strict-marker invariant.
Slice: selector-marker-guard
User Stories: US3
PRD Requirements: FR5, FR6
Depends on: 2, 3
Enables: 5
Parallelizable: no
Files to modify:
- `backend/tests/scripts/test_check_contract_boundary_governance.py`
- `backend/scripts/check_contract_boundary_governance.py`
Acceptance Criteria:
- Changes to selector/marker surfaces trigger governance bundle checks.
- Unregistered marker usage still hard-fails under strict-marker behavior.
- Governance checker validates coupling expectations for selector/marker trigger class.
TDD Plan:
- RED: Add failing governance tests for selector/marker trigger class and strict-marker regression case.
- GREEN: Extend trigger map and coupling logic for selector/marker surfaces.
- REFACTOR: Consolidate selector/marker trigger constants.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_selector_marker_trigger"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate --strict-markers -q`
Risks (if any): Marker namespace edits may affect unrelated test suites if not isolated.

### [ ] Task 5 — Assertion-safe negative CI smoke for fail-closed proof

Goal:
Add one deterministic negative smoke that proves missing-coupling conditions fail as expected without destabilizing normal CI semantics.
Slice: negative-smoke-proof
User Stories: US1, US3
PRD Requirements: FR7
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
- `.github/workflows/ci.yml`
- `backend/tests/scripts/test_check_contract_boundary_governance.py`
Acceptance Criteria:
- CI includes exactly one assertion-style negative smoke path for missing-coupling proof.
- Smoke asserts expected failure reason code/message and passes only when expected failure is observed.
- Normal governance pass path remains unchanged.
TDD Plan:
- RED: Add failing test that expects specific reason code/message for a controlled missing-coupling scenario.
- GREEN: Wire negative smoke command/assertion in CI and checker output contract.
- REFACTOR: Reuse shared assertion helper for smoke verdict parsing.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_check_contract_boundary_governance.py -k "wf0053_contract_negative_smoke_reason"`
- `rg -n "negative_smoke|wf0053|check_contract_boundary_governance" .github/workflows/ci.yml`
Risks (if any): Incorrect smoke assertion polarity can produce false-green CI behavior.

### [ ] Task 6 — Add bounded compatibility matrix extension + traceability evidence

Goal:
Add one targeted omitted-vs-explicit-default digest-equivalence case across `stage_gating`, `prompt_knobs`, and `reviewer_policy`, and capture traceability evidence.
Slice: compatibility-extension
User Stories: US4
PRD Requirements: FR8, FR9, FR10
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
- `backend/tests/engine/test_review_request_contracts.py`
- `backend/tests/fixtures/wf_0052_compatibility_matrix.yaml`
- `docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md`
Acceptance Criteria:
- One new deterministic matrix case covers all three surfaces and asserts digest equivalence behavior.
- Contract test selector for the new case is stable and WF-0053 namespaced.
- Walkthrough records evidence and confirms governance-only scope with no runtime semantic changes.
TDD Plan:
- RED: Add failing WF-0053 compatibility selector test using new fixture case.
- GREEN: Add minimal fixture data and test wiring to satisfy the case.
- REFACTOR: Normalize fixture naming/loader usage for consistency with existing compatibility tests.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0053_contract_compat_omitted_vs_explicit_default_three_surface"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0053_contract_compat_omitted_vs_explicit_default_three_surface or wf0049_contract_scope_pipeline_semantics_stable"`
- `rg -n "wf0053_contract_compat_omitted_vs_explicit_default_three_surface|governance-only" docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md`
Risks (if any): Existing matrix schema assumptions may need minor alignment for the additional case id.

## Changelog

- v0.1 (2026-03-04): Initial task breakdown from PRD.
- v0.2 (2026-03-04): Applied review edits: removed unnecessary `pytest.ini` touch from Task 4, tightened tracer requirement mapping, and added runtime-semantics regression verification to Task 6; marked Ready for Implementation.
