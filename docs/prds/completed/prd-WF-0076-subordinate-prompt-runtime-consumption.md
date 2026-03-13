<!-- docs/prds/completed/prd-WF-0076-subordinate-prompt-runtime-consumption.md -->
# WF-0076 — Subordinate Prompt Runtime Consumption

Artifact: prd
Version: v0.4
Status: Ready for Tasks
Last Updated: 2026-03-12

## 0. User Stories (MVP)

- US1: As a backend runtime maintainer, I want the structured-review activation path to carry official subordinate prompts into the active runtime contract, so that WF-0074/WF-0075 fidelity becomes reachable to execution instead of being discarded at snapshot build time.
- US2: As a backend runtime maintainer, I want `pipeline_v1` to consume that subordinate-prompt detail through the narrowest deterministic seam, so that structured-review behavior changes in a provable way without broad engine redesign.
- US3: As a maintainer protecting workflow honesty, I want ERC PoC proof-call verification plus explicit boundary guards, so that WF-0076 proves runtime consumption narrowly without reopening authoring/governance scope or overclaiming universal product benefit.

## Deferred Stories (Not in MVP)

- As a researcher, I want all calls with subordinate prompts to show equal end-user improvement immediately.
- As a maintainer, I want a generic multi-call ontology or broad prompt-engine redesign for subordinate prompts.
- As a maintainer, I want prompt-builder or researcher-facing prose refinement work beyond the active `pipeline_v1` seam needed for deterministic runtime proof.

## 1. In Scope

- Preserve prior truth that WF-0074 already solved subordinate-prompt authoring/governance and WF-0075 already solved ERC PoC proof-call completeness. `(US3)`
- Add the smallest activated runtime contract change needed to carry subordinate prompts from `structured_reviewer_service.py` into the live structured-review path instead of discarding them at snapshot build time. `(US1)`
- Source subordinate prompts for MVP from the existing `CallDefinition.canonical_json` fidelity already landed in WF-0074/WF-0075, using current expectation/evaluation-element links rather than new persistence or authoring surfaces. `(US1) (US3)`
- Prefer a narrow child `subordinate_prompts` payload on activated expectations when that remains sufficient to drive deterministic runtime effect in `pipeline_v1`. `(US1) (US2)`
- Start with one ERC PoC expectation path under `poc_idea_innovation` as the first implementation slice, then preserve broader page-43 completeness through regression coverage rather than a broader first runtime rewrite. `(US2) (US3)`
- Update the active structured-review execution path only as far as needed for deterministic proof that subordinate prompts influence runtime behavior on ERC PoC. `(US2)`
- Add targeted deterministic tests that prove the discard seam, the widened contract, the active runtime effect, and ERC PoC proof-call preservation. `(US2) (US3)`
- Preserve WF-0074 compatibility posture for existing flat canonical YAMLs unless a narrower rule is separately justified and re-approved. `(US3)`

## 2. Out of Scope

- Re-solving call-definition schema support, template defaults, onboarding workflow, or governance already closed in WF-0074. `(US3)`
- Re-solving ERC PoC page-43 proof-call completeness already closed in WF-0075. `(US3)`
- Broad engine redesign, generic ontology work, prompt-builder-first redesign, or multi-call migration. `(US2) (US3)`
- UI/BFF work or universal researcher-facing quality claims across all calls. `(US3)`

## 3. User / System Flow

- Happy path
  - The maintainer confirms the current `structured_reviewer_service.py` activation seam still emits `call_config_snapshot` with only `schema_version` and `expectations`, so subordinate prompts are dropped before validator and `pipeline_v1` execution. `(US1)`
  - The maintainer derives official subordinate prompts from the existing canonical call definition for the activated ERC PoC expectation path, avoiding new DB/model authoring work. `(US1) (US3)`
  - The maintainer widens the activated expectation payload minimally so each relevant activated expectation can carry its official subordinate prompts with stable prompt IDs and prompt text from the canonical call definition. `(US1) (US2)`
  - The validator accepts the widened snapshot deterministically, canonical digesting still succeeds, and no unrelated snapshot sections become required. `(US1) (US2)`
  - `pipeline_v1` consumes the new expectation-level subordinate-prompt payload through the live evaluator path, with subordinate-prompt influence surfacing first in deterministic finding `reason` output before any broader artifact expansion. `(US2)`
  - Targeted ERC PoC tests prove the active runtime artifact now includes official subordinate-prompt influence that was previously absent, while preserving proof-call fidelity and compatibility posture honesty. `(US2) (US3)`
- Failure path 1
  - The snapshot now serializes extra subordinate-prompt data, but `pipeline_v1` still behaves identically and no deterministic runtime artifact changes, so the workflow remains blocked as stored-but-unused one layer later. `(US2)`
