<!-- docs/prds/prd-WF-0070-erc-structured-review-step-gating.md -->
# WF-0070 — ERC Structured Review: Enforce Step 1 vs Step 2 Evaluation Gating

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-09

Type: feature

## 0. User Stories (MVP)

- US1: As an ERC researcher submitting a structured review, I want Step 1 and Step 2 to expose only the officially allowed proposal surfaces, so that I cannot accidentally submit or evaluate the wrong stage content.
- US2: As a researcher trusting a completed ERC review, I want the executed review stage and in-scope review surfaces to be inspectable in persisted review data and review detail, so that I can verify what was and was not evaluated.
- US3: As a maintainer hardening the ERC structured-review path, I want one authoritative stage-truth source to drive UI visibility, BFF/backend validation, runtime activation, and evidence projection, so that stage semantics cannot drift across layers.
- US4: As a release owner closing the ERC trust gap, I want fail-closed validation ordering and proof-backed runtime activation with no idempotency or payload-hash regressions, so that readiness claims are defensible.

## Deferred Stories (Not in MVP)

- DS1: Align the single-node `POST /api/reviews` path to the same ERC stage contract only if a later blocker proves the structured ERC trust claim cannot remain honest without it.
- DS2: Broaden staged-review support beyond the locked ERC structured-review path.
- DS3: Add prompt, extraction, supporting-context, or generalized provenance features beyond the minimum trust-closure evidence.
- DS4: Rework compliance messaging unless Phase 2 proves it is required to keep structured ERC stage truth honest.

## 1. In Scope

- Establish one authoritative ERC stage-truth source in canonical ERC call configuration for the structured-review path, and require every downstream stage-aware surface to derive from it. (US1, US2, US3)
- Enforce explicit Step 1 vs Step 2 selection/routing on the ERC structured-review path with fail-closed rejection of invalid stages and out-of-stage submitted nodes. (US1, US3, US4)
- Stage-scope runtime activation so execution cannot evaluate Step 2-only ERC surfaces or expectations during Step 1. (US1, US3, US4)
- Extend existing persisted structured payload coverage and review-detail boundary projection so the completed review makes stage-scoped coverage inspectable. (US2, US3, US4)
- Preserve deterministic structured-review boundary behavior for `Idempotency-Key`, payload-hash conflict handling, and validation-before-execution guarantees while tightening stage validation. (US3, US4)
- Lock the minimum verification matrix for this trust-closure slice and keep Phase 2 scoped to the seams required to satisfy it. (US2, US4)

## 2. Out of Scope

- Prompt tuning, extraction, hierarchy-navigation redesign, or supporting-context semantic expansion not strictly required for ERC stage truth. (DS2, DS3)
- New agencies, broader multi-call stage frameworks, or generic evaluator specialization. (DS2)
- Single-node review-path alignment unless Phase 2 proves the structured-review trust claim cannot remain honest without it. (DS1)
- Review-detail polish or explanatory UX beyond the minimum stage-scope evidence needed for trust closure. (DS3)
- Compliance-surface expansion unless stage-scoped compliance output is proven necessary to avoid wrong-stage messaging on the structured ERC path. (DS4)

## 3. User / System Flow

### Happy path

1. The researcher selects ERC Step 1 or Step 2 in the structured-review submit flow, and the request carries an explicit `review_stage` value instead of relying on implicit defaults. (US1, US3)
2. The frontend/BFF obtains the stage-aware ERC submission surface from the authoritative stage-truth source and only presents the leaf nodes allowed for the selected stage. (US1, US3)
3. The BFF rejects any invalid `review_stage` value fail-closed instead of coercing it to `STEP_1`, preserving the original request meaning. (US1, US4)
4. The backend validates the explicit stage and the submitted ERC leaf ids against the same authoritative stage-truth source before any runtime execution or persistence side effects occur. (US1, US3, US4)
5. The structured-review service derives a stage-scoped runtime snapshot from the authoritative source, intersects it with the submitted eligible leaves, and activates only the expectations in scope for that stage before pipeline execution begins. (US1, US3, US4)
6. The completed review persists explicit stage-scoped coverage evidence using the existing structured payload seam plus any minimal derived field required to reconstruct the activated ERC surface set honestly. (US2, US3)
7. Review detail projects stage-aware boundary buckets so Step 2-only ERC surfaces appear as out of scope during Step 1 rather than merely `not reviewed`. (US2, US4)
8. Readiness is claimed only after the locked verification matrix proves Step 1 prevention, Step 2 correctness, invalid-stage rejection, idempotency/payload-hash parity, and inspectable review evidence. (US2, US4)

