# Task: Review History ("My Reviews")

**WF ID**: WF-0014
**Status**: Done
**Version**: v1.0
**PRD**: [PRD](docs/prds/prd-WF-0014-review-history.md)

## Context
"My Reviews" page allows researchers to view their past review history.

## Checklist

### Backend
- [x] **Repo**: Add `list_reviews_for_external_user(user_id, limit)` to `ReviewRepository`.
- [x] **Schema**: Add `ReviewListItem` and `ReviewsListResponse` to `backend/app/schemas/api.py`.
- [x] **API**: Add `GET /reviews` endpoint to `backend/main.py` (`limit=50`).
- [x] **Tests**: Add `test_list_reviews` cases in `tests/test_api.py`.

### Frontend
- [x] **BFF Types**: Add `ReviewListItem` interface to `types.ts`.
- [x] **BFF Adapter**: Add `listReviews` to `adapter.ts`.
- [x] **BFF Route**: Create `GET /api/bff/reviews/route.ts`.
- [x] **UI**: Create `/app/reviews/page.tsx` (List view).
- [x] **Nav**: Add "My Reviews" `NavLink` to `app/layout.tsx`.

### Verification
- [x] **Auto**: Run backend tests (27/27 passed).
- [x] **Auto**: Run frontend build (passed).
- [x] **Manual**: Verify list population and navigation.
