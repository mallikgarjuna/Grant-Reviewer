# PRD — WF-0014: Review History ("My Reviews")

- **Status**: Ready for Tasks
- **Owner**: Assisted by Antigravity
- **Spec**: [Spec](docs/specs/features/spec-WF-0014-review-history.md)

## 1. Context & Scope

**Problem**: Users cannot access their past reviews once the browser tab is closed.
**Goal**: Provide a persistent, accessible history of all reviews owned by the authenticated user.
**Success Metrics**: Users view the `/app/reviews` page; User retention increases due to history access.

### In Scope
- **Backend API**: `GET /reviews` (List endpoint).
- **Frontend Page**: `/app/reviews` (List view).
- **Navigation**: "My Reviews" app shell link.
- **Data**: Fetching `Review` + `ProposalSnippet` + `FundingCall` + `ProposalNode` details (call name, section title).

### Out of Scope
- **Search/Filter**: No client-side or server-side filtering for MVP.
- **Pagination**: Simple limit=50, no load more.
- **Bulk Operations**: Deletion is one-by-one via detail page.

## 2. User Experience

1.  **Entry**: User clicks "My Reviews" in the header.
2.  **List View**:
    - Displays list of past reviews (cards).
    - Each card shows: Call Name, Section Title, Date, Status (Badge), Rating (Pill).
    - Sorted by newest first.
3.  **Empty State**: "No reviews yet" + "New Review" button.
4.  **Interaction**: Click card -> Navigate to `/app/reviews/{id}`.

## 3. Technical Requirements

### 3.1 Backend
- **Endpoint**: `GET /reviews`
    - Auth: `require_bff_user_id` dependency.
    - Query: `limit: int = 50`.
    - Logic: Query `Review` table, join `ProposalSnippet` -> `ProposalNode` -> `FundingCall`.
    - Response: List of `ReviewListItem`.
- **Repository**: `list_reviews_for_external_user(user_id: str, limit: int)`.
- **Security**: IDOR check implied by filtering on `external_user_id`.

### 3.2 Frontend (BFF)
- **Route**: `GET /api/bff/reviews` -> proxies backend.
- **Types**: `ReviewListItem`, `ReviewsListResponse`.
- **Adapter**: `listReviews(context)`.

### 3.3 Frontend (UI)
- **Page**: `/app/reviews/page.tsx`.
- **Components**: Reuse existing styling (Tailwind classes from design system).
- **Error Handling**: Standard error boundary or inline error state.

## 4. Verification Plan

### 4.1 Automated Tests
- `backend/tests/test_api.py`:
    - `test_list_reviews_auth_required`: 401 if no header.
    - `test_list_reviews_returns_user_items`: 200 OK + list.
    - `test_list_reviews_isolation`: Does not return other users' reviews.

### 4.2 Manual Verification
- Login as User A -> Create Review -> Verify appears in list.
- Login as User B -> Verify list is empty (or has own reviews).
- Verify navigation to detail page works.
