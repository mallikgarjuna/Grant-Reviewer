# WF-0033 — Data Contract Foundation PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-26

---

## 0. User Stories (MVP)

- US1: As the Universal Form Renderer (frontend), I want to fetch proposal nodes as a nested tree, so that I can render navigation + section hierarchy without program-specific code.
- US2: As the Universal Form Renderer (frontend), I want to fetch per-node metadata (constraints/rules/source references) by `logical_id`, so that I can render node-specific guidance and validations lazily.
- US3: As a backend maintainer, I want the existing flat nodes route to remain backward compatible, so that current clients do not break during migration.

## Deferred Stories (Not in MVP)

- DS1: As the frontend, I want a single endpoint that returns tree + metadata in one payload, so that I can avoid multiple network round trips.
- DS2: As the frontend, I want server-driven step gating (e.g., ERC Step 1 vs Step 2) expressed in the same contract, so that I can conditionally show/evaluate subsets.
- DS3: As the backend, I want a dedicated metadata table to support richer querying and versioning beyond canonical JSON.

## 1. In Scope

- Serve a tree-shaped node hierarchy for a call (in addition to the existing flat list). (US1, US3)
- Expose both DB UUID and V2 `logical_id` in UI-facing node DTOs. (US1, US2)
- Add a public metadata DTO route, sourced from `CallDefinition.canonical_json` (validated V2), optionally filtered for lazy loading. (US2)
- Define deterministic mismatch behavior between DB nodes and canonical JSON structure (errors vs warnings). (US1, US2)

## 2. Out of Scope

- Changing the underlying SQLModel schema / migrations. (DS3)
- Changing compliance engine logic or review engine logic. (DS2)
- Building the actual frontend universal renderer. (US1, US2 consumer)
- Re-authoring ERC call YAML content. (separate WF)

## 3. User / System Flow

### Happy Path (Tree + Metadata)

1. Frontend fetches call gating config for `call_logical_id`. (US3)
2. Frontend fetches nodes using `GET /calls/{call_id}/nodes?view=tree`. (US1)
3. Frontend renders navigation/structure using `nodes[]` roots + `children[]` recursively, binding input state by `logical_id`. (US1, US2)
4. Frontend lazily hydrates metadata for visible/selected nodes via `GET /api/public/calls/{call_logical_id}/nodes/metadata?node_logical_ids=...`. (US2)
5. Frontend renders node guidance/constraints using returned metadata DTOs. (US2)

### Failure Path A (Definition missing / legacy)

1. Frontend fetches call gating config and receives legacy mode. (US3)
2. Frontend uses legacy single-snippet flow (out of this PRD). (US3)

### Failure Path B (Mismatch between DB nodes and canonical JSON)

1. Frontend requests `view=tree`. (US1)
2. Backend detects that canonical JSON references unknown `logical_id` or DB is missing expected nodes. (US1, US2)
3. Backend returns a clear error code for hard failures; otherwise returns a best-effort tree and includes warnings in logs. (US1, US3)

## 4. Functional Requirements

- FR1 (US3): `GET /calls/{call_id}/nodes` defaults to the current flat list response (backward compatible).
- FR2 (US1): `GET /calls/{call_id}/nodes?view=tree` returns a nested tree where each node includes a `children[]` list (empty list for leaves).
- FR3 (US1, US2): Node DTOs exposed to the universal renderer include both `id: UUID` and `logical_id: str | None`.
- FR4 (US1): Tree ordering is stable and derived from canonical JSON ordering when present; otherwise fall back to DB `order_index`.
- FR5 (US2): `GET /api/public/calls/{call_logical_id}/nodes/metadata` returns per-node metadata DTOs keyed by `logical_id`.
- FR6 (US2): Metadata route supports optional filtering via `node_logical_ids` to return only requested nodes.
- FR7 (US1, US2): Metadata is sourced from `CallDefinition.canonical_json` (validated V2) and joined to DB nodes by `logical_id` when mapping to UUIDs.
- FR8 (US1, US3): On structural mismatch, API behavior is deterministic (documented error codes + best-effort rules).

## 5. Data & API Contracts

### 5.1 Nodes Endpoint (`/calls/{call_id}/nodes`) (US1, US3)

`GET /calls/{call_id}/nodes?view=flat|tree`

- Query params:
  - `view`: `"flat"` (default) or `"tree"`.
- Response (view=flat): existing `NodesResponse` (FR1).
  - `nodes: list[NodeSummary]`
- Response (view=tree): `NodesTreeResponse` (FR2).
  - `nodes: list[NodeTreeNode]` (root nodes only)

Node DTO fields (tree view): (FR2, FR3)

- `id: UUID`
- `logical_id: str | None`
- `parent_node_id: UUID | None`
- `title: str`
- `node_type: NodeType`
- `order_index: int`
- `has_expectations: bool`
- `children: list[NodeTreeNode]`

Validation / invariants:
- `children` is always present (may be empty). (FR2)
- Roots have `parent_node_id = null`. (FR2)
- `logical_id` may be null for legacy calls, but for V2 calls it should be populated. (FR3)

