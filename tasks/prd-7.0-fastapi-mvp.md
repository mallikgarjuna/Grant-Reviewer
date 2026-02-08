# PRD 7.0: FastAPI MVP

**Status**: Draft (v0.2 - Revised)  
**Date**: 2026-02-08  
**Phase**: Phase 1 (PRD)  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-7.0-fastapi-mvp.md`

---

## Goal

Expose the existing review flow over HTTP via a minimal FastAPI API so a UI can:
1) discover calls + proposal sections,  
2) submit a snippet for review, and  
3) fetch the resulting review + cards.

## Non-Goals (MVP)

- Authentication / user accounts (anonymous only; internal implementation detail)
- Async workers / background queues (request blocks on LLM call)
- Retries / backoff / rate-limit recovery (fail cleanly)
- Truncation / token-budgeting (fail fast on oversized snippets; no truncation)
- Pagination (note as TODO; implement later if needed)
- Strong idempotency / deduplication (multiple submissions may create multiple reviews)
- “True scoring” / AI-generated ratings (Phase 7.x/8.x; MVP uses placeholder ratings)

---

## User Stories

### US-7.1: Discover available calls
**As a** researcher,  
**I want** to select the relevant funding call,  
**So that** the app uses the correct rubric + proposal structure.

**Acceptance Criteria**
- `GET /calls` returns a list of active calls with stable IDs and minimal metadata.

### US-7.2: Choose a proposal section to review
**As a** researcher,  
**I want** to pick the correct proposal section (node) for my pasted text,  
**So that** the review uses the right expectations.

**Acceptance Criteria**
- `GET /calls/{call_id}/nodes` returns a flat list of nodes for the call.
- Each node includes `has_expectations: bool` so the UI can discourage selecting nodes that cannot be reviewed.
- `has_expectations` is a UI hint only; server-side validation on `POST /reviews` is authoritative.

### US-7.3: Submit a snippet and receive a review
**As a** researcher,  
**I want** to submit one snippet of text for a chosen section,  
**So that** I get rubric-grounded feedback.

**Acceptance Criteria**
- `POST /reviews` accepts `call_id`, `node_id`, `snippet_text`.
- In Phase 0, on success, response is **exactly**:
  ```json
  { "review_id": "uuid", "status": "COMPLETED" }
  ```
- On failure, returns a canonical error payload (see below).
- Enforces max snippet length (default **10,000 chars**) with a `400` error.
- Multiple submissions of the same payload may create multiple reviews (reviews are immutable snapshots).

### US-7.4: Fetch the review and cards
**As a** researcher,  
**I want** to view the results of my review,  
**So that** I can make edits based on actionable feedback.

**Acceptance Criteria**
- `GET /reviews/{review_id}` returns the review metadata plus cards in one payload.
- Includes `overall_summary` and `overall_rating` in `review` (see Ratings semantics).
- Cards are returned in a stable order (see ordering guarantee).
- Does not echo `snippet_text` by default.
- If `review.status != "COMPLETED"`, `cards` may be empty and summary/rating may be null.

---

## API Specification (MVP)

### 1) Health
`GET /health`

Response:
```json
{ "ok": true }
```

### 2) Calls
`GET /calls`

Response (example):
```json
{
  "calls": [
    {
      "id": "uuid",
      "code": "ERC-2026-COG",
      "name": "ERC Consolidator Grant 2026",
      "year": 2026,
      "agency_short_name": "ERC"
    }
  ]
}
```

### 3) Nodes (flat list)
`GET /calls/{call_id}/nodes`

Response (example):
```json
{
  "nodes": [
    {
      "id": "uuid",
      "parent_node_id": null,
      "title": "Part B1",
      "node_type": "SECTION",
      "order_index": 1,
      "has_expectations": false
    }
  ]
}
```

Semantics:
- `has_expectations = true` means the node currently has **>= 1** `NodeExpectation` (at request time).
- `has_expectations` is a derived UI hint and may change if an admin updates the call definition; `POST /reviews` validation is authoritative.

### 4) Create Review (synchronous)
`POST /reviews`

Request:
```json
{
  "call_id": "uuid",
  "node_id": "uuid",
  "snippet_text": "string"
}
```

Success response (locked):
```json
{ "review_id": "uuid", "status": "COMPLETED" }
```

Forward-compatibility note:
- The response shape is stable. In Phase 0, `status` will always be `"COMPLETED"` on success.
- In a future async phase, the same endpoint may return `"PENDING"` while preserving the same shape.

Validation rules:
- `node_id` must belong to `call_id` (`NODE_NOT_IN_CALL`).
- Node must have expectations (`NO_EXPECTATIONS`; aligns with AD 2.1).
- `len(snippet_text) <= 10000` (`SNIPPET_TOO_LONG`).

### 5) Get Review + Cards
`GET /reviews/{review_id}`

Response (example):
```json
{
  "review": {
    "id": "uuid",
    "status": "COMPLETED"
  },
  "cards": [
    {
      "id": "uuid",
      "node_expectation_id": "uuid",
      "rating": "NOTE",
      "feedback_text": "..."
    }
  ]
}
```

Notes:
- If `review.status == "COMPLETED"`, `review.overall_summary` is present and `cards` is non-empty.
- If `review.status != "COMPLETED"`, `cards` may be empty and `review.overall_summary` / `review.overall_rating` may be null.

---

## Canonical Error Shape

All non-2xx responses return:
```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

