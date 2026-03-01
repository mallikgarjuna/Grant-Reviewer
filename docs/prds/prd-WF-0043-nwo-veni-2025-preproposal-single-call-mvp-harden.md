# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-01

## 0. User Stories (MVP)

- US1: As a maintainer, I want deterministic contract tests for `POST /api/structured-review` so that API error semantics, idempotency, and persistence behavior for `nwo_veni_2025_preproposal` do not regress.
- US2: As a maintainer, I want deterministic reviewer-policy seam tests for the single-snippet flow (`POST /reviews`) so that blocking/post-check/prompt-only behavior stays stable for the same call.
- US3: As a maintainer, I want a compact verification bundle (fixture matrix + runbook docs) so that I can quickly re-verify trust-critical behavior before merge/release.

## Deferred Stories (Not in MVP)

- DS1: As a maintainer, I want expiry-time-travel idempotency tests so that TTL reuse can be asserted with explicit clock control.
- DS2: As a maintainer, I want browser/E2E automation for submit/review trust checks.
- DS3: As a maintainer, I want multi-call hardening templates that generalize beyond `nwo_veni_2025_preproposal`.

## 1. In Scope

- Add deterministic pytest contract tests for `POST /api/structured-review` focused on `nwo_veni_2025_preproposal`. (US1)
- Add a small deterministic fixture matrix for the hardening scenarios and wire tests to it. (US1, US3)
- Add deterministic tests for reviewer-policy enforcement modes in the single-snippet seam (`POST /reviews` service path), scoped to this call. (US2)
- Add/update verification bundle docs describing what is asserted and exact commands to run. (US3)
- Preserve current behavior; this WF hardens contracts, not product semantics. (US1, US2)

## 2. Out of Scope

- Any API behavior changes to error codes/status mappings/idempotency semantics/persistence side effects. (US1, US2)
- Browser automation tooling (Playwright/Cypress) or new tooling introduction. (US3)
- Multi-call expansion, prompt/model tuning, or engine redesign. (US1, US2)
- Time-control dependency/tooling for expiry-time-travel tests. (DS1)

## 3. User / System Flow

- Happy path:
1. Maintainer runs a focused pytest subset for WF-0043. (US1, US2, US3)
2. Test harness loads fixture cases for `nwo_veni_2025_preproposal` and executes endpoint/service contract assertions. (US1, US2, US3)
3. Results show pass/fail per contract invariant and provide a deterministic go/no-go signal for merge/release. (US1, US3)

- Failure path A (contract drift):
1. A code change alters an expected error code/status/ordering or idempotency mismatch behavior. (US1)
2. API contract tests fail with explicit assertion context tied to a fixture case. (US1, US3)

- Failure path B (persistence drift):
1. A code change alters persistence semantics (e.g., creating reviews on API validation errors, or failing to persist service-layer execution failures). (US1)
2. Persistence assertions fail and block merge until parity is restored or a deliberate contract change is approved. (US1)

- Failure path C (policy seam drift):
1. A code change alters `BLOCKING`/`POST_CHECK`/`PROMPT_ONLY` behavior in single-snippet flow. (US2)
2. Reviewer-policy seam tests fail on expected status/summary/warning invariants. (US2)

## 4. Functional Requirements

- FR1 (US1): Add deterministic API contract tests for `POST /api/structured-review` scoped to call code `nwo_veni_2025_preproposal`.
- FR2 (US1): Assert idempotency replay contract: same `Idempotency-Key` + same payload returns the same persisted review identity and stable status.
- FR3 (US1): Assert idempotency mismatch contract: same `Idempotency-Key` + different payload returns `IDEMPOTENCY_PAYLOAD_MISMATCH` with existing status mapping.
- FR4 (US1): Assert API validation/error paths do not create `Review` rows.
- FR5 (US1): Assert service/engine failure paths (after review creation) return `200` `{review_id, status}` and persist `ReviewStatus=FAILED` with stable summary conventions.
- FR6 (US2): Add deterministic reviewer-policy tests for single-snippet seam covering `BLOCKING`, `POST_CHECK`, and `PROMPT_ONLY`.
- FR7 (US3): Add a small fixture matrix (`8-12` cases) as the single source for WF-0043 contract scenarios.
- FR8 (US3): Add/update verification bundle docs to include exact commands, DB isolation requirement, and per-case scenario-table fields (HTTP, persistence, status/summary convention).
- FR9 (US1, US2): Do not introduce new tooling or alter existing production API contracts while implementing FR1-FR8.