### 5.2 Metadata DTO Endpoint (`/api/public/calls/{call_logical_id}/nodes/metadata`) (US2)

`GET /api/public/calls/{call_logical_id}/nodes/metadata?node_logical_ids=...`

- Query params:
  - `node_logical_ids`: optional repeated or comma-separated list (exact encoding to decide in implementation). (FR6)
- Response: `NodeMetadataResponse`
  - `call_logical_id: str`
  - `config_version: str`
  - `nodes: list[NodeMetadataDTO]`

NodeMetadataDTO (UI-oriented, derived from canonical JSON + DB join): (FR5, FR7)

- `logical_id: str`
- `node_id: UUID | None` (null if not mapped to an active DB node)
- `content_constraints: dict` (shape mirrors V2 canonical JSON)
- `compliance_rules: list` (shape mirrors V2 canonical JSON)
- `source_section: str | None`

Validation / error behavior (FR8):
- If call is not found: `CALL_NOT_FOUND`
- If definition/canonical JSON missing: return a clear error code OR a "legacy" empty response (decision in Phase 1.3).
- If requested `node_logical_ids` includes unknown values: either return partial success + list unknowns, or 4xx with details (decision in Phase 1.3).

### 5.3 Compatibility Notes

- Existing frontend mode gating endpoint remains the first hop; this WF does not change its schema. (US3)
- Flat list semantics remain unchanged. (FR1)

## 6. Components / Modules

- `backend/main.py`
  - Routes:
    - Extend `GET /calls/{call_id}/nodes` to accept `view` and return flat/tree. (FR1, FR2)
    - Add `GET /api/public/calls/{call_logical_id}/nodes/metadata`. (FR5)
- `backend/app/schemas/api.py`
  - Add `NodeTreeNode`, `NodesTreeResponse`, `NodeMetadataDTO`, `NodeMetadataResponse`. (FR2, FR5)
  - Ensure naming stays consistent with existing API schema conventions.
- `backend/app/services/`
  - Tree builder module/service:
    - Input: DB nodes + canonical JSON (proposal_nodes tree)
    - Output: ordered tree DTOs with `children`. (FR2, FR4)
  - Metadata projection module/service:
    - Input: `CallDefinition.canonical_json` + active DB nodes
    - Output: per-node metadata DTOs, optionally filtered. (FR5, FR6, FR7)
- `backend/app/repository.py` (or existing repository layer)
  - Add read helpers to fetch active nodes + call definition by logical id/code as needed.

Design tree (dependency order):
1. DTOs (schemas) define the contract.
2. Services produce DTO-ready structures from DB + canonical JSON.
3. Routes wire services into API endpoints.

## 7. Edge Cases

- Canonical JSON contains `children` references to missing/archived DB nodes. (US1)
- DB contains nodes that are not present in canonical JSON (extra nodes). (US1)
- Duplicate `logical_id` values in canonical JSON or DB (should be treated as a hard failure). (US1, US2)
- Cycles in canonical JSON `children` graph (hard failure with explicit error). (US1)
- Calls with definition present but `proposal_nodes` absent or malformed (fallback to flat; tree view errors clearly). (US1, US3)
- Large trees: ensure recursion depth is bounded and ordering is stable. (US1)

## 8. Testing Decisions (TDD)

- Public seams to test:
  - `GET /calls/{call_id}/nodes` (flat default). (FR1)
  - `GET /calls/{call_id}/nodes?view=tree` (tree shape + ordering). (FR2, FR4)
  - `GET /api/public/calls/{call_logical_id}/nodes/metadata` (bulk + filtered). (FR5, FR6, FR7)
- Minimal test types:
  - Integration-ish API tests using the test DB fixtures for one V2 call. (US1, US2, US3)
  - Unit tests for tree builder:
    - canonical JSON ordering respected
    - fallback ordering behavior
    - cycle detection
    - mismatch handling rules. (FR2, FR4, FR8)
- Mocking policy:
  - Mock only at boundaries (e.g., LLM); do not mock repository/service boundaries for these contract tests.

## 9. Telemetry (Minimal)

- Log warnings when:
  - canonical JSON and DB nodes disagree (counts, unknown logical IDs)
  - metadata is requested for unknown logical IDs
- Prefer structured logs with call identifiers (`call_id`, `call_logical_id`) and counts.

## 10. Deferred / Not in MVP

- Combined tree+metadata "god payload". (DS1)
- Step gating and dynamic evaluation routing. (DS2)
- Persisted metadata projections / versioned metadata store. (DS3)

## 11. Open Questions

1. For metadata filtering, should `node_logical_ids` be repeated params (`...?node_logical_ids=a&node_logical_ids=b`) or a comma-separated string? (US2)
2. For unknown `node_logical_ids`, should the endpoint be partial-success (200 + list unknowns) or strict (4xx)? (US2)
3. For calls lacking a V2 definition, should metadata endpoint return an empty payload (legacy-friendly) or a clear error? (US3)

## 12. Changelog

- v0.1 (2026-02-26): Initial PRD from brainstorm.
