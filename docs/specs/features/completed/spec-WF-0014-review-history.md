# Spec — WF-0014: Review History ("My Reviews")

- **Status**: Ready for PRD
- **Owner**: Assisted by Antigravity
- **Brainstorm**: [Brainstorm](docs/brainstorms/brainstorm-WF-0014-review-history.md)

## 1. Overview

**One-sentence summary**: A "My Reviews" list page allowing authenticated researchers to view their past grant proposal reviews, backed by a new paginated backend endpoint.

**User Problem**: Users currently lose access to their reviews if they close the tab, as there is no history view.

**Solution**:
1.  **Backend**: `GET /reviews` endpoint returning a list of reviews for the current user.
2.  **Frontend**: `/app/reviews` page displaying a list of review cards with metadata (status, call, section, date).
3.  **Navigation**: "My Reviews" link in the app header.

## 2. User Stories

1.  **View History**: As a researcher, I want to see a list of my past reviews so I can find previous feedback.
2.  **Check Status**: As a researcher, I want to see if a review is Completed, Failed, or Pending.
3.  **Contextualize**: As a researcher, I want to know which Funding Call and Section a review belongs to without opening it.
4.  **Navigate**: As a researcher, I want to click a review to view its full details.

## 3. Functional Requirements

### 3.1 Backend: List Endpoint
- **Route**: `GET /reviews`
- **Auth**: Required (`require_bff_user_id`).
- **Query Params**:
    - `limit`: integer, default 50, max 100.
    - (Future: `cursor` for pagination - out of scope for MVP).
- **Response**: JSON array of review summaries.
- **Ordering**: `created_at` DESC (newest first).
- **Isolation**: Must only return reviews belonging to `x-gr-user-id`.

### 3.2 Frontend: Review List Page
- **Route**: `/app/reviews`
- **Access**: Authenticated users only (redirect to login if guest - handled by middleware).
- **Layout**:
    - Header: "My Reviews".
    - Content: List of cards.
- **Card Content**:
    - Call Name (e.g., "ERC Starting Grant").
    - Node Title (e.g., "B1: Extended Synopsis").
    - Status Badge (Completed/Failed/Pending).
    - Rating Pill (Strong/Weak/etc. - aggregate).
    - Relative or absolute date.
    - Chevron/Link to `/app/reviews/{id}`.
- **States**:
    - **Loading**: Skeleton rows.
    - **Empty**: "No reviews yet" message + CTA to "New Review".
    - **Error**: API error message with retry option (or refresh).

### 3.3 Navigation
- **App Shell**: Add "My Reviews" link to the authenticated header navigation.

## 4. Technical Design

### 4.1 Data Model Changes
- No schema changes required (Reviews already exist and have `user_id`).
- **Repository**: New method `list_reviews_for_external_user(user_id, limit)` joining `Review` -> `ProposalSnippet` -> `ProposalNode` -> `FundingCall` to fetch titles efficiently.

### 4.2 API Contract
```json
{
  "reviews": [
    {
      "id": "uuid",
      "status": "COMPLETED",
      "overall_rating": "SUCCESS",
      "created_at": "ISO8601",
      "call_name": "ERC Starting Grant 2026",
      "node_title": "Part B1"
    }
  ]
}
```

### 4.3 Security & Privacy
- **IDOR Prevention**: Repository must filter strictly by `external_user_id` from the BFF header.
- **Data Minimization**: Endpoint returns only summary fields, not full snippet text or review cards.

## 5. MVP Limitations (Out of Scope)
- **Search/Filter**: No text search or filtering by call/status.
- **Complex Pagination**: No "Load More" or pages; just latest 50.
- **Bulk Actions**: No bulk delete.
- **Infinite Scroll**: Simple list for MVP.
