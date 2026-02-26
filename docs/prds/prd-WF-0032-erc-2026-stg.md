# WF-0032 — ERC Starting Grant 2026 PRD

Artifact: prd
Version: v0.4
Status: Part A Implemented (Pending Phase 3 Part B/C)
Last Updated: 2026-02-26

## 0. User Stories (MVP)
- US1: As a developer, I want to define hierarchical proposal node structures in the Call Definition V2 YAML so that complex multi-part forms (like ERC 2026 StG) can be modeled accurately.
- US2: As a backend system, I want the ingestion script to parse YAMLs with `parent_logical_id` references and correctly map them to the `parent_node_id` database schema without breaking flat-list legacy YAMLs.
- US3: As a researcher/UI consumer in the future, I want the `GET /calls/{id}/nodes` endpoint to return the flat list of nodes with their `parent_node_id` properly populated, so a client can build the tree.
- US4: As an evaluator model, I want to know which evaluation `stage` an element belongs to (e.g., `STEP_1`, `STEP_2`, `BOTH`) (stored strictly in `canonical_json`, not used in MVP runtime), so that future updates to the evaluation engine can run targeted reviews.
- US5: As a backend system, I want to safely reject missing parents or duplicate IDs to avoid data corruption or last-write-wins silently overwriting nodes.

## Deferred Stories (Not in MVP)
- As a researcher, I want the Dynamic UI to recursively render nested form sections (Deferred).
- As an evaluator engine, I want to only run Step 1 evaluations if the proposal is in Step 1 (Deferred).
- As a UI consumer, I want a natively nested tree API response instead of a flat list (Deferred).

## 1. In Scope
- Updating `CallDefinitionV2` Pydantic schemas to include `parent_logical_id` (str) on nodes.
- Updating `ContentConstraintsDefinitionV2` Pydantic schemas to include `max_pages` (int) as UI guidance.
- Updating schema to include `stage` metadata on evaluation elements (canonical_json only).
- Refactoring `scripts/ingest_call.py` to resolve string-based `parent_logical_id` to database `parent_node_id` UUIDs securely.
- Enforcing acyclic dependency (loop prevention) during ingestion.
- Authoring the ERC 2026 StG full-call structure in V2 YAML (`backend/data/calls/erc/erc_stg_2026_full.yaml`), with reviewer-policy metadata grounded in official ERC sources.
- Automated integration test for `GET /calls/{id}/nodes` verifying parent ids are correct in the flat list.
- Verifying the flat `nwo_veni` YAML still ingests seamlessly.

## 2. Out of Scope
- Frontend UI rendering of the nested tree.
- Backend evaluation engine logic updates to conditionally process Step 1 vs Step 2.
- Hard machine enforcement or heuristic calculation of `max_pages`.
- DB migration for stage or max_pages (`canonical_json` is the sole SSOT for these).
- Tree-shaped API response.
- PDF upload parsing.

## 3. User / System Flow
- **Happy Path:** (US1, US2, US3) Developer runs `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml`. The script parses the YAML, validates schemas, validates acyclic graphs/order, creates nodes hierarchically, and assigns `parent_node_id`. (FR1, FR2, FR5)
- **Failure Path 1: Missing Parent** (US2, US5) Developer references a `parent_logical_id` that does not exist in the YAML. Ingestion script throws a strict validation error and halts before DB commit. (FR7)
- **Failure Path 2: Circular Dependency** (US2) Developer authors nodes that reference each other in a loop. Ingestion validation catches cyclic reference error and halts. (FR2)
- **Failure Path 3: Duplicate ID** (US5) Developer authors multiple nodes with same ID. Ingestion fails fast before DB commit. (FR8)

## 4. Functional Requirements
- FR1 (US1, US2): The system must support `parent_logical_id` on YAML node definitions, mapping it to DB `parent_node_id`.
- FR2 (US2): The system must validate the node dependency tree to be acyclic during ingestion.
- FR3 (US1): The schema shall accept `max_pages` as an optional integer in `ContentConstraintsDefinitionV2`.
- FR4 (US4): The schema shall accept `stage` as an optional literal in evaluation elements (persisted only in `canonical_json`).
- FR5 (US3): The API endpoint `GET /calls/{id}/nodes` must correctly yield nodes with their `parent_node_id` relationships intact in a flat list.
- FR6 (US2): The ingestion script must gracefully handle flat YAMLs where `parent_logical_id` is omitted/null.
- FR7 (US5): The ingestion script must throw a strict validation error if a missing `parent_logical_id` is referenced.
- FR8 (US5): The ingestion script must reject duplicate node IDs.

## 5. Data & API Contracts
- `ProposalNodeDefinitionV2` schema updated: add `parent_logical_id: str | None = Field(default=None)`. (US1, FR1)
- `ContentConstraintsDefinitionV2` schema updated: add `max_pages: int | None = Field(default=None)`. (US1, FR3)
- Evaluation Element schema updated: add `stage: Literal["STEP_1", "STEP_2", "BOTH"] | None = Field(default="BOTH")`. (US4, FR4)
- **Ordering Contract**: `order_index` is implicitly the preorder traversal index derived from YAML list order + parent links. (No complex ordering API).
- **Stage Metadata**: `stage` is explicitly `canonical_json`-only. The evaluation engine must parse it from there later.

## 6. Components / Modules
- **`backend/app/schemas/call_definitions_v2.py`**: Add new fields. Add explicit validation for duplicate node IDs.
- **`backend/scripts/ingest_call.py`**: Significant refactor to do topological sorting / two-pass ingestion of nodes so parents exist before children are linked. Handle `order_index` calculation deterministically.
- **`backend/tests/integration/test_api.py`**: New automated tests validating parent ID retrieval.
- **`backend/data/calls/erc/erc_stg_2026_full.yaml`**: Canonical call logic artifact, including evaluable structure + criteria/elements + enforceable reviewer-policy rules.

## 7. Edge Cases
- YAML defines nodes out of topological order. (US2) -> Ingestion must resolve parent/child dependencies safely (e.g. topological sort).
- Node references its own logical ID. (US2) -> Acyclic validation error.
- Checksum changes: Changing ordering of nodes without changing content can invalidate canonical checksums requiring re-ingestion.

## 8. Testing Decisions (TDD)
- **Unit Test (Schema/Ingest):** Verify models accept new fields. Verify ingestion validation catches circular loops in Node dependency graphs.
- **Integration Test (DB Ingestion):** DB-backed test that ingests a V2 YAML with parents and asserts `ProposalNode.parent_node_id` is set correctly. Test nodes out of order + correct parent resolution.
- **Integration Test (API):** Assert returned nodes from API include non-null `parent_node_id` relationships for at least one node.

## 9. Telemetry (Minimal)
- N/A

## 10. Deferred / Not in MVP
- Text-to-page heuristic conversion.
- Dynamic Form recursive generation.
- Tree-shaped API response.
- Step 1 vs Step 2 evaluation engine gating logic.

## 11. Open Questions (if any)
- None

## 12. Changelog
- v0.1 (2026-02-25): Initial PRD from brainstorm
- v0.2 (2026-02-25): Applied risk audit self-edits.
- v0.3 (2026-02-25): Applied adversarial audit findings (flat API clarification, test gaps, duplicate ID FRs, canonical JSON constraints).
- v0.4 (2026-02-26): Reconciled implementation scope to full ERC YAML + reviewer-policy runtime hardening and added Part-A-complete status.
