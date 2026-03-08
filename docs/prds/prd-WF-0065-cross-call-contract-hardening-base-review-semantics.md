<!-- docs/prds/prd-WF-0065-cross-call-contract-hardening-base-review-semantics.md -->
# WF-0065 — Cross-Call Contract Hardening of Base Review Semantics

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-08

Type: feature

## 0. User Stories (MVP)

- US1: As a release owner, I want deterministic proof that the same base review contract semantics hold across one representative NWO, ERC, and MSCA call, so that launch trust does not depend on single-call slices.
- US2: As an engineer maintaining review creation boundaries, I want the real runtime seams for `POST /reviews` (`ReviewerService.generate_review`) and `POST /api/structured-review` (`StructuredReviewerService.generate_structured_review_pipeline_v1` plus `pipeline_v1`) to preserve paired semantic parity wherever the overlapping base-review contract surface exists, so that endpoint or service drift cannot hide fail-open behavior.
- US3: As a maintainer responsible for fail-closed safety, I want `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` proven as gate outcomes with no execution or persistence side effects, so that blocked requests cannot partially create reviews.
- US4: As a planner preparing Phase 2 tasks, I want the exact MVP proof set, parity assertions, and excluded scope written explicitly, so that implementation does not widen into supporting-context semantics, new-call onboarding, or redesign.

## Deferred Stories (Not in MVP)

- DS1: Add new supported calls, new family representatives, or broad promised-program expansion beyond the locked 3-call proof set.
- DS2: Redesign endpoint DTOs, routing, persistence models, or the broader review architecture.
- DS3: Expand supporting-context semantics or reopen WF-0063/WF-0064 hierarchical-submit behavior.
- DS4: Build a generalized new-call onboarding framework or unrelated cross-call test platform.

## 1. In Scope

- Lock the representative proof set to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. (US1, US4)
- Prove base-review semantic parity across the two real runtime paths: `POST /reviews` with `ReviewerService.generate_review`, and `POST /api/structured-review` with `StructuredReviewerService.generate_structured_review_pipeline_v1` plus the underlying `pipeline_v1` execution seam, limited to the overlapping contract surface each endpoint actually exposes today. (US1, US2)
- Cover deterministic success-path semantics plus fail-closed gate semantics for `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`. (US1, US2, US3)
- Assert the required parity dimensions: review status class, stable error-code/details shape, validation/gating order, idempotency replay behavior, idempotency payload-mismatch behavior, and no-persistence/no-execution guarantees for blocked paths. (US1, US2, US3)
- Allow only minimal seam-hardening changes needed to prove the contract, including replacing synthetic proof paths with real-call representative fixtures/helpers where current tests cannot support the locked proof set. (US1, US2, US4)

## 2. Out of Scope

- Supporting-context request semantics, supporting-node participation semantics, or any expansion of WF-0063/WF-0064 behavior. (DS3)
- New call onboarding, widening beyond one representative per active family, or broad family-wide variance studies unless a Phase 1 blocker is explicitly logged first. (DS1, DS4)
- Endpoint unification, routing flips, DTO convergence, persistence rewrites, or broad service/repository redesign. (DS2)
- Performance work, telemetry overhauls, or unrelated cleanup that is not required to prove the locked contract semantics. (DS2, DS4)

## 3. User / System Flow

### Happy path