### Failure path A — invalid stage value is coerced or normalized

1. The submit path receives an unsupported `review_stage` value or omits a required explicit stage. (US1, US4)
2. Any coercion to `STEP_1` or other fallback would change request meaning silently and weaken trust. (US1, US4)
3. The workflow remains blocked unless the boundary fails closed with an explicit validation error and no execution or persistence side effects. (US1, US4)

### Failure path B — visible/submittable surface and runtime activation drift apart

1. A researcher submits only Step 1-visible nodes, but runtime still activates Step 2-only ERC expectations or surfaces because execution derives scope from a different source. (US1, US3, US4)
2. The resulting review is not trustworthy even if the UI appeared correct. (US1, US2, US4)
3. The workflow remains blocked until runtime activation is derived from the same authoritative stage-truth source as UI visibility and request validation. (US1, US3, US4)

### Failure path C — review evidence is truthful about stage selection but not about stage scope

1. The persisted review stores `review_stage`, but review detail still labels Step 2-only ERC surfaces as `not reviewed` rather than out of scope for a Step 1 review. (US2, US4)
2. The researcher cannot verify which ERC surfaces were actually eligible and activated. (US2)
3. The workflow remains blocked until stage-aware boundary evidence distinguishes out-of-scope surfaces from in-scope-but-not-reviewed surfaces. (US2, US4)

## 4. Functional Requirements

- FR1 (US1, US3): The ERC structured-review path must require an explicit `review_stage` selection for Step 1 vs Step 2 and must not rely on hidden defaults or coercion.
- FR2 (US1, US3): The authoritative stage-truth source for ERC structured review is an authored proposal-surface stage-scope contract in the canonical ERC call definition, and all secondary stage-aware representations must be derived from it rather than authored independently.
- FR3 (US1, US3): The authoritative stage-truth source must resolve the current `b2_part2_scientific_proposal` drift explicitly so Step 2-only ERC surfaces are no longer treated as `BOTH` by default.
- FR4 (US1, US3, US4): The frontend and BFF must fail closed on invalid or unsupported `review_stage` values and must not normalize them to `STEP_1`.
- FR5 (US1, US3, US4): Backend request validation must reject submitted ERC leaf ids that are not allowed for the chosen stage before runtime execution begins, and the error must identify the offending node ids explicitly.
- FR6 (US1, US3, US4): Stage/node mismatch handling must preserve existing structured-review determinism: no silent dropping, no fallback rerouting, and no post-persistence failure behavior.
- FR7 (US1, US3, US4): Structured-review runtime must derive a stage-scoped active expectation set from the authoritative stage-truth source before evaluation, so Step 1 execution cannot activate Step 2-only ERC expectations or surfaces.
- FR8 (US3, US4): The implementation seam for stage-scoped execution must remain localized to configuration and activation boundaries; evaluator/pipeline internals must stay call-agnostic unless Phase 2 logs a blocker proving otherwise.
- FR9 (US2, US3): The completed review must persist enough stage-scoped coverage evidence to reconstruct the activated ERC surface set honestly; `review_stage` alone is insufficient.
- FR10 (US2, US3): Persisted structured-review evidence must extend existing `structured_payload.review_stage` and `structured_payload.submitted_leaf_ids` with one derived review-time stage-scope snapshot field capturing the in-scope ERC leaf set used for the completed review, and review-detail boundary buckets must be projected from that persisted evidence.
- FR11 (US2, US4): Review detail must project stage-aware boundary states that distinguish:
  - reviewed in-scope ERC surfaces,
  - visible/submitted but not reviewed in-scope ERC surfaces where applicable,
  - out-of-scope ERC surfaces for the selected stage.
