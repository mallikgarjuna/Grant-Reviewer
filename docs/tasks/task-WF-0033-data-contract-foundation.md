# WF-0033 — Data Contract Foundation Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-26

---

## Preflight (One-Time)

- Start the isolated test DB: `cd backend && docker compose -f docker-compose.test.yml up -d`
- Set `DATABASE_URL` to the test DB (never dev/prod), then run tests with `PYTHONPATH=.`.

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: add `view=tree` (DB-adjacency fallback)

Goal:
Add `view=flat|tree` to `GET /calls/{call_id}/nodes` with `flat` default and a minimal tree view built from DB `parent_node_id` + `order_index` (no canonical JSON yet).
Slice: tracer-bullet
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR3
Files to modify:
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_call_nodes_tree_api.py` (new)
Acceptance Criteria:
- `GET /calls/{call_id}/nodes` returns the current flat shape unchanged.
- Flat nodes include `logical_id: str | None` (additive field; existing clients continue to work).
- `GET /calls/{call_id}/nodes?view=tree` returns `nodes` as root nodes only, each with recursive `children` arrays (empty list for leaves).
- Tree nodes include `logical_id` (may be null if not present in DB fixtures yet).
TDD Plan:
- RED: Add `backend/tests/test_call_nodes_tree_api.py::test_call_nodes_view_tree_returns_nested_children` (and a flat-regression assertion).
- GREEN: Implement `view` parsing + tree DTOs + DB-adjacency builder.
- REFACTOR: Keep tree builder code small/contained (no new services yet).
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_call_nodes_tree_api.py`
Risks (if any):
- FastAPI `response_model` union shape needs careful typing to avoid breaking OpenAPI.

### [x] Task 2 — Canonical JSON tree: V2 `parent_logical_id` as source-of-truth

Goal:
Implement tree construction from V2 canonical JSON `proposal_nodes[]` using `id` + `parent_logical_id` and canonical list order for sibling ordering.
Slice: tree-sot
User Stories: US1
PRD Requirements: FR4, FR8
Files to modify:
- `backend/app/services/node_tree_service.py` (new)
- `backend/main.py`
- `backend/tests/test_node_tree_service.py` (new)
Acceptance Criteria:
- For V2 calls with a valid `proposal_nodes` list, `view=tree` uses canonical JSON ordering/parentage (not DB adjacency).
- For legacy/no-definition calls, behavior falls back to DB adjacency as in Task 1.
TDD Plan:
- RED: Add `backend/tests/test_node_tree_service.py::test_build_tree_from_parent_logical_id_orders_siblings_by_definition_order`.
- GREEN: Implement `NodeTreeService` and wire it into the route.
- REFACTOR: Keep service API narrow (inputs: canonical JSON + active nodes mapping).
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_node_tree_service.py`
Risks (if any):
- Fixtures may not yet include a deeply nested call; unit tests must cover ordering deterministically.

### [x] Task 3 — Deterministic mismatch + cycle failure behavior (409)

Goal:
Enforce fail-fast behavior for canonical-JSON/DB mismatch and for canonical cycles when serving `view=tree`.
Slice: tree-safety
User Stories: US1, US3
PRD Requirements: FR8
Files to modify:
- `backend/app/services/node_tree_service.py`
- `backend/main.py`
- `backend/tests/test_call_nodes_tree_api.py`
Acceptance Criteria:
- If canonical JSON references node logical IDs that are missing from active DB nodes, `view=tree` returns 409 `CALL_DEFINITION_NODE_MISMATCH` including missing IDs in `error.details`.
- If canonical `parent_logical_id` graph contains a cycle, `view=tree` returns 409 `CALL_DEFINITION_CYCLE`.
- Errors use the canonical API error envelope.
TDD Plan:
- RED: Add `backend/tests/test_call_nodes_tree_api.py::test_call_nodes_view_tree_mismatch_returns_409` and `backend/tests/test_call_nodes_tree_api.py::test_call_nodes_view_tree_cycle_returns_409`.
- GREEN: Implement mismatch/cycle checks and map to API exceptions.
- REFACTOR: Keep error codes centralized and consistently shaped.
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_call_nodes_tree_api.py`
Risks (if any):
- Need a safe place to add minimal cycle/mismatch fixtures without touching many unrelated files.

