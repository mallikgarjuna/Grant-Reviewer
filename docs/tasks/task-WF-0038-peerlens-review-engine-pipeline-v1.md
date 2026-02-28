# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-28

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: deterministic single-subject pipeline path

Goal:
- Prove one end-to-end deterministic path from `ReviewRequest v1` to `DiagnosticFinding v1[]` to `ReviewCard[]` for a single expectation and subject.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR2, FR3, FR4, FR6
Depends on: none
Enables: Task 2, Task 7, Task 8
Parallelizable: no
Files to modify:
- `backend/app/engine/pipeline_v1.py` (new)
- `backend/app/engine/contracts.py` (new)
- `backend/tests/test_review_engine_pipeline_v1.py` (new)
Acceptance Criteria:
- Pipeline entrypoint accepts a minimal valid `ReviewRequest v1` and returns deterministic `DiagnosticFinding v1[]`.
- Pipeline applies mode projection and compatibility mapping through stable seams (no DB writes required for tracer bullet).
- Test proves repeated identical input yields byte-for-byte equal structured output ordering.
TDD Plan:
- RED: add failing `backend/tests/test_review_engine_pipeline_v1.py::test_tracer_bullet_deterministic_pipeline_path`.
- GREEN: implement minimal pipeline orchestration and contract dataclasses to pass tracer scenario.
- REFACTOR: extract deterministic fixture builder in test (`skip` if none).
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_engine_pipeline_v1.py -k tracer_bullet`
Risks (if any):
- Tracer bullet may over-simplify mapping assumptions; later tasks must harden contract integrity failures.

### [ ] Task 2 — Implement `ReviewRequest v1` validator + digest enforcement

Goal:
- Enforce replayable input contract, including canonical digest verification and deterministic contract-error behavior.
Slice: request-contract
User Stories: US4
PRD Requirements: FR1, FR8
Depends on: Task 1
Enables: Task 3, Task 9
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py` (new)
- `backend/app/engine/contracts.py`
- `backend/tests/test_review_request_validator.py` (new)
Acceptance Criteria:
- Validator rejects malformed envelopes and digest mismatches with contract error classification.
- Validator accepts stable-key-order canonical payloads and enforces required v1 fields.
- Failure payloads are deterministic and contain machine-parseable error codes.
TDD Plan:
- RED: add failing tests for `CALL_CONFIG_DIGEST_MISMATCH` and malformed payload rejection.
- GREEN: implement strict validator + digest comparison utility.
- REFACTOR: isolate canonical serialization helper for reuse in tests and runtime.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_request_validator.py`
Risks (if any):
- Inconsistent canonicalization rules across modules can cause false digest mismatches.

### [ ] Task 3 — Add call-config activation and expectation ordering selector

Goal:
- Select active expectations/constraints for `stage_ref` and expose authoritative expectation ordering per subject from snapshot list order.
Slice: activation-ordering
User Stories: US1, US4
PRD Requirements: FR5, FR8
Depends on: Task 2
Enables: Task 5, Task 6
Parallelizable: yes (planning-only)
Files to modify:
- `backend/app/engine/call_config_activation.py` (new)
- `backend/app/engine/contracts.py`
- `backend/tests/test_call_config_activation.py` (new)
Acceptance Criteria:
- Activation logic is stage/step driven by call config only (no funder branching).
- Output includes stable expectation order keyed by subject and expectation id.
- Unknown/duplicate expectation ids in active scope fail deterministically.
- Selector tests include conformance cases grounded in existing authored calls (`nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`) and align with `docs/workflow/call-yaml-authoring-workflow.md` constraints.
TDD Plan:
- RED: add failing tests for stage activation, ordering, and duplicate expectation detection.
- GREEN: implement activation selector with explicit ordering extraction.
- REFACTOR: reduce repeated traversal logic into a single selector helper.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_call_config_activation.py`
- `cd backend && rg -n "nwo_veni_2025_preproposal|nwo_vidi_2025_full_proposal|erc_stg_2026_full" tests/test_call_config_activation.py`
Risks (if any):
- Misinterpreting stage activation shape in snapshots could over/under-activate expectations.