Status codes + codes (MVP):
- `404`: `CALL_NOT_FOUND`, `NODE_NOT_FOUND`, `REVIEW_NOT_FOUND`
- `400`: `NO_EXPECTATIONS`, `NODE_NOT_IN_CALL`, `SNIPPET_TOO_LONG`, `VALIDATION_ERROR`
- `502` (or `500`): `LLM_FAILED`, `LLM_INVALID_RESPONSE`
- `500`: `INTERNAL_ERROR`

`VALIDATION_ERROR` scope:
- Reserved for request schema issues only (missing fields, invalid UUID formats, wrong types).
- Domain-level failures must use specific codes (e.g., `NO_EXPECTATIONS`, `NODE_NOT_IN_CALL`).

---

## Behavioral Guarantees (Must Hold)

- **Phase 0 synchronous semantics**: `POST /reviews` returns `COMPLETED` only on success in Phase 0; later phases may introduce externally observable `PENDING` without changing response shape.
- **Cardinality**: if a review is `COMPLETED`, `len(cards)` equals the number of expectations for that node at review time.
- **Expectation linkage**: every card references a `NodeExpectation` that belongs to the reviewed node.
- **Atomicity (cards)**: no partial card persistence; either all cards are created (success) or none are (failure).
- **Ordering**: cards are returned sorted by `NodeExpectation.order_index` ascending (stable tie-breaker allowed for determinism).
- **Privacy/UX**: snippet text is not returned by default.
- **Immutability**: reviews are immutable snapshots. Re-submitting the same node/snippet creates a new review.
- **Failure persistence**: a failed request may still persist a `Review` with `status = FAILED` for traceability (but with zero cards).

---

## Operational Constraints

- **Latency target**: typical request completes in under ~30 seconds.
- **Timeout policy**: enforce a server-side timeout for the LLM call; on timeout return a clean `LLM_FAILED`-style error.
- **Client guidance**: clients should configure HTTP timeouts **>= 35s** for synchronous review creation.

---

## Ratings Semantics (Phase Alignment)

Ratings exist in the database schema, but “true scoring” is out of scope for this MVP.

MVP behavior:
- `ReviewCard.rating` is populated with a safe placeholder value (default: `"NOTE"`).
- `Review.overall_rating` may be null or a placeholder (default: `"NOTE"`).

Interpretation:
- Ratings in MVP should be treated as **non-authoritative** and used only for basic UI rendering (e.g., a neutral indicator).
- Phase 7.x/8.x can introduce real rating logic (deterministic or LLM-derived) without changing endpoint shapes.

---

## Admin TODO (Config Without Code Changes)

- Make max snippet length configurable by admin (preferred: via call YAML metadata → persisted per call), while keeping a safe default (10,000 chars).

---

## Out of Scope Ideas (Capture for Later)

- Async execution: `POST /reviews` returns `PENDING`, add polling/WebSocket, background workers.
- Idempotency key for `POST /reviews` to prevent duplicate review creation on retries/double-submits.
- Call/version immutability: versioned calls/nodes so reviews can be tied to a frozen rubric/structure snapshot.
- Pagination for `GET /calls` and potentially large card payloads.
- Admin toggles: enable/disable expectations without deleting; richer semantics than `has_expectations`.
- Robust retry/backoff / rate-limit handling and user-facing “retry recommended” guidance.
