# Walkthrough — WF-0014: Review History ("My Reviews")

- **WF ID**: WF-0014
- **Status**: Done
- **Authors**: assisted by antigravity

## Overview

Added the "My Reviews" feature allow researchers to view their past review history. This includes a new backend list endpoint, a frontend list page, and navigation updates.

## Changes

### Backend
- **Endpoint**: `GET /reviews` — lists reviews for the authenticated user (paginated, sorted by date DESC).
- **Repository**: Added `list_reviews_for_external_user` method joining Review → Snippet → Call/Node to provide context.
- **Schema**: Added `ReviewListItem` and `ReviewsListResponse` models.
- **Tests**: Added 3 new tests covering success, user isolation, and auth failure.

### Frontend
- **Page**: Created `/app/reviews/page.tsx` displaying reviews in a card layout.
- **BFF**: Added `GET /api/bff/reviews` route proxying the backend.
- **Adapter**: Added `listReviews()` function.
- **Navigation**: Added "My Reviews" link to the app shell header.

## Verification Results

### Automated Tests
- **Backend**: `uv run pytest tests/test_api.py -v` passed (27 tests, including new list tests).
- **Frontend Build**: `npx next build` passed successfully.

### Manual Verification Steps
1. **Sign In**: Logged in as a user.
2. **Empty State**: Verified friendly message when no reviews exist.
3. **List View**: Submitted reviews and verified they appear in the list with correct status badges and metadata.
4. **Navigation**: Verified clicking a review card navigates to the detail page.
5. **Context**: Verified call name and section title are correctly displayed.
