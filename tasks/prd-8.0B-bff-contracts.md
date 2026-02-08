# PRD 8.0B: BFF Contracts (Auth, Quotas, Idempotency, Ownership)

**Status**: Draft (v0.1)  
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

---

## Errors vs Review States

### Rule

- **API errors** are for: request rejection (validation/quota/disabled) or infra failures.
- **Review status** (`PENDING`, `COMPLETED`, `FAILED`) is a lifecycle state for an existing review.
- Once a review is created, `GET /reviews/{id}` should return `200` (subject to ownership), regardless of `status`.

**Acceptance Criteria**
- LLM failures produce a persisted `Review` with `status=FAILED` and are not represented as a 5xx API error to the client.

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

---

## Quotas (MVP)

### Policy (explicit, MVP)

- Quota is consumed when FastAPI accepts a **new** idempotency key for processing (LLM attempt starts).
- Failures after acceptance do not refund quota in v1.

### Error Contract

When quota is exceeded, FastAPI rejects `POST /reviews` with:
- code: `QUOTA_EXCEEDED` (HTTP 429)
- details include at least: `{ "limit": int, "remaining": int, "reset_at": "ISO8601" }`

---

## Global Kill Switch (MVP)

FastAPI must support an env kill switch:
- `REVIEWS_ENABLED=false` causes `POST /reviews` to return:
  - code: `REVIEWS_DISABLED` (HTTP 503)
  - message: “Reviews are temporarily disabled.”

---

## Review Ownership (MVP)

Reviews are private to the submitting user.

**Acceptance Criteria**
- `GET /reviews/{review_id}` requires BFF signature + user id and verifies ownership.
- If review does not exist **or is not owned**, return `REVIEW_NOT_FOUND` (HTTP 404).

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
{ "review_id": "uuid", "status": "COMPLETED|FAILED" }
```

Notes:
- `FAILED` is a lifecycle outcome (LLM failure / invalid structured output).
- Request rejection (quota, disabled, validation) uses canonical error shape.

### `GET /reviews/{review_id}` (updated semantics)

Headers (required):
- `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`

Response remains:
```json
{ "review": { "id": "uuid", "status": "PENDING|COMPLETED|FAILED", "overall_*": "..." }, "cards": [] }
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

