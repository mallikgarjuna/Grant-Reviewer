# WF-0016 — Upgrade Review Results UX Tasks

Artifact: task
Version: v1.0
Status: Done
Last Updated: 2026-02-17

## Overview
Upgrade the review results UX to make it more rigorous and readable. Currently, review cards are just a rating pill + text. We need to render the criterion name as a card heading, add visual rating indicators, and format the overall summary prominently.

## Task Breakdown (Sequential Order)

### Task 1 — Backend: Enrich Review API Response
- **Goal**: Ensure the API returns `criterion_description` (and proper Title) for each review card.
- **Files to modify**:
  - `backend/app/schemas/api.py`: Update `ReviewCardSummary` to include `criterion_description`.
  - `backend/app/services/reviewer.py` (or relevant mapper): Populate the new field from `EvaluationElement`.
  - `backend/tests/test_api.py`: Update `test_create_review_success_with_stub_mode` to assert `criterion_description` is present.
- **Acceptance Criteria**:
  - `GET /reviews/{id}` returns cards with `criterion_description`.
  - Tests pass: `cd backend && uv run pytest tests/test_api.py`.
- **Status**: [x] Completed (Tests passed)

### Task 2 — Frontend: Implement UX Components
- **Goal**: Create and integrate the new visual components.
- **Files to modify**:
  - `[NEW] frontend/src/components/review/ScoreBadge.tsx`: Visual traffic light (1-5).
  - `[NEW] frontend/src/components/review/ReviewSummary.tsx`: Top-level summary box.
  - `[MODIFY] frontend/src/components/review/ReviewCard.tsx`: Update layout to Key/Value style with headers + visual score.
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`: Integrate `ReviewSummary` at top.
- **Acceptance Criteria**:
  - Review cards show Criterion Name as H3 header.
  - Review cards show Visual dots/bars for score.
  - Review cards show description in footer.
  - Summary box appears at top of results.
  - `npm run build` passes.
- **Status**: [x] Completed (Build passed)

### Task 3 — Verification
- **Goal**: Verify end-to-end.
- **Steps**:
  1.  Run backend tests: `cd backend && uv run pytest`.
  2.  Run frontend build: `cd frontend && npm run build`.
  3.  Manual UI Check:
      - Start full stack (`scripts/dev_all.sh` or separate terminals).
      - Submit a review (using mocked/stubbed backend if needed).
      - Check visual result.
- **Status**: [x] Completed

## Workflow Status

### Phase 0: Brainstorming
- [x] Brainstorming Log (5 questions)

### Phase 1: Spec
- [x] Spec File

### Phase 2: PRD
- [x] PRD File

### Phase 3: Tasks
- [x] Task Breakdown

### Phase 4: Implementation
- [x] Task 1: Backend
- [x] Task 2: Frontend
- [x] Task 3: Verification