1. The maintainer selects the locked representative calls `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025` as the only cross-call MVP proof set. (US1, US4)
2. Deterministic tests exercise the path-specific service seams for the same base-review success case on each representative call: `ReviewerService.generate_review` for `/reviews`, and `StructuredReviewerService.generate_structured_review_pipeline_v1` plus `pipeline_v1` for `/api/structured-review`, using real supported call artifacts rather than synthetic stand-ins wherever parity evidence is claimed. (US1, US2, US4)
3. Deterministic endpoint tests exercise `POST /reviews` and `POST /api/structured-review` only where the overlapping base-review contract surface exists for the representative call/boundary case, while preserving each endpoint's existing request shape. (US1, US2)
4. Success-path assertions confirm that review creation semantics remain consistent across calls for status class, returned contract shape, and persistence behavior. (US1, US2)
5. Gate-path assertions confirm that `REVIEWS_DISABLED` and `QUOTA_EXCEEDED` stop the request at the API boundary, return stable existing error semantics, and prevent downstream review creation, `ReviewerService.generate_review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, `pipeline_v1` execution, and partial persisted review state. (US1, US2, US3)
6. Idempotency assertions confirm replay preserves the original review without creating a second row and payload mismatch preserves the existing conflict semantics without mutating persisted state. (US1, US2, US3)
7. The evidence bundle is accepted only if all locked parity assertions hold across the representative calls without widening into supporting-context or onboarding work. (US1, US3, US4)

### Failure path A — synthetic or single-call evidence is counted as cross-call proof

1. A test path still proves one family using synthetic seeded data instead of the locked representative call artifact. (US1, US4)
2. The workflow would overstate cross-call trust because one family is not covered by real representative semantics. (US1, US4)
3. The proof remains incomplete until the synthetic seam is replaced or supplemented with a real-call representative seam for the locked call code. (US1, US4)

### Failure path B — gate response returns but execution still leaks

1. `QUOTA_EXCEEDED` or `REVIEWS_DISABLED` returns the expected HTTP/error payload at an endpoint boundary. (US2, US3)
2. A hidden downstream service or pipeline path still executes, creates a review row, or mutates persisted state. (US2, US3)
3. The workflow fails because gate proof requires both returned semantics and explicit absence of execution/persistence side effects. (US2, US3)

### Failure path C — endpoint/service semantics drift across calls or surfaces

1. One representative call or one boundary surface diverges on status class, error details shape, validation-before-idempotency ordering, replay semantics, or conflict semantics. (US1, US2)
2. The contract is no longer dependable across calls even if individual tests remain green on narrower expectations. (US1, US2)
3. The workflow remains open until the semantic drift is either corrected or explicitly documented as a blocker for the locked proof set. (US1, US2, US4)

## 4. Functional Requirements

- FR1 (US1, US4): The MVP representative proof set must be exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- FR2 (US1, US2): Phase 2 tasks must cover the paired proof boundaries `POST /reviews` with `ReviewerService.generate_review`, and `POST /api/structured-review` with `StructuredReviewerService.generate_structured_review_pipeline_v1` plus the `pipeline_v1` execution seam, with endpoint assertions scoped to the overlapping base-review contract surface each endpoint actually exposes.
- FR3 (US1, US2): Cross-call proof must assert semantic parity, not just severity parity, for success and failure cases.
- FR4 (US1, US2, US3): Required parity assertions must include review status class, stable error codes, stable error details shape, validation/gating order, idempotency replay behavior, idempotency payload-mismatch conflict behavior, and execution/persistence side effects.
- FR5 (US2, US3): `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` must be proven at the API entry boundary with explicit no-execution and no-persistence guarantees for both downstream service paths.
- FR6 (US2, US3): For blocked gate outcomes, no review row, no partial persisted review state, and no downstream `ReviewerService.generate_review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, or `pipeline_v1` execution may occur.
- FR7 (US1, US2): Existing external endpoint contracts may keep distinct request DTOs, and parity is required only for overlapping semantics that both `/reviews` and `/api/structured-review` actually expose today.
- FR8 (US1, US2, US4): If current tests rely on synthetic seeded paths for a locked representative family, the workflow must introduce only the minimum real-call seam needed before that family can count toward parity evidence.
- FR9 (US1, US4): `nwo_veni_2025_preproposal` is the locked NWO representative call for MVP, even though the current API proof path still relies on a synthetic seed; Phase 2 must close that evidence gap without widening to additional NWO calls unless a blocker is documented.
- FR10 (US1, US4): `erc_stg_2026_full` is the locked ERC representative call for MVP because it already has real-call API/service proof seams in repo tests and corrected base-review contract semantics from prior workflows.
- FR11 (US1, US4): `MSCA-PF-2025` is the locked MSCA representative call for MVP and must preserve the existing fail-closed supporting-node baseline while this workflow focuses only on base-review semantics.
- FR12 (US1, US4): The workflow must stay evidence-first; any shared-core extraction or seam creation must remain subordinate to proving the locked semantics and must not force endpoint DTO convergence or broad redesign.
- FR13 (US4): Supporting-context semantics, new-call onboarding, and broader redesign must remain explicit non-goals in all downstream planning.
- FR14 (US1, US2, US3): If the locked 3-call proof set is found insufficient to expose a material semantic variance, the workflow must log a blocker and rationale before widening call coverage.

