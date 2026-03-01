# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-01

## Implementation Summary

- Delivered the WF-0041 single-call MVP on universal structured submit/review paths with sequential Task 1-9 execution and per-task commits.
- Extended backend review-detail contract with call identity fields (`call_id`, `call_code`) and ordering metadata (`ordering_source`, `unmapped_node_logical_ids`).
- Implemented deterministic review-card ordering (`order_index`, then `node_logical_id`) with legacy fallback (`review_payload_fallback`) for records lacking call linkage.
- Exposed backend call-config `domain_options[]` and removed hardcoded submit-domain call maps from runtime behavior.
- Made submit domain UX backend-driven: selector visibility/options are now driven only by config response `domain_options[]`.
- Enforced deterministic compliance split: blocking findings remain in `errors`, informational/non-enforceable constraints surface as non-blocking `warnings`.
- Added bounded reviewer-policy retry behavior in execution core (max one retry, two total attempts) without idempotency/error-semantic drift.
- Reworked review-detail page to call-driven ordering/grouping with skew-safe legacy fallback note when call metadata is unavailable.
- Added anti-hardcoding guardrails and non-Veni universality proof tests (arbitrary node counts, absent-domain behavior).
- Preserved `/app/reviews` persistence/history invariants and idempotency mismatch semantics with backend/frontend regression coverage.

## Task Commit Ledger

- `83df8fe` Task 1 — review detail call identity contract
- `49f02e9` Task 2 — backend ordering + legacy fallback
- `dc37c64` Task 3 — backend `domain_options[]` contract
- `6e7da12` Task 4 — frontend backend-driven domain wiring
- `bad4b03` Task 5 — compliance split + policy retry determinism
- `200df2b` Task 6 — informational guidance non-blocking UX
- `38b194a` Task 7 — call-driven review detail ordering/fallback
- `b2ac6e6` Task 8 — guardrails + universality proof tests
- `671eab0` Task 9 — persistence/history invariants
- Post-validation fixes:
- `ed13b8c` Universal submit — fix duplicate React list keys for repeated blocking messages
- `8af5b67` Universal submit — prefix blocking compliance messages with section label/fallback logical id

## Verification Evidence

### Per-task targeted verification

- Task 1: `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t1.db uv run pytest -q tests/test_api.py -k "review_detail and call_id and call_code"` and `cd frontend && npm run check:bff`.
- Task 2: `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t2.db uv run pytest -q tests/test_api.py -k "review_detail and (order_index or ordering_source or fallback)"`.
- Task 3: `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t3.db uv run pytest -q tests/test_api.py -k "call_config and domain_options"`.
- Task 4: `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "domain"` and `npx vitest run src/lib/submit/loadStructuredCalls.test.ts -t "config"`.
- Task 5: `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t5.db uv run pytest -q tests/test_compliance_engine.py tests/test_review_execution_core.py -k "informational or blocking or retry"`.
- Task 6: `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "informational"`.
- Task 7: `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "ordering|fallback|legacy"`.
- Task 8: `cd frontend && npm run test:ui && npm run check:bff && rg -n "VENI_NODE_LABELS|VENI_NODE_ORDER|DOMAIN_OPTIONS_BY_CALL" src -S`.
- Task 9: `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_t9.db uv run pytest -q tests/test_api.py -k "structured_review and (reviews_list or review_detail or idempotency)"` and frontend history/detail tests.

### Final verify bundle (Part C2)

- `pre-commit run --all-files`.
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0041_final.db uv run pytest -q tests/test_api.py tests/test_compliance_engine.py tests/test_review_execution_core.py` (`97 passed`).
- `cd frontend && npm run test:ui` (`28 passed`) and `npm run check:bff` (`ok`).

## Technical Audit Gate (Part B)

- No blocking findings in Part B technical audit.
- Non-blocking follow-up recommendations only:
  - Add explicit unknown-node-last ordering assertion in review-detail UI tests.
  - Add explicit `ordering_source="call_nodes"` assertion in backend structured happy-path test.

## Agentic Browser Validation Note

- Executed automated browser subagent test on the local development environment (`localhost:3000`).
- **Domain Selector:** Confirmed backend-driven domain mapping. The "Science Enw" option successfully appeared upon selecting the "NWO Veni 2025" call.
- **Frontend Validation:** The subagent verified that the frontend correctly blocks submission when no sections are filled (raising the "You must fill out at least one section before submitting" error).
- **Compliance Rules:** Manual UI validation through Direct API queries (due to subagent React state sync limitations) confirmed backend compliance rules accurately reject invalid state and return appropriate structured evaluation errors.
- **Review Detail Ordering:** Ran targeted UI component tests (`src/app/app/reviews/[reviewId]/page.test.tsx`) which proved that the review detail page successfully uses call-driven metadata (when available) and gracefully falls back to legacy ordering without breaking the UI.

## Remaining Risks

- Playwright automation suite is still missing for full end-to-end CI/CD integration, meaning browser validations remain manual/agentic rather than systematically enforced on PRs.

## Next Steps

1. Optional: add a lightweight browser E2E harness (Playwright) for submit -> history -> detail flow.
2. Start next WF for multi-call rollout beyond single-call MVP scope.
