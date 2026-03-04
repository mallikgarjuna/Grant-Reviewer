# WF-0048 — Agency/Call Variability Policy Contract PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-04

## 0. User Stories (MVP)

- US1: As a backend engine maintainer, I want the engine boundary to accept only a strict `ActivatedCallConfigSnapshotV1` contract, so that call variability is declared and typed rather than ad-hoc.
- US2: As a frontend/BFF integrator, I want deterministic contract-failure semantics with stable codes and field-path details, so that malformed payloads fail predictably and are easy to fix.
- US3: As a workflow owner, I want deterministic contract tests for success/failure paths, so that identical inputs always produce identical outcomes and regressions are caught early.

## Deferred Stories (Not in MVP)

- DS1: Frontend/BFF refactors beyond consuming the strict boundary and documented errors.
- DS2: Broader review-result DTO redesign unrelated to snapshot-boundary determinism.
- DS3: Call-definition ingestion hardening beyond what is needed for strict request-boundary validation.

## 1. In Scope

- Define and enforce `ActivatedCallConfigSnapshotV1` as a strict, versioned boundary model for `call_config_snapshot`. (US1)
- Enforce strict unknown-field rejection at top-level request and snapshot nested models. (US1, US2)
- Freeze deterministic contract-failure semantics and precedence rules for schema-vs-digest validation. (US2)
- Freeze deterministic field-path format, field-error ordering, and minimum `kind` vocabulary for malformed request errors. (US2)
- Add deterministic contract tests for malformed requests, digest mismatch, and deterministic success serialization. (US3)
- Enforce no call-identity branching in engine behavior for this scope. (US1, US3)
- Enforce implementation task slicing policy: each Phase 3 task slice targets <=3 files; larger work must be split into dependent slices. (US3)

## 2. Out of Scope

- Introducing a generic `extensions: dict` escape hatch in snapshot v1.
- Adding agency/call-code identity conditionals into core execution logic.
- Broad persistence/API/UI contract changes outside request snapshot boundary and deterministic tests.
- Performance optimization or architectural rewrites not required for contract enforcement.

## 3. User / System Flow

- Happy path:
1. Producer submits `ReviewRequestV1` with strict top-level fields and strict `call_config_snapshot` where `schema_version == "v1"`. (US1)
2. Engine performs strict schema validation (top-level and nested snapshot) and rejects any unknown or malformed fields. (US1, US2)
3. Engine canonicalizes validated snapshot JSON and verifies `call_config_digest` equality. (US2)
4. Engine executes pipeline using snapshot-declared variability surfaces only, without call identity branching. (US1, US3)
5. Engine returns deterministic serialized `PipelineResult.to_dict()` for identical validated payloads. (US3)

- Failure path A (schema/shape violation):
1. Request contains unknown field, missing required field, invalid type, or invalid value in top-level request or snapshot subtree. (US2)
2. Engine returns `MALFORMED_REVIEW_REQUEST` with `details.field_errors[]` using JSON Pointer paths and stable ordering. (US2)

- Failure path B (digest mismatch after valid schema):
1. Request passes strict schema validation. (US2)
2. Provided `call_config_digest` differs from digest of canonical JSON from the validated snapshot. (US2)
3. Engine returns `CALL_CONFIG_DIGEST_MISMATCH` deterministically. (US2)

- Failure path C (determinism regression attempt):
1. A change introduces nondeterministic fields or unstable ordering into serialized output. (US3)
2. Deterministic contract tests fail and block merge. (US3)

## 4. Functional Requirements