## 5. Data & API Contracts

- Contract C1 (US1, FR1, FR2, FR3): `POST /api/structured-review` requires `Idempotency-Key`; missing header remains a validation/API error path with no persisted `Review`.
- Contract C2 (US1, FR2, FR3): Idempotency behavior remains:
  - same key + same payload => replay existing review identity/status
  - same key + different payload => `IDEMPOTENCY_PAYLOAD_MISMATCH`
- Contract C3 (US1, FR4, FR5): Persistence invariants remain split by failure boundary:
  - endpoint request/validation errors => no persisted `Review`
  - post-persistence execution failures => persisted `Review` with `FAILED` status and deterministic summary convention
- Contract C4 (US2, FR6): Reviewer-policy modes in single-snippet seam remain:
  - `BLOCKING` => execution failure outcome with persisted failed review semantics
  - `POST_CHECK` => warning surfaced without blocking completion
  - `PROMPT_ONLY` => influences prompt construction only (non-blocking)
- Contract C5 (US3, FR7, FR8): Fixture matrix rows include scenario metadata fields:
  - `case_id`
  - `surface` (`structured_api` | `single_snippet_policy`)
  - `expected_http_status`
  - `expected_error_code` (nullable)
  - `expect_review_persisted`
  - `expected_review_status` (nullable)
  - `expected_summary_convention` (nullable)

## 6. Components / Modules

- `backend/tests/test_api.py`
  - Responsibility: endpoint-level contract assertions for `POST /api/structured-review` (FR1-FR5).
- `backend/tests/test_review_execution_core.py` and/or `backend/tests/test_reviewer_service.py`
  - Responsibility: deterministic reviewer-policy seam assertions for single-snippet flow (FR6).
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
  - Responsibility: centralized fixture matrix for hardening scenarios (FR7).
- `docs/brainstorms/brainstorm-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md`
  - Responsibility: verification bundle appendix alignment and scenario-table contract (FR8).

Design tree (dependencies + ordering):
1. Define fixture matrix shape and baseline cases. (FR7)
2. Add/adjust structured API contract assertions against fixture cases. (FR1-FR5)
3. Add/adjust reviewer-policy seam assertions. (FR6)
4. Align docs verification bundle with implemented cases and commands. (FR8)

Deep module boundaries:
- Test data boundary: fixture matrix is declarative and call-scoped.
- Assertion boundary: tests assert contracts only (status/error/persistence/summary conventions), not generated prose quality.
- Runtime boundary: production behavior unchanged unless tests reveal an existing regression.

## 7. Edge Cases

- E1 (US1, FR3): idempotency mismatch under conflict/retry path must still map to existing mismatch contract.
- E2 (US1, FR4): multiple validation failures in one payload must preserve current validation ordering semantics.
- E3 (US1, FR5): service-layer failure after review creation must preserve persisted failed-review discoverability for `/app/reviews`.
- E4 (US2, FR6): `POST_CHECK` warnings should be present but must not flip completion to failure.
- E5 (US3, FR7): fixture matrix stays intentionally small; adding broad decision-table coverage is deferred.

## 8. Testing Decisions (TDD)

- TDD seam S1 (US1, FR1-FR5): `POST /api/structured-review` endpoint contract tests.
  - Mock/stub boundary: LLM/external execution boundaries only where needed for determinism.
  - Prove-it tests: error/status/idempotency/persistence invariants per fixture case.
- TDD seam S2 (US2, FR6): single-snippet reviewer-policy enforcement seam tests.
  - Mock/stub boundary: LLM responses to trigger deterministic policy outcomes.
  - Prove-it tests: blocking vs warning vs prompt-only semantics.
- TDD seam S3 (US3, FR7, FR8): fixture matrix + docs consistency.
  - Prove-it tests: every matrix case maps to an assertion path and documented expectation fields.

## 9. Telemetry (Minimal)

- No new production telemetry required for this WF.
- Test output should include stable case identifiers to speed debugging (`case_id` in parametrized test names).

## 10. Deferred / Not in MVP

- Expiry-time-travel idempotency tests with controllable clock.
- Browser/E2E trust checks.
- Multi-call hardening generalization templates.

## 11. Open Questions (if any)

- OQ1: Whether current test harness can practically assert TTL-expiry reuse without introducing new tooling; default is documented defer.

## 12. Changelog

- v0.1 (2026-03-01): Initial PRD from brainstorm.
