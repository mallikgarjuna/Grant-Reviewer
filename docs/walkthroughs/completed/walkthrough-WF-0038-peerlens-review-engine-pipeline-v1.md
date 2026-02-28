# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-02-28

---

## What Changed

Implemented a call-agnostic review engine pipeline v1 in `backend/app/engine/` and integrated it into the structured-review service through deterministic contract boundaries.

Core additions:
- `ReviewRequest v1` contract + validator with digest enforcement.
- Activation/ordering selector from call-config structure.
- Pass 1 observations extractor (internal-only, deterministic anchors/hashes).
- Pass 2 finding evaluator with `check_id` catalog governance.
- Finding aggregation identity/order invariants.
- Mode projector (`DIAGNOSTIC` / `STRICT`) as projection-only behavior.
- Compatibility mapper (`DiagnosticFinding v1[] -> ReviewCard[]`).
- Engine error model and contract matrix tests.
- Pipeline telemetry with deterministic redaction (no raw text leakage).
- Stress matrix fixtures/tests across NWO/ERC/MSCA archetypes.
- Determinism + strict subset invariant suite.

## Evidence by Requirement Area

1. tracer bullet
- Deterministic single-subject end-to-end path validated in `tests/test_review_engine_pipeline_v1.py::test_tracer_bullet_deterministic_pipeline_path`.

2. error contract
- Matrix includes: `CALL_CONFIG_DIGEST_MISMATCH`, `MALFORMED_REVIEW_REQUEST`, `EXPECTATION_REF_UNRESOLVABLE`, `ENGINE_EXECUTION_FAILED`, `TIMEOUT`.
- Coverage in `tests/test_review_engine_error_contracts.py` and `tests/test_structured_reviewer_service.py` (`pipeline_v1` contract-failure tests).

3. STRICT / DIAGNOSTIC mode projection
- `STRICT` is validated as subset projection over `DIAGNOSTIC` outputs in `tests/test_engine_modes.py` and `tests/test_review_engine_determinism.py`.

4. stress
- Archetype matrix coverage implemented in `tests/fixtures/review_engine_stress_matrix.yaml` + `tests/test_review_engine_stress_matrix.py`.

5. determinism
- Repeated-run byte-stability and stable redacted anchor metadata covered in `tests/test_review_engine_determinism.py`.

6. conformance
- Stress/activation artifacts explicitly reference authored calls:
  - `nwo_veni_2025_preproposal`
  - `nwo_vidi_2025_full_proposal`
  - `erc_stg_2026_full`
- Conformance checks in `tests/test_call_config_activation.py` and stress fixture/test pair.

## Verification Commands (Executed)

```bash
cd backend && PYTHONPATH=. uv run pytest tests/test_review_engine_pipeline_v1.py tests/test_review_request_validator.py tests/test_call_config_activation.py tests/test_observation_extractor.py tests/test_finding_evaluator.py tests/test_diagnostic_finding_schema_growth.py tests/test_finding_aggregation.py tests/test_engine_modes.py tests/test_review_card_mapper.py tests/test_structured_reviewer_service.py tests/test_review_engine_error_contracts.py tests/test_engine_telemetry.py tests/test_review_engine_stress_matrix.py tests/test_review_engine_determinism.py
```

Executed with test-safe DB URL in environment for DB-backed tests:

```bash
DATABASE_URL=sqlite:////tmp/grant_reviewer_test.db
```

Walkthrough keyword conformance check:

```bash
cd /home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer && rg -n "tracer bullet|error contract|STRICT|DIAGNOSTIC|stress|determinism|conformance" docs/walkthroughs/walkthrough-WF-0038-peerlens-review-engine-pipeline-v1.md
```

## Deferred Scope

- Public API/UI first-class exposure of `DiagnosticFinding v1` remains deferred; compatibility mapping to `ReviewCard` remains active for v1.
- Engine telemetry currently records deterministic redacted metadata and counters only (no richer distributed tracing fields yet).

## Conformance Note: Promoted vs Excluded

Promoted to universal primitives:
- Stage-driven activation by call configuration metadata.
- Deterministic expectation ordering, finding identity, and mode projection.
- Contract-level error taxonomy and deterministic mapper/validator behavior.

Explicitly excluded to preserve call-agnostic behavior:
- Any funder-specific branching in engine logic (`if ERC ...`, `if NWO ...`).
- Funder/program-specific evaluator code paths.
