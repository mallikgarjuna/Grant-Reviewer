# Task 8.0B: BFF Contracts (Phase 2 Plan)

**Status**: [/] In Progress (v0.3 - Revised)  
**Date**: 2026-02-08  
**Last Updated**: 2026-02-08  
**Phase**: Phase 2 (Task breakdown)  
**PRD**: `tasks/prd-8.0B-bff-contracts.md`  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0-frontend-ui.md`

---

## Phase Clarification (read first)

- This file is a **Phase 2 artifact** (task breakdown).
- It plans the **Phase 3 implementation** of the contract decisions in PRD 8.0B.
- MVP bias: smallest set of backend + BFF contract plumbing needed to safely ship the first UI slice (8.0A) without cost leaks or data exposure.

## Scope Guardrails (recap)

- No payments; no org/team accounts; no sharing links.
- No async workers; `POST /reviews` remains synchronous in MVP.
- Next.js UI work is **not** implemented here (8.0A), but this plan includes the minimal BFF adapter + lint enforcement items required by PRD 8.0B.

## MVP Decisions Locked Here (to unblock Phase 3)

- **Idempotency concurrency (MVP simplification)**: rely on a DB unique constraint `(external_user_id, idempotency_key)` plus “fetch existing on conflict”. No row locking / “wait for completion” logic in MVP.
- **Retries**: BFF provides **manual-only** retry UX. No automatic retries (prevents duplicate LLM spend).
- **Timeout budget**: target ~`30s` max for `POST /reviews` LLM execution in MVP; on application-level timeout, persist `FAILED` and return `{review_id, status:"FAILED"}`.
- **Quota visibility**: no `GET /quota` in MVP. UI learns “remaining” only from `QUOTA_EXCEEDED.details` after a submit attempt.
- **Frontend sequencing**: 8.0B is executed **before** 8.0A; any Next.js scaffolding needed to enforce the BFF boundary should be treated as a minimal “8.0A.0 scaffolding” step (no app pages yet).

---

## 8.0B.1 Auth Trust: BFF Signature (FastAPI)

- [x] Add `BFF_SHARED_SECRET` env var and a request verifier:
  - validates `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`
  - rejects stale timestamps (e.g., > 5 minutes)
- [x] Add canonical error `UNAUTHORIZED` → 401 in centralized code→status mapping.
- [x] Require signature + user id for:
  - `POST /reviews`
  - `GET /reviews/{review_id}`
- [x] **Verify**: tests cover missing/invalid signature paths.

## 8.0B.2 Review Ownership (FastAPI)

- [x] Enforce ownership on `GET /reviews/{review_id}`:
  - verify the review belongs to the caller (Clerk user id)
  - return `REVIEW_NOT_FOUND` (404) if not found or not owned
- [x] Add distinct internal logging for ownership violations (still return 404 externally).
- [x] **Verify**: tests cover cross-user access returns 404 and logs the violation.

## 8.0B.3 Idempotency (FastAPI)

- [ ] Add `Idempotency-Key` requirement for `POST /reviews`.
- [ ] Persistence model (MVP per PRD):
  - store idempotency on `Review`
  - enforce DB uniqueness on `(external_user_id, idempotency_key)`
  - store `request_payload_sha256` and `idempotency_expires_at`
- [ ] Implement behavior:
  - replay with same payload → return same `{review_id, status}`
  - replay with different payload → `IDEMPOTENCY_PAYLOAD_MISMATCH` → 409
  - expired key treated as new key (and creates a new review)
- [ ] Concurrency behavior (MVP simplification):
  - Use DB uniqueness + conflict handling:
    - attempt to create the review row (status starts as `PENDING`)
    - on uniqueness conflict, fetch the existing review row and return it
  - If the existing row is still `PENDING`, return `{review_id, status:"PENDING"}` (rare edge case; caller can retry with same key).
- [ ] Add canonical error `IDEMPOTENCY_PAYLOAD_MISMATCH` → 409.
- [ ] **Verify**: tests cover replay, payload mismatch, and concurrent duplicate behavior.

## 8.0B.4 Review Execution Semantics (FastAPI)

- [ ] Keep MVP behavior: `POST /reviews` is synchronous and returns terminal status on the initial request.
- [ ] Add an application-level timeout for LLM execution (MVP target ~30s):
  - on timeout: persist `Review(status=FAILED)` and return `200` with `{review_id, status:"FAILED"}`
  - note: if upstream infra kills the request first, idempotency must still prevent duplicate spend on retry
- [ ] Change LLM failure handling to match PRD:
  - create/persist `Review(status=FAILED)` and return `200` with `{review_id, status:"FAILED"}`
  - do not surface LLM failures as 5xx canonical API errors to the caller
- [ ] Ensure `GET /reviews/{review_id}` returns `200` for `FAILED` (owned) with cards empty.
- [ ] **Verify**: table-driven tests for error/state separation.

## 8.0B.5 Quotas + Kill Switch (FastAPI)

- [ ] Add env kill switch: `REVIEWS_ENABLED` (default true):
  - when false, `POST /reviews` returns `REVIEWS_DISABLED` → 503 (before LLM)
  - `GET /reviews/*` unaffected
- [ ] Add quota enforcement (per Clerk user id, per-day, MVP default limit):
  - on exceed: `QUOTA_EXCEEDED` → 429 with `{limit, remaining, reset_at}`
  - quota consumed once per **new idempotency key** (not on replays)
  - failures after acceptance do not refund in v1
- [ ] Add canonical errors:
  - `QUOTA_EXCEEDED` → 429
  - `REVIEWS_DISABLED` → 503
- [ ] **Verify**: tests cover exceeded quota, replay not consuming quota, and kill switch behavior.

## 8.0B.6 Canonical Error Mapping Invariant

- [ ] Ensure FastAPI keeps a single `ERROR_STATUS_BY_CODE` mapping table and tests it (extend Task 7.0 patterns).
- [ ] **Verify**: Next/BFF logic branches on `error.code`, not HTTP status (documented + enforced in frontend linting once present).

## 8.0B.7 Frontend Enforcement (execute as 8.0A.0 scaffolding)

Rationale:
- The BFF boundary must be enforced mechanically, but we’re sequencing **contracts (8.0B)** before **UI work (8.0A)**.
- Therefore, we implement a minimal Next.js scaffold as the **first** sub-step of 8.0A (8.0A.0), then immediately add the adapter and staged linting before building any UI pages.

- [ ] Add `src/lib/bff/*` adapter module:
  - is the only module allowed to read `process.env.FASTAPI_BASE_URL`
  - provides typed functions like `listCalls()`, `listNodes(callId)`, `createReview(...)`, `getReview(reviewId)`
- [ ] Stage lint enforcement (to preserve MVP velocity):
  - Step 1 (early): document “adapter-only” rule + keep `FASTAPI_BASE_URL` server-only
  - Step 2 (after first BFF usage works): add lint rules in “warn” mode
  - Step 3 (once stable): flip to “error” enforcement
- [ ] Add a simple normalization layer:
  - converts canonical `{error:{code,...}}` into typed `Result<T, ApiError>`

## 8.0B.8 Verification (Manual, Stub Mode)

- [ ] In `LLM_MODE=stub`, verify end-to-end via BFF routes:
  - submit once → gets `COMPLETED`
  - resubmit with same idempotency key → same `review_id`
  - resubmit with same key but different payload → 409 `IDEMPOTENCY_PAYLOAD_MISMATCH`
  - view review detail → 200 (owned)

---

## Notes / Open Implementation Decisions (lock during Phase 3)

- DB migration approach (MVP): if we’re still using the “create tables on startup” workflow, schema changes may require DB reset locally; production needs a migration story before launch (likely 8.0C).
- Quota limit default: pick a conservative value (e.g., `FREE_DAILY_REVIEW_LIMIT=5`) via env var.
- Timeout budget: align backend and proxy timeouts so that “happy-path” synchronous execution is feasible (we can tune infra in 8.0C; for 8.0B we just document + enforce app-level LLM timeout).

## Deferred / Later (Non-Scope Ideas)

- `GET /quota` preflight endpoint (if we see UX confusion).
- Blocking “wait for completion” semantics for concurrent idempotent requests (likely only matters once we add async workers).
- Automatic retries/backoff (cost-risk; revisit post-MVP).

## Revision History

- **v0.1** (2026-02-08): Initial Phase 2 plan draft.
- **v0.2** (2026-02-08): Simplified idempotency concurrency strategy; added timeout/retry/lint staging policies and explicit MVP decisions.
- **v0.3** (2026-02-08): Clarified sequencing: implement backend contracts first (8.0B), then treat Next.js scaffold + adapter/lint as an explicit 8.0A.0 prerequisite.