- FR12 (US2, US4): Step 1 review detail must never imply that Step 2-only ERC surfaces were eligible but merely not reviewed.
- FR13 (US3, US4): Tightened stage validation must preserve existing `Idempotency-Key` replay and payload-hash conflict semantics for valid canonical requests and must not introduce nondeterministic ordering regressions.
- FR14 (US4): The minimum blocking verification matrix for this WF is:
  - Step 1 happy path,
  - Step 1 with Step 2 node mismatch,
  - Step 1 review-detail boundary proof showing Step 2-only surfaces are out of scope,
  - Step 2 happy path,
  - invalid-stage fail-closed proof at BFF/backend boundary,
  - idempotency and payload-hash parity proof after boundary hardening,
  - explicit review-evidence verification for the activated stage scope.
- FR15 (US4): No proceed recommendation is valid unless every blocking item in FR14 has an explicit planned verification seam, is later marked pass/fail with concrete evidence, and the final verification output includes a baseline-SHA or explicit commit-range-anchored scope proof.
- FR16 (US4): Final closure for this WF must include an audit-disposition ledger that closes every blocking finding and either closes or explicitly rejects each justified non-blocking finding with rationale before any proceed, implementation-ready, or ship recommendation.
- FR17 (US3, US4): Single-node `POST /api/reviews` alignment is explicitly deferred in Phase 1 because it uses a different service path from the structured ERC trust surface; if Phase 2 discovers a dependency on that path, it must be logged as a blocker or follow-on decision before implementation scope expands.

## 5. Data & API Contracts

### 5.1 Authoritative stage-truth contract

- The canonical ERC call definition must expose one authored proposal-surface stage-scope contract for structured review. (US1, US3, FR2, FR3)
- That contract must be rich enough to derive:
  - stage-eligible ERC proposal leaf ids for submission/visibility,
  - stage-eligible expectation activation inputs,
  - stage-aware evidence projection for persisted review payloads and review detail. (US1, US2, US3, FR2, FR7, FR9-FR12)
- Any existing node-level `review_stage` metadata used by UI helpers must become generated output from the authoritative proposal-surface contract rather than a peer-authored truth source. (US1, US3, FR2, FR3)

### 5.2 Submit and validation contract

- Structured-review requests for ERC must carry an explicit `review_stage` enum plus submitted leaf ids. (US1, US3, FR1, FR4, FR5)
- Boundary validation must fail closed for:
  - invalid `review_stage` values,
  - missing required explicit stage on ERC structured review,
  - submitted ERC leaf ids that are not stage-eligible under the authoritative contract. (US1, US4, FR4-FR6)
- Validation errors must preserve explicit offending-node traceability and must not rewrite the request into a different canonical meaning. (US1, US4, FR5, FR6)

### 5.3 Runtime activation contract

- Before pipeline execution, the structured-review service must derive a stage-scoped runtime snapshot from the authoritative stage-truth source and the validated submitted ERC leaves. (US1, US3, FR7, FR8)
- Runtime activation must use that snapshot, not raw repository expectations on submitted nodes alone. (US1, US3, FR7)
- If the current shared execution core cannot consume this activated snapshot without broad evaluator specialization, Phase 2 must stop and log the blocker rather than widening implementation opportunistically. (US3, US4, FR8)

### 5.4 Persisted evidence and review-detail contract

- Persisted structured-review payload data must expose the selected stage and the inspectable surface set that was eligible/activated for the review via a derived review-time stage-scope snapshot. (US2, US3, FR9, FR10)
- The preferred evidence seam is:
  - existing `review_stage`,
  - existing `submitted_leaf_ids`,
  - one persisted derived `stage_scope_leaf_ids`-style review-time snapshot of the in-scope ERC leaf set,
  - stage-aware review-detail boundary buckets projected from that persisted evidence. (US2, US3, FR9-FR12)
- Review-detail responses for ERC structured reviews must include enough stage-aware boundary data for the page to distinguish out-of-scope from merely not-reviewed surfaces without local heuristics or live recomputation from current call config. (US2, US4, FR11, FR12)

### 5.5 Boundary and idempotency contract

- Invalid-stage and stage/node mismatch errors must fail before any execution or persistence side effects. (US1, US4, FR4-FR6, FR13)
- Existing replay and payload-mismatch semantics for valid structured-review requests must remain unchanged after stage hardening. (US4, FR13, FR14)
- Phase 2 and Phase 3 verification must prove that tightened validation does not weaken current ordering guarantees around validation, idempotency handling, and payload-hash conflict behavior. (US4, FR13, FR14)
- Scope proof for any readiness/proceed recommendation must be anchored to a frozen baseline SHA or explicit commit range rather than worktree-only diffs. (US4, FR15, FR16)

