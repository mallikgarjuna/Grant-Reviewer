<!-- docs/prds/prd-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-06

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher using the ERC proof call, I want to complete and submit a hierarchical proposal flow, so that the product works beyond the Veni-shaped happy path.
- US2: As a researcher reviewing the result, I want review detail ordering, grouping, labels, and coverage to come from the selected call's stored metadata, so that feedback stays traceable to the actual call structure and evaluation criteria/elements.
- US3: As a product owner, I want the hierarchical proof path to preserve current review-create idempotency, persistence, and Veni parity, so that the unblocker does not regress working flows.

## Deferred Stories (Not in MVP)

- DS1: Universal support for every future call shape.
- DS2: Product-wide redesign of submit UX, review history, or review detail beyond what the proof path forces.
- DS3: New import/export, parsing, telemetry redesign, or execution-core redesign work not required by the proof call.
- DS4: Broader multi-call hardening beyond `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`.

## 1. In Scope

- Proof target is locked to `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`.
- Unblock hierarchical submit for the proof call by replacing the current nested-node unsupported path with a functional review-creation path. (US1)
- Ensure review creation succeeds for the proof path through the existing structured-review path (`/api/bff/structured-review` -> `/api/structured-review`) without changing its current idempotency mismatch/error semantics or persistence side effects. (US1, US3)
- Ensure review detail for the proof path derives grouping, ordering, labels, and coverage from stored review/call-linked data rather than `submitted_nodes` query-param fallback. (US2, US3)
- Keep legacy fallback explicit and scoped to older or mixed-version reviews only. (US2, US3)
- Preserve current Veni/flat-call behavior while adding the minimum generic handling the proof call forces. (US1, US3)
- Carry forward the brainstorm execution order: parity/plumbing first, hierarchical submit unblock second, proof-call review-detail flip third, parity verification last. (US1, US2, US3)
- Require automated tests plus one concrete end-to-end proof artifact tied directly to the ERC proof call. (US1, US2, US3)

## 2. Out of Scope

- General platform support for all future hierarchical or multi-step calls. (DS1)
- Architecture-first universal-call refactors not required by the ERC proof path. (DS1, DS4)
- Adjacent submit/review UX redesigns, including review-history redesign, import/export, and parsing workflows. (DS2, DS3)
- Telemetry redesign, policy redesign, or execution-core redesign unless a parity defect in the proof path forces a minimal change. (DS3)

## 3. User / System Flow

### Happy path

1. Researcher selects the ERC proof call `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`; submit flow resolves hierarchical call data instead of stopping on the current nested-node unsupported guardrail. (US1)
2. Submit UI renders the hierarchical proof-call structure in executable order and collects proposal text for the required nodes. (US1)
3. Researcher submits the hierarchical payload through the structured-review path; validation and payload plumbing accept the proof-call structure without changing existing idempotency semantics. (US1, US3)
4. Backend creates and persists the review using the existing review-create path and keeps `/app/reviews` history behavior intact. (US1, US3)
5. Researcher opens review detail; UI/API use stored review data plus call-linked node metadata to derive grouping, ordering, labels, and coverage for the proof call. (US2, US3)
6. Review detail renders explicit traceability to the proof call's sections and evaluation criteria/elements, with no silent fallback to `submitted_nodes` query-param ordering. (US2)

### Failure path A — idempotency replay or mismatch

1. Client retries the proof-call submission with the same idempotency key. (US3)
2. If payload matches, existing replay behavior is preserved; if payload differs, existing mismatch/error semantics remain unchanged. (US3)
3. No duplicate persistence side effects are introduced by hierarchical payload support. (US3)

### Failure path B — validation ordering or nested payload translation defect

1. Hierarchical proof-call payload fails validation or translation during review-create handling. (US1, US3)
2. System returns deterministic existing validation/error behavior rather than passing a malformed nested payload deeper into execution. (US3)
3. Tests must prove validation ordering remains stable for touched seams. (US3)

### Failure path C — legacy review-detail fallback

1. User opens an older or mixed-version review without required call-linked metadata. (US2, US3)
2. Review detail uses an explicit legacy fallback path with visible scoped behavior rather than silently presenting Veni-shaped ordering as if it were proof-call behavior. (US2, US3)
3. Proof-call reviews must never take this fallback path in tests or walkthrough evidence. (US2)

## 4. Functional Requirements

