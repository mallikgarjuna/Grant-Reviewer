# WF-0034 — Unify review service execution core PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-02-26

## 0. User Stories (MVP)

- US1: As a backend engineer, I want a shared internal review execution pipeline for single-node and structured flows, so that drift and duplicated fixes are reduced.
- US2: As a frontend/BFF integrator, I want endpoint contracts and semantics to remain stable, so that no client-facing behavior breaks during refactor.
- US3: As an engineering team, I want parity-focused tests around both endpoints and the shared core seam, so that we can refactor safely with fast feedback.
- US4: As maintainers, we want a staged migration path (endpoint-by-endpoint) so that rollout is reversible and low risk.

## Deferred Stories (Not in MVP)

- DS1: As product/engineering, we want to deprecate `POST /reviews` and converge create flows on structured review after compatibility migration.
- DS2: As platform/ops, we want full telemetry platform rollout and alerting (beyond seam-level hooks).
- DS3: As performance owners, we want behavior-changing optimizations (parallel node calls, retries/backoff policy changes, mega-prompt strategy).

## 1. In Scope

- Extract shared internal execution pipeline concerns:
  - policy injection and policy post-checks
  - LLM call seam (timeouts preserved; retry seam only)
  - response parsing and response validation
  - telemetry seam (non-invasive/no-op acceptable initially)
- Keep external create endpoint contracts separate and stable:
  - `POST /reviews` (single-node)
  - `POST /api/structured-review` (multi-node)
- Preserve endpoint-specific persistence semantics:
  - single-node snippet-linked persistence
  - structured payload and deterministic `NOT_ASSESSABLE` handling
- Add parity testing seams:
  - endpoint-level contract/parity checks
  - shared-core service tests with deterministic stubs
- Incremental migration sequence with rollback-safe transitions.

## 2. Out of Scope

- Deprecating/removing `POST /reviews`.
- Any request/response DTO changes for existing endpoints.
- Any behavior change to error mapping/order, idempotency semantics, or persistence side effects.
- Full telemetry stack rollout or alerting program.
- Performance behavior changes (new retry policies, parallelization, prompt strategy changes).
- Database schema migrations not required for parity-preserving refactor.
- Temporary "shadow mode" dual-write/dual-execution rollout in this WF.

## 3. User / System Flow

### Happy Path

1. Developer updates shared-core module and adapters while preserving existing endpoint method signatures. (US1, US2)
2. `POST /reviews` continues current route-level validation/idempotency behavior and delegates into single-node service using shared execution core seam. (US2, US4)
3. `POST /api/structured-review` continues current route-level validation/idempotency behavior and delegates into structured service using shared execution core seam. (US2, US4)
4. Shared core performs policy selection/injection, prompt build call path, LLM call seam, parse/validate, and policy post-checks, returning normalized execution result. (US1)
5. Endpoint services persist results using existing endpoint-specific semantics and return unchanged response contracts. (US2)
6. Parity tests confirm unchanged external behavior and preserved side effects. (US3)

### Failure Path A — Validation/Policy Drift Detected in Tests

1. Parity tests fail due to changed error ordering/code or persistence side effect after extraction. (US3)
2. Team reverts adapter change or adjusts shared core to match baseline endpoint behavior. (US4)
3. Migration to next endpoint is blocked until parity is restored. (US3, US4)

### Failure Path B — Timeout/Error Mapping Regresses

1. Shared seam accidentally alters timeout or exception mapping semantics for one endpoint. (US2, US3)
2. Endpoint contract tests surface mismatch against baseline behavior. (US3)
3. Change is rolled back or patched before progressing rollout. (US4)

### Failure Path C — Structured Persistence Semantics Drift

1. Structured path loses deterministic `NOT_ASSESSABLE` behavior or review payload semantics. (US2, US3)
2. Structured-focused parity tests fail on persisted artifacts/card status behavior. (US3)
3. Shared-core boundary is tightened to keep persistence endpoint-owned. (US1, US2)

## 4. Functional Requirements

