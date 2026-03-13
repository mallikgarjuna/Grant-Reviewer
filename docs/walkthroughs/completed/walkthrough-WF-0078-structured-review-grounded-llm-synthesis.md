<!-- docs/walkthroughs/completed/walkthrough-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-13

Type: feature

## Summary

WF-0078 closed as a backend-only seam proof for `ERC-2026-PoC`.
`pipeline_v1` remains the deterministic SSOT.
Per-card additive synthesis now runs only downstream in `StructuredReviewerService` via `StructuredReviewSynthesisService`, and persisted `ReviewCard.feedback_text` remains the WF-0077 deterministic fallback surface.

## What Changed

- Added `backend/app/services/structured_review_synthesis_service.py` with a typed same-card request/result contract plus fail-closed parsing for accepted vs rejected synthesis outcomes.
- Updated `backend/app/services/structured_reviewer_service.py` to build bounded ERC PoC-only synthesis requests after deterministic feedback generation, attempt additive synthesis, and retain seam-only proof via in-memory `last_synthesis_requests` / `last_synthesis_results`.
- Added DB-backed service tests covering:
  - accepted tracer-bullet synthesis without replacing deterministic `feedback_text`
  - per-card fail-closed fallback for timeout, client error, malformed output, and ungrounded output
  - whole-review completion when all additive attempts reject
  - emitted payload exclusion of raw machine `reason`, full-call/legacy artifacts, and unrelated-card context
  - non-targeted no-attempt behavior outside `ERC-2026-PoC`
- Added no-DB helper tests covering wrong-element, ambiguous-card/mismatched, and malformed-output rejection.

## Verification

- `pre-commit run --all-files` -> passed
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py` -> `45 passed in 21.80s`
- `cd backend && uv run pytest tests/test_structured_review_synthesis_service.py` -> `3 passed in 1.47s`
- `cd backend && uv run pytest -m no_db` -> `316 passed, 224 deselected in 8.00s`

## Audit Outcome

Phase 3.2 found no blocking issues.
One non-blocking observability note remains: unexpected synthesis exceptions are currently labeled as `client_error` to preserve fail-closed review completion.

## Carry-Through Decision

WF-0078 intentionally stops at the backend seam.
Persistence, repository reads, API detail models, export text, and frontend review-detail rendering still consume deterministic `feedback_text`.
No schema/API/frontend rollout is claimed here; any researcher-visible synthesized companion remains a dependent follow-on slice.

## Remaining Risks

- Additive synthesis observability is intentionally coarse for now because fail-closed completion was prioritized over differentiated internal error labeling.
- Researcher-visible rollout still requires an explicit persistence/API/frontend carry-through decision and verification in a new workflow.