## 5. Data & API Contracts

### 5.1 Representative proof-set contract

- The locked representative calls are:
  - `nwo_veni_2025_preproposal`
  - `erc_stg_2026_full`
  - `MSCA-PF-2025`
  These are the only calls whose cross-call evidence counts toward MVP closure. (US1, US4, FR1, FR9, FR10, FR11)
- `nwo_veni_2025_preproposal` currently has canonical call data and seeded API/service paths, but Phase 2 must promote it to a real-call representative seam before NWO evidence can count as closed. (US1, US4, FR8, FR9)
- `erc_stg_2026_full` and `MSCA-PF-2025` already have real-call helper/seam coverage in current API tests and therefore anchor the initial parity shape for Phase 2 planning. (US1, US4, FR10, FR11)

### 5.2 Endpoint semantic parity contract

- `POST /reviews` and `POST /api/structured-review` may keep different request payload shapes and different request-building helpers. (US2, FR7)
- For overlapping create-review semantics that both endpoints actually expose today, `/reviews` and `/api/structured-review` must preserve explicit parity on:
  - success-path review status class and response contract shape,
  - validation-before-idempotency ordering,
  - idempotency replay behavior,
  - idempotency payload-mismatch conflict behavior,
  - `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` gate semantics,
  - persistence/no-persistence side effects. (US1, US2, US3, FR3, FR4, FR5, FR6, FR7)
- Cross-endpoint parity does not require DTO unification; it requires semantic equivalence wherever the contract overlaps. (US2, FR7, FR12)

### 5.3 Service and engine parity contract

- `ReviewerService.generate_review` is the service-level proof seam for the single-node `/reviews` runtime path. (US2, FR2)
- `StructuredReviewerService.generate_structured_review_pipeline_v1` is the service-level proof seam for the structured `/api/structured-review` runtime path. (US2, FR2)
- `pipeline_v1` is the underlying execution seam used to prove that structured endpoint/service parity is not masking internal fail-open drift. (US2, US3, FR2, FR5, FR6)
- Service/engine proof must cover the same representative-call matrix and must include at least one deterministic success case per representative call plus fail-closed gate assertions showing the API boundary stops before either service path or `pipeline_v1` is entered. (US1, US2, US3, FR2, FR4, FR5, FR6)

### 5.4 Fail-closed gate contract

- `QUOTA_EXCEEDED` preserves the current HTTP 429 class and stable error-code semantics; the proof must also show zero review creation, zero partial persistence, and zero pipeline execution under the blocked request. (US2, US3, FR4, FR5, FR6)
- `REVIEWS_DISABLED` preserves the current HTTP 503 class and stable error-code semantics; the proof must also show zero review creation, zero partial persistence, and zero pipeline execution under the blocked request. (US2, US3, FR4, FR5, FR6)
- Gate proof must be explicit at API entry boundaries and cannot be inferred from boundary payloads alone; it must also show neither downstream service seam was entered. (US2, US3, FR5, FR6)

### 5.5 Idempotency and persistence contract

