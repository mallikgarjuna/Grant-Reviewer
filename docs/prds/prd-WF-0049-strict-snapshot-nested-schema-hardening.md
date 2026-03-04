# WF-0049 — Strict Snapshot Nested Schema Hardening PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## 0. User Stories (MVP)

- US1: As a backend engine maintainer, I want strict nested snapshot models at the request boundary, so that undeclared nested payload drift is rejected deterministically.
- US2: As a producer/BFF integrator, I want stable, actionable validation failures for nested schema errors, so that payload fixes are unambiguous and repeatable.
- US3: As a workflow owner, I want digest computation to remain deterministic under nested strictness, so that omitted/default nested fields do not produce false digest mismatches.
- US4: As a release owner, I want compatibility evidence for current producer payload classes, so that rollout risk is controlled before enforcement.

## Deferred Stories (Not in MVP)

- DS1: Product/UI behavior changes outside request-boundary contract validation.
- DS2: New snapshot major/minor version introduction (for example `v1.1`) unless additive strictness proves incompatible.
- DS3: Pipeline stage semantics, review output DTO redesign, or unrelated engine refactors.

## 1. In Scope

- Replace loose nested extension surfaces (`dict[str, object]` / `list[dict[str, object]]`) with strict, versioned nested models for currently active/used request-boundary surfaces. (US1)
- Enforce unknown-field rejection at every nested level within `ActivatedCallConfigSnapshotV1`. (US1, US2)
- Preserve schema-first then digest validation precedence with deterministic failure semantics. (US2, US3)
- Define deterministic malformed-field error shape/path ordering for nested failures. (US2)
- Add producer compatibility fixtures for known payload classes and lock deterministic digest behavior across omitted/default nested fields. (US3, US4)
- Keep scope strictly at request-boundary nested contract hardening with no product expansion. (US1-US4)

## 2. Out of Scope

- Adding an `extensions: dict` escape hatch in snapshot v1.
- Call-identity or agency-specific branching in engine behavior.
- New user-facing product flows, pipeline stage changes, or scoring policy changes.
- Broad migration program for new schema version labels (`v1.1`) in this WF.

## 3. User / System Flow

- Happy path:
1. Producer submits `ReviewRequestV1` containing `call_config_snapshot` with `schema_version: "v1"` and nested structures restricted to declared strict models. (US1)
2. Boundary validator parses top-level and nested snapshot fields, rejecting unknown keys/types at all levels with deterministic ordering if present. (US1, US2)
3. On schema success, system computes digest from the schema-validated projection (not raw payload) and compares against provided digest. (US3)
4. If digest matches, request proceeds unchanged into existing pipeline execution path. (US3, US4)
5. Compatibility tests confirm known producer payload classes validate or fail with deterministic field errors. (US4)

- Failure path A (nested unknown/malformed field):
1. Payload includes undeclared nested key or invalid nested type/value. (US1, US2)
2. Validator returns `MALFORMED_REVIEW_REQUEST` with deterministic `details.field_errors[]` including JSON Pointer paths to nested locations. (US2)

- Failure path B (schema invalid plus digest mismatch candidate):
1. Payload has nested schema errors and a non-matching digest. (US2, US3)
2. Validator returns schema failure only; digest mismatch is intentionally not evaluated until schema success. (US2, US3)

- Failure path C (rollout compatibility break):
1. A current producer payload class contains undeclared nested keys after stricting. (US4)
2. Compatibility fixture test fails and blocks rollout until producer aligns or explicit contract decision is made. (US4)

## 4. Functional Requirements

- FR1 (US1): `ActivatedCallConfigSnapshotV1` nested extension surfaces used by current producers shall be represented by explicit Pydantic models, not loose dict/list-of-dict types.
- FR2 (US1, US2): Unknown nested fields shall be rejected deterministically at every modeled level (`extra="forbid"` equivalent behavior).
- FR3 (US1): Nested strictness shall apply only to active/used extension surfaces in MVP; inactive/deferred surfaces remain out of scope and must not introduce permissive catch-alls.
- FR4 (US2): Nested validation failures shall return `MALFORMED_REVIEW_REQUEST` with stable `details.field_errors[]` entries.
- FR5 (US2): Each `field_errors[]` entry shall include deterministic JSON Pointer `path`, stable `kind`, and stable message template.
- FR6 (US2, US3): Validation precedence shall remain schema-first; digest mismatch evaluation occurs only after full schema success.
- FR7 (US3): Digest input shall be canonicalized from the schema-validated projection to avoid nondeterminism from omitted/default nested fields.
- FR8 (US3): Deterministic digest tests shall prove equivalent semantic payloads (including omitted optional nested defaults) yield stable digest behavior.
- FR9 (US4): A producer compatibility fixture matrix shall cover known payload classes and assert pass/fail expectations deterministically.
- FR10 (US4): Rollout policy for this WF shall require compatibility evidence before strict nested hardening is treated as release-ready.
- FR11 (US1-US4): No call-identity branching or product behavior expansion is allowed in implementation for this WF.
- FR12 (US2, US4): Contract hardening changes shall remain request-boundary only and preserve existing pipeline response contract semantics.

