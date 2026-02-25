# WF-0032 — ERC Starting Grant 2026 PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-25

## 0. User Stories (MVP)
- US1: As a developer, I want to define hierarchical proposal node structures in the Call Definition V2 YAML so that complex multi-part forms (like ERC 2026 StG) can be modeled accurately.
- US2: As a backend system, I want the ingestion script to parse YAMLs with `parent_logical_id` references and correctly map them to the `parent_node_id` database schema without breaking flat-list legacy YAMLs.
- US3: As a researcher/UI consumer in the future, I want the `GET /calls/{id}/nodes` endpoint to return the deeply nested structural tree of the call.
- US4: As an evaluator model, I want to know which evaluation `stage` an element belongs to (e.g., `STEP_1`, `STEP_2`, `BOTH`), so that future updates to the evaluation engine can run targeted reviews.

## Deferred Stories (Not in MVP)
- As a researcher, I want the Dynamic UI to recursively render nested form sections (Deferred).
- As an evaluator engine, I want to only run Step 1 evaluations if the proposal is in Step 1 (Deferred).

## 1. In Scope
- Updating `CallDefinitionV2` Pydantic schemas to include `parent_logical_id` (str) on nodes.
- Updating `ContentConstraintsDefinitionV2` Pydantic schemas to include `max_pages` (int) as UI guidance.
- Updating schema to include `stage` metadata (e.g., `Literal["STEP_1", "STEP_2", "BOTH"]`) on evaluation elements.
- Refactoring `scripts/ingest_call.py` to resolve string-based `parent_logical_id` to database `parent_node_id` UUIDs during insertion.
- Enforcing acyclic dependency (loop prevention) during ingestion.
- Authoring the complete ERC 2026 StG call structure (B1, B2, CV, Track Record, Resources) in a new V2 YAML (`erc_stg_2026.yaml`).
- Automated integration test for `GET /calls/{id}/nodes` verifying hierarchical tree response natively.
- Verifying the flat `nwo_veni` YAML still ingests seamlessly.

## 2. Out of Scope
- Frontend UI rendering of the nested tree.
- Backend evaluation engine logic updates to conditionally process Step 1 vs Step 2.
- Hard machine enforcement or heuristic calculation of `max_pages`.
- Modifications to `proposal_node` table to normalize new constraints (kept inside `canonical_json`).
- Alembic database migration for new columns.
- PDF upload parsing.

## 3. User / System Flow
- **Happy Path:** (US1, US2, US3) Developer runs `uv run python scripts/ingest_call.py calls/erc_stg_2026.yaml`. The script parses the YAML, validates schemas, validates acyclic graphs, creates nodes hierarchically, and assigns `parent_node_id`. Later, `GET /calls/{id}/nodes` returns the full nested node tree.
- **Failure Path 1: Missing Parent** (US2) Developer references a `parent_logical_id` that does not exist in the YAML. Ingestion script throws a strict validation error and halts before DB commit.
- **Failure Path 2: Circular Dependency** (US2) Developer authors nodes that reference each other in a loop. Ingestion script (or schema) throws a cyclic reference error before DB commit.

## 4. Functional Requirements
- FR1 (US1, US2): The system must support `parent_logical_id` on YAML node definitions, mapping it to DB `parent_node_id` during ingestion.
- FR2 (US2): The system must validate the node dependency tree to be acyclic.
- FR3 (US1): The schema shall accept `max_pages` as an optional integer in `ContentConstraintsDefinitionV2`.
- FR4 (US4): The schema shall accept `stage` as an optional literal in evaluation elements.
- FR5 (US3): The API endpoint `GET /calls/{id}/nodes` (or equivalent read boundary) must correctly yield nodes with their `parent_node_id` relationships intact.
- FR6 (US2): The ingestion script must gracefully handle flat YAMLs where `parent_logical_id` is omitted/null.

## 5. Data & API Contracts
- `ProposalNodeDefinitionV2` schema updated: add `parent_logical_id: str | None = Field(default=None)`. (US1, FR1)
- `ContentConstraintsDefinitionV2` schema updated: add `max_pages: int | None = Field(default=None)`. (US1, FR3)
- Evaluation Element schema updated: add `stage: Literal["STEP_1", "STEP_2", "BOTH"] | None = Field(default="BOTH")`. (US4, FR4)

## 6. Components / Modules
- **`backend/app/schemas/call_definitions_v2.py`**: Add new fields. Add model validation for cyclic references if possible statically, or flag for ingest time.
- **`backend/scripts/ingest_call.py`**: Significant refactor to do topological sorting / two-pass ingestion of nodes so parents exist before children are linked.
- **`backend/tests/integration/test_api_calls.py`** (or similar): New automated tests validating tree ingestion and retrieval.
- **`backend/calls/erc_stg_2026.yaml`**: The new canonical call logic artifact.

## 7. Edge Cases
- YAML defines nodes out of topological order. (US2) -> Ingestion must resolve order.
- Node references its own logical ID. (US2) -> Acyclic validation error.

## 8. Testing Decisions (TDD)
- **Unit Test (Schema):** Verify models accept new fields, and that `CallDefinitionV2` model validator catches a basic circular loop between nodes.
- **Integration Test:** Use a dummy complex YAML fixture with at least 3 levels of depth. Verify DB state logic post-ingestion. Query the nodes to ensure `parent_node_id` is correct.

## 9. Telemetry (Minimal)
- N/A

## 10. Deferred / Not in MVP
- Text-to-page heuristic conversion.
- Dynamic Form recursive generation.

## 11. Open Questions (if any)
- None

## 12. Changelog
- v0.1 (2026-02-25): Initial PRD from brainstorm
