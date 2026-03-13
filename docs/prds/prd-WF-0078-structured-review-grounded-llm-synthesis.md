<!-- docs/prds/prd-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-13

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher using the structured `/app` review flow for `ERC-2026-PoC`, I want this workflow to prove a bounded additive seam for grounded synthesized proposal-improvement feedback, so that a later carry-through slice can expose stronger revision help without weakening deterministic trust.
- US2: As a maintainer of the structured-review system, I want `pipeline_v1` to remain the deterministic source of truth while synthesis runs only downstream in `StructuredReviewerService`, so that trust, rollback, and audit boundaries remain intact.
- US3: As a maintainer protecting review honesty, I want synthesis to fail closed per card back to WF-0077 deterministic guidance and to keep raw machine `reason` audit-only, so that rejected or malformed synthesis never becomes researcher-visible truth.
- US4: As a product owner rolling this out safely, I want MVP scope limited to `ERC-2026-PoC` with an additive contract that can remain backend-only unless carry-through is explicitly proven necessary, so that this WF stays narrow and implementation can be split into atomic three-file tasks later.

## Deferred Stories (Not in MVP)

- As a researcher, I want grounded synthesis to be available immediately for all structured-review calls.
- As a maintainer, I want synthesis to persist through all review-detail and export surfaces for every call family without separate rollout proof.
- As a maintainer, I want whole-review or whole-submission synthesis instead of per-card synthesis.
- As a maintainer, I want raw machine `reason` or broader audit traces transformed into researcher-facing prose.

## 1. In Scope

- Add a bounded per-card LLM synthesis layer downstream of deterministic findings for the structured `/app` flow on `ERC-2026-PoC` only. `(US1) (US2) (US4)`
- Keep `pipeline_v1` unchanged as the deterministic source of truth for validation, evaluation, finding generation, and machine traceability. `(US2) (US3)`
- Orchestrate synthesis at the existing structured-review presentation seam in `backend/app/services/structured_reviewer_service.py`, potentially via a narrow collaborator owned by that seam. `(US2) (US4)`
- Ground synthesis inputs only in approved per-card context: deterministic card/finding identity, same-card node context, relevant evaluation criteria/elements, deterministic WF-0077 guidance, approved canonical subordinate-prompt or guidance context, and a bounded excerpt from the same node text under review. `(US1) (US2) (US3)`
- Preserve deterministic `feedback_text` as the stable fallback surface while introducing an optional additive synthesized companion field plus a seam-scoped synthesis outcome marker for targeted cards at the backend seam proof boundary. Public/API/frontend provenance carry-through remains dependent scope, not MVP-default scope. `(US1) (US3) (US4)`
- Enforce fail-closed behavior per card so timeout, client error, malformed output, or grounding rejection degrades only that card to deterministic WF-0077 guidance. `(US1) (US3)`
- Force Phase 2 planning to keep implementation slices atomic, with tasks preferring no more than three touched files and TDD proof for each behavior change. `(US2) (US4)`

## 2. Out of Scope

- Replacing or modifying `pipeline_v1` to make the LLM part of primary evaluation logic. `(US2) (US3)`
- Moving MVP synthesis into `ReviewExecutionCore`, the legacy `ReviewerService` path, or frontend-only rewriting. `(US2) (US4)`
- Using full proposal text, full call definitions, unrelated findings, or raw machine `reason` as synthesis prompt input. `(US2) (US3)`
- Broad rollout beyond `ERC-2026-PoC` during MVP. `(US4)`
- Guaranteeing immediate persistence/API/frontend/export exposure unless Phase 2 proves that backend-only seam proof is not an honest rollout boundary. `(US4)`
- Turning synthesis into a generic grant-writing coach or free-form critique engine. `(US1) (US3)`

## 3. User / System Flow