- FR1 (US1): `ReviewRequestV1.call_config_snapshot` shall be typed as `ActivatedCallConfigSnapshotV1` and not a loose `dict` boundary.
- FR2 (US1, US2): Top-level request model and all `ActivatedCallConfigSnapshotV1` nested models shall reject unknown fields deterministically.
- FR3 (US1): `ActivatedCallConfigSnapshotV1` shall require `schema_version` with value `"v1"`.
- FR4 (US1): `ActivatedCallConfigSnapshotV1` shall require `expectations: list[ActivatedExpectationV1]` and support only declared extension points (stage gating, hierarchy/nesting, evaluation criteria/elements, compliance rules, reviewer-policy, prompt knobs).
- FR5 (US2): Schema validation and unknown-field rejection shall return `MALFORMED_REVIEW_REQUEST` with `details.field_errors[]`.
- FR6 (US2): `details.field_errors[]` shall use JSON Pointer `path` values and stable sort order: `path`, then `kind`, then `message`.
- FR7 (US2): Minimum stable `kind` vocabulary shall be `unknown_field`, `missing_field`, `type_error`, `value_error`.
- FR8 (US2): Validation precedence shall be strict schema validation first, then digest validation; digest mismatch is evaluated only after schema success.
- FR9 (US2): Digest mismatch shall return `CALL_CONFIG_DIGEST_MISMATCH` with deterministic semantics.
- FR10 (US1, US3): Core behavior in this scope shall not branch on call/agency identity; behavior derives from snapshot-declared surfaces only.
- FR11 (US3): Deterministic contract tests shall prove unknown-field rejection, schema-before-digest precedence, and digest mismatch behavior.
- FR12 (US3): Deterministic contract tests shall prove identical validated payloads produce identical canonical `PipelineResult.to_dict()` JSON.
- FR13 (US3): Phase 3 implementation planning shall enforce <=3 files per task slice; if work exceeds 3 files, it must be split into dependent slices with explicit ordering metadata.
- FR14 (US2, US3): `details.field_errors[].message` shall use stable template wording for each `kind` to avoid validator-library wording drift.

## 5. Data & API Contracts

- C1 (US1, FR1, FR3, FR4): `ReviewRequestV1` contract includes required fields:
  - `request_id: str`
  - `mode: "DIAGNOSTIC" | "STRICT"`
  - `stage_ref: str`
  - `call_config_snapshot: ActivatedCallConfigSnapshotV1`
  - `call_config_digest: "sha256:<hex>"`
  - `proposal_nodes: dict[str, str]`
  - unknown top-level fields are rejected.

- C2 (US1, FR3, FR4): `ActivatedCallConfigSnapshotV1` strict contract:
  - `schema_version: "v1"` (required)
  - `expectations: list[ActivatedExpectationV1]` (required)
  - optional strict sub-model surfaces only:
    - `stage_gating`
    - `hierarchy` / `nesting`
    - `evaluation_criteria` / `evaluation_elements`
    - `compliance_rules`
    - `reviewer_policy`
    - `prompt_knobs`
  - unknown fields are rejected at every level.

- C3 (US2, FR5, FR6, FR7, FR14): Malformed request error contract:
  - code: `MALFORMED_REVIEW_REQUEST`
  - payload: `details.field_errors: list[{path, kind, message}]`
  - `path` format: JSON Pointer (example: `/call_config_snapshot/expectations/0/check_id`)
  - order: stable ascending by `path`, then `kind`, then `message`.
  - `message` format: stable templates per `kind`; do not expose raw validator-native strings.

- C4 (US2, FR8, FR9): Validation precedence + digest contract:
  1. Parse + strict schema validation for full request and snapshot.
  2. Only on schema success, compute canonical JSON digest and compare to `call_config_digest`.
  3. On mismatch, return `CALL_CONFIG_DIGEST_MISMATCH`.

- C5 (US3, FR12): Deterministic success contract:
  - same validated request payload yields identical canonical JSON of `PipelineResult.to_dict()`.
  - serialized output must exclude nondeterministic values (e.g., timestamps/random ids) from contract surface.

State transitions:
- `received` -> `schema_validated` -> `digest_validated` -> `executed` -> `serialized`
- failure terminals:
  - `failed_contract_malformed` (at `schema_validated`)
  - `failed_contract_digest` (at `digest_validated`)

## 6. Components / Modules

- `backend/app/engine/contracts.py`
  - Responsibility: define strict typed request/snapshot boundary models and schema constraints. (FR1-FR4)
- `backend/app/engine/review_request_validator.py`
  - Responsibility: enforce validation ordering, deterministic malformed error details, and digest checks. (FR5-FR9)
