# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-01

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: deterministic success replay + persistence contract

Goal:
- Prove one end-to-end hardening slice for `POST /api/structured-review` where identical payload + `Idempotency-Key` replay is deterministic and persisted review identity/status remain stable for `/app/reviews` retrieval behavior.
Slice: tracer-bullet-structured-api-replay
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR10
Depends on: none
Enables: Task 2, Task 3, Task 5
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Fixture matrix includes a `structured_api` success replay case for `nwo_veni_2025_preproposal` with explicit expected HTTP/persistence/status metadata fields.
- API contract test asserts same key + same payload returns stable review identity and stable status.
- Test asserts created review remains persisted and discoverable by history-facing API surfaces that back `/app/reviews` behavior.
TDD Plan:
- RED: add failing parametrized contract test in `backend/tests/test_api.py` for replay identity/status stability and persisted review visibility expectation.
- GREEN: minimally wire fixture row consumption and assertions; keep production code unchanged unless a real regression is exposed.
- REFACTOR: extract fixture-to-assertion helpers for replay/persistence checks (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t1.db uv run pytest -q tests/test_api.py -k "wf0043_contract_structured_api_replay"`
Risks (if any):
- Historical-data assumptions for `/app/reviews` discoverability can create false negatives if assertions are not scoped to the created test record.

### [x] Task 2 — Structured API error semantics matrix (no persistence on API-side failures)

Goal:
- Lock deterministic status/error semantics for API-side validation and pre-persistence failures without changing existing mappings.
Slice: structured-api-error-contracts
User Stories: US1
PRD Requirements: FR1, FR3, FR4, FR9
Depends on: Task 1
Enables: Task 4, Task 5
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Matrix rows cover required deterministic core error codes for this WF scope (`VALIDATION_ERROR`, `UNKNOWN_NODE_ID`, `REVIEW_STAGE_NODE_MISMATCH`, `IDEMPOTENCY_PAYLOAD_MISMATCH`).
- If `QUOTA_EXCEEDED` or `REVIEWS_DISABLED` rows are not deterministic in local test setup, they are explicitly documented as deferred in Task 6 verification notes.
- API tests assert existing HTTP status + error code mappings per case, including payload mismatch semantics.
- API-side error/validation cases assert no `Review` persistence side effects.
TDD Plan:
- RED: add failing matrix-driven contract tests for status/code mappings and no-persist invariants.
- GREEN: implement fixture-driven assertions and deterministic setup/stubs only in test layer.
- REFACTOR: consolidate repeated error response assertion helpers.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t2.db uv run pytest -q tests/test_api.py -k "wf0043_contract_structured_api_error"`
Risks (if any):
- Some quota/disable paths may require deterministic service stubbing to avoid flaky environment-dependent outcomes.

### [x] Task 3 — Structured API post-persistence failure semantics (`FAILED` review retained)

Goal:
- Lock the split boundary where post-creation execution failures return stable API contract while persisting failed review state.
Slice: structured-api-post-persist-failure
User Stories: US1
PRD Requirements: FR5, FR9
Depends on: Task 1
Enables: Task 5
Parallelizable: yes
Files to modify:
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Matrix includes a deterministic service/engine failure case after review creation.
- API test asserts response remains `200` with `{review_id, status}` contract (existing semantics), while persisted review status is `FAILED`.
- Test asserts deterministic summary convention for failed persisted reviews used by review history/detail surfaces.
TDD Plan:
- RED: add failing test for post-persistence failure response and persisted failed state summary convention.
- GREEN: add deterministic failure seam setup in tests and assert existing behavior.
- REFACTOR: share persistence lookup helper with Task 1 assertions.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t3.db uv run pytest -q tests/test_api.py -k "wf0043_contract_structured_api_failed_persisted"`
Risks (if any):
- Failure seam placement may accidentally exercise pre-persistence path unless test seam explicitly forces post-create failure.

### [x] Task 4 — Single-snippet reviewer-policy mode seam contracts

Goal:
- Add deterministic seam tests for `BLOCKING`, `POST_CHECK`, and `PROMPT_ONLY` enforcement behavior in single-snippet flow while preserving existing semantics.
Slice: single-snippet-policy-seam
User Stories: US2
PRD Requirements: FR6, FR9
Depends on: Task 2
Enables: Task 5
Parallelizable: yes
Files to modify:
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
- `backend/tests/test_review_execution_core.py`
Acceptance Criteria:
- Matrix includes three `single_snippet_policy` rows for `BLOCKING`, `POST_CHECK`, and `PROMPT_ONLY`.
- Seam tests assert `BLOCKING` produces execution failure semantics, `POST_CHECK` surfaces warnings without blocking completion, and `PROMPT_ONLY` remains non-blocking/prompt-influence only.
- Assertions are deterministic and scoped to the single call `nwo_veni_2025_preproposal`.
TDD Plan:
- RED: add failing policy-mode seam tests in `backend/tests/test_review_execution_core.py` keyed by matrix `case_id`.
- GREEN: add deterministic stubs/fixtures for policy outcomes in tests only.
- REFACTOR: extract reusable policy assertion helper for warning/failure semantics.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t4.db uv run pytest -q tests/test_review_execution_core.py -k "wf0043_contract_single_snippet_policy"`
Risks (if any):
- Over-mocking can hide integration boundary drift unless assertions verify persisted outcome shape where relevant.

### [x] Task 5 — Deterministic fixture matrix coverage + focused-run selector

Goal:
- Ensure fixture matrix is the single WF-0043 scenario source and provide deterministic focused-run convention for pre-merge verification.
Slice: fixture-matrix-coverage-and-focused-run
User Stories: US3
PRD Requirements: FR7, FR10
Depends on: Task 1, Task 2, Task 3, Task 4
Enables: Task 6
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/wf_0043_contract_matrix.yaml`
- `backend/tests/test_api.py`
- `backend/tests/test_review_execution_core.py`
Acceptance Criteria:
- Matrix has `8-12` deterministic rows and all required metadata fields from PRD Contract C5.
- WF-0043 tests in both files are discoverable via a stable focused-run naming convention (`wf0043_contract_<surface>_<case_id>`) with deterministic subset execution.
- Each matrix `case_id` maps to at least one assertion path in endpoint or seam tests.
TDD Plan:
- RED: add failing coverage guard assertion(s) that detect missing/unmapped matrix rows in targeted tests.
- GREEN: finalize case wiring and stable selector naming in tests.
- REFACTOR: deduplicate matrix loader/selector helpers across test modules.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t5.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_"`
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t5b.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_structured_api or wf0043_contract_single_snippet_policy"`
Risks (if any):
- Selector convention can drift if case IDs/marks are not enforced consistently between modules.

### [x] Task 6 — Verification bundle docs for WF-0043 hardening

Goal:
- Publish the compact verification bundle documenting scenario expectations, deterministic commands, and invariants to preserve.
Slice: wf0043-verification-docs
User Stories: US3
PRD Requirements: FR8, FR9, FR10
Depends on: Task 5
Enables: none
Parallelizable: no
Files to modify:
- `docs/brainstorms/brainstorm-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md`
Acceptance Criteria:
- Docs include a case table aligned to fixture matrix fields (`case_id`, surface, expected HTTP/error, persistence, expected status/summary convention).
- Docs list exact deterministic pytest commands for focused WF-0043 subset and DB isolation requirement.
- Docs include an explicit note for any intentionally deferred non-deterministic scenarios (if any), including reason and follow-up WF reference.
- Docs explicitly state guardrails: preserve API error semantics/idempotency and `/app/reviews` persistence behavior; no new tooling.
TDD Plan:
- N/A (documentation-only task).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t6.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_"`
- `rg -n "case_id|expected_http_status|expect_review_persisted|summary|Idempotency-Key|/app/reviews|no new tooling" docs/brainstorms/brainstorm-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md`
Risks (if any):
- Docs can drift from fixture matrix if case IDs are renamed without synchronized updates.

## Changelog

- v0.1 (2026-03-01): Initial task breakdown from PRD.
- v0.2 (2026-03-01): Applied task-review refinements (deterministic focused-run naming convention, verification command tightening) and marked Ready for Implementation.
- v0.3 (2026-03-01): Adversarial review revisions (strict selector naming contract, deterministic verification command alignment across tasks, and explicit deferred-scenario documentation rule).
