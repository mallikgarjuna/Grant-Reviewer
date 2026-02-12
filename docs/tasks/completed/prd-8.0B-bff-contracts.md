# PRD 8.0B: BFF Contracts (Auth, Quotas, Idempotency, Ownership)

**Status**: Draft (v0.2 - Revised)  
**Date**: 2026-02-08  
**Phase**: Phase 1 (PRD)  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0-frontend-ui.md`

---

## Goal

Define and implement the **contract layer** that makes the MVP safe and scalable to iterate:

- Enforce the **BFF boundary mechanically** (Next.js is the product boundary).
- Add **idempotency** so retries/timeouts don’t create duplicate LLM spend.
- Add **quota enforcement** + a global **kill switch** to control cost.
- Enforce **review ownership** (private-by-default).
- Clarify **errors vs lifecycle states** so UI logic is simple and consistent.

This PRD is explicitly **MVP** scope: minimal rules and surfaces that prevent cost leaks and contract drift.

## Non-Goals (8.0B)

- Frontend UI pages/components (handled in 8.0A).
- Deployment wiring (Vercel/Render provisioning, secrets, DNS, TLS) (handled in 8.0C).
- Payments, billing tiers, org/team accounts.
- Public share links for reviews.
- Background workers / async job queues.
- Quota “remaining” preflight endpoint (explicitly deferred; see Deferred section).

---

## Architectural Contract (MVP)

### Responsibility Split (Hard Rule)

**FastAPI (domain + execution)**

- Validates invariants (call/node relationships, snippet length, expectations exist).
- Enforces quota allow/deny decisions.
- Executes LLM calls and persists immutable review snapshots.
- Enforces review ownership on all read operations.
- Returns **canonical errors** only for request rejection or infrastructure failures.

**Next.js (BFF + UX)**

- Owns auth gating (Clerk), redirects, and post-login routing.
- Owns user-facing error messages and UX state.
- Owns retries UX, **only** via idempotency.
- Provides a single BFF adapter that normalizes all FastAPI responses into typed UI-safe results.

### Mechanical Enforcement (Must)

**Acceptance Criteria**

- Next.js codebase has a single adapter module (e.g., `src/lib/bff/*`) that is the only place allowed to:
  - know `FASTAPI_BASE_URL`
  - call FastAPI server-to-server
  - parse canonical error payloads
- UI components must not call FastAPI directly.

**Technical enforcement (MVP)**
- `FASTAPI_BASE_URL` must be a **server-only** environment variable (never exposed to the browser bundle).
- Add lint enforcement in the Next.js repo:
  - forbid importing/reading `process.env.FASTAPI_BASE_URL` outside `src/lib/bff/*`
  - forbid direct `fetch("https://<fastapi-host>", ...)` outside `src/lib/bff/*`

Rationale: MVP is where conventions decay fastest; simple tooling keeps the boundary intact.

---

## Errors vs Review States

### Rule

- **API errors** are for: request rejection (validation/quota/disabled) or infra failures.
- **Review status** (`PENDING`, `COMPLETED`, `FAILED`) is a lifecycle state for an existing review.
- Once a review is created, `GET /reviews/{id}` should return `200` (subject to ownership), regardless of `status`.

**Acceptance Criteria**

- LLM failures produce a persisted `Review` with `status=FAILED` and are not represented as a 5xx API error to the client.
- `GET /reviews/{review_id}` must work for `FAILED` and `PENDING` (empty cards allowed) as long as the review exists and is owned.

### Canonical error code is authoritative

Rule:
- HTTP status is **derivable** from `error.code`.
- BFF logic branches on `error.code` (not raw HTTP status).

Implementation note:
- Keep a single `ERROR_STATUS_BY_CODE` map in FastAPI and reuse it everywhere (handlers + tests), as in Task 7.0.

---

## Auth + Request Trust Model (MVP)

### External Identity

- Use Clerk `userId` as the stable external identity (`external_user_id`).
- FastAPI receives `external_user_id` on every protected request.

### BFF Signature

To prevent direct browser abuse of FastAPI endpoints, protected FastAPI routes require a BFF signature:

- `X-GR-User-Id`: Clerk user id (string)
- `X-GR-Timestamp`: unix seconds
- `X-GR-Signature`: HMAC-SHA256 over `(user_id + "." + timestamp + "." + sha256(body))` using shared secret `BFF_SHARED_SECRET`

**Acceptance Criteria**

- Missing/invalid signature returns canonical error `UNAUTHORIZED` (HTTP 401).
- Timestamp must be recent (e.g., within 5 minutes) to prevent replay.

---

## Idempotency (MVP)

### Contract

`POST /reviews` must accept an `Idempotency-Key` header.

Rules:

- Same user + same idempotency key + same payload → return the same review.
- Same user + same idempotency key + **different** payload → reject with `IDEMPOTENCY_PAYLOAD_MISMATCH` (HTTP 409).
- Idempotency keys expire after **24 hours** (MVP default).

**Acceptance Criteria**

- Users can safely retry after timeouts without creating duplicate reviews.
- Replays do not consume quota again.

### Persistence + concurrency (required for correctness)

MVP decision: store idempotency state **on the Review** (not a separate table) to ship faster.

Required DB-level constraint:
- `(external_user_id, idempotency_key)` must be **unique**.

Required fields (conceptual; exact schema in Phase 2 plan):
- `Review.external_user_id` (Clerk user id)
- `Review.idempotency_key`
- `Review.request_payload_sha256`
- `Review.idempotency_expires_at`

Concurrency rule:
- If two requests with the same `(external_user_id, idempotency_key)` arrive concurrently:
  - the first creates the review and starts processing
  - the second must return the existing review:
    - if payload hash differs → `IDEMPOTENCY_PAYLOAD_MISMATCH` (409)
    - otherwise return `{review_id, status}` (status may be `PENDING` if in-flight)

---

## Quotas (MVP)

### Policy (explicit, MVP)

- Quota is consumed when FastAPI accepts a **new** idempotency key for processing (LLM attempt starts).
- Failures after acceptance do not refund quota in v1.

### Error Contract

When quota is exceeded, FastAPI rejects `POST /reviews` with:

- code: `QUOTA_EXCEEDED` (HTTP 429)
- details include at least: `{ "limit": int, "remaining": int, "reset_at": "ISO8601" }`

### Quota visibility (explicit MVP decision)

MVP decision: do **not** add a preflight `GET /quota` endpoint in 8.0B.

Rationale:
- ship faster by relying on `QUOTA_EXCEEDED.details` after a submit attempt
- avoid designing a “remaining quota” UX prematurely

Deferred idea: add `GET /quota` later if we see confusion or high drop-off at submit.

---

## Global Kill Switch (MVP)

FastAPI must support an env kill switch:

- `REVIEWS_ENABLED=false` causes `POST /reviews` to return:
  - code: `REVIEWS_DISABLED` (HTTP 503)
  - message: “Reviews are temporarily disabled.”

Clarification:
- Kill switch affects **new submissions only**.
- Viewing existing reviews (`GET /reviews/{id}`) should continue to work.
- Next.js is responsible for banner/messaging when submissions are disabled.

---

## Review Ownership (MVP)

Reviews are private to the submitting user.

**Acceptance Criteria**

- `GET /reviews/{review_id}` requires BFF signature + user id and verifies ownership.
- If review does not exist **or is not owned**, return `REVIEW_NOT_FOUND` (HTTP 404).

Observability (must-have):
- Internally log ownership violations distinctly (e.g., `OWNERSHIP_VIOLATION`) while still returning `REVIEW_NOT_FOUND` externally.

---

## API Changes (MVP)

This PRD updates the existing FastAPI MVP endpoints from Task 7.0.

### Protected Endpoints

Protected (require BFF signature + user id):

- `POST /reviews`
- `GET /reviews/{review_id}`

Discovery endpoints may remain public in MVP:

- `GET /calls`
- `GET /calls/{call_id}/nodes`

### `POST /reviews` (updated semantics)

Request body stays:

```json
{ "call_id": "uuid", "node_id": "uuid", "snippet_text": "string" }
```

Headers (required):

- `Idempotency-Key: <string>`
- `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`

Success response (shape stays stable):

```json
{ "review_id": "uuid", "status": "PENDING|COMPLETED|FAILED" }
```

Notes:

- **MVP execution model**: synchronous call that returns a terminal status (`COMPLETED` or `FAILED`) for the initial request.
  - Edge case: idempotent replay during an in-flight execution may return `PENDING`.
- `FAILED` is a lifecycle outcome (LLM failure / invalid structured output), not an API error.
- Request rejection (quota, disabled, validation) uses canonical error shape.

### `GET /reviews/{review_id}` (updated semantics)

Headers (required):

- `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`

Response remains:

```json
{
  "review": {
    "id": "uuid",
    "status": "PENDING|COMPLETED|FAILED",
    "overall_*": "..."
  },
  "cards": []
}
```

Notes:

- Returns `200` for `FAILED` reviews (cards empty; summary may contain failure message).
- Returns `404` if not found or not owned.

---

## Canonical Error Codes (Additions)

Add to the existing canonical error taxonomy:

- `UNAUTHORIZED` → 401
- `QUOTA_EXCEEDED` → 429
- `REVIEWS_DISABLED` → 503
- `IDEMPOTENCY_PAYLOAD_MISMATCH` → 409

Rule:
- Status code is informational; `error.code` is authoritative.

All errors keep the shape:

```json
{ "error": { "code": "...", "message": "...", "details": {} } }
```

---

## Verification (MVP)

### Automated (no OpenAI calls)

- Tests cover:
  - BFF signature required on protected endpoints
  - idempotency replay returns same review id
  - concurrent idempotency: second request returns same review id (or `PENDING`) and does not create a duplicate
  - idempotency payload mismatch returns 409
  - quota exceeded returns 429 + details shape
  - kill switch returns 503
  - ownership check blocks cross-user access (returns 404)
  - LLM failure results in `status=FAILED` with a retrievable review via `GET /reviews/{id}`

### Manual (stub mode)

- In `LLM_MODE=stub`, run the full flow through Next BFF route handlers:
  - fetch calls/nodes
  - submit review with idempotency key
  - reload/submit again with same key and confirm no duplicate
  - fetch review detail

---

## Deferred / Later (Non-Scope Ideas)

- `GET /quota` endpoint for proactive “remaining quota” UI.
- Org/team quotas and shared review access.
- Public share links for reviews.
- Async/background review execution (return `PENDING` more commonly) + UI polling as primary flow.
- Provider hardening for Postgres connection limits (poolers like pgBouncer) if concurrency grows.

## Revision History

- **v0.1** (2026-02-08): Initial PRD draft.
- **v0.2** (2026-02-08): Added technical enforcement, error-code authority rule, DB idempotency constraints, explicit execution model, ownership observability, explicit quota-visibility decision, and deferred ideas list.