- `backend/tests/engine/` contract tests
  - Responsibility: prove deterministic failure/success semantics and no regression in ordering/paths. (FR10-FR12)

Design tree (dependencies + ordering):
1. Lock strict boundary model and allowed surfaces. (FR1-FR4)
2. Lock deterministic failure semantics and validation precedence. (FR5-FR9)
3. Lock deterministic tests for failure/success behavior and serialization invariance. (FR10-FR12)
4. Plan implementation slices with <=3 files each and explicit dependencies. (FR13)

Deep modules:
- Boundary contract module: small stable interface; hides strict schema internals.
- Validator module: deterministic normalization/order semantics hidden behind stable error contract.
- Contract test module: public proof surface for deterministic behavior.

Suggested file paths (coarse):
- `backend/app/engine/contracts.py`
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`

Phase 3 slice blueprint (task planning constraints):
- Slice A — strict boundary model:
  - Files (max 3): `backend/app/engine/contracts.py`, `backend/tests/engine/test_review_request_contracts.py`
  - Depends on: none
  - Enables: Slice B
  - Parallelizable: no
- Slice B — validator semantics + deterministic malformed errors:
  - Files (max 3): `backend/app/engine/review_request_validator.py`, `backend/tests/engine/test_review_request_contracts.py`
  - Depends on: Slice A
  - Enables: Slice C
  - Parallelizable: no
- Slice C — deterministic replay/success serialization proofs:
  - Files (max 3): `backend/tests/engine/test_review_request_contracts.py`
  - Depends on: Slice B
  - Enables: downstream hardening WFs
  - Parallelizable: no

## 7. Edge Cases

- E1 (US2): Unknown top-level field and invalid snapshot field both present; response remains `MALFORMED_REVIEW_REQUEST` with all field errors stably ordered.
- E2 (US2): Request has schema violations and wrong digest; digest mismatch is not surfaced because schema-first precedence applies.
- E3 (US2): Multiple field errors at mixed nesting depth; JSON Pointer formatting and sorting remain stable.
- E4 (US3): Same payload replayed repeatedly across runs; serialized output stays byte-stable after canonicalization.
- E5 (US1, US3): Snapshot contains implicit call identity hints; validator treats them as unknown/invalid if not in declared surfaces.

## 8. Testing Decisions (TDD)

- RED-GREEN requirement: every behavior change in boundary contract/validator starts with a failing contract test then minimal implementation fix.
- Seam S1 (US1, US2; FR1-FR7): Request/snapshot strict schema tests.
  - Test unknown fields, required fields, type/value errors, JSON Pointer paths, stable field-error ordering.
  - Mocking: no mocks inside schema/validator logic.
- Seam S2 (US2; FR8, FR9): Validation precedence + digest mismatch tests.
  - Prove schema failure suppresses digest mismatch; prove digest mismatch only after schema success.
- Seam S3 (US1, US3; FR10): No call identity branching regression tests.
  - Prove behavior selection is snapshot-driven, not call/agency-driven.
- Seam S4 (US3; FR11, FR12): Deterministic replay tests.
  - Prove identical payload -> identical canonical `PipelineResult.to_dict()` JSON.

Deterministic selector convention:
- `wf0048_contract_<surface>_<case_id>` for each contract test surface.

## 9. Telemetry (Minimal)

- Emit deterministic contract failure code counts by code (`MALFORMED_REVIEW_REQUEST`, `CALL_CONFIG_DIGEST_MISMATCH`).
- Telemetry must not mutate serialized contract output semantics.

## 10. Deferred / Not in MVP

- Result DTO cleanup beyond deterministic snapshot-boundary contract tests.
- Producer-pipeline hardening beyond required boundary compatibility changes.
- Additional snapshot versions beyond `schema_version: "v1"`.

## 11. Open Questions (if any)

- None blocking for Phase 2 task generation.

## 12. Changelog

- v0.1 (2026-03-04): Initial PRD from brainstorm.
- v0.2 (2026-03-04): Applied risk-audit hardening for stable malformed-message templates, explicit <=3-file Phase 3 task-slice blueprint, and marked Ready for Tasks.
