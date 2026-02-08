# Task 7.0: FastAPI MVP (Phase 2 Plan)

**Status**: [/] In Progress  
**Phase**: Phase 2 (Task breakdown)  
**PRD**: `tasks/prd-7.0-fastapi-mvp.md`  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-7.0-fastapi-mvp.md`

---

## MVP Scope Guardrails (recap)

- Minimal endpoints only: `/health`, `/calls`, `/calls/{call_id}/nodes`, `POST /reviews`, `GET /reviews/{review_id}`
- Synchronous review creation (Phase 0 behavior), but response shape must allow future `PENDING`
- Canonical error shape: `{ "error": { "code", "message", "details" } }`
- Max snippet length: default 10,000 chars (admin-configurable later; no truncation)
- Ratings are placeholders (`NOTE`) in MVP; real scoring is out of scope

---

## 7.1 Dependencies & App Wiring
- [ ] 7.1.1 Add FastAPI server deps (`fastapi`, `uvicorn`) to `backend/pyproject.toml` <!-- touches <=3 files -->
- [ ] 7.1.2 Replace placeholder `backend/main.py` with a FastAPI app instance
- [ ] 7.1.3 Add `GET /health` endpoint
- [ ] 7.1.4 **Verify**: start server and `curl /health`

## 7.2 API Schemas & Error Model
- [ ] 7.2.1 Add request/response Pydantic models for:
  - `GET /calls`
  - `GET /calls/{call_id}/nodes`
  - `POST /reviews`
  - `GET /reviews/{review_id}`
- [ ] 7.2.2 Add canonical error response helper + exception handlers mapping codes/statuses per PRD
- [ ] 7.2.3 **Verify**: invalid UUID / missing fields return `VALIDATION_ERROR` (schema-level only)

## 7.3 Calls & Nodes Discovery Endpoints
- [ ] 7.3.1 Implement `GET /calls` (active calls)
- [ ] 7.3.2 Implement `GET /calls/{call_id}/nodes` (flat list + `has_expectations`)
  - Compute `has_expectations` without N+1 queries (single grouped query)
  - Document: hint only; `POST /reviews` is authoritative
- [ ] 7.3.3 **Verify**: after ingesting a call YAML, endpoints return expected data

## 7.4 Review Endpoints (Create + Fetch)
- [ ] 7.4.1 Implement `POST /reviews`
  - Validate `node_id` belongs to `call_id` (`NODE_NOT_IN_CALL`)
  - Enforce snippet length (`SNIPPET_TOO_LONG`)
  - On success (Phase 0): return `{review_id, status:"COMPLETED"}`
  - On failure: canonical error shape (`NO_EXPECTATIONS`, `LLM_FAILED`, etc.)
  - Ensure rating placeholders remain `NOTE`
- [ ] 7.4.2 Implement `GET /reviews/{review_id}`
  - Return `review` + `cards`
  - Include `overall_summary` + `overall_rating` (nullable if not completed)
  - Return cards ordered by `NodeExpectation.order_index` ascending
- [ ] 7.4.3 **Verify**: run a successful review and confirm cards count/order invariants

## 7.5 Tests (No OpenAI calls)
- [ ] 7.5.1 Add FastAPI tests using TestClient
- [ ] 7.5.2 Mock/override LLM client so tests never call OpenAI
- [ ] 7.5.3 Add tests for:
  - `SNIPPET_TOO_LONG`
  - `NO_EXPECTATIONS`
  - `NODE_NOT_IN_CALL`
  - canonical error shape consistency
- [ ] 7.5.4 **Verify**: test suite passes locally

## 7.6 End-to-End Verification (Manual)
- [ ] 7.6.1 `uv run python scripts/ingest_call.py ... --dry-run` (sanity)
- [ ] 7.6.2 Start API server, run:
  - `GET /calls`
  - `GET /calls/{call_id}/nodes`
  - `POST /reviews` (note: calls OpenAI; cost)
  - `GET /reviews/{review_id}`
- [ ] 7.6.3 Write walkthrough: `knowledge_base/walkthroughs/walkthrough_task_7.0_fastapi_mvp.md`

---

## Notes / Phase Gates

- Adding dependencies (`fastapi`, `uvicorn`) is required for this task; confirm before Phase 3 execution if needed.
- Any step that would touch more than 3 files should be broken into a subtask and re-confirmed before proceeding.
