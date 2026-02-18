# PRD: WF-0016 — Upgrade Review Results UX

**Status**: Approved
**Owner**: AIEng_MG
**Version**: 1.0
**Last Updated**: 2026-02-17

## 1. Overview
The current Review Results UX is functional but lacks visual hierarchy and impact. Users struggle to quickly identify which criteria they failed or passed. This PRD defines the upgrade to a "Scorecard" style UI with clear headers, visual ratings, and a top-level summary.

## 2. Goals
- **Scannability**: Users can see their 1-5 ratings at a glance.
- **Clarity**: Criterion Name is the primary identifier for feedback.
- **Hierarchy**: Summary is distinct from details.

## 3. Scope
### 3.1. In Scope
- **Backend**: Adding `criterion_description` and `criterion_name` (as title) to `ReviewCardSummary` API response.
- **Frontend**: Creating `ScoreBadge` component.
- **Frontend**: Updating `ReviewCard` to use the new layout.
- **Frontend**: Creating `ReviewSummary` component.
- **Frontend**: Integrating these into the Review Details page.

### 3.2. Out of Scope
- Changing the rubric ingestion logic.
- Changing the LLM prompting logic (we assume the score is already generated correctly).
- Mobile-specific layout optimizations (responsive is expected but not mobile-first overhaul).

## 4. Requirement Specifications
### 4.1. Functional Requirements
- **FR1**: The Review Card header MUST display the Criterion Name.
- **FR2**: The Review Card header MUST display a visual score (1-5 color-coded).
- **FR3**: The Review Card footer MUST display the Criterion Description.
- **FR4**: A Review Summary box MUST appear above the list of cards.
- **FR5**: The Review Summary MUST show the Overall Rating and Overall Summary text.

### 4.2. UX/UI Requirements
- **Score Colors**:
  - 5 (Excellent): Green
  - 4 (Good): Light Green / Teal
  - 3 (Fair): Yellow
  - 2 (Poor): Orange
  - 1 (Bad): Red
- **Typography**: Criterion Name should be `font-semibold` or `font-bold`.

## 5. Technical Design
### 5.1. API Schema Changes
- **File**: `backend/app/schemas/api.py`
- **Model**: `ReviewCardSummary`
- **Change**: Add `criterion_description: str | None`. Ensure `criterion` field maps to `EvaluationCriterion.name` (Title) or `EvaluationElement.name` depending on granularity. Currently it maps to the element name. We might need `criterion_title` vs `criterion_subtitle` if we want both.
- **Decision**: Let's keep `criterion` as the main title (Element Name) and add `description` (Element Description). The Spec asked for "Criterion Name" as header. Our model has `EvaluationElement` linked to `EvaluationCriterion`.
  - If we want the Grouping (Criteria > Element), that's harder.
  - **Simplification**: Just display the `EvaluationElement.name` as the card title. Add `description` from `EvaluationElement.description`.

### 5.2. Frontend Architecture
- **New Components**:
  - `src/components/review/ScoreBadge.tsx`: Accepts `rating` (ReviewRating enum). Renders pill or dots.
  - `src/components/review/ReviewSummary.tsx`: Accepts `ReviewSummary` object.
- **Modified Components**:
  - `src/components/review/ReviewCard.tsx`: Update layout.

## 6. Verification Plan
### 6.1. Automated Tests
- **Backend Unit Tests**: Verify `ReviewCardSummary` includes description.
- **Frontend Unit Tests**: Verify `ScoreBadge` returns correct color class for each rating.

### 6.2. Manual Verification
- **Scenario**: Run a new review.
- **Checklist**:
  1.  Submit a snippet.
  2.  Monitor results page.
  3.  Verify Top Summary box exists and has content.
  4.  Verify Cards have bold Titles (Element Names).
  5.  Verify Cards have colored score indicators.
  6.  Verify Cards show description in footer.
