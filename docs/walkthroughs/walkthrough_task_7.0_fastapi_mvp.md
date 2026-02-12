# Walkthrough: Task 7.0 - FastAPI MVP

**Completed**: 2026-02-08  
**Task ID**: 7.0  
**Pipeline Phase**: Phase 3 (Implementation)

## Summary

Implemented the first FastAPI API surface for Grant Reviewer and exposed the existing review flow over HTTP with canonical error handling, forward-compatible status typing, and local stub mode for zero-cost verification.

## What Was Built

### API Runtime
- Added FastAPI app entrypoint in `backend/main.py` with startup table initialization.
- Implemented endpoints:
  - `GET /health`
  - `GET /calls`
  - `GET /calls/{call_id}/nodes`
  - `POST /reviews`
  - `GET /reviews/{review_id}`
- Added canonical error shape and centralized error code → HTTP status mapping.

### Data Access Enhancements
- Extended `ReviewRepository` with:
  - active calls query (`FundingCall` + `FundingAgency`)
  - call node listing with grouped `has_expectations` computation
  - review lookup and ordered review-card retrieval

### API Schemas
- Added typed API request/response models in `backend/app/schemas/api.py`.
- Kept `review.status` as enum (`PENDING`, `COMPLETED`, `FAILED`) for forward compatibility.

### Stub LLM Mode
- Added `LLM_MODE=stub` support in `backend/app/services/llm_client.py`.
- Stub client returns deterministic schema-valid JSON and avoids external API calls.
- Added `LLM_MODE` to `backend/.env.example`.

### Dependencies and Tests
- Added dependencies in `backend/pyproject.toml`:
  - runtime: `fastapi`, `uvicorn`
  - dev/test: `pytest`, `httpx`
- Added API tests in `backend/tests/test_api.py` (10 tests total).

## Verification Results

### Automated
Command:
```bash
cd backend && uv run pytest tests/test_api.py -q
```
Result:
```text
10 passed in 3.54s
```

Coverage of key invariants:
- canonical error shape and schema-validation mapping
- `SNIPPET_TOO_LONG`, `NO_EXPECTATIONS`, `NODE_NOT_IN_CALL`
- status forward-compat support
- atomic failure path: failed review persists with `status=FAILED` and zero cards
- centralized error-code/status mapping consistency

### Manual (Stub Mode, No OpenAI Cost)
Commands:
```bash
cd backend && uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run
cd backend && LLM_MODE=stub uv run python -c "from fastapi.testclient import TestClient; from main import app; c=TestClient(app); calls=c.get('/calls'); print('calls_status', calls.status_code); call_id=calls.json()['calls'][0]['id']; nodes=c.get(f'/calls/{call_id}/nodes'); print('nodes_status', nodes.status_code); node_id=next(n['id'] for n in nodes.json()['nodes'] if n['has_expectations']); review=c.post('/reviews', json={'call_id':call_id,'node_id':node_id,'snippet_text':'manual stub verification text'}); print('create_status', review.status_code, review.json().get('status')); review_id=review.json()['review_id']; detail=c.get(f'/reviews/{review_id}'); print('detail_status', detail.status_code, 'cards', len(detail.json().get('cards', [])))"
```
Observed:
- `calls_status 200`
- `nodes_status 200`
- `create_status 200 COMPLETED`
- `detail_status 200 cards 1`

## Notes

- Real OpenAI-backed API verification in this walkthrough was intentionally skipped to avoid external cost/latency; stub mode verifies full endpoint flow and contract behavior.