- FR1 (US1): The delivered MVP must be scoped to one proof call only: `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`.
- FR2 (US1): Submit flow must replace the current nested-node unsupported state with a functional hierarchical path for the proof call.
- FR3 (US1, US3): Hierarchical submit support must preserve existing structured-review idempotency replay and payload-mismatch/error semantics.
- FR4 (US1, US3): Successful hierarchical submissions must preserve existing review persistence side effects and `/app/reviews` history visibility.
- FR5 (US2): Proof-path review detail must derive grouping, ordering, labels, and coverage from stored review/call-linked data rather than `submitted_nodes` query-param fallback.
- FR6 (US2, US3): Legacy fallback behavior is allowed only for older or mixed-version reviews and must be explicit in UI/API behavior and tests.
- FR7 (US1, US3): Existing Veni/flat-call behavior must remain unchanged for submit and review detail.
- FR8 (US1, US2, US3): Execution order is mandatory: first no-behavior-change plumbing/parity, then hierarchical submit unblock, then proof-call review-detail flip, then parity verification.
- FR9 (US1, US3): Shared concerns in scope are limited to submit validation/plumbing, review-create contract handling, call-linked review-detail ordering/coverage, and the minimal retry/idempotency path already used by review creation.
- FR10 (US2): Review-detail success for the proof path must include visible traceability to the proof call's actual sections and evaluation criteria/elements.
- FR11 (US1, US3): The workflow must remain stop-safe after each ordered step without leaving Veni behavior degraded.
- FR12 (US1, US2, US3): Closure requires both automated coverage and one concrete end-to-end proof artifact tied directly to the ERC proof call.
- FR13 (US3): Failure modes explicitly called out in the brainstorm must be tested/planned: idempotency replay/mismatch, validation ordering, unsupported nested payload translation, and legacy fallback leakage into the proof path.
- FR14 (US2, US3): Review-detail coverage for the proof path must be derived from persisted submitted-node data or an equivalent persisted review-linked source, not from URL query params or cards-only inference.

## 5. Data & API Contracts

### 5.1 Submit / review-create contract

- Hierarchical proof-call payloads must be accepted through the existing structured-review path (`/api/bff/structured-review` -> `/api/structured-review`) once nested rendering is enabled. (US1, FR2, FR3)
- Existing structured-review request/response and idempotency semantics remain authoritative for replay and payload mismatch handling. (US3, FR3)
- Validation ordering must remain deterministic for hierarchical payloads so malformed nested inputs fail at the intended contract boundary. (US3, FR13)
- Review creation keeps existing persistence and history side effects. (US3, FR4)
- Successful structured review for the proof path must persist the submitted node logical IDs, or an equivalent persisted review-linked coverage source, so review detail can compute reviewed vs not-reviewed sections without URL query params. (US2, US3, FR14)

### 5.2 Review detail contract

- Proof-path review detail uses stored review data plus call-linked metadata already exposed by review detail and call-node seams (`call_id`, `call_code`, ordering metadata, node linkage) as the source of truth. (US2, FR5, FR10)
- Source-of-truth precedence for proof-call reviews is fixed: persisted submitted-node coverage source and stored review node linkage first, fetched call-node metadata second for ordering/labels/grouping enrichment, and never `submitted_nodes` query-param fallback. (US2, FR5, FR10, FR14)
- Grouping, ordering, labels, and coverage must be derived from call-linked data for proof-call reviews. (US2, FR5)
- `submitted_nodes` query-param behavior must not be the source of truth for proof-call review detail. (US2, FR5)
- Legacy or mixed-version reviews may use explicit fallback behavior only when required call-linked metadata is absent; partially mapped proof-call reviews must surface explicit unmapped state instead of silently degrading to legacy ordering. (US2, US3, FR6)

### 5.3 State transitions

- `Hierarchical draft` -> `Review created with persisted submitted-node coverage` -> `Review visible in history` for the proof call when submit and review-create succeed. (US1, US2, US3, FR2, FR4, FR14)
- `Hierarchical draft` -> `Validation failure` when nested payload validation/translation fails before execution. (US3, FR13)
- `Retry with same idempotency key + same payload` -> existing replay result; `same key + different payload` -> existing mismatch/error result. (US3, FR3, FR13)
- `Review detail with call-linked metadata` -> call-aware render; `review detail without call-linked metadata` -> explicit legacy fallback render. (US2, US3, FR5, FR6)

## 6. Components / Modules

