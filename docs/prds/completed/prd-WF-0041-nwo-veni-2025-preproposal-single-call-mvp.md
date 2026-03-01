# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-01

## 0. User Stories (MVP)

- US1: As an applicant, I want to select `nwo_veni_2025_preproposal` and complete a fully call-driven submit form, so that I can submit without call-specific frontend/backend hardcoding.
- US2: As an applicant, I want deterministic compliance checks to block only enforceable violations and show non-enforceable constraints as informational guidance, so that blocking is honest and predictable.
- US3: As an applicant, I want review results that are traceable to proposal sections and evaluation criteria/elements with call-driven ordering/grouping, so that I can trust and act on feedback.
- US4: As an operator/product owner, I want this delivered as a single-call MVP on the universal engine while preserving existing API semantics/idempotency/review persistence, so that the product remains stable.

## Deferred Stories (Not in MVP)

- DS1: Multi-call product expansion beyond `nwo_veni_2025_preproposal`.
- DS2: Multi-agency abstractions or framework work not required by this call.
- DS3: Iterative revise/resubmit loop UX improvements beyond existing `/app/reviews` history behavior.
- DS4: Heuristic enforcement for non-enforceable constraints (for example, plain-text `max_items` parsing).
- DS5: Assisted extraction and document ingestion (`.docx`/`.pdf`).

## 1. In Scope

