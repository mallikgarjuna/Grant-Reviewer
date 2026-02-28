# WF-0037 — NWO Vidi 2025 Full Proposal Call Definition PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-28

## 0. User Stories (MVP)

- US1: As a maintainer, I want a source-grounded V2 call definition for NWO Vidi 2025 (full proposal), so that it can be ingested and served consistently via existing call/config/metadata endpoints.
- US2: As a researcher (later), I want the Vidi full proposal call to be selectable as a structured-nodes call, so that I can submit text per proposal section and receive evaluation-criteria-grounded feedback.

## Deferred Stories (Not in MVP)

- DS1: As a maintainer, I want explicit domain selection + domain-specific constraints/criteria branching (AES/TTW vs SSH/SGW vs ENW), so that domain-specific rules are enforced without ambiguity.
- DS2: As a researcher, I want non-evaluable “explanatory notes” guidance surfaced separately from evaluable guidance, so the UI can help without confusing what is assessed.
- DS3: As a researcher, I want nested proposal structures to render in a universal submit UI (recursive renderer), so nested calls like ERC are supported.

## 1. In Scope

- Author canonical V2 YAML for Vidi full proposal:
  - `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`
- Author traceability manifest with file hashes + “used for” mapping:
  - `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`
- Encode:
  - Proposal node structure (narrative sections only) with stable logical IDs
  - Evaluation criteria/elements grounded in the official call PDF (full proposal criteria)
  - Enforceable content constraints only (word limits; represent page limits as non-deterministic warnings)
  - Call metadata including deadlines (verbatim from official sources)
  - Reviewer policy rules grounded in official sources (DORA/bibliometrics ban; bias/personal-attributes avoidance)
- Verification:
  - Schema validation (`CallDefinitionV2.model_validate`)
  - `ingest_call.py --dry-run`
  - DB/API preflight smoke-test against a dedicated test DB:
    - `GET /calls`
    - `GET /calls/{call_id}/nodes` and `?view=tree`
    - `GET /api/public/calls/{call_logical_id}/config`
    - `GET /api/public/calls/{call_logical_id}/nodes/metadata`

## 2. Out of Scope

- Any UI changes (universal submit form, call picker changes, recursion rendering).
- Any new backend endpoints or contract changes.
- Pre-proposal definition (this WF models full proposal only).
- Domain branching (unless explicitly promoted as a follow-on WF).
- Deterministic enforcement of formatting/layout rules (fonts/margins/page layout) on plain text input.

## 3. User / System Flow

Happy path (US1):
1. Maintainer authors/updates `nwo_vidi_2025_full_proposal.yaml` + `sources.md`. (US1)
2. Maintainer runs schema validation and dry-run ingest; fixes any schema/reference issues. (US1)
3. Maintainer ingests YAML into a test DB and runs DB/API preflight smoke-test to confirm runtime shapes. (US1)
4. Existing API endpoints serve the call summary, nodes (flat/tree), config gating, and metadata. (US1)

Failure path A: YAML invalid or references broken (US1)
1. Schema validation or dry-run ingest fails due to YAML syntax/schema/reference issues. (US1)
2. Maintainer corrects YAML (IDs, missing elements, invalid policy rules) and reruns validation. (US1)

Failure path B: Runtime mismatch after DB ingest (US1)
1. DB ingest succeeds but metadata/config/nodes endpoints return inconsistent logical IDs (unknown nodes) or wrong shapes. (US1)
2. Maintainer fixes logical IDs / node list alignment and repeats ingest + preflight. (US1)

## 4. Functional Requirements