- `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
  - Locked proof target and source of structure/evaluation traceability. (FR1, FR10, FR12)
- `frontend/src/lib/submit/renderModel.ts`
  - Current nested-node blocker seam that must stop rejecting the proof call. (FR2, FR8)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
  - Submit UI seam that currently surfaces the unsupported nested state and must support the proof path. (FR2, FR8)
- Review-create backend seams
  - Contract-validation, idempotency, and persistence surfaces that must remain stable while accepting hierarchical payloads. (FR3, FR4, FR9, FR13)
- Structured-review transport seams
  - Actual proof-path submission boundary (`/api/bff/structured-review` -> `/api/structured-review`) whose idempotency and validation behavior must remain stable. (FR3, FR8, FR13)
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Review-detail composition seam that must render the proof path from call-linked metadata and keep legacy fallback explicit. (FR5, FR6, FR7, FR8)
- Existing call-node / review-detail API schemas and services
  - Call-aware metadata source used to order and label proof-call review detail. (FR5, FR10)
- Review persistence / detail contract seams
  - Must expose a persisted submitted-node coverage source for proof-call coverage summaries so nodes with zero emitted cards do not disappear from coverage accounting. (FR14)

Design tree / dependencies / ordering:
1. Confirm no-behavior-change plumbing and parity seams needed for hierarchical payload acceptance while preserving Veni behavior. (FR7, FR8, FR11)
2. Unblock hierarchical submit at the renderer/UI boundary for the ERC proof call. (FR2, FR8)
3. Preserve structured-review invariants: validation ordering, idempotency, retry, persistence, and history. (FR3, FR4, FR9, FR13)
4. Persist proof-path submitted-node coverage data and flip review detail fully onto review-linked/call-linked ordering, grouping, and coverage sources. (FR5, FR6, FR10, FR14)
5. Prove parity plus end-to-end closure with automated tests and one concrete evidence artifact. (FR7, FR12, FR13, FR14)

Deep module guidance:
- Reuse existing generic seams where they already exist; do not introduce a separate proof-call-only product path.
- Keep public seams small and stable: submit rendering/modeling, review-create contract handling, and review-detail composition over persisted review data plus call metadata.

Suggested file-path clusters (coarse only):
- submit rendering/UI seams under `frontend/src/lib/submit/` and `frontend/src/components/submit/`
- review detail seam under `frontend/src/app/app/reviews/[reviewId]/`
- review-create and review-detail contract seams under `backend/app/`

## 7. Edge Cases

- Proof-call hierarchy contains nested sections that previously triggered `nested_nodes`; submit must now remain operable. (US1, FR2)
- Hierarchical payload reaches review-create with malformed nested structure; validation ordering must fail deterministically and preserve existing semantics. (US3, FR13)
- Same idempotency key is replayed with matching vs mismatching hierarchical payloads; behavior must remain unchanged. (US3, FR3, FR13)
- Proof-call node submits successfully but produces zero review cards because it has no assessable expectations; coverage summary must still show that node as reviewed from persisted coverage data. (US2, US3, FR14)
- Proof-call review detail encounters missing or unmapped node linkage; grouping/coverage behavior must remain explicit and traceable rather than silently flattening into Veni-shaped output. (US2, FR5, FR10, FR13)
- Legacy/mixed-version reviews lacking call-linked metadata must use explicit fallback behavior without leaking into proof-call tests or walkthrough evidence. (US2, US3, FR6, FR13)
- Veni/flat-call submit and review-detail behavior must remain stable while the proof call is unblocked. (US1, US3, FR7)

## 8. Testing Decisions (TDD)

- Behavior changes in this WF require RED -> GREEN -> REFACTOR.
- Public test seams:
  - hierarchical submit path from proof-call input to successful review creation. (FR2, FR3, FR4, FR12)
  - proof-call review-detail path using call-linked grouping, ordering, labels, and coverage rather than `submitted_nodes` fallback. (FR5, FR10, FR12)
  - Veni/flat-call regression coverage for submit and review detail. (FR7, FR12)
  - failure-mode parity coverage for idempotency replay/mismatch, validation ordering, unsupported nested payload translation, and legacy fallback explicitness. (FR3, FR6, FR13)
  - explicit review-detail degradation coverage proving missing or partially unmapped call-linked metadata produces visible unmapped state for the proof call and only older/mixed-version reviews use legacy fallback. (FR5, FR6, FR13)
  - persisted coverage-source coverage proving nodes submitted through structured review still appear as reviewed even when they emit zero cards. (FR14)
- Boundary mocking:
  - mock only external boundaries where necessary; do not mock the contract logic that proves submit acceptance, review-create invariants, or review-detail ordering behavior.
- Proof obligation:
  - one concrete end-to-end evidence artifact must be produced for `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`; automated tests alone are insufficient. (FR12)
  - required evidence contents: selected proof-call identity, successful submit/review-create result, and review-detail output showing call-aware grouping/ordering/traceability for the same review. (FR12)
- Verification posture:
  - prove the integrated proof path early to expose downstream runtime/contract mismatches rather than trusting isolated unit coverage. (FR8, FR12)

## 9. Telemetry (Minimal)

- Minimal instrumentation only if required to debug proof-path failures without expanding scope.
- Any touched telemetry should distinguish proof-call review-create success/failure, explicit legacy fallback usage, and parity-relevant idempotency/validation failures.
- Telemetry redesign is not part of MVP. (DS3)

## 10. Deferred / Not in MVP

- Generalized support for all hierarchical calls or future multi-step evaluation flows.
- Product-wide review-detail or submit UX redesign beyond proof-path forcing changes.
- Broader platform abstractions, execution-core redesign, or telemetry redesign.
- Import/export and parsing workflows.

## 11. Open Questions (if any)

- None blocking for Phase 1 PRD; scope, proof target, invariants, execution order, proof seams, and closure evidence minimums are locked from the finalized brainstorm.

## 12. Changelog

- v0.1 (2026-03-06): Initial PRD from finalized brainstorm for the ERC hierarchical proof path.
- v0.2 (2026-03-06): Applied risk-audit edits for proof-artifact minimums and explicit review-detail source/fallback precedence; marked Ready for Tasks.
- v0.3 (2026-03-06): Adversarial audit revision: aligned the PRD to the actual structured-review boundary and required persisted submitted-node coverage data for proof-path review detail.
