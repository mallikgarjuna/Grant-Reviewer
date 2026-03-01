# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-01

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: review detail call identity contract

Goal:
- Prove a thin vertical slice where review detail exposes generic call identity fields and the frontend review detail path remains compatible.
Slice: tracer-bullet-review-detail-contract
User Stories: US3, US4
PRD Requirements: FR8, FR9, FR10
Depends on: none
Enables: Task 2, Task 7
Parallelizable: no
Files to modify:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- `GET /reviews/{review_id}` returns `call_id` and `call_code` for review detail.
- Existing review-detail fields and error semantics remain unchanged.
- Frontend review-detail path remains non-breaking when new fields are present.
TDD Plan:
- RED: add failing API contract test in `backend/tests/test_api.py` asserting `call_id`/`call_code` are present for review detail.
- GREEN: minimally extend response schema/build path in `backend/app/schemas/api.py` and `backend/main.py`.
- REFACTOR: deduplicate review-detail serialization helper usage (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t1.db uv run pytest -q tests/test_api.py -k "review_detail and call_id and call_code"`
- `cd frontend && npm run check:bff`
Risks (if any):
- Legacy review records may not carry call linkage; must be handled in later compatibility tasks.

### [x] Task 2 — Backend review detail deterministic ordering + legacy fallback

Goal:
- Make review-detail ordering deterministic and backward-compatible for records lacking call metadata.
Slice: backend-ordering-fallback
User Stories: US3, US4
PRD Requirements: FR6, FR13, FR14, FR15
Depends on: Task 1
Enables: Task 7
Parallelizable: no
Files to modify:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Ordering uses `order_index` ascending then `node_logical_id` ascending fallback.
- Unknown/missing node mappings are ordered last and flagged as unmapped in response metadata.
- Legacy records without call linkage return `ordering_source: "review_payload_fallback"` and remain retrievable.
- Tests explicitly cover both response shapes (`call_id` present vs null/fallback ordering source) for skew-safe compatibility.
TDD Plan:
- RED: add failing tests in `backend/tests/test_api.py` for tie/null ordering, unknown nodes, and legacy fallback path.
- GREEN: implement deterministic ordering and fallback response metadata in API layer.
- REFACTOR: extract ordering comparator/fallback mapping helper for readability and shared shape assertions.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t2.db uv run pytest -q tests/test_api.py -k "review_detail and (order_index or ordering_source or fallback)"`
Risks (if any):
- Existing persisted data may surface edge-case nulls that require explicit guardrails.

### [x] Task 3 — Backend call config contract exposes `domain_options[]`

Goal:
- Expose domain UX options from backend call metadata/config with stable shape and ordering.
Slice: backend-domain-options-contract
User Stories: US1, US2
PRD Requirements: FR3, FR12, FR18
Depends on: none
Enables: Task 4, Task 8
Parallelizable: yes
Files to modify:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- `GET /api/public/calls/{call_logical_id}/config` returns `domain_options: [{value,label,order_index}]` (possibly empty).
- Options are deterministic (`order_index`, then `value`) and sourced from call metadata, not per-call constants.
TDD Plan:
- RED: add failing API contract tests for populated and empty `domain_options`.
- GREEN: implement metadata extraction/response wiring.
- REFACTOR: centralize domain-options extraction helper.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t3.db uv run pytest -q tests/test_api.py -k "call_config and domain_options"`
Risks (if any):
- Incorrect extraction from call definition could silently reintroduce frontend workarounds.

### [x] Task 4 — Submit UI consumes backend `domain_options[]` (remove hardcoding)

Goal:
- Remove call-specific domain option hardcoding and drive selector visibility/options entirely from backend config.
Slice: frontend-domain-options-wiring
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR12, FR18
Depends on: Task 3
Enables: Task 6, Task 8
Parallelizable: no
Files to modify:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/lib/submit/loadStructuredCalls.ts`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
Acceptance Criteria:
- Runtime domain selector behavior is driven by backend `domain_options[]` contract.
- Domain selector appears only when backend config exposes options.
- Existing submit behavior remains stable when options are absent.
TDD Plan:
- RED: add failing UI tests in `UniversalSubmitForm.test.tsx` for backend-driven domain selector visibility/options.
- GREEN: wire form state to backend `domain_options` and ensure structured-call loading path remains compatible.
- REFACTOR: simplify domain-state reset logic on call changes.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "domain"`
- `cd frontend && npx vitest run src/lib/submit/loadStructuredCalls.test.ts -t "config"`
Risks (if any):
- Draft restore logic may preserve stale domain values if selector options change.

### [x] Task 5 — Backend compliance and policy retry determinism

Goal:
- Lock deterministic compliance classification and bounded reviewer-policy retry semantics without changing external errors/idempotency.
Slice: backend-compliance-policy-determinism
User Stories: US2, US3, US4
PRD Requirements: FR4, FR5, FR9, FR11, FR16
Depends on: none
Enables: Task 6, Task 8
Parallelizable: yes
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/tests/test_compliance_engine.py`
- `backend/tests/test_review_execution_core.py`
Acceptance Criteria:
- Enforceable constraints remain blocking; non-enforceable constraints remain informational.
- Reviewer policy executes with max one retry (two attempts total), preserving existing external failure semantics on terminal failure.
TDD Plan:
- RED: add failing tests for enforceable/informational split and single-retry policy behavior.
- GREEN: implement minimal bounded retry + deterministic classification guarantees.
- REFACTOR: isolate retry-attempt policy constant/helper.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t5.db uv run pytest -q tests/test_compliance_engine.py tests/test_review_execution_core.py -k "informational or blocking or retry"`
Risks (if any):
- Retry path can unintentionally bypass policy if failure handling is not strict.

### [x] Task 6 — Submit UI informational guidance section (non-blocking)

Goal:
- Render non-enforceable constraints as a dedicated informational section without blocking submission.
Slice: frontend-informational-guidance
User Stories: US2
PRD Requirements: FR5, FR17
Depends on: Task 4, Task 5
Enables: Task 8
Parallelizable: no
Files to modify:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
Acceptance Criteria:
- Informational findings render in a dedicated non-blocking area separate from hard-block errors.
- Submission remains blocked only for deterministic enforceable failures.
TDD Plan:
- RED: add failing tests for informational-only result sets and mixed blocking+informational result sets.
- GREEN: implement dedicated informational rendering path and preserve block semantics.
- REFACTOR: normalize compliance message formatting helpers (`skip` if none).
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "informational"`
Risks (if any):
- Mixed states may create confusing UX if labels are not explicit.

### [x] Task 7 — Review detail page call-driven ordering + skew-safe fallback

Goal:
- Replace Veni-specific review-detail assumptions with call-driven ordering and compatibility fallbacks.
Slice: frontend-review-detail-call-driven
User Stories: US3, US4
PRD Requirements: FR1, FR6, FR7, FR13, FR14, FR15, FR18
Depends on: Task 1, Task 2
Enables: Task 8
Parallelizable: no
Files to modify:
- `frontend/src/lib/bff/types.ts`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Page uses review-detail call metadata and call nodes to group/order cards deterministically.
- Missing new fields degrades gracefully (no crash) and shows fallback note for legacy data.
- No per-call label/order constants remain in review detail.
TDD Plan:
- RED: add failing page tests for call-driven ordering, legacy fallback note, and mixed-version payloads.
- GREEN: implement ordering/fallback rendering logic.
- REFACTOR: extract ordering/grouping logic into pure helper in the page module.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "ordering|fallback|legacy"`
Risks (if any):
- Node metadata fetch timing can cause transient partial renders without robust guards.

### [x] Task 8 — Guardrails and universality proof tests

Goal:
- Add regression guardrails that enforce no-hardcoding seams and validate arbitrary node-count/domain-absence behavior with a non-Veni fixture.
Slice: guardrails-and-universality
User Stories: US1, US4
PRD Requirements: FR18, FR19
Depends on: Task 3, Task 4, Task 6, Task 7, Task 9
Enables: none
Parallelizable: no
Files to modify:
- `frontend/src/lib/submit/domainOptions.ts`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Tests fail if per-call maps/branches/constants are reintroduced in protected submit/review-detail seams.
- At least one non-Veni structured fixture proves arbitrary node-count handling and domain selector absence when `domain_options[]` is empty.
- Legacy hardcoded domain-options helper path is removed (or reduced to inert compatibility shim with no per-call map constants).
TDD Plan:
- RED: add failing guardrail tests for hardcoded behavior and non-Veni fixture expectations.
- GREEN: adjust implementation seams only as needed to satisfy guardrails.
- REFACTOR: deduplicate fixture builders across UI tests.
Verification Steps:
- `cd frontend && npm run test:ui`
- `cd frontend && npm run check:bff`
- `rg -n "VENI_NODE_LABELS|VENI_NODE_ORDER|DOMAIN_OPTIONS_BY_CALL" frontend/src -S`
Risks (if any):
- Guardrail tests can become brittle if assertions target implementation detail instead of behavior.

### [ ] Task 9 — Persistence and `/app/reviews` history invariants

Goal:
- Prove FR10 invariants end-to-end: successful structured review persists and remains visible/retrievable in review history surfaces.
Slice: persistence-history-invariants
User Stories: US4
PRD Requirements: FR10, FR9
Depends on: Task 1, Task 2, Task 5, Task 7
Enables: Task 8
Parallelizable: no
Files to modify:
- `backend/tests/test_api.py`
- `frontend/src/app/app/page.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Successful structured review creation remains persisted and appears in `/app/reviews` list behavior.
- Review detail remains retrievable from history path after contract/fallback changes.
- Idempotency mismatch behavior remains unchanged while preserving persistence semantics.
TDD Plan:
- RED: add failing backend/frontend tests for review list visibility after create and detail retrieval from history route.
- GREEN: apply minimal compatibility fixes only if tests expose regressions.
- REFACTOR: consolidate repeated review-history fixtures/helpers across page tests.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t9.db uv run pytest -q tests/test_api.py -k "structured_review and (reviews_list or review_detail or idempotency)"`
- `cd frontend && npx vitest run src/app/app/page.test.tsx src/app/app/reviews/[reviewId]/page.test.tsx -t "reviews|history|detail"`
Risks (if any):
- Cross-layer fixture drift can produce false negatives if backend and frontend assumptions diverge.

## Changelog

- v0.1 (2026-03-01): Initial task breakdown from PRD v0.3 with atomic slices, dependency metadata, and explicit TDD plans.
- v0.2 (2026-03-01): Applied task-review revisions (explicit frontend type-sync seam for `domain_options[]`, hardcoded-domain-helper retirement tasking, and readiness polish); marked Ready for Implementation.
- v0.3 (2026-03-01): Applied adversarial pass revisions (stronger tracer-bullet compatibility check, backend mixed-shape assertions, submit-loader integration seam, explicit FR10 persistence/history task, and hardened anti-hardcoding verification).
