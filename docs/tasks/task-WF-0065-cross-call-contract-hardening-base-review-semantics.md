<!-- docs/tasks/task-WF-0065-cross-call-contract-hardening-base-review-semantics.md -->
# WF-0065 — Cross-Call Contract Hardening of Base Review Semantics

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-08

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: prove the real-call NWO structured path end to end

Goal:
Replace the synthetic NWO evidence gap with one real-call tracer bullet that proves `nwo_veni_2025_preproposal` works across the structured API, structured service, and `pipeline_v1` seams.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1, FR2, FR8, FR9
Depends on: none
Enables: 2, 4, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
May touch files:
- `backend/tests/fixtures/review_engine_stress_matrix.yaml`
Out of scope: ERC/MSCA expansion, `/reviews` parity, gate-path assertions, DTO redesign
Stop if: proving the NWO real-call tracer requires onboarding a new call artifact, changing endpoint request shapes, or introducing a second review engine seam
Session boundary after: no
Acceptance Criteria:
- `nwo_veni_2025_preproposal` is exercised from the canonical call artifact rather than a synthetic seeded substitute on the structured proof path.
- The tracer covers `POST /api/structured-review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, and `pipeline_v1` with consistent success semantics.
- The tracer makes the current NWO evidence gap explicit if any seam still cannot use the real canonical artifact.
TDD Plan:
- RED: add failing `wf0065` NWO real-call tracer tests in `backend/tests/test_api.py`, `backend/tests/test_structured_reviewer_service.py`, and `backend/tests/test_review_engine_pipeline_v1.py`.
- GREEN: make the smallest fixture/helper change needed so the structured path consumes the real `nwo_veni_2025_preproposal` canonical artifact.
- REFACTOR: collapse only duplicated real-call setup helpers if the tracer introduces repeated canonical-call loading logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and nwo and structured"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0065 and nwo"`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0065 and nwo"`
Risks (if any): A green structured tracer can still overstate closure if one seam silently keeps using synthetic graph state.

### [ ] Task 2 — Expand structured success parity from the tracer to the locked 3-call proof set

Goal:
Extend the structured success-path matrix from the NWO tracer to `erc_stg_2026_full` and `MSCA-PF-2025` so the locked representative set shares the same structured success semantics.
Slice: structured-success-matrix
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR10, FR11
Depends on: 1
Enables: 3, 4, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
May touch files:
- `backend/tests/fixtures/review_engine_stress_matrix.yaml`
Out of scope: `/reviews` single-node parity, gate-path proofs, supporting-context semantics
Stop if: the ERC/MSCA representatives require widening to additional calls or a new shared harness that is broader than the locked proof contract
Session boundary after: yes
Acceptance Criteria:
- Structured API, structured service, and `pipeline_v1` success assertions cover exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- The planned assertions check semantic parity, not just status-code presence, across the structured seams for the 3 locked calls.
- No additional representative call is introduced without a documented blocker.
TDD Plan:
- RED: expand the `wf0065` structured tracer tests into a 3-call matrix in the same three test files.
- GREEN: apply only the minimal fixture/helper adjustments needed to keep the structured success matrix deterministic across the locked calls.
- REFACTOR: extract a narrow representative-call parameter source only if the same 3-call matrix is repeated verbatim across all three structured seams.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and structured and representative"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0065 and representative"`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0065 and representative"`
Risks (if any): A broad parameter harness can hide call-specific drift if it stops asserting per-call semantic details.

### [ ] Task 3 — Add the paired `/reviews` and `ReviewerService.generate_review` success matrix