- Failure path 2
  - The proposed seam depends on prompt-builder behavior or another non-active path that the live structured-review runtime does not exercise, so the proof is rejected as invalid for WF-0076. `(US2) (US3)`
- Failure path 3
  - The implementation broadens into authoring/governance redo, multi-call rollout, or universal product claims beyond ERC PoC evidence, so the change is rejected as scope drift. `(US3)`

## 4. Functional Requirements

- FR1 (US1): `backend/app/services/structured_reviewer_service.py` must stop emitting an expectations-only runtime snapshot for activated expectations that have canonical subordinate prompts available.
- FR2 (US1): The preferred MVP contract shape is an additive `subordinate_prompts` child payload on each activated expectation, with fallback to another equivalently narrow active-runtime field only if expectation-level carriage proves insufficient during Phase 2.
- FR3 (US1): Each activated subordinate prompt item must preserve a stable prompt ID and prompt text, and may include source locator metadata when needed for deterministic proof.
- FR3A (US1) (US3): MVP subordinate-prompt lookup must come from the already-ingested canonical call-definition payload for the active call, joined through existing expectation/evaluation-element identity, without introducing new DB fields, migrations, or authoring workflows.
- FR4 (US1) (US2): `backend/app/engine/contracts.py` and `backend/app/engine/review_request_validator.py` must accept the widened activated expectation contract without making unrelated snapshot sections mandatory.
- FR5 (US2): The active `pipeline_v1` execution path must consume subordinate-prompt detail at the narrowest live seam that can change deterministic runtime behavior.
- FR6 (US2): The first MVP runtime-effect proof must target one ERC PoC expectation path under `poc_idea_innovation` and use evaluator-produced finding `reason` as the first live artifact.
- FR7 (US2): MVP proof of runtime effect must be stronger than “the snapshot has more fields”; it must show changed evaluator-produced finding `reason` content on the active pipeline path before any review-card-level assertion is used.
- FR8 (US2): Phase 2 must include one negative live-path proof showing that when subordinate-prompt carriage is absent from an otherwise valid activated expectation payload, the chosen runtime artifact loses the official subordinate-prompt signal.
- FR9 (US2): If review-card assertions are used as part of proof, they must be deterministic and source-grounded, not subjective prose-quality judgments.
- FR10 (US3): ERC PoC remains the first and only required proof-call for MVP, and no requirement in this WF may claim equal benefit for all calls.
- FR11 (US3): WF-0074 compatibility posture for existing flat canonical YAMLs must remain preserved unless a later phase produces explicit proof and re-approval for narrowing it.
- FR12 (US3): Closure evidence must include a baseline-anchored `main...HEAD` scope proof plus approved-artifact citations that preserve the distinction between solved fidelity work and newly solved runtime consumption.
- FR13 (US3): Closure evidence must remain fail-closed with row-based verification results and a findings-disposition artifact before any proceed or ship recommendation.

## 5. Data & API Contracts

- Activated expectation contract `(US1) (FR1) (FR2) (FR3) (FR4)`
  - Target seam: `backend/app/engine/contracts.py`
  - Required additive shape on each activated expectation:
    - `expectation_id`
    - `node_logical_id`
    - existing `check_id` / `required`
    - optional `subordinate_prompts: [{id, prompt, source_locator?}]`
  - Validation rules:
    - `subordinate_prompts` is optional and additive for compatibility;
    - each subordinate prompt item must be a typed object, not a free-form string;
    - prompt item `id` and `prompt` must be non-empty;
    - prompt item IDs must be unique within the parent expectation when present.
- Canonical subordinate-prompt source contract `(US1) (US3) (FR3A)`
  - Target seam: `backend/app/services/structured_reviewer_service.py`
  - Required behavior:
    - MVP lookup must read subordinate prompts from the existing `CallDefinition.canonical_json` already ingested for the active call;
    - mapping must reuse existing expectation/evaluation-element identity instead of adding new persistence or schema layers;
    - missing canonical subordinate prompts must fail closed at the targeted expectation path rather than silently fabricating prompts.
- Snapshot serialization and digest contract `(US1) (FR4)`
  - Target seams: `backend/app/services/structured_reviewer_service.py`, `backend/app/engine/review_request_validator.py`
  - Required behavior:
    - the activated snapshot must serialize subordinate prompts deterministically when present;
    - canonical digest calculation must continue to cover the widened payload;
    - calls without subordinate prompts or legacy flat call definitions must remain valid without synthetic filler fields.
