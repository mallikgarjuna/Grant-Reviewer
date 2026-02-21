# Brainstorm — WF-0014: Review History ("My Reviews")

- **WF ID**: WF-0014
- **Version**: v0.1
- **Last Updated**: 2026-02-16
- **Status**: Active brainstorm

---

## 1. Problem Statement

When a user submits a proposal snippet for review and closes the tab (or navigates away), the review is effectively lost — there is no way to find it again without the exact URL. The current flow only redirects to `/app/reviews/{reviewId}` after submission, and that ID is only stored in a temporary `localStorage` review-attempt object.

**Core gap**: no `GET /reviews` list endpoint, no BFF route for listing, no `/app/reviews` list page, and no nav link in the app shell.

---

## 2. User Stories

1. **As a returning researcher**, I want to see a list of all my past reviews so I can revisit feedback without remembering URLs.
2. **As a researcher**, I want to quickly see the status (Pending / Completed / Failed) and date of each review.
3. **As a researcher**, I want to click a review in the list to see its full detail page.
4. **As a researcher**, I want the list to show which funding call and section each review was for.

---

## 3. Scope (MVP)

### In scope
- **Backend**: `GET /reviews` endpoint — returns paginated list of reviews owned by the authenticated user, most recent first.
- **Backend schema**: New `ReviewListItem` Pydantic model with fields: `id`, `status`, `overall_rating`, `created_at`, `call_name`, `node_title`.
- **Repository**: `list_reviews_for_external_user` method — query joining Review → ProposalSnippet → FundingCall + ProposalNode.
- **BFF**: `GET /api/bff/reviews` route — calls backend `GET /reviews`.
- **BFF adapter**: `listReviews()` function.
- **Frontend types**: `ReviewListItem` + `ReviewsListResponse` types.
- **Frontend page**: `/app/reviews/page.tsx` — list view with status badges, call name, section, date, link to detail.
- **App shell nav**: Add "My Reviews" link next to "New Review".
- **Empty state**: Friendly message when user has no reviews yet.
- **Loading state**: Skeleton or loading indicator while fetching.
- **Error state**: Display API error gracefully.

### Out of scope (future)
- Pagination UI (cursor-based or offset) — keep default `limit=50` for MVP.
- Search / filter / sort controls.
- Bulk delete.

---

## 4. Key Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Pagination strategy | Simple `limit` param (default 50, max 100) | MVP simplicity; 50 reviews is well within typical user history |
| Sorting | `created_at DESC` (newest first) | Most natural for "recent reviews" |
| Auth | Reuse existing `require_bff_user_id` / `external_user_id` pattern | Consistent with `POST/GET/DELETE /reviews` |
| Data enrichment | Join call name + node title in the list query | Avoids N+1 and gives context in one round-trip |

---

## 5. Component Touch Points

### Backend
- `backend/app/repositories/review_repository.py` — new `list_reviews_for_external_user()` method
- `backend/app/schemas/api.py` — new `ReviewListItem` + `ReviewsListResponse` schemas
- `backend/main.py` — new `GET /reviews` endpoint
- `backend/tests/test_api.py` — test for list endpoint

### Frontend
- `frontend/src/lib/bff/types.ts` — new types
- `frontend/src/lib/bff/adapter.ts` — new `listReviews()` function
- `frontend/src/app/api/bff/reviews/route.ts` — add `GET` handler
- `frontend/src/app/app/reviews/page.tsx` — **new** list page
- `frontend/src/app/app/layout.tsx` — add "My Reviews" nav link

---

## 6. Open Questions

_None — scope is well-defined and the pattern is established by existing CRUD endpoints._

---

## Changelog

- **v0.1** (2026-02-16): Initial brainstorm from P0 #1 promotion.