- Single-call MVP implementation for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml` only.
- End-to-end universal flow: call selection, call-driven node rendering (arbitrary count), compliance precheck, structured review, and call-driven review detail rendering.
- Removal of per-call maps/branches/constants for labels, ordering, and domain options in frontend/backend.
- Generic contract additions needed for call-driven review detail (`call_id`, `call_code`) and backend-driven domain UX (`domain_options[]`, may be empty).
- Compliance behavior constrained to deterministic enforceable checks (presence + word limits + domain-aware word limits) with informational non-enforceable guidance.
- Preservation of current API error semantics, idempotency behavior, and review persistence/listing in `/app/reviews`.

## 2. Out of Scope

- Any new call as product scope.
- New evaluation logic beyond call-driven universal execution/presentation requirements.
- Changes to external contract semantics for known errors (`DOMAIN_REQUIRED`, `DOMAIN_INVALID`, `UNKNOWN_NODE_ID`, `IDEMPOTENCY_PAYLOAD_MISMATCH`, `QUOTA_EXCEEDED`).
- Review-history feature redesign.
- ERC/MSCA-specific domain concepts or multi-step evaluation gating.

## 3. User / System Flow

### Happy path

1. Operator ingests and activates `nwo_veni_2025_preproposal` from canonical YAML with standard ingestion flow; call becomes selectable in app. (US1, US4)
2. Applicant selects call; submit UI fetches call-driven nodes/metadata and renders all required proposal sections without per-call assumptions on count/order/labels. (US1)
3. If selected call metadata exposes non-empty `domain_options[]`, UI shows domain selector; otherwise it remains hidden. (US1, US2)
4. Applicant fills structured proposal text by node and submits. (US1)
5. Compliance precheck runs deterministic enforceable checks and returns blocking/non-blocking output with clear separation. (US2)
6. On compliant payload, universal structured-review endpoint executes and persists review/cards. (US3, US4)
7. Review detail fetches call-aware data, orders/groups sections by node `order_index`, and shows per-card proposal section + evaluation element + criterion traceability. (US3)
8. Persisted review appears in `/app/reviews` history and remains retrievable. (US4)

### Failure path A — deterministic compliance block

1. Compliance finds enforceable violations (for example missing required content or word-limit violation) and blocks review creation. (US2)
2. UI surfaces blocking issues and keeps non-enforceable constraints informational-only. (US2)
3. Applicant revises input and resubmits. (US2)

### Failure path B — domain input contract error

1. Selected call requires valid domain context for domain-limited checks and payload is missing/invalid domain. (US2)
2. API returns existing domain error semantics (`DOMAIN_REQUIRED` or `DOMAIN_INVALID`) without behavior drift. (US2, US4)
3. UI prompts correction and retry. (US2)

### Failure path C — idempotency mismatch

1. Client retries with same idempotency key but different payload. (US4)
2. API returns unchanged `IDEMPOTENCY_PAYLOAD_MISMATCH`; no duplicate persisted review is created. (US4)
3. User/client resolves conflict and retries with correct key behavior. (US4)

### Failure path D — reviewer policy output block

1. Structured-review output violates reviewer-policy forbidden-term checks during post-validation. (US3, US4)
2. Server performs one retry with stricter instruction while preserving policy enforcement. (US3, US4)
3. If retry still violates policy, request fails with existing failure semantics and no contract drift. (US4)

## 4. Functional Requirements

- FR1 (US1, US4): The shipped MVP must target only `nwo_veni_2025_preproposal` while remaining universal/call-driven (no per-call maps/branches/constants for labels/order/domain options in frontend/backend).
- FR2 (US1): Submit UI must render proposal nodes from backend call data and support arbitrary node counts without code changes.
- FR3 (US1, US2): Domain selector UX must be backend-driven via `domain_options[]`; selector appears only when options are present and may be absent for non-domain calls.
- FR4 (US2): Compliance blocking must remain deterministic and limited to enforceable checks (presence + word limits + domain-aware word limits where defined).
- FR5 (US2): Non-enforceable constraints must be surfaced as informational guidance and never trigger blocking.
- FR6 (US3): Review detail rendering must be fully call-driven and use call node `order_index` for deterministic ordering/grouping.
- FR7 (US3): Review detail cards must visibly include proposal section context plus evaluation element and criterion traceability.
- FR8 (US3, US4): Review detail response contract must include generic `call_id` and `call_code` fields to enable call-driven node lookup/rendering.
- FR9 (US4): Existing API error semantics and idempotency semantics must remain unchanged.
- FR10 (US4): Submission side effects must remain unchanged: successful review execution persists Review records and keeps `/app/reviews` history intact.
- FR11 (US3, US4): Structured-review execution must keep reviewer-policy enforcement and include one server-side retry seam before final failure when forbidden-term policy validation fails.
- FR12 (US1, US2): `domain_options[]` contract must be explicit and stable (per option: machine `value`, human `label`, deterministic `order_index`), and sourced only from backend call metadata/config.
- FR13 (US3): Review detail ordering must be deterministic with explicit fallback rules: primary sort `order_index` ascending, secondary sort `node_logical_id` ascending for ties/nulls.
- FR14 (US4): Review detail must remain backward-compatible for persisted reviews lacking call linkage; API returns graceful nulls/flags and frontend shows stable fallback order without hardcoded call maps.
- FR15 (US4): Frontend/backend rollout must be skew-safe: frontend tolerates absent new fields, backend tolerates optional consumer behavior, and no runtime hard-fail during phased deploy.
- FR16 (US3, US4): Reviewer-policy retry semantics must be bounded and deterministic (max 1 retry, total attempts = 2) with unchanged idempotency and external error semantics.
- FR17 (US2): Informational (non-enforceable) constraints must be surfaced in submit UX in a dedicated non-blocking section distinct from blocking issues.
- FR18 (US1, US4): “No hardcoding anywhere” must be enforced by automated checks/tests that fail on per-call maps/branches/constants in targeted frontend/backend seams.
- FR19 (US1): Universality proof gates are required in tests: one non-Veni structured-call fixture must pass node-count/order/domain-absence behavior checks.

## 5. Data & API Contracts

### 5.1 Call metadata / configuration contract

- Backend call metadata/config endpoint is the sole source for `domain_options` and returns:
  - `domain_options: Array<{ value: string; label: string; order_index: number }>` (may be empty). (US1, US2, FR3, FR12)
  - deterministic ordering by `order_index` then `value`.
- Frontend treats `domain_options` as authoritative for selector visibility/options and must not derive options from call code or local constants. (US1, FR3, FR12, FR18)

### 5.2 Compliance contract

- Request includes selected call context, node payloads keyed by node logical identifiers, and optional domain when applicable. (US1, US2, FR2, FR3, FR4)
- Response distinguishes deterministic blocking findings from informational findings.
- Blocking findings map only to enforceable checks; informational findings include non-enforceable constraints. (US2, FR4, FR5)
- Domain contract errors preserve existing semantics/codes. (US2, US4, FR9)
- Submit UX renders informational findings in a dedicated non-blocking guidance section and never intermixes them with blocking list semantics. (US2, FR17)

### 5.3 Structured review create contract

- Existing create request/response and idempotency behavior remain stable. (US4, FR9)
- On success, review persistence behavior remains stable and history listing remains available in `/app/reviews`. (US4, FR10)
- Reviewer-policy forbidden-term validation remains active with bounded retry policy:
  - maximum one retry per request (two total attempts),
  - same idempotency key/payload context across attempts,
  - unchanged external failure/error semantics if both attempts fail policy validation. (US3, US4, FR11, FR16)

### 5.4 Review detail contract (generic extension)

- `GET /reviews/{review_id}` response adds `call_id` and `call_code` as generic fields. (US3, FR6, FR8)
- Review card payload continues to provide section/evaluation trace fields used by UI (`node_title`, `evaluation_element_name`, `criterion`), with optional stable IDs as informational affordance if present. (US3, FR7)
- Frontend fetches call nodes by `call_id` for deterministic ordering/grouping without hardcoded per-call arrays. (US3, FR6, FR8)
- Deterministic ordering algorithm:
  - primary: node `order_index` ascending,
  - secondary fallback for ties/nulls: `node_logical_id` ascending,
  - unknown/missing node references ordered last by `node_logical_id` ascending and labeled as unmapped. (US3, FR6, FR13)
- Backward compatibility for legacy persisted reviews:
  - if `call_id`/`call_code` unavailable, API returns null plus `ordering_source: "review_payload_fallback"`,
  - UI uses stable in-review payload order fallback and displays non-blocking “call metadata unavailable” note. (US4, FR14, FR15)

### 5.5 State transitions

- `Draft input` -> `Compliance blocked` (no review persisted) when deterministic enforceable checks fail. (US2, FR4)
- `Draft input` -> `Compliance clear` -> `Review created` -> `Review visible in history` on successful execution. (US4, FR10)
- `Retry with same idempotency key + same payload` -> existing result; `same key + different payload` -> `IDEMPOTENCY_PAYLOAD_MISMATCH`. (US4, FR9)
- `Policy post-check fail on attempt 1` -> `retry attempt 2` -> `success` or `terminal failure` with unchanged external semantics. (US4, FR11, FR16)

## 6. Components / Modules

- `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
  - Single-call MVP source of truth for proposal structure, evaluation criteria/elements, and enforceable constraints.
