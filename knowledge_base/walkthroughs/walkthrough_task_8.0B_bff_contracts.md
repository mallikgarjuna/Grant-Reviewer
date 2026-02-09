# Walkthrough: Task 8.0B - BFF Contracts

**Completed**: 2026-02-08  
**Task ID**: 8.0B  
**Pipeline Phase**: Phase 3 (Implementation)

## Summary

Implemented backend contract hardening for MVP BFF integration:
- BFF signature verification on protected review endpoints
- review ownership enforcement with masked 404
- idempotency keys with payload-mismatch protection
- synchronous failure-state semantics (`FAILED` as review status, not API error)
- quota enforcement and global submission kill switch

## What Was Built

### API protection and ownership
- Added request signature verification via `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`.
- Protected endpoints:
  - `POST /reviews`
  - `GET /reviews/{review_id}`
- Enforced ownership on review fetches; non-owner access is externally masked as `REVIEW_NOT_FOUND`.
- Added internal ownership-violation logging for observability.

### Idempotency and state semantics
- Added `Idempotency-Key` requirement for `POST /reviews`.
- Added idempotency fields on `Review` with DB uniqueness on `(external_user_id, idempotency_key)`.
- Implemented replay behavior:
  - same key + same payload => same review response
  - same key + different payload => `IDEMPOTENCY_PAYLOAD_MISMATCH` (409)
- Changed LLM/validation failure behavior to persist `Review(status=FAILED)` and return `200` with failed status.
- Added service-level timeout handling (`REVIEW_TIMEOUT_SECONDS`, default 30s) to persist `FAILED`.

### Cost controls
- Added kill switch: `REVIEWS_ENABLED=false` returns `REVIEWS_DISABLED` (503) for new submissions.
- Added per-user daily quota check (`FREE_DAILY_REVIEW_LIMIT`, default 5):
  - rejection code `QUOTA_EXCEEDED` (429) with `{limit, remaining, reset_at}`
  - idempotent replay does not consume additional quota

### Canonical error mapping
- Extended centralized `ERROR_STATUS_BY_CODE` in `backend/main.py`:
  - `UNAUTHORIZED` -> 401
  - `IDEMPOTENCY_PAYLOAD_MISMATCH` -> 409
  - `QUOTA_EXCEEDED` -> 429
  - `REVIEWS_DISABLED` -> 503

## Verification Results

### Automated
Command:
```bash
cd backend && uv run pytest -q
```
Result:
```text
19 passed in 5.06s
```

Newly verified behaviors include:
- missing/invalid signatures rejected with 401
- non-owner review access masked as 404
- idempotency replay returns same review id
- idempotency payload mismatch returns 409
- timeout path persists `FAILED` and returns 200
- quota exceeded returns 429 with expected details
- kill switch blocks new submissions but still allows existing review fetch

### Manual (Stub Mode)
Executed TestClient-based manual checks in `LLM_MODE=stub`:
- create review with signed headers => `200 COMPLETED`
- fetch review as owner => `200`, cards returned
- replay same idempotency key => `200`, same `review_id`
- reuse same key with different payload => `409 IDEMPOTENCY_PAYLOAD_MISMATCH`

## Deferred to Task 8.0A.0

- Next.js scaffold and `src/lib/bff/*` adapter implementation
- staged frontend lint enforcement around `FASTAPI_BASE_URL` access
- frontend-side normalization layer (`Result<T, ApiError>`)
