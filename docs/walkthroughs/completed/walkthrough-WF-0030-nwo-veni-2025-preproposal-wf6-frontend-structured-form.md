# WF-0030 — NWO Veni 2025 Preproposal Structured AI Review (WF-6 Phase)

Artifact: walkthrough
Version: v0.1
Status: Done
Last Updated: 2026-02-24

## Summary

Implemented and hardened the WF-0030 frontend structured submission flow for NWO Veni, including compliance-first orchestration, structured review routing, review detail grouping/coverage clarity, and local dev/test DB safety guardrails to prevent fixture contamination.

## What Was Built

- Veni structured submission UI and orchestration:
  - hardcoded 3-node form (`academic_profile`, `key_outputs`, `research_idea`)
  - local draft persistence and restore
  - compliance check -> bypass modal -> structured review flow
  - idempotency propagation and submission lifecycle handling
- BFF support for structured flow:
  - `/api/bff/check-compliance`
  - `/api/bff/structured-review`
- Review detail UX hardening:
  - explicit reviewed/not-reviewed coverage summary
  - per-section card grouping with application-form ordering
  - explicit "Not reviewed section" placeholders when node text was omitted
  - card title hierarchy switched to evaluation element (criterion moved to metadata)
  - NOT_ASSESSABLE reason + reviewer focus rendering
- Backend review-detail contract extensions:
  - evaluation element + guidance metadata
  - node metadata for grouping
  - stable card retrieval even after element archival (historical rendering)
- Safety hardening for local development/testing:
  - isolated test DB compose stack
  - pytest guard that refuses non-test DB URLs for DB-backed tests
  - reset scripts for deterministic dev/test DB state

## Files Added

- `backend/docker-compose.test.yml`
- `backend/scripts/reset_dev_db.sh`
- `backend/scripts/reset_test_db.sh`
- `backend/tests/conftest.py`

## Files Updated (Key)

- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/submit/VeniSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
- `frontend/src/components/review/ReviewCard.tsx`
- `frontend/src/lib/bff/types.ts`
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_api.py`
- `backend/README.md`
- `backend/pyproject.toml`
- `docs/tasks/task-WF-0030-nwo-veni-2025-preproposal-wf6-frontend-structured-form.md`
- `docs/parking_lot.md`
- `docs/logs/decisions.md`
- `docs/lessons.md`
- `AGENTS.md`

## Verification Evidence

- Frontend:
  - `cd frontend && npm run test:ui` (passing; includes submit orchestration + review detail tests)
- Backend API targeted (test DB):
  - `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest -q tests/test_api.py -k "empty_nodes_returns_422 or single_node_submission or archived"` (passing)
  - `cd backend && DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest -q tests/test_api.py -k "structured_review_e2e_happy_path_three_nodes or structured_review_e2e_partial_submission_marks_alignment_not_assessable"` (passing)
- Repo hygiene:
  - `pre-commit run --all-files` (passing)

## Key Risks Addressed

- Confusing single-node submission output clarified with explicit reviewed/not-reviewed sections.
- Repeated criterion headings made actionable by promoting evaluation element as primary heading.
- Local DB contamination from DB-backed tests eliminated through test DB isolation and reset scripts.
- Empty submit path now blocked client-side with explicit validation message.

## Known MVP Limits

- `/app/reviews/[reviewId]` still contains Veni-specific node mapping constants; dynamic call-aware mapping is deferred and tracked in `docs/parking_lot.md` (P2 #18).
- Coverage summary and "not reviewed" placeholders depend on `submitted_nodes` query param from submit flow; direct deep links gracefully degrade by hiding coverage summary.

## Commit Trail (Part A/B/C relevant)

- `afafe88` clarify and order structured review cards
- `b7186a4` enforce test DB isolation and reset runbooks
- `52c1163` promote evaluation element as card title
- `8c520fe` add single-node and NOT_ASSESSABLE hardening tests
- `43966e8` update task artifact with hardening completion
- `a92228b` harden empty submit and coverage fallback