### [ ] Task 4 — Implement Pass 1 observation extraction boundary (internal-only)

Goal:
- Normalize anchored `Observation v1` objects as internal pipeline artifacts without creating API/UI contract leakage.
Slice: pass1-observations
User Stories: US1, US4
PRD Requirements: FR3, FR7
Depends on: Task 2
Enables: Task 5
Parallelizable: yes (planning-only)
Files to modify:
- `backend/app/engine/observations/extractor.py` (new)
- `backend/app/engine/contracts.py`
- `backend/tests/test_observation_extractor.py` (new)
Acceptance Criteria:
- Pass 1 returns typed anchors with deterministic structural locators for identical inputs.
- Observation schema remains internal and not imported by API schema modules.
- Missing dependency context emits observation data needed for downstream `NOT_ASSESSABLE` findings.
TDD Plan:
- RED: add failing tests for anchor determinism and missing dependency-context observation.
- GREEN: implement extractor with deterministic locator strategy.
- REFACTOR: remove duplicated anchor-construction branches (`skip` if none).
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_observation_extractor.py`
Risks (if any):
- Anchor locator instability can break deterministic replay.

### [ ] Task 5 — Implement Pass 2 finding evaluator + `check_id` catalog governance

Goal:
- Evaluate observations against active expectations and emit single-primary `DiagnosticFinding v1` using an engine-owned `check_id` catalog.
Slice: pass2-findings
User Stories: US1, US4
PRD Requirements: FR4, FR10, FR11
Depends on: Task 3, Task 4
Enables: Task 6, Task 11
Parallelizable: no
Files to modify:
- `backend/app/engine/findings/evaluator.py` (new)
- `backend/app/engine/findings/check_catalog.py` (new)
- `backend/tests/test_finding_evaluator.py` (new)
Acceptance Criteria:
- Evaluator emits only allowed `finding_kind`, `severity`, and catalog-backed `check_id` values.
- Unknown `check_id` usage fails deterministically as contract violation.
- Missing declared dependency context yields `assessment_status=NOT_ASSESSABLE` with explicit reason.
TDD Plan:
- RED: add failing tests for catalog enforcement and dependency-missing `NOT_ASSESSABLE` behavior.
- GREEN: implement evaluator + starter catalog taxonomy.
- REFACTOR: centralize enum-to-string mapping for stable serialized output.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_finding_evaluator.py`
Risks (if any):
- Catalog drift can introduce unstable downstream interpretation.

### [ ] Task 6 — Add finding aggregation identity + deterministic ordering

