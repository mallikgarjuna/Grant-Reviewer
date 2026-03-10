<!-- docs/walkthroughs/completed/walkthrough-WF-0071-node-hierarchy-selector.md -->
# Walkthrough — WF-0071 Node Hierarchy Selector

## Overview
This walkthrough demonstrates the completion of WF-0071, which introduced hierarchical node parsing and selection. Users can now see a structured grouping of sections in the submission form and ancestors breadcrumbs in the review cards.

## Changes Made
- **Frontend Logic**: Updated `renderModel.ts` to transform flat node lists into hierarchical structures with `isContainer` identification.
- **Submission Form**: Refactored `UniversalSubmitForm.tsx` to render 1-level visual grouping. Grouping headers are informational and cannot be selected for submission.
- **Review Card**: Enhanced `ReviewCard.tsx` (and its parent) to construct and display ancestor breadcrumbs for better structural context.

## Verification Results

### Automated Tests
- `vitest`: PASS (76 tests) across:
  - `src/lib/submit/renderModel.test.ts` (parsing + "Uncategorized" fallback)
  - `src/components/submit/UniversalSubmitForm.test.tsx` (unselectable group headers + leaf submission)
  - `src/components/review/ReviewCard.test.tsx` (breadcrumb construction)
  - `src/app/app/reviews/[reviewId]/page.test.tsx` (review page integration expectations)

### Visual Verification
Visual verification was performed on `localhost:3000`.

#### Submission Form Hierarchy
- The submit form groups leaf nodes under 1-level parent headers (for example, `Part A`, `Part B1`).
- Parent headers are informational only (cannot be selected/submitted).

#### Review Card Breadcrumbs
- Review cards display the full ancestor path (for example, `Part A > Budget > Resources and Time Commitment`).

## Remaining Risks
- None identified. The 1-level flat grouping handles existing complex calls (ERC, MSCA) as intended for the MVP.

## Next Steps
1. Ship the feature branch to `main`.
2. Archive workflow artifacts.
