# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review

Artifact: walkthrough
Version: v0.1
Status: Done
Last Updated: 2026-02-22

## Summary

Implemented MVP structured multi-node review flow for NWO Veni preproposal with deterministic assessability gating, idempotent API behavior, persistence/read-path support, and backward-compatible review detail/list endpoints.

## What Was Built

- Domain and migration changes for structured reviews:
  - `Review.proposal_snippet_id` nullable
  - `Review.review_type` and `Review.structured_payload`
  - `ReviewCard.assessment_status` and `ReviewCard.not_assessable_reason`
- Shared LLM helper extraction to `backend/app/services/llm_helpers.py` and reuse in both reviewer services.
- Prompt builder extension with optional `cross_node_context`.
- Repository write/read path adaptation for structured reviews (`snippet_id=NULL`) including owner resolution and NULL-safe delete/list behavior.
- New `StructuredReviewerService` with:
  - assessable vs `NOT_ASSESSABLE` partitioning
  - hardcoded alignment dependency rule for `research_idea` expectations requiring `academic_profile` and `key_outputs`
  - partial-failure retention (`FAILED` review can keep partial cards)
- New `POST /api/structured-review` endpoint with:
  - BFF auth + idempotency + quota checks
  - structured payload/node validation and unknown/duplicate checks
  - route wiring to `StructuredReviewerService`
- API detail response extension for structured cards:
  - `assessment_status`
  - `not_assessable_reason`
  - card loading for failed structured reviews
- Post-implementation risk fixes:
  - fixed structured review visibility in history list query (NULL-safe LEFT JOIN filter)
  - restored structured `call_name` via persisted payload metadata fallback
  - documented NOTE-only rating behavior for structured cards as intentional MVP
- Optional Task 9 completed:
  - thin API E2E smoke for 3-node happy path
  - thin API E2E smoke for partial submission producing alignment `NOT_ASSESSABLE` cards

## Files Added

- `backend/app/services/llm_helpers.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/schemas/structured_review.py`
- `backend/migrations/versions/20260222_1020_add_structured_review_fields.py`
- `backend/tests/test_prompt_builder.py`
- `backend/tests/test_structured_reviewer_service.py`

## Files Updated

- `backend/app/models/domain.py`
- `backend/app/repositories/review_repository.py`
- `backend/app/schemas/api.py`
- `backend/app/services/prompt_builder.py`
- `backend/app/services/reviewer_service.py`
- `backend/main.py`
- `backend/tests/test_api.py`
- `docs/tasks/task-WF-0029-nwo-veni-2025-preproposal-wf5-structured-review.md`

## Verification Evidence

- `cd backend && uv run pytest tests/test_structured_reviewer_service.py` (5 passed)
- `cd backend && uv run pytest tests/test_prompt_builder.py` (2 passed)
- `cd backend && uv run pytest tests/test_api.py -q` (47 passed)
- `cd backend && uv run pytest tests/` (64 passed)
- `cd backend && uv run ruff check app tests`
- `pre-commit run --all-files`

## Known MVP Limits

- Structured review card severity is NOTE-only by design; assessability status carries actionable state.
- Structured payload size validation is handled in route/domain checks to preserve current API error semantics.
- E2E smoke tests use a deterministic in-test seeded graph aligned to NWO IDs rather than full YAML ingest.

## Next Steps

- Add one YAML-ingest-backed E2E for WF-0029 to detect fixture drift.
- If UX requires richer severity, add explicit rating mapping in structured LLM response schema and service.