- `backend/scripts/ingest_call.py`
  - Standard ingestion/activation path for canonical call definitions.
- `backend/main.py`
  - Public API seams for compliance, structured review create, and review detail contracts.
- `backend/app/services/compliance_engine.py`
  - Deterministic enforceable compliance checks and non-enforceable informational output separation.
- `backend/app/services/review_execution_core.py`
  - Universal structured review execution path.
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
  - Call-driven submit form rendering, including backend-driven domain UX.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Call-driven review detail grouping/ordering and traceability presentation.

Design tree / ordering:
1. Lock generic contract seams (`domain_options[]` shape, review detail `call_id` + `call_code`, deterministic ordering/fallback rules) and preserve existing semantics. (FR3, FR8, FR9, FR12, FR13)
2. Remove hardcoded frontend/backend call maps/branches and wire call-driven submit/review detail behavior with automated guardrails. (FR1, FR2, FR6, FR7, FR18)
3. Keep compliance honesty contract explicit and stable in API/UI surfaces, including informational guidance rendering. (FR4, FR5, FR17)
4. Implement skew-safe rollout and legacy-data compatibility for review detail. (FR14, FR15)
5. Verify persistence/idempotency/history invariants remain unchanged and reviewer-policy retry remains bounded/deterministic. (FR9, FR10, FR11, FR16)

Deep module seams:
- Compliance engine remains deterministic-check authority with explicit enforceable vs informational partition.
- Review execution core remains universal executor; review detail rendering remains presentation-layer composition over persisted cards + call metadata.

## 7. Edge Cases