- FR1 (US1): Provide a canonical V2 call YAML at `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`.
- FR2 (US1): Provide a source manifest at `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md` listing official inputs, paths, SHA256, and mapping to YAML sections.
- FR3 (US1): Encode `funding_call.deadlines` with stable semantic keys and verbatim `datetime_local` + `timezone` from the official Call PDF.
- FR4 (US1): Encode full proposal evaluation criteria/elements grounded in the Call PDF §4.3.2, with `source_hint` per evaluation element.
- FR5 (US1): Encode narrative proposal nodes grounded in the full proposal form, including enforceable word limits (ERROR) and non-deterministic page limits (WARNING).
- FR6 (US1): Encode reviewer policy rules grounded in the Call PDF (DORA: no JIF/h-index; bias avoidance), with enforcement strength matching source clarity.
- FR7 (US1): `ingest_call.py --dry-run` must validate the YAML successfully with no DB required.
- FR8 (US1): DB ingest into a dedicated test DB must succeed and the four endpoint families must return consistent results (no unknown nodes; correct nested/flat shapes).

## 5. Data & API Contracts

Existing API contracts must remain unchanged (US1):

- `/calls` returns a list including `{ id, code, name, year, agency_short_name }`. (FR8)
- `/calls/{call_id}/nodes` returns flat `nodes[]` with `parent_node_id` links when applicable. (FR8)
- `/calls/{call_id}/nodes?view=tree` returns roots with recursive `children[]`. (FR8)
- `/api/public/calls/{call_logical_id}/config` returns `{ ui_mode, expected_nodes }`. (FR8)
- `/api/public/calls/{call_logical_id}/nodes/metadata` returns metadata keyed by `logical_id` and `unknown_node_logical_ids` must be empty for a consistent call definition. (FR8)

Validation constraints (US1):

- All `proposal_nodes[].id` are unique. (FR1)
- All `node_expectations[].evaluation_element_id` reference a defined evaluation element. (FR4, FR5)
- Reviewer policy rules using `POST_CHECK`/`BLOCKING` must include `forbidden_terms`. (FR6)

## 6. Components / Modules

No new runtime modules are required (US1). The work product is:

- Authored call definition artifacts (YAML + `sources.md`) under `backend/data/calls/`.
- Existing ingestion pipeline:
  - V2 schema validation: `backend/app/schemas/call_definitions_v2.py`
  - Ingestion CLI: `backend/scripts/ingest_call.py`
- Existing runtime consumers:
  - `/api/public/.../config` and `/api/public/.../nodes/metadata` use canonical JSON derived from the call definition.

## 7. Edge Cases

- AES-specific impact clause exists in the Call PDF: without domain branching, it may be encoded as an OPTIONAL evaluation element, but must not be treated as universally applicable. (US1)
- Deadline timezone string: store verbatim label from source; do not silently convert. (US1)
- Pre-proposal vs full proposal criteria: must not leak pre-proposal-only evaluation elements into full proposal criteria. (US1)
- “Public summary in Dutch” exists in the form: excluded from `proposal_nodes` unless later explicitly required in evaluable scope. (US1)

## 8. Testing Decisions (TDD)

- No new production code is required for this WF by default.
- Verification tests/seams (US1):
  - Schema validation: `CallDefinitionV2.model_validate(...)` against the YAML.
  - Dry-run ingest: `scripts/ingest_call.py ... --dry-run`.
  - DB/API preflight: ingest into `grant_reviewer_test` and validate endpoint consistency using `fastapi.testclient.TestClient` (LLM stub mode).
- If regressions are found later, add a small DB/API integration test that asserts:
  - the call exists by `code`
  - config/metadata `expected_nodes` match `proposal_nodes` IDs
  - nested vs flat expectations for parent links are correct

## 9. Telemetry (Minimal)

- None (maintenance workflow). Rely on existing ingest logs for verification evidence.

## 10. Deferred / Not in MVP

- Domain-specific call variants modeled via `domain_id` branching.
- Non-evaluable guidance surfaced in a separate YAML field.
- Nested universal submit UI (recursion).
- UI-facing deadline display or deadline-based gating.

## 11. Open Questions

- Should we standardize timezones to IANA identifiers (e.g., `Europe/Amsterdam`) while preserving the verbatim label somewhere else, or keep verbatim only?
- If AES-only impact considerations must be enforced, do we need domain branching sooner than planned?

## 12. Changelog

- v0.1 (2026-02-28): Initial PRD from brainstorm.
