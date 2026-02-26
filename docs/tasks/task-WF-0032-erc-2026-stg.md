# WF-0032 — ERC Starting Grant 2026 Tasks

Artifact: task
Version: v0.7
Status: Ready for Implementation
Last Updated: 2026-02-26

## Changelog

- v0.1 (2026-02-26): Initial task breakdown from PRD.
- v0.2 (2026-02-26): Applied internal review edits for strict TDD plans and atomicity regarding DB transactions vs schema validation.
- v0.3 (2026-02-26): Applied adversarial review edits (graphlib topo sort, explicit session flushes/rollbacks).
- v0.4 (2026-02-26): Applied adversarial pass 2 edits (test paths, preorder index logic, DB assertions for rollback and stage, deterministic parsing prep).
- v0.5 (2026-02-26): Fix test file paths/commands; align stage assertions to canonical_json evaluation elements; use repo test DB compose URL.
- v0.6 (2026-02-26): Align Task 5 DB verification with test DB safety rules and docker-compose.test.yml.
- v0.7 (2026-02-26): Re-open Task 5; block YAML authoring until official ERC 2026 StG source documents are provided.

## Task Breakdown (Sequential Order)

### [x] Task 1 — Update Core Schemas & Validation
Goal: Add `parent_logical_id`, `max_pages`, and `stage` to the V2 schemas. Apply pre-validation for duplicate node IDs. Add defense-in-depth duplicate check in ingestion loop.
Slice: Core Schema Definitions
User Stories: US1, US4, US5
PRD Requirements: FR1, FR3, FR4, FR8
Files to modify:
- `backend/app/schemas/call_definitions_v2.py`
- `backend/tests/test_call_definitions_v2_schema.py`
Acceptance Criteria: Pydantic models successfully parse new fields and reject duplicate node IDs in the list.
TDD Plan: RED (write failing validation tests for duplicate IDs and missing fields in `test_call_definitions_v2_schema.py`) -> GREEN (add fields and validators to schema) -> REFACTOR (skip)
Verification Steps: `cd backend && uv run pytest tests/test_call_definitions_v2_schema.py`
Risks: Minimal.

### [x] Task 2 — Ingestion Parser & Topological Sort Validations
Goal: Implement the logic to build the dependency tree from the flat YAML nodes, checking for cycles, self-parents, and missing parent IDs. Create a pure-function API for the tree/graph checks.
Slice: Ingestion Graph Logic
User Stories: US2, US5
PRD Requirements: FR2, FR6, FR7, FR8
Files to modify:
- `backend/scripts/ingest_call.py`
- `backend/tests/test_ingest_call_graph_pure.py`
- `backend/tests/fixtures/hierarchy_v2.yaml`
Acceptance Criteria: Pure graph parser accepts valid flat lists (no parents), accepts correctly ordered lists with parents, errors on missing parents, self-parents, duplicate IDs, and cycles. Exposes clear pure helper functions. Use `graphlib.TopologicalSorter` from the standard library for cycle detection ONLY. Ensure deterministic "preorder traversal" (using list order + parent links) is resolved correctly rather than relying on unstable topo sort ties.
TDD Plan: RED (supply cyclic graph, missing parent graph, self-parent graph from fixture to pure unit test marked with `@pytest.mark.no_db`) -> GREEN (build acyclic check with `graphlib` and parsing logic into reusable pure functions) -> REFACTOR (extract graph functions safely)
Verification Steps: `cd backend && uv run pytest -m no_db tests/test_ingest_call_graph_pure.py`
Risks: Preorder determination requires careful tracking of original YAML list order vs parent relationships.

### [x] Task 3 — Ingestion DB Commit & Parent ID Resolution
Goal: Create the `ProposalNode` rows in the preorder sequence so that `parent_node_id` (UUID) can be resolved from `parent_logical_id`. Ensure `session.flush()` is called within the sequence. Store `order_index` mapped to the preorder traversal.
Slice: DB Ingestion
User Stories: US2, US4
PRD Requirements: FR1, FR4, FR6, FR7
Files to modify:
- `backend/scripts/ingest_call.py`
- `backend/tests/test_ingest_call_v2_db.py`
Acceptance Criteria: DB reflects nodes with correct `parent_node_id` foreign keys, `order_index` exactly matches the deterministic preorder traversal, rollback leaves DB untouched on failure, and evaluation element `stage` is persisted in `CallDefinition.canonical_json` (canonical_json-only; not used in runtime).
TDD Plan: RED (write DB-backed test using hierarchy fixture: expect `parent_node_id` populated, `order_index` matching preorder, explicit test for transactional rollback on failure leaving DB empty, and evaluation element `stage` present in stored `canonical_json`) -> GREEN (in 2nd pass of ingestion, look up the newly created UUID of the parent, assign it, and set `order_index`. Ensure `session.flush()` is used between interdependent insert operations) -> REFACTOR (none)
Verification Steps:
1. `cd backend && docker compose -f docker-compose.test.yml up -d`
2. `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && uv run pytest tests/test_ingest_call_v2_db.py`
Risks: Transaction boundaries might be tricky if saving and searching sequentially. Ensure session is flushed to generate UUIDs before referencing them, and proper rollback handling exists. Test DB is required.

### [x] Task 4 — Flat API Verification (Tracer Bullet E2E)
Goal: Ensure the overarching API yields the properly linked flat list of nodes, validating the E2E contract.
Slice: API E2E
User Stories: US3
PRD Requirements: FR5
Files to modify:
- `backend/tests/test_api.py`
Acceptance Criteria: True E2E test: Ingests the V2 hierarchy fixture YAML into the test db, then `GET /calls/{id}/nodes` returns JSON where nodes contain non-null `parent_node_id` mapping to another node in the list.
TDD Plan: RED (update api test to ingest the new hierarchy fixture and assert `parent_node_id` is present and correct) -> GREEN (None required if Tasks 1-3 are correct) -> REFACTOR (None)
Verification Steps:
1. `cd backend && docker compose -f docker-compose.test.yml up -d`
2. `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && uv run pytest tests/test_api.py -k hierarchy_ingest`
Risks: Real E2E requires clean DB teardown between ingestion steps.

### [ ] Task 5 — Author ERC 2026 StG YAML (Blocked: Source Intake Required)
Goal: Write the final declarative canonical artifact for the ERC 2026 Starting Grant based only on official source documents provided in this workflow.
Slice: Canonical Data
User Stories: US1
PRD Requirements: FR1, FR3, FR4
Files to modify:
- `backend/data/calls/erc_stg_2026_step1.yaml`
Acceptance Criteria:
- Official ERC StG 2026 source documents (application form + assessment criteria/reviewer guidance) are provided and referenced.
- YAML structure, constraints, and evaluation criteria/elements are traceable to those sources.
- A valid YAML struct details nodes and constraints using `parent_logical_id`.
TDD Plan: N/A
Verification Steps:
1. Source intake completed and documented (titles/version/date + supplied location).
2. `cd backend && uv run python scripts/ingest_call.py data/calls/erc_stg_2026_step1.yaml --dry-run`
3. `cd backend && docker compose -f docker-compose.test.yml up -d`
4. `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && uv run python scripts/ingest_call.py data/calls/erc_stg_2026_step1.yaml`
Risks: Authoring without official sources creates non-defensible YAML and must be avoided.