- Happy path
  - A researcher submits or opens an `ERC-2026-PoC` structured review in `/app`, and the backend completes deterministic review generation through `pipeline_v1`. `(US1) (US2)`
  - `StructuredReviewerService` receives deterministic cards/findings, builds a bounded per-card synthesis input from approved same-card context only, and requests optional synthesized explanation without mutating deterministic source data. `(US1) (US2) (US3)`
  - The service validates the structured synthesis response, accepts only grounded per-card output that maps cleanly to the originating card, and produces deterministic `feedback_text` plus an additive synthesized companion/seam-outcome payload at the backend seam proof surface. `(US1) (US3) (US4)`
  - Any broader researcher-visible rollout claim remains deferred until a later task slice explicitly proves persistence/API/review-detail/export/frontend carry-through for that additive field. `(US1) (US2) (US4)`
- Failure path 1
  - The LLM client times out, errors, or is unavailable for one card, so that card drops synthesis and remains on deterministic WF-0077 guidance while the overall review still completes. `(US1) (US3)`
- Failure path 2
  - The model returns malformed output or content that fails grounding, provenance, or card-identity validation, so the synthesized companion field is rejected and that card stays deterministic-only. `(US2) (US3)`
- Failure path 3
  - The required user-visible rollout would need persistence, API, review-detail, export, or frontend carry-through that the current contract cannot support honestly, so MVP must stop at backend seam proof or explicitly plan a dependent carry-through slice rather than overloading `feedback_text`. `(US2) (US4)`

## 4. Functional Requirements

- FR1 (US1) (US2): The structured-review path must attempt synthesis only after deterministic findings/cards already exist from `pipeline_v1`.
- FR2 (US2) (US3): `pipeline_v1` must remain the deterministic source of truth and must not be widened into LLM-backed execution or evaluation for this WF.
- FR3 (US1) (US2) (US3): The orchestration seam for MVP must live in `StructuredReviewerService` or a helper owned by that service seam, not in `ReviewExecutionCore`, frontend-only rewriting, or the legacy review path.
- FR4 (US1) (US2) (US3): Synthesis must run per card, not whole review and not whole node, so degradation can happen card-by-card.
- FR5 (US1) (US2) (US3): The approved synthesis prompt boundary must exclude full-submission prompting, unrelated evaluation elements, unrelated node findings, legacy review artifacts, and raw machine `reason`.
- FR6 (US1) (US3) (US4): The seam-proof output contract must preserve deterministic `feedback_text` as the stable fallback surface and add an optional synthesized companion field plus a seam-scoped synthesis outcome marker for targeted in-scope cards. Public/API/frontend provenance carry-through is deferred unless a dependent slice explicitly opens it.
- FR7 (US2) (US3): Any synthesized payload that is malformed, fails schema validation, fails grounding checks, or cannot be attached unambiguously to its originating card must be rejected before user exposure.
- FR8 (US1) (US3): A synthesis failure for one card must not fail the entire review when deterministic output for that card remains available.
- FR9 (US2) (US3): Raw machine `reason` must remain preserved for audit/debug/traceability and must stay excluded from LLM prompt inputs.
- FR10 (US4): MVP behavior must be locked to `ERC-2026-PoC`; non-targeted calls must retain current deterministic behavior unless a later artifact re-approves widening.
- FR10A (US2) (US4): Non-targeted calls/cards must not invoke the synthesis collaborator or emit synthesis-specific companion/outcome data; they must remain on the current deterministic contract unchanged.
- FR11 (US1) (US4): Phase 1 closes MVP as backend-only seam proof; any persistence/API/frontend/export carry-through required for broader researcher-facing rollout must be planned as a separate dependent slice rather than implied by this PRD.
- FR12 (US2) (US4): Phase 2 must decompose implementation into atomic tasks that prefer no more than three touched files each and use TDD for all behavior changes.
- FR13 (US2) (US3): Verification must cover partial-card degradation, whole-review deterministic success when all synthesis is rejected, and boundary preservation against scope drift into legacy paths or execution seams.
- FR14 (US1) (US3): Researcher-facing wording must remain evaluation-criteria/elements grounded and must not present unsupported advice as deterministic truth.

