# Spec: WF-0016 — Upgrade Review Results UX

**Status**: Draft
**Owner**: AIEng_MG
**Last Updated**: 2026-02-17

## 1. Overview
Upgrading the Review Results UX to move from a flat list of text to a structured, scorecard-style presentation. The goal is to make the feedback immediately actionable and scannable.

## 2. User Stories
- **US 1**: As a researcher, I want to see a clear "traffic light" or numerical score for each criterion so I know where my proposal is weak.
- **US 2**: As a researcher, I want to see the Criterion Name as the main heading of each card, not the review text, so I can map feedback to requirements.
- **US 3**: As a researcher, I want a high-level summary at the top of the results to get a quick "pulse check" before diving into details.

## 3. UX Design
### 3.1. Review Summary (New Component)
- **Position**: Top of the results list.
- **Style**: Distinct background (e.g., `bg-muted/50` or light parchment).
- **Content**:
  - "Review Summary" heading.
  - "Overall Score" (calculated average of criteria scores, e.g., "3.8 / 5").
  - "Key Action Items" (synthesis of lowest-scoring criteria).

### 3.2. Review Card (Redesign)
- **Header**:
  - Left: Criterion Name (H3).
  - Right: Visual Score Indicator.
- **Score Visual**:
  - 5 segments (dots or bars).
  - Color coded:
    - 4-5: Green (`text-green-600`)
    - 3: Yellow (`text-yellow-600`)
    - 1-2: Red (`text-red-600`)
- **Body**:
  - Review text (markdown supported).
  - "Reasoning" section (collapsible or clearly labeled).
  - "Quote" (if available).
- **Footer**:
  - Criterion Description (small text, muted).

## 4. Technical Implementation
### 4.1. Backend / BFF
- **Model**: `Review` in `backend/app/models/domain.py`.
- **Requirement**: Ensure the `Review` object sent to frontend includes:
  - `criterion`: Full object or flattened fields (`title`, `description`, `weight`).
  - Currently `ProposalReview` contains a list of `Review` objects. Each `Review` links to a `criterion_id`.
  - **Change**: The BFF (or backend service) must dereference `criterion_id` to include the Criterion data in the response, OR the frontend must have the Rubric loaded to map IDs to Names.
  - **Decision**: Backend should Hydrate the response. It's cleaner for the frontend. Return a `ReviewRead` DTO that includes `criterion_title` and `criterion_description`.

### 4.2. Frontend
- **Components**:
  - `src/components/review/ReviewCard.tsx`: Update to receive `criterion` data and render new layout.
  - `src/components/review/ReviewSummary.tsx`: New component to calculate/display summary.
  - `src/components/review/ScoreBadge.tsx`: New component for visual score (circles/bars).
- **State**:
  - No complex state changes; just rendering props.

## 5. Verification Plan
- **Manual**: Run a review (using the demo script or UI) and verify:
  - Criteria names are headers.
  - Scores are visual.
  - Summary appears at top.
  - Colors match the score (Red/Yellow/Green).
- **Automated**:
  - Unit test for `ReviewCard` rendering.
  - Unit test for `ScoreBadge` color logic.