Goal:
Prove the overlapping base-review success contract on the single-node path for the same locked 3-call set without widening beyond the current `/reviews` surface.
Slice: paired-boundary-success
User Stories: US1, US2
PRD Requirements: FR2, FR3, FR4, FR7
Depends on: 2
Enables: 4, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/tests/test_reviewer_service.py`
May touch files:
- `backend/app/services/reviewer_service.py`
- `backend/main.py`
Out of scope: structured-path work already covered by Tasks 1-2, endpoint DTO convergence, non-overlapping endpoint semantics
Stop if: the `/reviews` proof needs more than the overlapping base-review contract surface or requires redesigning `ReviewerService.generate_review`
Session boundary after: yes
Acceptance Criteria:
- The single-node path has explicit representative-call success tests for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- `/reviews` and `ReviewerService.generate_review` are proven on the overlapping base-review contract surface only.
- The paired success assertions verify returned success contract shape in addition to representative-call coverage.
- Any missing single-node seam needed for the 3-call proof is introduced minimally and remains subordinate to evidence collection.
TDD Plan:
- RED: add failing `wf0065` representative-call success tests in `backend/tests/test_reviewer_service.py` and matching `/reviews` endpoint assertions in `backend/tests/test_api.py`.
- GREEN: make the minimum `ReviewerService.generate_review` change needed so the representative-call success matrix is deterministic and matches the approved contract.
- REFACTOR: extract only a tiny request-builder/helper if endpoint and service setup duplication obscures the paired-boundary assertions.
Verification Steps:
- `cd backend && uv run pytest tests/test_reviewer_service.py -k "wf0065 and representative"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and create_review and representative"`
- `cd backend && rg -n "generate_review|wf0065|nwo_veni_2025_preproposal|erc_stg_2026_full|MSCA-PF-2025" app/services/reviewer_service.py tests/test_reviewer_service.py tests/test_api.py`
Risks (if any): A new reviewer-service seam can drift from the endpoint contract if the task proves one boundary but not the other.

### [ ] Task 4 — Lock validation/idempotency parity on the overlapping endpoint surface

Goal:
Align `POST /reviews` and `POST /api/structured-review` on validation-before-idempotency ordering, replay behavior, and payload-mismatch behavior for the overlapping base-review contract.
Slice: endpoint-idempotency-parity
User Stories: US2, US3
PRD Requirements: FR3, FR4, FR7
Depends on: 3
Enables: 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/main.py`
May touch files:
- `backend/tests/test_reviewer_service.py`
Out of scope: service-level gate instrumentation, non-overlapping request validation, persistence redesign
Stop if: parity requires unifying endpoint DTOs or changing idempotency semantics that are currently outside the overlapping contract surface
Session boundary after: no
Acceptance Criteria:
- Both endpoints explicitly preserve validation-before-idempotency ordering on the in-scope proof cases.
- Replay returns the original review without creating a second row on both endpoints.
- Payload mismatch preserves existing conflict semantics without mutating the persisted review on both endpoints.
- Replay and payload-mismatch assertions preserve stable error `details` shape wherever the overlapping endpoint contract exposes it.
TDD Plan:
- RED: add failing cross-endpoint `wf0065` tests in `backend/tests/test_api.py` for validation ordering, replay, mismatch, and stable error `details` shape on the locked proof calls.
- GREEN: apply the minimum API-boundary fix in `backend/main.py` only if current ordering or idempotency behavior drifts from the approved contract.
- REFACTOR: collapse duplicate endpoint assertion helpers only if they keep the per-endpoint semantic checks explicit.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and (idempotency or replay or mismatch or validation_order)"`
- `cd backend && rg -n "Idempotency-Key|get_active_review_by_idempotency|payload mismatch|wf0065" main.py tests/test_api.py`
Risks (if any): A parity helper that hides endpoint-specific assertions can miss drift in error `details` shape or ordering.

### [ ] Task 5 — Prove `REVIEWS_DISABLED` is fail-closed at both API boundaries