- Replay of the same idempotency key and same payload must preserve the original review outcome without creating a second review row. (US2, US3, FR4)
- Reuse of the same idempotency key with a mismatched payload must preserve the current conflict semantics without mutating the original persisted review. (US2, US3, FR4)
- Validation and named gate checks must preserve their existing ordering relative to idempotency on each in-scope endpoint. (US2, FR4)

## 6. Components / Modules

- `backend/tests/test_api.py`
  - Main endpoint parity surface for `POST /reviews` and `POST /api/structured-review`, including gate, idempotency, and persistence assertions only where their overlapping base-review contract surface exists. (FR2, FR4-FR9)
- `backend/app/services/reviewer_service.py` and single-node service tests
  - Single-node service parity surface for `ReviewerService.generate_review` on the locked representative calls used by `/reviews`. (FR2-FR6)
- `backend/tests/test_structured_reviewer_service.py`
  - Service-level parity surface for `StructuredReviewerService.generate_structured_review_pipeline_v1` on the locked representative calls. (FR2, FR4, FR8-FR11)
- `backend/tests/engine/` and existing `pipeline_v1` contract/stress tests
  - Engine seam for proving that cross-call parity is not hiding internal execution drift. (FR2-FR6)
- Existing canonical call YAML and ingest paths under `backend/data/calls/canonical/` and `backend/scripts/ingest_call.py`
  - Source of real-call representative fixtures/helpers; Phase 2 should reuse these instead of inventing a new onboarding path. (FR1, FR8-FR11)
- `backend/main.py`
  - Public API boundary that must retain current error/status semantics while exposing no fail-open behavior behind the gate. (FR2, FR4-FR7)
- Minimal shared test helpers/selectors if needed
  - Allowed only to remove synthetic proof gaps or reduce duplicated semantic assertions; they must not force DTO convergence or redesign runtime architecture. (FR8, FR12)