### [x] Task 4 — Tracer bullet: metadata DTO endpoint (bulk)

Goal:
Add `GET /api/public/calls/{call_logical_id}/nodes/metadata` returning per-node metadata DTOs from `CallDefinition.canonical_json` joined to active DB nodes by `logical_id`.
Slice: metadata-tracer
User Stories: US2
PRD Requirements: FR5, FR7, FR8
Files to modify:
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_call_nodes_metadata_api.py` (new)
Acceptance Criteria:
- If call definition missing, return 409 `CALL_DEFINITION_MISSING`.
- If definition present, response includes `nodes[]` with `logical_id`, `node_id` (when present), and the UI-critical fields (`label`, `node_type`, `parent_logical_id`, `guidance_text`) plus `content_constraints`, `compliance_rules`, `source_section`.
TDD Plan:
- RED: Add `backend/tests/test_call_nodes_metadata_api.py::test_call_nodes_metadata_missing_definition_returns_409` and `backend/tests/test_call_nodes_metadata_api.py::test_call_nodes_metadata_bulk_success`.
- GREEN: Implement DTOs + route (keep implementation minimal).
- REFACTOR: Avoid mixing business logic into route handler beyond a small extraction.
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_call_nodes_metadata_api.py`
Risks (if any):
- Some fixtures may not include `guidance_text` / `content_constraints`; tests should allow `null` values.

### [ ] Task 5 — Metadata filtering + unknown IDs partial success

Goal:
Support `node_logical_ids` filtering and return `unknown_node_logical_ids` while still returning known nodes (200).
Slice: metadata-filter
User Stories: US2
PRD Requirements: FR6, FR9
Files to modify:
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_call_nodes_metadata_api.py`
Acceptance Criteria:
- When `node_logical_ids` filter is provided, response includes only requested known nodes.
- Unknown requested IDs are returned in `unknown_node_logical_ids` (sorted, unique).
- No filter preserves bulk behavior (Task 4).
TDD Plan:
- RED: Add `backend/tests/test_call_nodes_metadata_api.py::test_call_nodes_metadata_filter_returns_unknowns`.
- GREEN: Implement filter parsing and response shaping.
- REFACTOR: Keep parsing consistent with existing patterns (repeated query params).
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_call_nodes_metadata_api.py`
Risks (if any):
- Query param parsing differences (repeated vs CSV); stick to repeated params per PRD.

### [ ] Task 6 — Refactor: extract metadata builder service

Goal:
Move metadata DTO construction out of route handler into a dedicated service for reuse/testing.
Slice: metadata-refactor
User Stories: US2
PRD Requirements: FR5, FR6, FR7
Files to modify:
- `backend/app/services/node_metadata_service.py` (new)
- `backend/main.py`
- `backend/tests/test_call_nodes_metadata_api.py`
Acceptance Criteria:
- Route handler delegates to `NodeMetadataService` and behavior remains identical to Tasks 4–5.
- Service has unit tests for basic projection behavior (optional if covered by API tests and would exceed file budget).
TDD Plan:
- RED: Add/adjust tests to exercise the service seam (either unit-level or via API tests with thin wrapper assertions).
- GREEN: Implement service and wire it.
- REFACTOR: Keep service inputs explicit (call definition canonical JSON + active node mapping).
Verification Steps:
- `cd backend && export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/grant_reviewer_test && PYTHONPATH=. uv run pytest -q tests/test_call_nodes_metadata_api.py`
Risks (if any):
- Refactor drift; keep this task purely structural with no contract changes.

## Changelog

- v0.1 (2026-02-26): Initial task breakdown from PRD.
- v0.2 (2026-02-26): Tightened atomic file targets, removed ambiguity, and made TDD plan/verification steps implementation-ready.
- v0.3 (2026-02-26): Added one-time preflight, made `logical_id` additive on flat nodes, and moved canonical-tree testing to a unit seam to keep tasks atomic.