## 5. Data & API Contracts

- C1 (US1, FR1, FR2, FR3): `ReviewRequestV1.call_config_snapshot` remains `ActivatedCallConfigSnapshotV1` with `schema_version: "v1"`; nested active extension surfaces are strict typed models with unknown-field rejection.
- C2 (US2, FR4, FR5): Malformed request contract for nested violations:
  - `error.code = "MALFORMED_REVIEW_REQUEST"`
  - `details.field_errors[]` entries include:
    - `path` (JSON Pointer, nested-capable)
    - `kind` (stable controlled vocabulary)
    - `message` (stable template wording)
  - ordering is deterministic by `path`, then `kind`, then `message`.
- C3 (US2, US3, FR6, FR7): Digest contract:
  - Step 1: strict full schema validation (top-level + nested).
  - Step 2: compute canonical digest from schema-validated projection.
  - Step 3: compare to provided digest and emit `CALL_CONFIG_DIGEST_MISMATCH` only when Step 1 succeeded.
- C4 (US3, FR8): Canonicalization rules for digest determinism:
  - exclude unset optional nested fields from projection.
  - avoid synthetic default injection unless field is explicitly set.
  - ensure deterministic key ordering and serialization.
- C5 (US4, FR9, FR10): Producer compatibility matrix contract:
  - each fixture case includes payload class id, expected outcome (`pass` or deterministic `field_errors`), and rationale.
  - fixture outputs are stable and CI-selectable.

State transitions:
- `received` -> `schema_validated` -> `digest_validated` -> `accepted`
- failure terminals:
  - `failed_contract_malformed` at schema stage
  - `failed_contract_digest` at digest stage

## 6. Components / Modules

- `backend/app/engine/contracts.py`
  - Define strict nested snapshot models and boundary typing surfaces. (FR1-FR3)
- `backend/app/engine/review_request_validator.py`
  - Enforce schema-first ordering, deterministic field errors, and digest checks. (FR4-FR8)
- `backend/tests/engine/` contract tests
  - Validate nested strictness, compatibility fixtures, and digest determinism. (FR8-FR10)

Design tree (dependencies + ordering):
1. Define strict nested models for active surfaces and remove loose nested contract surfaces. (FR1-FR3)
2. Lock deterministic nested error semantics and validation precedence. (FR4-FR7)
3. Add compatibility matrix and digest determinism proofs. (FR8-FR10)
4. Verify scope constraints prevent call-identity/product expansion. (FR11, FR12)

Deep modules:
- Boundary models expose small stable interfaces while hiding nested validation internals.
- Validator exposes stable failure contracts while hiding canonicalization/order mechanics.
- Contract tests serve as executable safety boundary for producer compatibility and rollout readiness.

Suggested file paths (coarse):
- `backend/app/engine/contracts.py`
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`

## 7. Edge Cases

- E1 (US2): Multiple nested unknown fields across different branches return all errors with deterministic global ordering.
- E2 (US2, US3): Nested schema invalid + digest mismatch candidate returns only malformed schema failure due to precedence.
- E3 (US3): Optional nested field omitted vs explicitly set to default does not change digest outcome when semantics are equivalent.
- E4 (US4): Producer payload class with legacy undeclared nested key fails deterministically and is flagged in compatibility matrix.
- E5 (US1, US4): Strict nested models reject accidental call/agency metadata leakage not declared in snapshot schema.

## 8. Testing Decisions (TDD)

- TDD rule: each behavior hardening starts with failing test (RED), minimal implementation (GREEN), then refactor.
- Seam S1 (US1, US2; FR1-FR5): Nested schema strictness tests.
  - prove unknown nested key/type/value rejection with deterministic JSON Pointer paths.
  - no mocking inside schema model validation boundaries.
- Seam S2 (US2, US3; FR6, FR7): Validation precedence + digest gating tests.
  - prove digest mismatch is suppressed when schema invalid.
  - prove digest mismatch triggers only after schema success.
- Seam S3 (US3; FR7, FR8): Digest determinism tests.
  - replay semantically equivalent payloads with omitted/default nested fields and assert deterministic digest behavior.
- Seam S4 (US4; FR9, FR10): Producer compatibility matrix tests.
  - fixture-driven pass/fail expectations for known producer payload classes.
- Seam S5 (US1-US4; FR11, FR12): Scope guard tests.
  - verify request-boundary-only changes do not alter pipeline output contract semantics.

Deterministic selector naming:
- `wf0049_contract_<surface>_<case_id>`

## 9. Telemetry (Minimal)

- Track count of malformed nested schema rejections and digest mismatches by stable code.
- Telemetry is observational only and must not alter response contracts.

## 10. Deferred / Not in MVP

- Snapshot version bump/migration framework (`v1.1+`) unless hard blocker emerges.
- Hardening of inactive nested surfaces not used by current producers.
- Any UI/product expansion beyond contract error consumption.

## 11. Open Questions (if any)

- None blocking for Phase 2 task generation under current Q&A decisions.

## 12. Changelog

- v0.1 (2026-03-04): Initial PRD from brainstorm.
