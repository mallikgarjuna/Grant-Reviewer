# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-01

## Implementation Summary

- Delivered WF-0043 as a deterministic contract-hardening slice for `nwo_veni_2025_preproposal` with no production API behavior changes.
- Added a dedicated fixture matrix at `backend/tests/fixtures/wf_0043_contract_matrix.yaml` covering structured API + single-snippet policy surfaces.
- Added structured API contract tests for:
  - idempotency replay stability and persisted history/detail discoverability
  - deterministic error semantics (`VALIDATION_ERROR`, `UNKNOWN_NODE_ID`, `REVIEW_STAGE_NODE_MISMATCH`, `IDEMPOTENCY_PAYLOAD_MISMATCH`)
  - post-persistence failure contract (`200` + persisted `FAILED` + summary prefix convention)
- Added single-snippet reviewer-policy seam tests covering `BLOCKING`, `POST_CHECK`, and `PROMPT_ONLY` behavior.
- Added matrix coverage/selector guardrails for deterministic focused execution (`wf0043_contract_*`).
- Updated WF verification bundle appendix with matrix-aligned scenario table, deterministic commands, DB isolation guidance, and explicit deferred scenarios.

## Task Commit Ledger

- `0f9a270` Task 1 — tracer bullet replay + persistence contract
- `e4545e7` Task 2 — structured API error semantics matrix
- `17830a4` Task 3 — post-persistence failure contract
- `4fcdd6f` Task 4 — single-snippet policy mode seam contracts
- `53e025b` Task 5 — fixture matrix coverage + focused selector
- `173b2e6` Task 6 — verification bundle docs
- Post-review hardening:
- `1824c5b` tighten matrix-by-surface validation and PROMPT_ONLY prompt-influence assertions

## Verification Evidence

### Focused WF-0043 suite

- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t5.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_"` (`11 passed`).
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_t5b.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_structured_api or wf0043_contract_single_snippet_policy"` (`11 passed`).

### Final verify gate

- `pre-commit run --all-files` (passed).
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_verify.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_"` (`11 passed`).
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0043_reviewfix.db uv run pytest -q tests/test_api.py tests/test_review_execution_core.py -k "wf0043_contract_"` (`11 passed`).

## Technical Audit Summary

- Phase 3 Part B found no blocking defects.
- Senior adversarial review findings were addressed:
  - removed cross-surface coverage coupling
  - consumed policy-case expectation fields in seam tests
  - added explicit PROMPT_ONLY prompt-influence assertion
  - removed ambiguous matrix expectation values for mismatch error case

## Remaining Risks

- Deferred in this WF by design: deterministic local coverage for `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` matrix rows remains a follow-up item.

## Next Steps

1. Optional: add deterministic toggles for quota/kill-switch scenarios and promote them from deferred notes into mandatory matrix rows.
2. Start next hardening WF for cross-call generalization once this single-call contract suite is accepted.
