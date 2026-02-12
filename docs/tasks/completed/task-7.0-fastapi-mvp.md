# Task 7.0: FastAPI MVP (Phase 2 Plan)

**Status**: [x] Complete  
**Phase**: Phase 2 (Task breakdown)  
**PRD**: `tasks/prd-7.0-fastapi-mvp.md`  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-7.0-fastapi-mvp.md`

---

## Phase Clarification (read first)

- This file is a **Phase 2 artifact** (task breakdown).
- It plans the **Phase 3 implementation** of the **Phase 0 MVP behavior** decisions (synchronous review creation, no async workers).
- When this plan says “Phase 0 behavior”, it refers to the **MVP runtime semantics**, not the pipeline phase that produced this file.

## MVP Scope Guardrails (recap)

- Minimal endpoints only: `/health`, `/calls`, `/calls/{call_id}/nodes`, `POST /reviews`, `GET /reviews/{review_id}`
- Synchronous review creation (Phase 0 behavior), but response shape must allow future `PENDING`
- Canonical error shape: `{ "error": { "code", "message", "details" } }`
- Max snippet length: default 10,000 chars (admin-configurable later; no truncation)
- Ratings are placeholders (`NOTE`) in MVP; real scoring is out of scope and must not leak into API glue code
- No retries/backoff, no pagination, no auth (explicitly out of scope for Phase 3)

---

## 7.1 Dependencies & App Wiring

- [x] 7.1.1 Add FastAPI server deps (`fastapi`, `uvicorn`) to `backend/pyproject.toml` <!-- touches <=3 files -->
- [x] 7.1.2 Replace placeholder `backend/main.py` with a FastAPI app instance
- [x] 7.1.3 Add `GET /health` endpoint
- [x] 7.1.4 **Verify**: start server and `curl /health`

## 7.2 API Schemas & Error Model

- [x] 7.2.1 Add request/response Pydantic models for:
  - `GET /calls`
  - `GET /calls/{call_id}/nodes`
  - `POST /reviews`
  - `GET /reviews/{review_id}`
- [x] 7.2.2 Ensure `review.status` is typed as an enum that already includes: `PENDING`, `COMPLETED`, `FAILED` (even if Phase 0 never returns `PENDING` on success)
- [x] 7.2.3 Add canonical error response helper + exception handlers mapping codes/statuses per PRD
- [x] 7.2.4 Centralize **error_code → HTTP status** mapping in one place (single dict/table) and reference it everywhere (handlers + tests)
- [x] 7.2.5 **Verify**: invalid UUID / missing fields return `VALIDATION_ERROR` (schema-level only)
- [x] 7.2.6 **Verify**: response schemas accept `PENDING`/`FAILED` without code changes (forward-compat check)

## 7.3 Calls & Nodes Discovery Endpoints

- [x] 7.3.1 Implement `GET /calls` (active calls)
- [x] 7.3.2 Implement `GET /calls/{call_id}/nodes` (flat list + `has_expectations`)
  - Compute `has_expectations` without N+1 queries (single grouped query)
  - Document: `has_expectations` is a derived, best-effort UI hint; `POST /reviews` is authoritative
  - MVP compromise: no caching/invalidation story beyond “computed at request time”
- [x] 7.3.3 **Verify**: after ingesting a call YAML, endpoints return expected data

## 7.4 Review Endpoints (Create + Fetch)

- [x] 7.4.1 Implement `POST /reviews`
  - Validate `node_id` belongs to `call_id` (`NODE_NOT_IN_CALL`)
  - Enforce snippet length (`SNIPPET_TOO_LONG`)
  - On success (Phase 0): return `{review_id, status:"COMPLETED"}`
  - On failure: canonical error shape (`NO_EXPECTATIONS`, `LLM_FAILED`, etc.)
  - Ensure rating placeholders remain `NOTE` and are assigned in **ReviewerService** (not in API handlers)
- [x] 7.4.2 Implement `GET /reviews/{review_id}`
  - Return `review` + `cards`
  - Include `overall_summary` + `overall_rating` (nullable if not completed)
  - Return cards ordered by `NodeExpectation.order_index` ascending
- [x] 7.4.3 Decide and implement non-COMPLETED behavior:
  - If review exists and `status != COMPLETED`, return `200` with `cards: []` and nullable `overall_*` fields (do not 404-until-complete)
- [x] 7.4.4 **Verify**: run a successful review and confirm cards count/order invariants

## 7.5 Tests (No OpenAI calls)

- [x] 7.5.1 Add FastAPI tests using TestClient
- [x] 7.5.2 Mock/override LLM client so tests never call OpenAI
- [x] 7.5.3 Add tests for:
  - `SNIPPET_TOO_LONG`
  - `NO_EXPECTATIONS`
  - `NODE_NOT_IN_CALL`
  - canonical error shape consistency
- [x] 7.5.4 Add an explicit atomicity test for failure paths:
  - Simulate LLM failure or invalid JSON
  - Assert: review is `FAILED` and **zero ReviewCards** exist for it (no partial cards)
- [x] 7.5.5 **Verify**: error_code → HTTP status mapping is consistent (table-driven test)
- [x] 7.5.6 **Verify**: test suite passes locally

## 7.6 End-to-End Verification (Manual)

- [x] 7.6.1 `uv run python scripts/ingest_call.py ... --dry-run` (sanity)
- [x] 7.6.2 Add a “Fake LLM” manual verification mode (recommended for iteration speed)
  - MVP decision: implement `LLM_MODE=stub` (or similar) that returns deterministic, schema-valid JSON without calling OpenAI
  - Use this mode for frequent manual verification
- [x] 7.6.3 Start API server, run:
  - `GET /calls`
  - `GET /calls/{call_id}/nodes`
  - `POST /reviews` in stub mode (no cost)
  - Optional: `POST /reviews` in real mode (calls OpenAI; cost)
  - `GET /reviews/{review_id}`
- [x] 7.6.4 Write walkthrough: `knowledge_base/walkthroughs/walkthrough_task_7.0_fastapi_mvp.md`

---

## Notes / Phase Gates

- Adding dependencies (`fastapi`, `uvicorn`) is required for this task; confirm before Phase 3 execution if needed.
- Any step that would touch more than 3 files should be broken into a subtask and re-confirmed before proceeding.