- FR1 (US1): System MUST provide a shared internal execution pipeline module that is callable by both single-node and structured review services.
- FR2 (US1): Shared execution pipeline MUST include policy rule injection/selection and policy post-check evaluation.
- FR3 (US1): Shared execution pipeline MUST include LLM invocation seam and response parse/validation seam.
- FR4 (US1, US2): Shared execution pipeline MUST return normalized execution result data without performing endpoint-specific persistence writes.
- FR5 (US2): `POST /reviews` request/response DTOs and status/error semantics MUST remain unchanged.
- FR6 (US2): `POST /api/structured-review` request/response DTOs and status/error semantics MUST remain unchanged.
- FR7 (US2): Endpoint-specific idempotency semantics (including payload mismatch behavior) MUST remain unchanged per endpoint baseline.
- FR8 (US2): Endpoint-specific persistence side effects MUST remain unchanged (single-node snippet linkage; structured payload + deterministic `NOT_ASSESSABLE` behavior).
- FR9 (US3): Add/maintain endpoint-level parity tests that assert unchanged behavior for both endpoints.
- FR10 (US3): Add shared-core service tests with deterministic LLM stubs for positive and failure paths.
- FR11 (US4): Migration MUST be incremental (one endpoint at a time) with the ability to stop/revert without cross-endpoint contract changes.
- FR12 (US1, US3): Add standardized telemetry seam events/hooks at execution boundaries in a no-op/non-invasive manner.

## 5. Data & API Contracts

### External API Contracts (Preserve)

- Contract C1 (US2, FR5, FR7): `POST /reviews`
  - Request remains single-node: `review_stage`, `call_id`, `node_id`, `snippet_text`.
  - Response remains `CreateReviewResponse` with `review_id`, `status`.
  - Validation/error code semantics remain baseline-compatible (including idempotency mismatch behavior).

- Contract C2 (US2, FR6, FR7): `POST /api/structured-review`
  - Request remains multi-node: `review_stage`, `call_id`, `nodes[] { node_logical_id, text }`.
  - Response remains `CreateReviewResponse` with `review_id`, `status`.
  - Validation/error code semantics remain baseline-compatible (including idempotency mismatch behavior).

### Internal Shared-Core Contract (New, Internal Only)

- Contract C3 (US1, FR1, FR2, FR3, FR4):
  - Input (conceptual): call context (`call_id`, `review_stage`), node execution context (`node_logical_id`, `node_text`, expectations/policy inputs).
  - Output (conceptual): normalized execution result:
    - execution status/outcome
    - parsed validated findings
    - policy post-check outcomes (blocking/warning metadata)
    - failure classification suitable for endpoint-stable error mapping
    - non-invasive telemetry payload/hooks
  - Does NOT own endpoint-specific DB write semantics.

### State / Transition Expectations

- Contract C4 (US2, FR8):
  - Single-node and structured flows keep existing persistence pathways and status transitions.
  - Structured deterministic `NOT_ASSESSABLE` card behavior remains endpoint/service-owned.

### Validation Rules (Parity Guardrails)

- Contract C5 (US2, FR5, FR6, FR7, FR8):
  - Preserve ordering/priority of route/service checks where externally observable.
  - Preserve current timeout/error mapping behavior in first migration slice.
  - Preserve existing idempotency key and payload-hash mismatch semantics per endpoint baseline.

## 6. Components / Modules

### Boundaries and Responsibilities

- `backend/main.py`
  - Keep route contracts, auth/header/idempotency/quota/route-level validation semantics unchanged.

- `backend/app/services/reviewer_service.py`
  - Single-node orchestration adapter; remains owner of single-node persistence semantics.
  - Delegates execution steps to shared core seam.

- `backend/app/services/structured_reviewer_service.py`
  - Structured orchestration adapter; remains owner of structured persistence semantics.
  - Delegates execution steps to shared core seam.

- `backend/app/services/review_execution_core.py` (new)
  - Shared internal execution concerns: policy injection/post-checks, LLM call seam, parse/validate seam, telemetry seam.
  - Returns normalized execution result; no endpoint-specific persistence writes.

