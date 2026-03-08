<!-- docs/walkthroughs/walkthrough-WF-0065-cross-call-contract-hardening-base-review-semantics.md -->
# WF-0065 — Cross-Call Contract Hardening of Base Review Semantics

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-08

## Scope

Implemented the approved WF-0065 scope only:
- Locked representative call set: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, `MSCA-PF-2025`
- Paired endpoint boundary rule: `/reviews` and `/api/structured-review`
- Fail-closed gate semantics: `REVIEWS_DISABLED`, `QUOTA_EXCEEDED`

Out-of-scope areas were not expanded (supporting-context semantics, new call onboarding, endpoint redesign).

## What Changed

1. Structured tracer + matrix proofs (Tasks 1-2)
- Added `wf0065` tracer and representative matrix tests for:
  - `POST /api/structured-review`
  - `StructuredReviewerService.generate_structured_review_pipeline_v1`
  - `pipeline_v1`
- Shifted NWO tracer coverage to real canonical artifact ingestion (no synthetic substitute for tracer proof).

2. Paired boundary single-node proofs (Task 3)
- Added `backend/tests/test_reviewer_service.py` for `ReviewerService.generate_review` representative-call success matrix.
- Added matching `/reviews` representative-call success matrix assertions in API tests.

3. Idempotency/validation parity proofs (Task 4)
- Added representative-call cross-endpoint tests for:
  - validation-before-idempotency ordering
  - replay invariants (single persisted row)
  - payload mismatch conflict semantics
  - stable error `details` shape for exposed contracts
- Part C1 review fix: added explicit persisted-review non-mutation assertions before/after mismatch on both endpoints.

4. Fail-closed gate proofs (Tasks 5-6)
- Added representative-call gate tests proving `REVIEWS_DISABLED` and `QUOTA_EXCEEDED`:
  - preserve stable HTTP + error code contracts
  - block both API boundaries before service/pipeline invocation
  - produce zero review persistence side effects

## Verification Evidence

Preflight baseline:
- `cd backend && uv run pytest -m no_db`
- Result: `234 passed, 179 deselected`

Task-level verification (all passed):
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and nwo and structured"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_structured_reviewer_service.py -k "wf0065 and nwo"`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0065 and nwo"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and structured and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_structured_reviewer_service.py -k "wf0065 and representative"`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0065 and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_reviewer_service.py -k "wf0065 and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and create_review and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and representative and (idempotency or replay or mismatch or validation_order)"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and reviews_disabled and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0065 and quota_exceeded and representative"`
- `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py tests/test_reviewer_service.py tests/test_structured_reviewer_service.py tests/test_review_engine_pipeline_v1.py -k "wf0065 and representative"`

Phase 3.3 verification:
- `pre-commit run --all-files` passed.
- Representative suite aggregate result: `27 passed, 146 deselected`.

## Risks / Follow-ups

- Representative matrix literals are duplicated across multiple test modules; this is currently acceptable for explicitness, but centralizing these in one shared fixture could reduce hidden drift risk in a future maintenance slice.