Design tree / dependencies / ordering:
1. Freeze the exact proof set and parity dimensions so Phase 2 cannot widen scope implicitly. (FR1, FR3, FR4, FR9-FR14)
2. Close the current NWO evidence gap by replacing or supplementing the synthetic API/service path with a real-call representative seam for `nwo_veni_2025_preproposal`. (FR8, FR9)
3. Align representative-call success-path assertions across endpoint, single-node service, structured service, and engine seams. (FR2-FR4, FR10, FR11)
4. Align fail-closed gate assertions for `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, including no-execution/no-persistence checks for both service paths and the structured engine seam. (FR4-FR6)
5. Align idempotency replay and mismatch assertions across the in-scope endpoint surfaces. (FR4, FR7)
6. Add minimal shared helpers only where needed to keep parity assertions explicit and deterministic. (FR8, FR12)

Deep module guidance:

- Keep the proof surface small and explicit: one representative call per active family, two endpoint seams, two service seams, and one structured engine seam.
- Treat synthetic-vs-real representative evidence as a contract issue, not just a test-style issue.
- Treat no-execution/no-persistence proof as mandatory for fail-closed claims.
- Keep `/reviews` and `/api/structured-review` semantically aligned only on overlapping exposed semantics and without forcing request-shape unification.
- Reuse existing canonical call artifacts and test helpers where possible; do not build a broad new harness unless the current seams cannot prove the locked contract.
- If a minimal shared seam is needed, land it under no-behavior-change parity tests first.

Suggested file-path clusters (coarse only):

- API/service/engine parity tests under `backend/tests/`
- representative call fixtures under `backend/data/calls/canonical/`
- endpoint/service boundary logic under `backend/main.py` and `backend/app/services/`

## 7. Edge Cases

- A representative family passes because the test path still uses a seeded graph that shares call code but not the real canonical artifact; this does not count as closed evidence. (US1, US4, FR8, FR9)
- `POST /reviews` and `POST /api/structured-review` return matching statuses but diverge on error `details` shape or idempotency ordering; this is semantic drift, not acceptable variation. (US1, US2, FR3, FR4, FR7)
- A gate blocks response creation but a partially persisted review row remains in storage; fail-closed proof is invalid. (US2, US3, FR5, FR6)
- Pipeline execution is skipped on one endpoint but still enters `pipeline_v1` through another path for the same blocked condition; paired-boundary proof fails. (US2, US3, FR2, FR5, FR6)
- The team widens to `erc_cog_2026_full`, `nwo_vidi_2025_full_proposal`, or other calls without first documenting why the locked representative set is insufficient; this is scope drift. (US4, FR13, FR14)
- A new shared test/helper seam quietly changes endpoint behavior while trying to reduce duplication; parity tests must prove no behavior change before that helper can count toward evidence. (US2, US4, FR8, FR12)

## 8. Testing Decisions (TDD)

- This WF is a behavior-hardening workflow. Phase 3 implementation must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public seams under test must be:
  - `POST /reviews` where the overlapping contract surface exists
  - `POST /api/structured-review` where the overlapping contract surface exists
  - `ReviewerService.generate_review`
  - `StructuredReviewerService.generate_structured_review_pipeline_v1`
  - `pipeline_v1` contract/stress seams (US1, US2, FR2)
- Mock only external boundaries such as quota sources, policy toggles, or LLM edges. Do not mock the create-review, idempotency, gate-ordering, or persistence logic being proven. (US2, US3, FR4-FR6)
- Required automated coverage:
  - representative-call success-path parity tests for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025` across the single-node service seam, structured service seam, and structured engine seam wherever that runtime path exists. (US1, US2, FR1-FR4, FR9-FR11)
  - endpoint parity tests proving overlapping create-review semantics only where both `POST /reviews` and `POST /api/structured-review` expose that contract today. (US1, US2, FR2-FR4, FR7)
  - fail-closed tests for `QUOTA_EXCEEDED` proving stable error semantics plus zero review creation, zero partial persistence, and zero pipeline execution. (US2, US3, FR4-FR6)
  - fail-closed tests for `REVIEWS_DISABLED` proving stable error semantics plus zero review creation, zero partial persistence, and zero pipeline execution. (US2, US3, FR4-FR6)
  - idempotency replay tests proving no duplicate review creation. (US2, US3, FR4)
  - idempotency mismatch tests proving existing conflict semantics with no mutation of persisted state. (US2, US3, FR4)
  - NWO representative proof-seam test coverage proving `nwo_veni_2025_preproposal` evidence is grounded in the real canonical call artifact before NWO parity is marked complete. (US1, US4, FR8, FR9)

## 8.1 Readiness Gate

- No `Ready for Implementation` recommendation is valid unless every required parity assertion in Section 8 has an explicit planned test seam and no unresolved blocker remains on representative-call coverage.
- No implementation-complete or ship recommendation is valid without passing evidence for every required automated check, zero unresolved blocking findings, and closure of non-blocking findings unless explicitly rejected with rationale.
- If the locked 3-call proof set becomes insufficient during implementation, the workflow must stop, log the blocker, and obtain an explicit rescoping decision before widening call coverage.

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- One narrow diagnostic hook is acceptable only if needed to prove that blocked requests did not enter `pipeline_v1` or persist a review row, and only if existing test seams cannot show that deterministically.

## 10. Deferred / Not in MVP

- Cross-call proof for additional ERC or NWO representatives beyond the locked one-per-family set.
- Supporting-context semantics, hierarchical submit expansion, or supporting-node review participation.
- Endpoint deprecation work, routing unification, or DTO redesign.
- Generalized onboarding/testing infrastructure whose value is broader than the locked proof contract.

## 11. Open Questions (if any)

- None at PRD level. The NWO real-call proof seam is an in-scope implementation requirement, not an open scope question.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
- v0.2 (2026-03-08): Applied risk-audit edits to fail-close endpoint parity scope around overlapping exposed contract surfaces and marked Ready for Tasks.
- v0.3 (2026-03-08): Corrected Phase 1 runtime-path contracts so `/reviews` maps to `ReviewerService.generate_review` and gate proofs attach to the API boundary with downstream non-invocation checks.