### Design Tree (Dependencies + Ordering)

1. Establish parity tests and baseline assertions.
2. Introduce shared-core module interfaces and no-op telemetry seam.
3. Migrate structured path to shared core (higher complexity).
4. Re-run parity; stabilize.
5. Migrate single-node path.
6. Re-run parity; stabilize and finalize.

### Deep Modules

- `review_execution_core.py` is the deep module:
  - Small interface: execute one node execution unit with policy + validation seams.
  - Hidden complexity: policy selection, LLM seam behavior preservation, parse/validate pipeline, warning/blocking outputs.
  - Stable seam: adapters should consume typed result, not internal implementation details.

### Suggested File Paths

- `backend/app/services/review_execution_core.py` (new)
- `backend/app/services/reviewer_service.py` (adapt)
- `backend/app/services/structured_reviewer_service.py` (adapt)
- `backend/tests/test_api.py` (contract parity assertions)
- `backend/tests/...` service-level tests for shared core seam

## 7. Edge Cases

- EC1 (US2): Same idempotency key with different payload remains mismatch error per endpoint baseline.
- EC2 (US2, US3): Validation ordering differences may alter exposed error code priority; parity tests must catch this.
- EC3 (US2): Structured path must retain deterministic `NOT_ASSESSABLE` behavior for missing cross-node context.
- EC4 (US3): LLM timeout path must preserve status/error semantics and summary behavior for both adapters.
- EC5 (US1, US3): Shared core must not accidentally enforce one endpoint’s persistence assumptions onto the other.
- EC6 (US3, US4): Partial migration phase must keep untouched endpoint behavior stable while first endpoint is flipped.

## 8. Testing Decisions (TDD)

TDD scope applies to behavior-preserving refactor boundaries and regression prevention.

- Public seams under test:
  - Endpoint contracts via API tests (`/reviews`, `/api/structured-review`) (FR5, FR6, FR7, FR8, FR9)
  - Shared core service seam behavior via deterministic stubbed tests (FR1, FR2, FR3, FR4, FR10)

- Boundary mocking strategy:
  - Mock/stub only LLM boundary and external non-deterministic calls.
  - Avoid mocking business logic branches inside shared core and adapters.

- Minimal test types per story:
  - US1: service-level shared-core tests for policy injection/post-check + parse/validate.
  - US2: endpoint API parity tests for unchanged request/response/error/idempotency semantics.
  - US3: regression-focused failure path tests (timeout, policy violation, validation mismatch).
  - US4: incremental migration guard tests ensuring one endpoint can switch without affecting the other.

- Prove-it tests:
  - Idempotency mismatch parity per endpoint.
  - Timeout/error mapping parity per endpoint.
  - Structured persistence semantics parity including `NOT_ASSESSABLE`.

## 9. Telemetry (Minimal)

- Add standardized internal execution events/hooks:
  - execution started/completed
  - policy check outcome (warning/blocking counts)
  - parse/validation failure reason class
  - timeout/failure category
- Initial requirement is seam creation with non-invasive behavior (no product-facing behavior changes).

## 10. Deferred / Not in MVP

- Endpoint consolidation/deprecation (`POST /reviews` to structured-only create flow).
- Performance behavior changes (parallelization, retries/backoff tuning, prompt strategy changes).
- Full telemetry platform rollout (Sentry dashboards/alerts).
- Contract redesigns (new grouped response shapes, DTO changes).

## 11. Open Questions (if any)

- None for Phase 2 entry.
- Defaults applied:
  - Shared-core contract should be introduced with explicit typed interfaces in this WF to reduce drift in Task planning.
  - Migration should rely on parity tests and incremental endpoint flips; no shadow mode in MVP.

## 12. Changelog

- v0.1 (2026-02-26): Initial PRD from brainstorm.
- v0.2 (2026-02-26): Applied risk-audit tightenings (parity clarity, out-of-scope guardrails, explicit defaults) and marked Ready for Tasks.