## 6. Components / Modules

- Canonical ERC call-definition authoring seam in canonical ERC call data and its schema boundary
  - Must become the sole authored proposal-surface stage-truth source for structured review. (FR2, FR3)
- Frontend ERC structured-review submit surface
  - Must show only stage-eligible ERC leaves and carry explicit stage selection. (FR1, FR4)
- `frontend/src/app/api/bff/structured-review/route.ts` or equivalent BFF seam
  - Must fail closed on invalid stage input and preserve the explicit request meaning sent to backend. (FR4, FR13)
- Backend structured-review API boundary in `backend/main.py`
  - Must validate stage + submitted ERC leaves against the authoritative contract before runtime side effects. (FR5, FR6, FR13)
- Structured-review service and activation seam under `backend/app/services/` / runtime builder
  - Must create the stage-scoped runtime snapshot and activate only in-scope expectations before pipeline evaluation. (FR7, FR8)
- Review persistence/repository seam
  - Must persist the minimum stage-scoped evidence surface needed for stable scope reconstruction. (FR9, FR10)
- Review-detail response assembly and BFF normalization seams
  - Must project stage-aware boundary buckets truthfully to the UI. (FR10-FR12)
- Backend and frontend test seams
  - Must prove the blocking matrix in FR14 without widening into unrelated calls or generalized stage systems. (FR14-FR17)

Design tree / dependencies / ordering:
1. Freeze the authoritative ERC stage-truth source and the exact derived outputs it must feed. (FR2, FR3)
2. Freeze fail-closed boundary validation behavior and ordering invariants. (FR4-FR6, FR13)
3. Implement stage-scoped runtime activation from the same authoritative source. (FR7, FR8)
4. Extend persisted evidence and review-detail projection so the activated scope is inspectable. (FR9-FR12)
5. Add the blocking verification matrix, scope proof, and audit-disposition closure requirements before any readiness claim. (FR14-FR17)

Deep module guidance:

- Prefer one narrow config/activation seam over ERC-specific branching scattered across UI, BFF, backend, and evaluator internals.
- Treat derived UI metadata, validation snapshots, runtime activation inputs, and evidence fields as projections of one source, not independent truths.
- Reuse existing persisted structured payload and review-detail response seams, but anchor review-detail projection to one persisted review-time stage-scope snapshot rather than live recomputation.
- Keep Phase 2 localized to the structured ERC trust-closure slice; adjacent compliance or single-node work is allowed only if proven necessary to keep this contract honest.

Suggested file-path clusters (coarse only):

- canonical ERC call-definition and schema seams under `backend/`
- structured-review API/service/runtime seams under `backend/`
- structured-review BFF and submit UI under `frontend/src/app/`
- review-detail projection/render seams under `backend/` and `frontend/src/app/`
- backend/frontend verification seams under test directories

## 7. Edge Cases

- The canonical ERC config still permits mixed `BOTH` and `STEP_2` semantics to collapse `b2_part2_scientific_proposal` into a Step 1-visible surface; this is a blocking contract defect, not an acceptable derived result. (US1, US3, FR2, FR3)
- The BFF rejects invalid enums correctly, but the backend still defaults absent or malformed stage input later in the flow; this is still fail-open behavior. (US1, US4, FR4, FR5, FR13)
- A Step 1 request submits only valid Step 1 leaves, but runtime activates Step 2-only expectations because activation still trusts repository expectations on submitted nodes; this violates the trust-closure claim. (US1, US3, FR7, FR8)
- Persisted data stores `review_stage` and `submitted_leaf_ids` but cannot reconstruct which additional surfaces were in scope for the stage; one minimal derived evidence field is required before closure can be claimed. (US2, US3, FR9, FR10)
- Review detail distinguishes reviewed vs `not reviewed` but has no explicit out-of-scope bucket for Step 2-only surfaces during Step 1; this overstates eligibility and remains blocking. (US2, US4, FR11, FR12)
- Tightening stage validation changes idempotency replay or payload-hash conflict behavior for valid requests; this is a regression even if stage checks themselves pass. (US4, FR13, FR14)
- Phase 2 discovers that single-node review-path semantics contradict the structured ERC contract for the same call; this must be raised as an explicit blocker or follow-on decision, not silently widened into scope. (US3, US4, FR17)
- Phase 3 verification passes the runtime/tests, but closure evidence relies only on worktree state or leaves justified audit findings unresolved; this remains a blocking failure even if the implementation itself is correct. (US4, FR15, FR16)

