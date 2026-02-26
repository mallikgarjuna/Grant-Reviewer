# WF-0034 — Unify review service execution core Walkthrough

Artifact: walkthrough
Version: v1.1
Status: Complete
Last Updated: 2026-02-26

## 1. Goal Overview
Unify single-node and structured review execution behind a shared core seam while preserving endpoint contracts, persistence ownership boundaries, and failure semantics.

## 2. What Changed
- Added `backend/app/services/review_execution_core.py` as the shared assessable-node execution seam.
- Migrated structured assessable execution to the shared core while keeping deterministic `NOT_ASSESSABLE` card creation in `StructuredReviewerService`.
- Migrated single-node `/reviews` LLM execution path in `ReviewerService` to the shared core while preserving adapter-owned persistence and endpoint-visible semantics.
- Added no-op-safe telemetry hooks for start/complete/failure execution boundaries in the shared core.
- Added endpoint parity and cross-regression tests for both `/reviews` and `/api/structured-review`.
- Added focused shared-core no-DB tests for success, timeout classification, policy post-check classification, and telemetry emissions.

## 3. Verification Evidence
- `pre-commit run --all-files` passed.
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' PYTHONPATH=. uv run pytest tests/test_review_execution_core.py tests/test_reviewer_policy.py tests/test_structured_reviewer_service.py tests/test_api.py` -> `80 passed`.
- Per-task verification commands in the task artifact were executed and passed during Phase 3 Part A.

## 4. Part B Technical Audit Summary
- No blocking findings.
- Non-blocking findings were incorporated in follow-up C1:
  - Added explicit structured policy-blocking summary parity coverage.
  - Tightened structured contract parity success status assertion to `COMPLETED`.
  - Deduplicated adapter failure summary formatting through shared core formatter.

## 5. Commit Trail (Phase 3)
- `69b4724` Task 1: tracer shared-core seam for structured path.
- `85bc53f` Task 2: structured failure parity tests.
- `ee46231` Task 3: deterministic not-assessable boundary guard.
- `d7157eb` Task 4: single-node happy-path migration.
- `8f5b88f` Task 5: single-node timeout/idempotency/policy parity locks.
- `0c7d1f0` Task 6: shared-core seam test suite.
- `de6042e` Task 7: telemetry seam + non-invasive coverage.
- `b784a05` Task 8: endpoint contract parity guards.
- Follow-up C1/C2 patch: incorporated Part B non-blocking audit findings.

## 6. Remaining Risks
- Future wording-level API assertions could expose summary-text drift across adapters.
- Telemetry payload growth should remain side-effect-free and non-blocking.

## 7. Next Steps
- Execute `ship it` flow for WF-0034.
- Start the next workflow from `docs/parking_lot.md`.