Goal:
Show that `REVIEWS_DISABLED` stops requests before `ReviewerService.generate_review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, or `pipeline_v1` can execute, with no persisted review side effects.
Slice: gate-reviews-disabled
User Stories: US2, US3
PRD Requirements: FR4, FR5, FR6
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/main.py`
May touch files:
- `backend/tests/test_review_engine_pipeline_v1.py`
Out of scope: quota semantics, telemetry expansion beyond a narrow diagnostic seam, service redesign
Stop if: proving non-invocation requires moving gate logic below the API boundary or adding a broad new instrumentation framework
Session boundary after: no
Acceptance Criteria:
- `REVIEWS_DISABLED` preserves the current stable HTTP and error-code contract on both endpoints.
- `REVIEWS_DISABLED` preserves the current stable error `details` shape wherever the overlapping endpoint contract exposes it.
- Blocked requests do not invoke `ReviewerService.generate_review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, or `pipeline_v1`.
- Blocked requests do not create a review row or partial persisted review state.
TDD Plan:
- RED: add failing `wf0065` `REVIEWS_DISABLED` tests in `backend/tests/test_api.py` that assert boundary payloads, stable error `details` shape, downstream non-invocation, and no-persistence evidence.
- GREEN: make only the smallest API-boundary change needed if either endpoint currently leaks execution or persistence after the gate.
- REFACTOR: extract a tiny blocked-request assertion helper only if both endpoints repeat the same fail-closed checks verbatim.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and reviews_disabled"`
- `cd backend && rg -n "REVIEWS_DISABLED|generate_review|generate_structured_review_pipeline_v1|pipeline_v1" main.py tests/test_api.py`
Risks (if any): Asserting only the returned 503 response can miss hidden review writes or deferred pipeline entry.

### [ ] Task 6 — Prove `QUOTA_EXCEEDED` is fail-closed at both API boundaries

Goal:
Show that `QUOTA_EXCEEDED` preserves the same fail-closed boundary guarantees as `REVIEWS_DISABLED`, including zero downstream execution and zero persisted review state.
Slice: gate-quota-exceeded
User Stories: US2, US3
PRD Requirements: FR4, FR5, FR6
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/main.py`
May touch files:
- `backend/tests/test_review_engine_pipeline_v1.py`
Out of scope: pricing/quota policy redesign, new quota telemetry, unrelated quota-source mocking changes
Stop if: proving no side effects requires bypassing the real API entry gate or changing quota policy semantics rather than enforcing fail-closed behavior
Session boundary after: yes
Acceptance Criteria:
- `QUOTA_EXCEEDED` preserves the current stable HTTP and error-code contract on both endpoints.
- `QUOTA_EXCEEDED` preserves the current stable error `details` shape wherever the overlapping endpoint contract exposes it.
- Blocked requests do not invoke `ReviewerService.generate_review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, or `pipeline_v1`.
- Blocked requests do not create a review row or partial persisted review state.
- The final task-level verification proves the full locked 3-call, paired-boundary, fail-closed scope without widening into supporting-context semantics, new-call onboarding, or extra representative calls.
TDD Plan:
- RED: add failing `wf0065` `QUOTA_EXCEEDED` tests in `backend/tests/test_api.py` that assert payloads, stable error `details` shape, downstream non-invocation, and no-persistence evidence across the paired boundaries.
- GREEN: make only the smallest API-boundary fix needed if the quota gate leaks execution or persistence.
- REFACTOR: keep cleanup limited to local fail-closed test helpers that do not broaden the workflow surface.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0065 and quota_exceeded"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0065" tests/test_reviewer_service.py tests/test_structured_reviewer_service.py tests/test_review_engine_pipeline_v1.py`
- `cd backend && rg -n "QUOTA_EXCEEDED|generate_review|generate_structured_review_pipeline_v1|pipeline_v1" main.py tests/test_api.py`
Risks (if any): Sharing too much gate test setup between the two endpoints can hide a fail-open leak on one boundary.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
- v0.2 (2026-03-08): Applied review-gate edits to remove the forced `reviewer_service.py` touch, require explicit success/error details-shape parity, and lock final verification to the approved 3-call proof set; marked Ready for Implementation.
