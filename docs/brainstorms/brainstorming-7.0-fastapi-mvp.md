# Brainstorming Log: FastAPI MVP (Task 7.0) — Phase 0

**Date**: 2026-02-08
**Objective**: Define the smallest FastAPI surface that enables a real client flow (pick a call + section, submit text, view results) using the already-working service layer.

## 0. Critical Review Notes (Incorporated)
This Phase 0 note was reviewed for ambiguities and API-shape risks. Updates below lock down:
- `POST /reviews` response contract (no “optional” fields)
- Review lifecycle semantics (what statuses are externally observable)
- Canonical error payload shape
- Explicit invariants (cardinality, atomicity, ordering)
- One missing guardrail: max `snippet_text` length (fail fast with `400`)

## 1. The Problem
Today, the backend can run end-to-end via scripts (`backend/scripts/run_review.py`), but there is no HTTP interface. To reach the product goal (researchers get rubric-grounded feedback), we need a minimal API that a UI can call without hardcoding database IDs.

## 2. Constraints / Guardrails
- **API-first** (user confirmed).
- **Minimal endpoint set** (user confirmed).
- **No auth for MVP**: anonymous sessions remain internal; no user accounts yet.
- **LLM side effects**: `POST /reviews` will call OpenAI (cost + latency). No background workers in MVP.
- **Current service behavior**: synchronous call path; `Review.status` exists for future async polling but is not required for MVP.

## 2.1 MVP Decisions (Locked for Task 7.0)
### Review Lifecycle (External Semantics)
- `POST /reviews` is **synchronous** in MVP.
- On success, `POST /reviews` returns `status = "COMPLETED"` only.
- `PENDING` may exist briefly in the database during execution, but is **not** part of the successful response contract for MVP.
- On failure, `POST /reviews` returns an error response (no `PENDING` response payload in MVP).

### `POST /reviews` Response Shape (Locked)
Use a single, stable response contract:
```json
{
  "review_id": "uuid",
  "status": "COMPLETED"
}
```
Rationale: simplest contract, naturally supports later async without breaking clients (clients already have `review_id` to fetch).

### `GET /reviews/{review_id}` Payload (MVP)
- Returns the review metadata + cards in one payload for UI simplicity (no separate `/cards` endpoint in MVP).
- Does **not** echo `snippet_text` back by default.
- Includes `overall_summary` and `overall_rating` in the `review` object.

### Error Payload Shape (Canonical)
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
Notes:
- `details` is optional and may be `{}`.
- `message` must be safe for end-users (no secrets / stack traces).

### Ordering Guarantee (Cards)
`GET /reviews/{review_id}` returns `cards` in a **stable order**:
- Primary: `NodeExpectation.order_index` ascending.
- If equal/missing: stable secondary by `ReviewCard.id` ascending (implementation detail; just for determinism).

### Multiple Reviews per Node
Allowed. Multiple reviews can exist for the same `(call_id, node_id)`:
- Reviews are immutable snapshots.
- No idempotency guarantees in MVP.
- Phase 7.x can add an optional idempotency key.

### Snippet Retention / Exposure
- Snippet text is stored in `ProposalSnippet` for the TTL window (per existing domain model decisions).
- API does not return snippet text by default in responses.

### Latency / Timeouts (MVP)
- Target: < 30s typical end-to-end per request.
- Server should fail with a clean error if the LLM call times out (use an explicit timeout policy).

### Snippet Length Guardrail (Fail Fast)
- Enforce a maximum snippet length at the API boundary (MVP default: **10,000 characters**).
- If exceeded: `400` with `error.code = "SNIPPET_TOO_LONG"`.
Rationale: fast, user-friendly failure beats opaque upstream failures; truncation is explicitly out of scope.
TODO (Admin): make the max snippet length configurable by admins (e.g., via call YAML metadata → persisted setting per call), without requiring code changes.

## 3. Minimal “Usable” API Surface
This set supports a working UI: populate dropdowns, pick a section, submit a snippet, render results.

### 3.1 Health
- `GET /health`
  - Returns `{ "ok": true }`.

### 3.2 Discovery (avoid hardcoded IDs)
- `GET /calls`
  - Returns active calls (id, code, name, year, agency short_name).
- `GET /calls/{call_id}/nodes`
  - Returns proposal nodes for the call (flat list).
  - Each node includes: `id`, `parent_node_id`, `title`, `node_type`, `order_index`.
  - Include `has_expectations: bool` for basic UX (avoid trial-and-error selection in UI).

### 3.3 Reviews
- `POST /reviews`
  - Body: `call_id`, `node_id`, `snippet_text`
  - Behavior: synchronous execution for MVP:
    - Creates review, calls LLM, validates JSON, persists cards atomically.
    - Returns exactly: `{ "review_id": "...", "status": "COMPLETED" }`
  - Validation:
    - `node_id` must belong to `call_id` (explicit check; error `NODE_NOT_IN_CALL`).
    - node must have expectations (AD 2.1; error `NO_EXPECTATIONS`).
    - snippet length <= max (error `SNIPPET_TOO_LONG`).
- `GET /reviews/{review_id}`
  - Returns `review` + `cards` (single payload for MVP simplicity).
  - Alternative: add `GET /reviews/{review_id}/cards` later only if payload size becomes an issue.

## 4. Error Semantics (MVP)
Status codes:
- `404`: unknown call/node/review ID (`CALL_NOT_FOUND`, `NODE_NOT_FOUND`, `REVIEW_NOT_FOUND`)
- `400`: domain validation errors (`NO_EXPECTATIONS`, `NODE_NOT_IN_CALL`, `SNIPPET_TOO_LONG`, `VALIDATION_ERROR`)
- `502` (or `500`): upstream LLM failure / invalid response (`LLM_FAILED`, `LLM_INVALID_RESPONSE`)
- `500`: unexpected failures (`INTERNAL_ERROR`)

All errors use the canonical error payload shape.

## 4.1 Service/DB Invariants (Must Hold via API)
- **Cardinality**: if a review is `COMPLETED`, the number of returned `cards` equals the number of expectations for that node at review time.
- **Expectation linkage**: each card references a `NodeExpectation` that belongs to the reviewed node.
- **All-or-nothing cards**: no partial card persistence; either all cards are created (success) or none are (failure).
- **Failure traceability**: failed attempts may still persist a `Review` with `status = FAILED` and stored `prompt_sent` / `raw_llm_response` for debugging (no cards).

## 5. Verification Plan (for Phase 3)
- Start API, call `GET /health`.
- Ingest a call YAML, then:
  - `GET /calls` returns it.
  - `GET /calls/{call_id}/nodes` returns nodes.
- `POST /reviews` with a node that has expectations returns `COMPLETED` and cards.
- `POST /reviews` with a node that has **0 expectations** returns `400` with the expected message (AD 2.1).

## 6. Open Questions (to answer in PRD/Task Plan)
Remaining questions (non-blocking, can be decided in PRD):
- Should we support filtering nodes to only those with expectations (recommended: not in MVP; just use `has_expectations`)?
- Do we want a dedicated endpoint for the node tree (nested) vs flat list (default: flat list for simplicity)?

Future-proofing notes (no implementation in MVP):
- Pagination for `GET /calls` if it grows.
- Pagination for cards if card volume grows.
- Async review execution (observable `PENDING` + polling).