## 5. Data & API Contracts

- Per-card synthesis input contract `(US1) (US2) (US3) (FR1) (FR4) (FR5)`
  - Required fields:
    - deterministic card/finding identity;
    - same-card node logical/title context;
    - relevant evaluation criterion/element labels;
    - deterministic WF-0077 guidance for that card;
    - approved canonical subordinate-prompt or guidance context for the same evaluation element;
    - bounded excerpt from the same submitted node text under review.
  - Validation rules:
    - no full-submission text;
    - no unrelated findings or elements;
    - no raw machine `reason`;
    - no legacy review-path artifacts.
- Per-card seam-proof output contract `(US1) (US3) (US4) (FR6) (FR7) (FR10A)`
  - Required behavior:
    - deterministic card identity remains unchanged;
    - deterministic `feedback_text` remains available as fallback/user-visible deterministic guidance;
    - optional synthesized companion payload is accepted only after contract and grounding validation;
    - a seam-scoped synthesis outcome marker distinguishes accepted synthesis from deterministic fallback for targeted in-scope cards;
    - rejected synthesis content is dropped, not partially surfaced.
- Response and carry-through decision contract `(US1) (US4) (FR6) (FR11)`
  - Required behavior:
    - this PRD locks MVP to backend seam proof only;
    - Phase 2 must treat persistence/API/review-detail/export/frontend propagation as an explicit follow-on decision, not an implied side effect;
    - broader ship-ready researcher-facing rollout requires a separate dependent plan for additive field/provenance carry-through wherever final user-visible data is read.
- Seam outcome and optional public provenance contract `(US1) (US3) (US4) (FR6) (FR7) (FR10A) (FR11)`
  - `accepted_synthesis`: validated synthesized companion payload accepted for an in-scope targeted card at the backend seam proof surface.
  - `deterministic_fallback`: synthesis was attempted for an in-scope targeted card but skipped by policy, failed, timed out, or was rejected, so deterministic guidance remains the only accepted output for that card.
  - if Phase 2 does not open API/persistence/frontend carry-through, this outcome marker may remain internal/service-test-visible rather than public.
- Internal orchestration states `(US2) (US3) (FR7) (FR8) (FR10) (FR10A)`
  - synthesis not attempted for out-of-scope or disabled paths;
  - synthesis attempted for in-scope cards before validation;
  - rejected attempts remain internal-only and must never reach user-visible output.

## 6. Components / Modules

- Deterministic engine boundary
  - `backend/app/engine/pipeline_v1.py`
  - Responsibility: remain unchanged as the deterministic source of findings, review-card structure, and machine traceability.
- MVP orchestration seam
  - `backend/app/services/structured_reviewer_service.py`
  - Responsibility: own post-pipeline per-card synthesis orchestration, fallback decisions, and final response assembly for the structured-review path.
- Likely synthesis collaborator
  - Suggested coarse path: `backend/app/services/structured_review_synthesis_service.py` or equivalent helper owned by the structured-review seam.
  - Responsibility: build approved input payloads, invoke the narrow LLM client boundary, validate output shape, and return either accepted synthesis or deterministic fallback.
- Existing LLM dependency boundary
  - `backend/app/services/llm_client.py`
  - Responsibility: remain a narrow dependency boundary rather than becoming a structured-review execution engine.
