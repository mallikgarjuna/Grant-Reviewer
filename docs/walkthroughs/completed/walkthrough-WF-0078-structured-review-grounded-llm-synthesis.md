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

- Added `backend/app/services/structured_review_synthesis_service.py` with a typed same-card request/result contract, explicit node-title carriage, and fail-closed parsing for accepted vs rejected synthesis outcomes.
- Updated `backend/app/services/structured_reviewer_service.py` to build bounded ERC PoC-only synthesis requests after deterministic feedback generation, attempt additive synthesis only for approved WF-0077 deterministic guidance with canonical subordinate-prompt context, and retain seam-only proof via in-memory `last_synthesis_requests` / `last_synthesis_results`.
- Added DB-backed service tests covering:
  - accepted tracer-bullet synthesis without replacing deterministic `feedback_text`
  - per-card fail-closed fallback for timeout, client error, malformed output, and ungrounded output
  - explicit no-attempt gating when an ERC PoC card lacks approved deterministic guidance
  - same-card node-title carriage through the emitted seam request/prompt
  - whole-review completion when all additive attempts reject
  - emitted payload exclusion of raw machine `reason`, full-call/legacy artifacts, and unrelated-card context
  - non-targeted no-attempt behavior outside `ERC-2026-PoC`
- Added no-DB helper tests covering wrong-element, ambiguous-card/mismatched, and malformed-output rejection.

## Verification

- `pre-commit run --all-files` -> passed
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py` -> `48 passed in 19.74s`
- `cd backend && uv run pytest tests/test_structured_review_synthesis_service.py` -> `3 passed in 1.10s`
- `cd backend && uv run pytest -m no_db` -> `316 passed, 227 deselected in 8.62s`

## Audit Outcome

Phase 3.2 initially found two blocking contract gaps and one non-blocking observability gap:
- synthesis was attempted for any non-empty ERC PoC card instead of only approved WF-0077 deterministic-guidance cards with canonical subordinate-prompt context;
- same-card node title context was missing from the typed synthesis request;
- unexpected synthesis exceptions were folded into `client_error`.
All three findings were closed in Phase 3.3 and re-verified.

## Carry-Through Decision

WF-0078 intentionally stops at the backend seam.
Persistence, repository reads, API detail models, export text, and frontend review-detail rendering still consume deterministic `feedback_text`.
No schema/API/frontend rollout is claimed here; any researcher-visible synthesized companion remains a dependent follow-on slice.

## Remaining Risks

- Researcher-visible rollout still requires an explicit persistence/API/frontend carry-through decision and verification in a new workflow.