- Active runtime-consumption contract `(US2) (FR5) (FR6) (FR7) (FR8) (FR9)`
  - Target seam: `backend/app/engine/pipeline_v1.py` and `backend/app/engine/findings/evaluator.py`
  - Required behavior:
    - the live pipeline must read the widened expectation payload and incorporate subordinate prompt data into evaluator-produced finding `reason` content that it actually uses;
    - the first proof artifact is evaluator-produced finding `reason` for one activated ERC PoC expectation under `poc_idea_innovation`;
    - review-card assertions are secondary proof only after the evaluator `reason` seam is covered;
    - observation-detail or prompt-builder-first proof is out of MVP scope unless a later workflow proves the active runtime path for this seam actually routes through those surfaces.
- Proof-call contract `(US2) (US3) (FR10)`
  - Proof surface: `ERC-2026-PoC` only for MVP.
  - Required behavior:
    - the proof-call must preserve the existing page-43 subordinate prompts already verified in WF-0075;
    - the first runtime slice should anchor to `poc_idea_innovation` before broader ERC PoC preservation is proven through regression coverage;
    - deterministic proof must show those official concerns now reach the active runtime path rather than stopping at canonical storage.
- Boundary and closure contract `(US3) (FR11) (FR12) (FR13)`
  - Required behavior:
    - approved WF-0074 and WF-0075 artifacts remain cited as prior truth;
    - compatibility posture for legacy flat canonical YAMLs remains unchanged unless separately re-approved;
    - closure requires a verification matrix and findings-disposition ledger with explicit evidence pointers.

## 6. Components / Modules

- Activation seam
  - `backend/app/services/structured_reviewer_service.py`
  - Responsibility: map canonical subordinate-prompt fidelity into the activated review request payload without broad runtime redesign.
- Contract / validator seam
  - `backend/app/engine/contracts.py`
  - `backend/app/engine/review_request_validator.py`
  - Responsibility: define and validate the minimal additive expectation payload and digest behavior.
- Active runtime seam
  - `backend/app/engine/pipeline_v1.py`
  - `backend/app/engine/findings/evaluator.py`
  - Responsibility: consume subordinate prompts on the live structured-review path and emit deterministic runtime-effect evidence.
- Proof seam
  - `backend/tests/test_structured_reviewer_service.py`
  - `backend/tests/test_call_subordinate_prompt_coverage.py`
  - Responsibility: prove the discard baseline, the activated contract widening, the active runtime effect, and ERC PoC preservation.
- Design tree (dependencies + ordering)
  - 1. Freeze prior truth and prove the current discard seam in the structured-review service.
  - 2. Add the minimal activated expectation payload for subordinate prompts.
  - 3. Widen validator/contract support only as far as needed for deterministic serialization and digesting.
  - 4. Consume the payload in the active `pipeline_v1` path at the narrowest effectful seam.
  - 5. Add deterministic proof for ERC PoC runtime influence and preserve prior-truth boundaries.
- Deep modules / stable seams
  - Prefer one small activated-expectation interface with hidden mapping logic inside the service, plus one small live-pipeline consumption seam that can be tested without redesigning the broader review engine.

## 7. Edge Cases

- If an activated expectation has no canonical subordinate prompts by source, the runtime payload must remain absent or empty for that expectation rather than fabricating prompts. `(US1)`
- If a call definition stays on the temporary flat compatibility posture, runtime activation must remain valid without requiring subordinate-prompt fields everywhere. `(US3)`
- If multiple subordinate prompts exist under one expectation, proof cannot collapse them into one indistinguishable summary string if that would prevent deterministic source-grounded assertions. `(US2)`
- If a proposed proof seam depends on `extract_observations` inputs such as snapshot `proposal_nodes`, that seam is out of MVP unless Phase 2 first proves the structured-review activation path already populates it without widening scope. `(US2) (US3)`
- If the first runtime slice tries to cover all ERC PoC page-43 expectations at once, the task plan is too broad and must be split back to one expectation path plus regressions. `(US2) (US3)`
- If a chosen proof seam changes only telemetry while all live runtime artifacts remain unchanged, that proof is insufficient because it does not show subordinate prompts influence structured-review behavior. `(US2)`
- If ERC PoC proof passes but other calls remain unproven, closure language must state that boundary explicitly. `(US3)`

## 8. Testing Decisions (TDD)

- Public seam first
  - Write a failing targeted test proving the current ERC PoC structured-review request still drops subordinate prompts from the activated runtime snapshot. `(US1) (FR1)`
  - Write a failing targeted test proving subordinate prompts are sourced from existing canonical call-definition JSON rather than a new persistence seam. `(US1) (FR3A)`
  - Write a failing contract/validator test proving the minimal widened expectation payload shape is required to accept deterministic subordinate-prompt carriage. `(US1) (FR2) (FR4)`
  - Write a failing live-pipeline test proving subordinate prompts are still absent from evaluator-produced finding `reason` output before implementation. `(US2) (FR5) (FR6)`
  - Write a failing negative live-path test proving that an otherwise valid payload without subordinate-prompt carriage cannot produce the new official-concern signal. `(US2) (FR8)`
