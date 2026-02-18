# Brainstorm: WF-0016 — Upgrade Review Results UX

**Date**: 2026-02-17
**Status**: Phase 0.1 (Baseline)

## Overview
The goal is to upgrade the review results UX. Currently, it's just a flat list of cards with a rating pill and text. We want to make it structured, hierarchical, and visually scan-able.

## 5 Key Questions (Baseline)

### Q1: What is the primary frustration with the current review card design?
**Answer**:
Currently, the review cards display the *Proposal Snippet* or *Funding Call Section* but bury the *Evaluation Criterion* inside the text or as a secondary element. The user cares most about "How did I perform against Criterion X?". The current design prioritizes the input over the output structure. The rating (1-5) is just a pill, which lacks visual weight. The overall summary is often lost or not clearly distinguished from individual criteria feedback.

### Q2: How should we visualize the 1-5 rating scale?
**Answer**:
A "traffic light" or "scorecard" visual is standard.
- **5 (Excellent)**: Deep Green / Checked.
- **4 (Good)**: Light Green.
- **3 (Fair)**: Yellow / Warn.
- **2 (Poor)**: Orange.
- **1 (Bad)**: Red.
Ideas:
- Use a 5-segment bar or dots.
- Use a prominent colored badge with the score (e.g., "4/5").
- Color-code the card border or header background to match the score.
- Ensure accessibility (color + text/icon).

### Q3: How do we handle the hierarchy of Agency > Call > Section > Criterion?
**Answer**:
The review is typically for a specific *Section* (e.g., "Methodology"). The Section has multiple *Criteria* (e.g., "Feasibility", "Innovation").
The results should be grouped by Section if we review a whole proposal, or if reviewing a snippet against multiple criteria, grouped by Criterion.
Since our current flow receives a snippet and checks it against a rubric (which has criteria), the output is a list of *Reviews* (one per criterion).
**Design**:
- **Heading**: The Criterion Name (e.g., "Innovation Potential").
- **Sub-heading**: The specific phrasing from the rubric.
- **Body**: The AI feedback.
- **Rating**: Visual indicator.
- **Quote**: Reference to the specific part of the snippet (if applicable).

### Q4: Where does the "Overall Summary" belong?
**Answer**:
It needs to be at the top, distinct from the individual criteria cards.
- **Placement**: Sticky top or very first card.
- **Style**: "Executive Summary" style. Larger font, different background (e.g., light blue/parchment).
- **Content**: High-level strengths, weaknesses, and a holistic score (if applicable, though usually we just score criteria).

### Q5: What are the technical implications for the Frontend/BFF?
**Answer**:
- **Frontend**: New `ReviewCard` component. Needs to accept `criterion_name`, `criterion_description`, `score`, `reasoning`, `feedback`.
- **BFF/Backend**: The `Review` model already has `score`, `reasoning`, `feedback`. We need to ensure `criterion` details are fully available to the frontend.
  - Currently `Review` links to `EvaluationCriterion`. The Pydantic model response needs to include the criterion *text* and *title*, not just the ID.
  - We might need to update the `Review` schema in `models/domain.py` or the response DTO to flatten this data for easy consumption.

## Conclusion / Next Steps
The core changes are:
1.  **Backend**: Ensure `Review` objects returned to frontend contain full Criterion metadata (Title, Description).
2.  **Frontend**: Re-design `ReviewCard.tsx` to be a "Scorecard".
3.  **Frontend**: Create a `ReviewSummary` component for the top.
4.  **Frontend**: Group results by Section (if multiple sections) or just list them clearly if single section.

Propagate to Spec.