- Selected call has empty `domain_options[]`: domain selector is hidden and flow remains valid. (US1, US2, FR3)
- Selected call has non-empty `domain_options[]` and domain omitted/invalid: deterministic domain error semantics are returned with no contract drift. (US2, FR3, FR9)
- Review contains cards referencing nodes while call metadata fetch fails transiently: UI must fail gracefully without falling back to hardcoded call mappings. (US3, FR1, FR6)
- Non-enforceable constraints exist in call definition (for example `max_items`): surfaced as informational only, never blocking. (US2, FR5)
- Repeated submit attempts with idempotency collisions: preserve mismatch semantics and avoid duplicate persistence side effects. (US4, FR9, FR10)
- Reviewer-policy validation fails after retry: response remains deterministic failure with unchanged external semantics and no silent policy bypass. (US4, FR11)
- Multiple nodes share/miss `order_index`: ordering remains deterministic via secondary fallback rule and does not regress into arbitrary UI order. (US3, FR13)
- Legacy persisted review lacks `call_id`: detail page remains viewable with documented fallback ordering and explicit note, no hard failure. (US4, FR14, FR15)
- Frontend deployed before backend contract expansion (or vice versa): no fatal runtime error; feature degrades gracefully until both sides are upgraded. (US4, FR15)

## 8. Testing Decisions (TDD)

- RED/GREEN/REFACTOR required for any behavioral edits affecting contracts, compliance decisions, and call-driven rendering.
- Test seams (public):
  - compliance API behavior for enforceable blocking vs informational-only output. (FR4, FR5)
  - review detail API schema includes `call_id` + `call_code`, deterministic ordering fallback behavior, and preserves existing fields/error semantics. (FR8, FR9, FR13, FR14)
  - submit/review-detail frontend behavior removes call-specific maps and consumes backend-driven metadata for nodes/domain/ordering. (FR1, FR2, FR3, FR6)
  - persistence/idempotency regression tests for structured review create and `/app/reviews` visibility invariants. (FR9, FR10)
  - reviewer-policy retry behavior test that proves one retry occurs and terminal failure semantics stay unchanged when both attempts violate policy. (FR11)
  - skew-compat tests for frontend/backend mixed-version response shapes (with and without new fields) to prove graceful degradation. (FR15)
  - informational-guidance UX test proving non-enforceable constraints are visible but never block submission. (FR17)
  - static/contract guard tests that fail when per-call maps/branches/constants are introduced in protected seams. (FR18)
- Boundary mocking:
  - mock external LLM boundary only; do not mock compliance logic, contract validation ordering, or persistence assertions.
- Universality safety check (tests-only):
  - include at least one existing non-Veni structured call fixture in tests to guard against hidden “3-node/Veni-shaped” assumptions, without expanding product scope.
  - required assertions: arbitrary node-count rendering, deterministic ordering, and absent-domain behavior (no selector when `domain_options[]` empty). (FR2, FR19)

## 9. Telemetry (Minimal)

- Compliance telemetry: counts of blocking vs informational findings by call code.
- Structured review telemetry: success/failure rates and error-code distribution (including preserved contract codes).
- Review detail telemetry: render failures caused by missing call metadata or ordering data.
- Idempotency telemetry: mismatch/error counts to detect regressions in request-key behavior.
- Reviewer-policy telemetry: attempt count per request (`attempt_1`, `attempt_2`) and terminal policy-failure counts.
- Contract-compat telemetry: counts of review-detail responses using fallback `ordering_source`.

## 10. Deferred / Not in MVP

- Multi-call rollout and generalized “framework” abstractions.
- Review-history UX redesign beyond preserving current behavior.
- Heuristic parsing/enforcement of non-deterministic constraints.
- Document-upload ingestion and extraction enhancements.
- Multi-step gating workflows for other funders/programs.

## 11. Open Questions (if any)

- None for MVP; ordering fallback, legacy compatibility, domain contract shape, skew-safe rollout, and retry bounds are fixed in this PRD.

## 12. Changelog

- v0.1 (2026-03-01): Initial PRD from brainstorm SSOT for single-call universal MVP constraints.
- v0.2 (2026-03-01): Applied risk-audit revisions (flow traceability tags, reviewer-policy retry requirement, and aligned contract/edge/test coverage); marked Ready for Tasks.
- v0.3 (2026-03-01): Addressed principal-risk audit gaps by locking domain contract schema, deterministic ordering fallbacks, legacy/skew compatibility, bounded retry semantics, informational UX contract, no-hardcoding enforcement gates, and universality proof requirements.