Goal:
- Enforce one finding per `(primary_expectation_ref, subject_ref, check_id)` and deterministic sort order.
Slice: aggregation-ordering
User Stories: US2, US4
PRD Requirements: FR4, FR5
Depends on: Task 3, Task 5
Enables: Task 7, Task 8
Parallelizable: no
Files to modify:
- `backend/app/engine/findings/aggregator.py` (new)
- `backend/app/engine/contracts.py`
- `backend/tests/test_finding_aggregation.py` (new)
Acceptance Criteria:
- Duplicate identity tuples are merged/rejected deterministically per contract rule.
- Sort order is `severity desc -> call-defined expectation order -> check_id`.
- Repeated runs over identical payloads produce stable ordering.
TDD Plan:
- RED: add failing tests for duplicate identity conflict and ordering tie-break behavior.
- GREEN: implement aggregation identity guard + orderer.
- REFACTOR: extract comparator utility for reuse by mapper tests.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_finding_aggregation.py`
Risks (if any):
- Incorrect severity rank mapping can invert strict-mode semantics.

### [ ] Task 7 — Implement deterministic mode projector (`DIAGNOSTIC` / `STRICT`)

Goal:
- Guarantee `STRICT` is a projection-only filter over the already computed `DIAGNOSTIC` findings.
Slice: mode-projection
User Stories: US2
PRD Requirements: FR2
Depends on: Task 1, Task 6
Enables: Task 8
Parallelizable: yes (planning-only)
Files to modify:
- `backend/app/engine/modes.py` (new)
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_engine_modes.py` (new)
Acceptance Criteria:
- `DIAGNOSTIC` returns full ordered findings.
- `STRICT` returns only `severity==ERROR` from the same computed set (subset invariant).
- Mode projection does not mutate finding content or ordering among retained items.
TDD Plan:
- RED: add failing mode-subset invariant tests and no-mutation assertions.
- GREEN: implement pure projector and pipeline wiring.
- REFACTOR: simplify mode dispatch branching in pipeline module.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_engine_modes.py tests/test_review_engine_pipeline_v1.py -k mode`
Risks (if any):
- Re-computation per mode could violate projection-only semantics.

### [ ] Task 8 — Build compatibility adapter `DiagnosticFinding v1[] -> ReviewCard[]`

Goal:
- Map findings deterministically to existing `ReviewCard` shape, including severity/rating roll-up and expectation-resolution integrity checks.
Slice: compatibility-mapper
User Stories: US3, US4
PRD Requirements: FR6
Depends on: Task 1, Task 6, Task 7
Enables: Task 9, Task 11
Parallelizable: no
Files to modify:
- `backend/app/engine/compat/review_card_mapper.py` (new)
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_review_card_mapper.py` (new)
Acceptance Criteria:
- Adapter creates exactly one card per `(subject_ref.node_logical_id, primary_expectation_ref)`.
- Severity maps to rating deterministically (`ERROR->CRITICAL`, `WARNING->WARNING`, `NOTE->NOTE`).
- Unresolvable expectation refs fail with explicit integrity contract error (`EXPECTATION_REF_UNRESOLVABLE`).
TDD Plan:
- RED: add failing cardinality, severity mapping, and unresolved expectation tests.
- GREEN: implement mapper and deterministic roll-up rules.
- REFACTOR: extract stable reason-join helper for `NOT_ASSESSABLE` roll-up.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_card_mapper.py`
Risks (if any):
- Hidden coupling to persistence IDs can break call-config-scoped expectation identity.

### [ ] Task 9 — Integrate pipeline in structured review service behind deterministic error contracts

Goal:
- Wire pipeline v1 into structured review orchestration with explicit contract vs execution failure boundaries.
Slice: service-integration
User Stories: US1, US3, US4
PRD Requirements: FR1, FR6
Depends on: Task 2, Task 8
Enables: Task 10
Parallelizable: no
Files to modify:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/engine/errors.py` (new)
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Structured review path can execute via pipeline v1 seams without breaking existing `ReviewCard` persistence/read APIs.
- Contract errors are surfaced as deterministic, non-partial failures.
- Execution failures remain classified separately (`ENGINE_EXECUTION_FAILED`, `TIMEOUT`) via a shared engine error model.
TDD Plan:
- RED: add failing integration tests for digest mismatch and expectation-resolution failure abort behavior.
- GREEN: implement service wiring and error mapping.
- REFACTOR: remove duplicated error-shaping branches across structured and single flows.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "pipeline_v1 or contract_error"`
Risks (if any):
- Service-level fallback behavior may accidentally emit partial cards.

### [ ] Task 10 — Add minimal telemetry and anchor redaction safeguards

Goal:
- Emit run-level pipeline telemetry while preventing raw text leakage from `TEXT_SPAN` anchors.
Slice: telemetry-privacy
User Stories: US4
PRD Requirements: FR7
Depends on: Task 9
Enables: Task 11
Parallelizable: yes (planning-only)
Files to modify:
- `backend/app/engine/telemetry.py` (new)
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_engine_telemetry.py` (new)
Acceptance Criteria:
- Telemetry includes run metadata and finding counters by kind/severity/assessment status.
- Telemetry payload never includes raw proposal text or raw `TEXT_SPAN` excerpts.
- Redaction is deterministic (stable hashes/locators for identical inputs).
TDD Plan:
- RED: add failing telemetry tests that detect accidental raw text/anchor content leakage.
- GREEN: implement telemetry hooks + redaction utility.
- REFACTOR: unify payload shaping for success/failure paths.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_engine_telemetry.py`
Risks (if any):
- Logger-side string interpolation can leak raw text if guards are incomplete.

### [ ] Task 11 — Encode stress-test matrix (NWO/ERC/MSCA) and determinism acceptance suite

Goal:
- Prove call-agnostic behavior across archetypes and lock determinism invariants for ordering, anchors, and mode projections.
Slice: stress-matrix
User Stories: US1, US2, US4
PRD Requirements: FR10
Depends on: Task 5, Task 8, Task 10
Enables: Task 12
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/review_engine_stress_matrix.yaml` (new)
- `backend/tests/test_review_engine_stress_matrix.py` (new)
- `backend/tests/test_review_engine_pipeline_v1.py`
Acceptance Criteria:
- Acceptance suite covers NWO/ERC/MSCA scenarios listed in PRD with explicit expected outcomes.
- Tests confirm no funder-specific branching and stable output ordering across repeated runs.
- Strict-mode subset invariant is validated against stress fixtures.
- Stress fixtures are explicitly derived from current authored call YAML structures (`backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`, `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`, `backend/data/calls/erc/erc_stg_2026_full.yaml`) without copying funder-specific semantics into engine logic.
TDD Plan:
- RED: add failing archetype fixture tests for declared dependency gaps and expectation-driven finding emission.
- GREEN: implement fixture harness assertions using existing pipeline outputs.
- REFACTOR: de-duplicate fixture loading/helpers across stress and tracer tests.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_engine_stress_matrix.py tests/test_review_engine_pipeline_v1.py -k "stress or determinism"`
- `cd backend && rg -n "nwo_veni_2025_preproposal|nwo_vidi_2025_full_proposal|erc_stg_2026_full" tests/fixtures/review_engine_stress_matrix.yaml tests/test_review_engine_stress_matrix.py`
Risks (if any):
- Fixture assumptions may drift from real call-config authoring patterns.

### [ ] Task 12 — Capture implementation evidence and handoff walkthrough

Goal:
- Record Phase 3-ready implementation and verification evidence for the pipeline v1 contract boundaries.
Slice: implementation-evidence
User Stories: US1, US4
PRD Requirements: FR1, FR6, FR10
Depends on: Task 11
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0038-peerlens-review-engine-pipeline-v1.md`
Acceptance Criteria:
- Walkthrough includes evidence for tracer bullet, contract errors, strict/diagnostic projection, and stress-matrix outcomes.
- Commands and test targets are reproducible and mapped to tasks.
- Any deferred scope is explicitly listed.
- Walkthrough includes a conformance note showing which authored-call patterns were promoted to universal primitives vs explicitly excluded to preserve call-agnostic behavior.
TDD Plan: N/A (documentation evidence task)
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_engine_pipeline_v1.py tests/test_review_request_validator.py tests/test_call_config_activation.py tests/test_observation_extractor.py tests/test_finding_evaluator.py tests/test_finding_aggregation.py tests/test_engine_modes.py tests/test_review_card_mapper.py tests/test_structured_reviewer_service.py tests/test_engine_telemetry.py tests/test_review_engine_stress_matrix.py`
- `cd /home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer && rg -n "tracer bullet|contract error|STRICT|DIAGNOSTIC|stress" docs/walkthroughs/walkthrough-WF-0038-peerlens-review-engine-pipeline-v1.md`
Risks (if any):
- Broad verification command runtime may be high in local dev without test DB/LLM stubs prepared.

## Changelog

- v0.1 (2026-02-28): Initial task breakdown from PRD
- v0.2 (2026-02-28): Applied Phase 2 review edits (tightened Task 9 service boundary and corrected ERC stress-matrix label); marked Ready for Implementation
- v0.3 (2026-02-28): Added confidence gates tying activation/stress/walkthrough tasks to existing authored call YAML structures and call-authoring workflow guardrails.