- Conditional carry-through seams
  - `backend/app/schemas/api.py`
  - `backend/main.py`
  - persistence/review-detail/export surfaces and `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Responsibility: only enter scope if Phase 2 proves additive synthesized companion/provenance must survive beyond backend seam proof for honest rollout.
- Design tree (dependencies + ordering)
  - 1. Lock the additive synthesis contract, approved input boundary, and deterministic fallback/provenance rules. `(FR5) (FR6) (FR7) (FR11)`
  - 2. Prove the structured-review seam can attempt per-card synthesis without changing deterministic finding generation. `(FR1) (FR2) (FR3) (FR4)`
  - 3. Prove rejection and fail-closed behavior for timeout, client error, malformed output, and ungrounded output. `(FR7) (FR8) (FR13)`
  - 4. Prove raw machine `reason` preservation and exclusion from prompt material. `(FR5) (FR9)`
  - 5. Prove non-targeted calls/cards do not invoke synthesis or widen their contract. `(FR10) (FR10A)`
  - 6. Keep this PRD closed at backend seam proof, and treat additive carry-through as a dependent next slice if broader rollout is desired. `(FR6) (FR10) (FR11)`
  - 7. Keep implementation tasks atomic and topologically ordered with three-file slices preferred. `(FR12)`
- Deep module guidance
  - Keep the first-slice public contract unchanged unless a dependent carry-through task is explicitly opened; seam-proof fields may remain internal/service-test-visible in MVP.
  - Hide prompt construction, validation, and rejection logic inside the service/helper seam so rollback returns cleanly to WF-0077 behavior.

## 7. Edge Cases

- The model returns advice tied to an evaluation element not present in the originating deterministic card; that synthesis must be rejected. `(US1) (US3)`
- The bounded submitted-text excerpt is too thin to support a clear explanation; the card must remain on deterministic guidance instead of inventing critique. `(US1) (US3)`
- Some cards in the same review accept synthesis while others reject it; the mixed response remains valid if each card preserves honest provenance and fallback behavior. `(US1) (US3)`
- All in-scope cards reject synthesis; the review must still complete truthfully in deterministic mode. `(US1) (US3)`
- A non-targeted call or out-of-scope card reaches the synthesis collaborator anyway; that is invalid even if the final user-visible text looks unchanged because it widens cost/coupling beyond the approved slice. `(US2) (US4)`
- The additive synthesized companion field exists only at the backend seam but not in persisted or exported review reads; that state may be acceptable for seam proof but not for a broader ship claim. `(US4)`

## 8. Testing Decisions (TDD)

- RED first
  - Add failing tests at the structured-review seam proving:
    - accepted in-scope per-card synthesis does not yet attach the validated synthesized companion/outcome payload at the chosen seam-proof surface;
    - rejected per-card synthesis does not yet fail closed cleanly to deterministic guidance;
    - non-targeted calls/cards can still reach the synthesis seam or emit synthesis-specific contract data;
    - all-cards-rejected reviews do not yet prove truthful deterministic completion.
    `(US2) (US3) (US4) (FR6) (FR7) (FR8) (FR10A) (FR12)`
- GREEN scope
  - Implement the smallest service-level change that introduces per-card synthesis orchestration after deterministic findings while preserving deterministic `feedback_text` fallback. `(US1) (US2) (FR1) (FR3) (FR4) (FR6)`
- Required regression coverage
  - Prove no change to deterministic finding generation or targeted seam ownership. `(FR1) (FR2) (FR3)`
  - Prove raw machine `reason` remains preserved and excluded from prompt inputs. `(FR5) (FR9)`
  - Prove timeout, client error, malformed output, unsupported-element output, and ambiguous-card output all fail closed to deterministic guidance. `(FR7) (FR8) (FR13)`
  - Prove one rejected card does not fail the whole review and that a fully rejected review still returns deterministic results. `(FR8) (FR13)`
  - Prove non-targeted calls/cards remain unchanged and do not invoke the synthesis collaborator or emit synthesis-specific contract fields. `(FR10) (FR10A)`
  - Prove backend seam proof does not require schema/persistence/frontend carry-through in the first slice, and require separate tests only if a later dependent carry-through slice is explicitly planned. `(FR11) (FR12)`
- Test seams
  - `StructuredReviewerService.generate_structured_review_pipeline_v1`
  - Public entrypoints of any new structured-review synthesis collaborator
- What to mock
  - Mock the LLM client boundary and external failure modes only.
  - Do not mock deterministic finding-generation semantics being preserved by the seam.
- Minimal test types
  - Service-level unit/integration-ish tests for the first backend slice.
  - Schema/API/persistence/frontend tests only in a later dependent slice if carry-through becomes required.

## 9. Telemetry (Minimal)

- Minimum MVP telemetry is runtime-observable fallback classification sufficient for debugging synthesis rejection categories if already available at the service layer.
- New product telemetry is optional and deferred unless Phase 2 proves it is required to operate fail-closed behavior safely.

## 10. Deferred / Not in MVP

- Cross-call rollout beyond `ERC-2026-PoC`.
- Whole-review synthesis or broader full-submission prompting.
- Replacing deterministic `feedback_text` with synthesized text as the only user-visible surface.
- Turning raw machine audit data into prompt input or user-visible prose.
- Legacy `/reviews` path integration or execution-core refactors.
- Frontend redesign work unrelated to truthful additive synthesis/provenance carry-through.

## 11. Open Questions (if any)

- none

## 12. Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | Phase 2/3 artifact + targeted backend tests | `fail` (default until executed) | required | must prove `pipeline_v1` remains unchanged as the source of findings |
| Narrow seam proof | service-level tests + code review | `fail` (default until executed) | required | must prove synthesis is added after deterministic findings at the `StructuredReviewerService` seam |
| Raw machine reason preservation | targeted backend test/assertion | `fail` (default until executed) | required | must prove raw machine `reason` is still preserved for audit/debug |
| Prompt-boundary proof | synthesis input contract tests | `fail` (default until executed) | required | must prove prompt inputs exclude raw machine `reason`, full-submission scope, and unrelated findings |
| Output-validation proof | synthesis output contract tests | `fail` (default until executed) | required | must prove malformed or ambiguous output is rejected before exposure |
| Partial-card degradation proof | targeted backend tests | `fail` (default until executed) | required | must prove one rejected synthesis payload only degrades the affected card |
| Whole-review deterministic success proof | targeted backend tests | `fail` (default until executed) | required | must prove the review still completes truthfully when all synthesis is rejected |
| Non-targeted no-attempt proof | targeted backend tests | `fail` (default until executed) | required | must prove out-of-scope calls/cards remain unchanged, do not invoke synthesis, and do not emit synthesis-specific contract data |
| Backend-only seam-proof compatibility | targeted backend tests + planning artifact review | `fail` (default until executed) | required | must prove the first slice closes honestly without forcing public schema/persistence/frontend carry-through |
| Dependent carry-through trigger proof | Phase 2 task decision evidence | `fail` (default until executed) | required | must prove any persistence/API/review-detail/export/frontend work is opened only as an explicit dependent slice |
| Honest non-determinism test strategy | Phase 2 task plan + verification selectors | `fail` (default until executed) | required | must avoid brittle live-model exact-string assertions |
| Scope-boundary proof | `main...HEAD` review + artifact citations | `fail` (default until executed) | required | must prove no widening into legacy `/reviews`, execution-core substitution, or reopened WF-0075/76/77 scope |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

- No proceed or ship recommendation is valid unless the required rows above pass, or explicitly skip with approved rationale where allowed.

## 13. Changelog

- v0.1 (2026-03-13): Initial PRD from brainstorm.
- v0.2 (2026-03-13): Applied audit hardening by locking MVP to backend seam proof, separating public provenance from internal orchestration state, and making the first TDD obligations concrete before marking the PRD ready for Tasks.
- v0.3 (2026-03-13): Closed the backend-proof versus public-contract contradiction by making seam-only outcome tracking explicit, requiring no-attempt proof for non-targeted calls/cards, and deferring public provenance carry-through to a dependent slice.