- Test seams
  - `StructuredReviewerService.generate_structured_review_pipeline_v1`
  - `validate_review_request_payload`
  - `run_review_pipeline` and `evaluate_expectations`
  - ERC PoC real-call coverage proof in `backend/tests/test_call_subordinate_prompt_coverage.py`
- What to mock
  - Mock only outer boundaries needed to capture runtime artifacts deterministically; do not mock the activated snapshot projection, validator behavior, or the live pipeline seam being proven.
- Minimal test types
  - Service-level regression proving the current discard seam and the new activated payload. `(US1) (FR1) (FR2)`
  - Contract/validator regression for digest-safe widened payload acceptance and malformed subordinate-prompt rejection. `(US1) (FR3) (FR4)`
  - Live-pipeline regression proving subordinate prompts influence evaluator-produced finding `reason` output for one ERC PoC expectation path. `(US2) (FR5) (FR6) (FR7) (FR9)`
  - Negative live-pipeline regression proving the signal disappears when subordinate-prompt carriage is absent from an otherwise valid request. `(US2) (FR8)`
  - ERC PoC regression preserving page-43 proof-call completeness while the runtime seam changes. `(US3) (FR10)`
  - Compatibility regression or approved-artifact citation preserving WF-0074 flat-call posture. `(US3) (FR11)`

## 9. Telemetry (Minimal)

- Reuse deterministic test artifacts and pipeline outputs as proof surfaces.
- If telemetry is referenced at all, it may only support proof and cannot be the sole runtime-effect artifact.

## 10. Deferred / Not in MVP

- Generic cross-call subordinate-prompt rollout.
- Prompt-builder-first or prose-polishing work outside the active live-runtime seam.
- Researcher-facing UX changes or product-marketing claims beyond ERC PoC proof.
- Schema/governance expansion already handled in WF-0074.

## 11. Open Questions (if any)

- none

## 12. Verification Evidence Matrix (Fail-Closed)

| Verification item | Evidence shape | Result (`pass`/`fail`/`skipped`) | Evidence ref | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Runtime discard seam proof | targeted structured-review service snapshot test | `fail` (default until executed) | required | must prove exactly where subordinate prompts are dropped today |
| Minimal contract widening | contract/validator test for widened expectation payload | `fail` (default until executed) | required | must prove the smallest additive runtime shape is accepted deterministically and malformed subordinate-prompt payloads fail closed |
| Canonical source lookup proof | targeted structured-review service test against the active call definition | `fail` (default until executed) | required | must prove subordinate prompts come from `CallDefinition.canonical_json` through existing expectation/evaluation-element identity rather than a hardcoded or parallel seam |
| Runtime consumption proof | service test plus one active `pipeline_v1` or adjacent live-path test | `fail` (default until executed) | required | must prove subordinate prompts influence active structured-review runtime behavior, not just storage |
| Negative live-path proof | targeted live-path test with subordinate-prompt carriage removed from an otherwise valid activated payload | `fail` (default until executed) | required | must prove the official subordinate-prompt signal disappears without carriage so positive-only proof cannot pass |
| Output-level improvement proof | deterministic live execution-surface and/or review-card assertion | `fail` (default until executed) | required | must prove more complete official-concern carry-through or omission reduction in operationalized terms |
| ERC PoC proof-call preservation | targeted ERC PoC regression | `fail` (default until executed) | required | must preserve WF-0075 completeness while using ERC PoC as the first proof surface |
| WF-0074 compatibility-posture preservation | regression and/or approved-artifact citation | `fail` (default until executed) | required | must preserve temporary compatibility for existing flat canonical YAMLs unless re-approved |
| Boundary honesty | `main...HEAD` scope proof plus approved-artifact citations | `fail` (default until executed) | required | must preserve the distinction between solved fidelity and newly solved runtime consumption |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close every blocking finding and close or reject justified non-blocking findings with rationale |

- Proceed recommendation remains blocked unless every required row above is `pass`, or explicitly `skipped` with accepted rationale during review.

## 13. Changelog

- v0.1 (2026-03-12): Initial PRD from brainstorm.
- v0.2 (2026-03-12): Narrowed the first runtime slice to one ERC PoC expectation path, preferred evaluator-produced finding detail as the first proof artifact, added a required negative live-path proof, and marked the PRD ready for Tasks.
- v0.3 (2026-03-12): Locked the MVP source seam to existing canonical call-definition JSON, fixed the first proof artifact to evaluator-produced finding `reason`, and ruled observation/prompt-builder-first proof out of MVP unless a later workflow proves those paths are active.
- v0.4 (2026-03-12): Closed review-gate gaps by requiring explicit proof of canonical source lookup, malformed-payload rejection, and a negative live-path case before any proceed recommendation.