## 8. Testing Decisions (TDD)

- This WF is a behavior-hardening workflow. Phase 3 must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public seams under test must include:
  - ERC structured-review submit/BFF validation,
  - backend structured-review request validation,
  - stage-scoped runtime activation,
  - persisted structured-review evidence,
  - review-detail/BFF projection for stage-aware boundaries. (US1, US2, US3, US4)
- Mock only external boundaries such as LLM calls or quota/policy toggles. Do not mock the stage-truth derivation, validation, activation, persistence evidence, or review-detail boundary mapping being proven. (US2, US3, US4)
- Required automated coverage:
  - a derivation-parity test proving UI eligibility metadata and runtime activation inputs are both produced from the same authored proposal-surface stage-truth contract. (US1, US3, FR2, FR7, FR8)
  - Step 1 happy-path test proving only Step 1-eligible ERC surfaces are accepted and activated. (US1, US4, FR4-FR8, FR14)
  - Step 1 mismatch test proving Step 2-only ERC nodes are rejected fail-closed with explicit offending ids before execution. (US1, US4, FR5, FR6, FR14)
  - Step 2 happy-path test proving Step 2 surfaces activate correctly without Step 1 regressions. (US1, US4, FR7, FR14)
  - Invalid-stage boundary tests at BFF and backend proving no coercion to `STEP_1` and no side effects. (US1, US4, FR4, FR13, FR14)
  - Idempotency replay and payload-mismatch tests proving current semantics remain intact after stage hardening. (US4, FR13, FR14)
  - Persisted-evidence and review-detail tests proving Step 1 exposes Step 2-only surfaces as out of scope rather than merely `not reviewed`. (US2, US4, FR9-FR12, FR14)
  - At least one representative end-to-end proof spanning submit, validation, activation, persistence, and review detail for ERC structured review. (US2, US4, FR14, FR15)
  - Closure evidence proving the final proceed recommendation is anchored to an explicit baseline SHA or commit range and includes an audit-disposition ledger for all justified findings. (US4, FR15, FR16)

## 8.1 Readiness Gate

- This WF is not ready for Tasks unless the PRD stays within the structured ERC trust-closure slice and leaves no unresolved blocking contract ambiguity on authoritative stage truth, runtime activation, or inspectable evidence. (US3, US4)
- No implementation-ready or ship recommendation is valid unless every blocking verification item in FR14 has an explicit planned seam, later pass/fail evidence, a baseline-anchored scope proof, and an audit-disposition ledger closing or explicitly rejecting every justified finding. (US4, FR14-FR16)
- If Phase 2 cannot keep evaluator/pipeline internals call-agnostic, cannot avoid duplicate peer-authoritative stage mappings, cannot prove inspectable executed scope, cannot preserve idempotency/payload-hash guarantees, or cannot keep the single-node path deferred honestly, implementation planning must stop and surface the blocker. (US3, US4, FR17)

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- One narrow diagnostic or persisted derived field is acceptable only if existing structured payload and review-detail seams cannot prove executed ERC stage scope honestly. (US2, US3, FR9, FR10)

## 10. Deferred / Not in MVP

- Single-node review-path alignment.
- Broader staged-call generalization beyond ERC structured review.
- Compliance-message redesign beyond the minimum needed for stage-truth honesty.
- Prompt/extraction/supporting-context expansion or generic provenance systems.

## 11. Open Questions (if any)

- Whether structured-review compliance feedback needs explicit stage labeling to avoid referencing out-of-scope ERC surfaces during Step 1. This remains deferred unless Phase 2 proves it is necessary for trust closure.

## 12. Changelog

- v0.1 (2026-03-09): Initial PRD from brainstorm.
- v0.2 (2026-03-09): Applied risk-audit edits to lock the authored proposal-surface stage-truth source, persist a review-time stage-scope snapshot for inspectable evidence, add derivation-parity test coverage, and mark Ready for Tasks.
- v0.3 (2026-03-09): Hardened proceed-proof requirements with baseline-anchored scope and audit-disposition closure, and resolved the single-node defer boundary explicitly in Phase 1.
