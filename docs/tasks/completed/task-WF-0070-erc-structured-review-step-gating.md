<!-- docs/tasks/task-WF-0070-erc-structured-review-step-gating.md -->
# WF-0070 — ERC Structured Review: Enforce Step 1 vs Step 2 Evaluation Gating — Tasks

Artifact: task
Version: v0.3
Status: Approved for Implementation
Last Updated: 2026-03-10

---

## Task Breakdown (Sequential Order)

---

### [x] Task 1 — Author proposal-surface stage-scope contract in canonical ERC call YAML

Goal: Make the canonical ERC call definition the sole authored proposal-surface stage-truth source for structured review. Resolve the `b2_part2_scientific_proposal` drift (currently `BOTH`) to the correct `STEP_2`-only contract. All downstream tasks derive from this source.
Slice: stage-truth-source
User Stories: US1, US3
PRD Requirements: FR2, FR3, FR8
Depends on: none
Enables: Task 2, Task 3, Task 4, Task 5
Parallelizable: no
Files to modify:
  Must touch files:
    - `backend/data/calls/erc_stg/call.yaml` (or equivalent canonical ERC call definition file)
  May touch files:
    - `backend/app/schemas/call.py` or equivalent call-definition schema if a new `proposal_stage_scope` field must be introduced or validated
  Out of scope: node-level `review_stage` metadata derivation code changes (Task 2), runtime activation code (Task 5), test harness changes (Tasks 6–9)
Stop if:
  - The canonical ERC call YAML has no schema seam for per-surface stage scope and adding one would require redesigning the shared call-definition schema broadly → surface as blocker.
  - The correct `STEP_2` classification for `b2_part2_scientific_proposal` contradicts locked domain evidence → surface as blocker.
Session boundary after: no
Acceptance Criteria:
  - `call.yaml` contains one authored `proposal_surface_stage_scope` section listing each ERC structured-review proposal surface with its canonical stage (`STEP_1`, `STEP_2`, or `BOTH`).
  - `b2_part2_scientific_proposal` is marked `STEP_2` (not `BOTH`).
  - No other file treats ERC surface-stage truth as an independently authored peer source.
TDD Plan:
  RED: Write `test_erc_call_stage_scope_contract.py` asserting (a) `proposal_surface_stage_scope` key exists, (b) each surface has exactly one of `STEP_1|STEP_2|BOTH`, (c) `b2_part2_scientific_proposal == STEP_2`. Run → fails (field absent).
  GREEN: Author the `proposal_surface_stage_scope` block in `call.yaml` → test passes.
  REFACTOR: Confirm field name is consistent with existing call-definition conventions; rename if needed.
Verification Steps:
  - `pytest backend/tests/unit/test_erc_call_stage_scope_contract.py -v` → all assertions pass.
  - `grep -n "b2_part2_scientific_proposal" backend/data/calls/erc_stg/call.yaml` → shows `STEP_2`.
  - Manual: confirm no other YAML section re-authors stage truth for the same surfaces.
Risks:
  - Existing tests or fixtures may assert `BOTH` for `b2_part2_scientific_proposal`; those go RED and must be updated in Task 2 REFACTOR or this task's REFACTOR step.

---

### [x] Task 2 — Derive node-level stage-eligibility metadata from the authoritative contract

Goal: Replace or regenerate the existing `review_stage` node metadata used by the frontend `isNodeEligibleForStage()` helper so it is produced from (derived from) the Task 1 authoritative contract rather than being a peer-authored truth source. Add a derivation-parity test confirming UI eligibility metadata and runtime activation inputs both trace to the same source.
Slice: stage-truth-source
User Stories: US1, US3
PRD Requirements: FR2, FR3, FR7, FR8
Depends on: Task 1
Enables: Task 3, Task 4, Task 5
Parallelizable: no
Files to modify:
  Must touch files:
    - Backend derivation helper or service that generates/exposes per-node stage eligibility from the canonical call config (e.g., `backend/app/services/call_config_service.py` or equivalent)
  May touch files:
    - Any fixture or seed file caching per-node `review_stage` values that now contradict the Task 1 source
  Out of scope: frontend code changes (Task 8), runtime activation code (Task 5), persisted evidence fields (Task 6)
Stop if:
  - Derivation cannot be made without introducing a new peer-authored mapping file independent of Task 1's contract → surface as blocker.
  - Fixing derived metadata for `b2_part2_scientific_proposal` propagates breaking changes to more than 3 unrelated call configurations → surface as blocker before proceeding.
Session boundary after: no
Acceptance Criteria:
  - A derivation-parity test passes proving that the set of ERC proposal-surface stage labels provided to the UI and the set provided to runtime activation are both produced from the same Task 1 authored contract — not two independent mappings.
  - No fixture or code file independently authors a `review_stage` node value for ERC proposal surfaces contradicting the Task 1 contract.
TDD Plan:
  RED: Write `test_erc_stage_derivation_parity.py` asserting `derive_ui_stage_labels(surface_id)` and `derive_activation_stage(surface_id)` return the same value for each ERC surface and both trace to Task 1 contract. Run → fails if two separate sources exist.
  GREEN: Implement/refactor derivation helper to use Task 1 contract as single source → test passes.
  REFACTOR: Remove any stale fixture/seed file duplicating stage truth; update affected unit tests to use derived values.
Verification Steps:
  - `pytest backend/tests/unit/test_erc_stage_derivation_parity.py -v` → passes.
  - `grep -rn "b2_part2_scientific_proposal" backend/` → all occurrences reference authoritative contract derivation; no hardcoded `BOTH` or `STEP_2` remain outside the canonical YAML.
Risks:
  - Existing unit tests may mock `review_stage: BOTH` for `b2_part2_scientific_proposal` → must be updated.

---

### [x] Task 3 — Fail-closed BFF: reject invalid/missing `review_stage` instead of coercing to STEP_1

Goal: Harden the BFF structured-review route (`frontend/src/app/api/bff/structured-review/route.ts` or equivalent) to fail closed on invalid or absent `review_stage` values instead of normalizing them to `STEP_1`. This preserves explicit request meaning at the earliest trust boundary.
Slice: fail-closed-validation
User Stories: US1, US4
PRD Requirements: FR1, FR4, FR6, FR13
Depends on: Task 1
Enables: Task 4, Task 9
Parallelizable: no
Files to modify:
  Must touch files:
    - `frontend/src/app/api/bff/structured-review/route.ts` (or equivalent BFF route file)
  May touch files:
    - BFF validation schema or enum definition for `review_stage` if one exists separately
  Out of scope: backend validation changes (Task 4), runtime activation (Task 5), backend test files (Tasks 6–9)
Stop if:
  - Removing the coercion breaks an upstream caller dependency that cannot be updated within this WF → surface as blocker.
  - The coercion actually lives elsewhere in the frontend layer (not the BFF route) → update task target file but do not widen scope.
Session boundary after: no
Acceptance Criteria:
  - POST to BFF with an invalid `review_stage` enum value → explicit 4xx error, no execution or persistence side effects.
  - POST with missing `review_stage` → explicit 4xx error.
  - POST with `review_stage: STEP_1` or `STEP_2` → passes through unmodified.
  - No coercion to `STEP_1` remains anywhere in the BFF code path.
TDD Plan:
  RED: Write `bff-structured-review.test.ts` asserting (a) invalid enum → error, (b) missing stage → error, (c) `STEP_1` → passthrough, (d) `STEP_2` → passthrough. Run → (a) and (b) fail because current code coerces to `STEP_1`.
  GREEN: Replace coercion with enum validation + fail-closed error response → tests pass.
  REFACTOR: Align error shape with existing BFF error conventions; skip if already aligned.
Verification Steps:
  - `npm test -- --testPathPattern=bff/structured-review` (or project equivalent) → all four cases pass.
  - Manual: POST with `review_stage: "INVALID"` → 4xx; no server-side side effects.
Risks:
  - If BFF currently uses `STEP_1` as a safe default elsewhere (not just the coercion), that assumption breaks and must be logged as a known-gap blocker.

---

### [x] Task 4 — Backend: validate submitted ERC leaf ids against authoritative stage-truth before execution

Goal: Harden `POST /api/structured-review` to validate, fail-closed, that every submitted ERC leaf id is eligible under the chosen `review_stage` (from the Task 1 authoritative contract) before any runtime execution or persistence side effect. Errors must identify offending node ids explicitly.
Slice: tracer-bullet / fail-closed-validation
User Stories: US1, US3, US4
PRD Requirements: FR4, FR5, FR6, FR13
Depends on: Task 1, Task 2
Enables: Task 5, Task 9
Parallelizable: no
Files to modify:
  Must touch files:
    - `backend/main.py` or equivalent backend structured-review API endpoint handler
  May touch files:
    - `backend/app/validators/structured_review_validator.py` or equivalent request validation module if the leaf-id stage check lives there
  Out of scope: runtime activation changes (Task 5), persisted evidence fields (Task 6), review-detail projection (Task 7), single-node `POST /api/reviews` path
Stop if:
  - Backend validation requires touching the single-node `POST /api/reviews` path to remain honest → surface as explicit blocker/follow-on (FR17); do not widen scope.
  - Tightening stage validation changes observable behavior of the `Idempotency-Key` replay or payload-hash conflict path for valid canonical requests → surface as blocker; do not proceed.
Session boundary after: yes
Acceptance Criteria:
  - Valid `review_stage` + in-scope leaf ids → passes validation, proceeds to execution.
  - `review_stage: STEP_1` + a `STEP_2` leaf id → rejected before execution with an explicit error listing offending leaf id(s); no side effects.
  - Missing or malformed `review_stage` → explicitly rejected with 422 error; no backend defaulting to a valid stage.
  - No silent dropping, no fallback rerouting, no post-persistence failure mode.
  - Existing `Idempotency-Key` replay and payload-hash conflict behavior for valid requests is unchanged.
  - A request with valid `review_stage` but empty `submitted_leaf_ids: []` is handled deterministically — either accepted as a zero-node run or rejected with an explicit validation error; no silent undefined behaviour. (SF2: edge-case from FR5)
TDD Plan:
  RED: Write `test_backend_stage_leaf_validation.py` cases: (a) valid Step 1 → passes, (b) Step 1 + Step 2 leaf id → 422 with offending ids, (c) valid Step 2 → passes, (d) invalid or missing stage → 422, (e) idempotency replay of valid request → semantics preserved. Run → (b), (d) and/or (e) fail if current code is fail-open.
  GREEN: Add/extend stage-aware leaf-id validation using Task 2 derivation helper → all cases pass.
  REFACTOR: Confirm validation runs strictly before any execution or persistence call; move if needed.
Verification Steps:
  - `pytest backend/tests/unit/test_backend_stage_leaf_validation.py -v` → all cases pass.
  - `pytest backend/tests/integration/ -k "structured_review" -v` → no idempotency or payload-hash regressions.
Risks:
  - Current `matches_review_stage()` node-granularity check may silently pass some Stage 2 leaf ids; this task replaces or wraps that check with the authoritative contract lookup.

---

### [x] Task 5 — Stage-scoped runtime activation: derive activated expectation set from authoritative contract before execution

Goal: Before pipeline execution, the structured-review service must derive a stage-scoped runtime snapshot (activated expectation set) from the Task 1 authoritative contract and the validated submitted ERC leaves, rather than trusting repository expectations on submitted nodes alone. Step 1 execution must not activate Step 2-only ERC expectations.
Slice: runtime-activation
User Stories: US1, US3, US4
PRD Requirements: FR7, FR8, FR13
Depends on: Task 1, Task 2, Task 4
Enables: Task 6, Task 7
Parallelizable: no
Files to modify:
  Must touch files:
    - `backend/app/services/structured_review_service.py` or equivalent runtime builder / activation seam
  May touch files:
    - `backend/app/services/expectation_builder.py` (or equivalent runtime expectation-builder — resolve actual path before editing; do not widen if not needed)
  Out of scope: persisted evidence fields (Task 6), review-detail projection (Task 7), evaluator/pipeline core internals (must remain call-agnostic per FR8)
Stop if:
  - The shared execution core cannot consume the stage-scoped activation snapshot without broad evaluator specialization requiring ERC-specific branches inside the evaluator or pipeline core → surface as blocker (FR8, FR17); do not proceed.
  - Activation fix requires touching `activate_expectations_for_stage()` in a way that affects all call types, not just ERC structured review → surface as blocker.
Session boundary after: yes
Acceptance Criteria:
  - Step 1 structured-review request → activates only expectation items associated with Step 1-eligible ERC surfaces.
  - Step 2 structured-review request → activates only expectation items for Step 2-eligible surfaces (including `BOTH`).
  - Zero Step 2-only ERC expectations are activated during a Step 1 run.
  - Evaluator/pipeline core contains no new ERC-specific branching; stage scope is expressed entirely as a pre-execution activation snapshot passed into the existing core interface.
TDD Plan:
  RED: Write `test_erc_stage_scoped_activation.py` cases: (a) Step 1 → activated expectations contain only Step 1-eligible items, (b) Step 2 → activated expectations contain Step 2-eligible items, (c) Step 1 → zero Step 2-only expectations activated. Run → (a) and (c) fail (current code builds expectations directly from repo expectations on submitted nodes).
  GREEN: Implement pre-execution stage-scope snapshot derivation; pass snapshot to execution core → tests pass.
  REFACTOR: Grep evaluator/pipeline core for new ERC-specific conditionals → none; refactor to activation seam if any found.
Verification Steps:
  - `pytest backend/tests/unit/test_erc_stage_scoped_activation.py -v` → all cases pass.
  - Grep evaluator/pipeline core files for new ERC-specific conditionals → none found.
Risks:
  - If the repo expectation builder does not accept a pre-scoped activation input today, a new seam must be added at the service layer without touching evaluator internals.

---

### [x] Task 6 — Persist `stage_scope_leaf_ids` to structured-review payload

Goal: Extend the persisted structured-review payload with one derived `stage_scope_leaf_ids` field capturing the in-scope ERC leaf set used for the completed review. This makes executed scope reconstructable without live recomputation from current call config.
Slice: persisted-evidence
User Stories: US2, US3
PRD Requirements: FR9, FR10, FR13
Depends on: Task 1, Task 2, Task 5
Enables: Task 7, Task 9
Parallelizable: no
Files to modify:
  Must touch files:
    - Review persistence/repository seam (`backend/app/repositories/review_repository.py` or `backend/app/models/review.py` or equivalent)
  May touch files:
    - One database migration file if `stage_scope_leaf_ids` is a new persisted column
  Out of scope: review-detail projection (Task 7), frontend rendering (Task 8), BFF normalization not related to the new field, single-node path
Stop if:
  - Adding `stage_scope_leaf_ids` requires schema changes to a shared base model used across all review types in a way that cannot be scoped to structured ERC reviews only → surface as blocker.
  - The persistence seam lacks a test harness and adding one would require more than 2 additional files → surface scope concern.
Session boundary after: no
Acceptance Criteria:
  - After a successful ERC Step 1 or Step 2 structured-review run, the persisted review record includes `stage_scope_leaf_ids` containing the exact set of ERC leaf ids in scope for the completed review stage.
  - `review_stage` and `submitted_leaf_ids` remain unchanged.
  - The field value is derived from the Task 1 authoritative contract snapshot at review-run time, not recomputed live from current config at read time.
TDD Plan:
  RED: Write `test_structured_review_persisted_evidence.py` asserting that after a successful ERC structured-review the stored record has a non-empty `stage_scope_leaf_ids` matching the expected set for the stage. Run → fails (field absent).
  GREEN: Add `stage_scope_leaf_ids` field, populate from activation snapshot during persistence; add migration → test passes.
  REFACTOR: Confirm field is populated only for ERC structured reviews (not all review types); add scope guard if needed.
Verification Steps:
  - `pytest backend/tests/unit/test_structured_review_persisted_evidence.py -v` → passes.
  - `alembic upgrade head` (or equivalent) → completes without error.
  - `pytest backend/tests/integration/ -k "structured_review" -v` → no idempotency or payload-hash regressions.
Risks:
  - Migration ordering; ensure this migration does not conflict with any outstanding unmerged migration on `main`.

---

### [x] Task 7 — Review-detail projection: stage-aware boundary buckets distinguishing out-of-scope from not-reviewed

Goal: Update backend review-detail response assembly (and BFF normalization if needed) so that ERC Step 1 review detail projects Step 2-only surfaces as explicitly `out_of_scope` rather than `not_reviewed`, using persisted `stage_scope_leaf_ids` from Task 6. Projection must not require live recomputation from current call config.
Slice: persisted-evidence
User Stories: US2, US4
PRD Requirements: FR10, FR11, FR12, FR13
Depends on: Task 5, Task 6
Enables: Task 8, Task 9
Parallelizable: no
Files to modify:
  Must touch files:
    - Backend review-detail response assembly module (`backend/app/services/review_detail_service.py` or equivalent)
  May touch files:
    - BFF review-detail normalization layer (`frontend/src/app/api/bff/review-detail/route.ts` or equivalent) if stage-aware buckets must be surfaced through the BFF
  Out of scope: frontend rendering of the buckets (Task 8), compliance-message redesign (DS4), visual polish
Stop if:
  - Projecting `out_of_scope` requires live recomputation from current call config rather than from persisted `stage_scope_leaf_ids` → violates FR11; must be resolved before proceeding.
  - Review-detail response schema is shared with all review types and `out_of_scope` cannot be added without affecting all paths → surface as blocker or scoped addition.
Session boundary after: no
Acceptance Criteria:
  - Review-detail response for an ERC Step 1 review includes three explicit buckets: reviewed in-scope ERC surfaces, visible/submitted-but-not-reviewed in-scope surfaces, and out-of-scope Step 2-only surfaces.
  - No Step 2-only ERC surface appears in the `not_reviewed` bucket for a Step 1 review.
  - Projection derives from persisted `stage_scope_leaf_ids`, not from a live config re-fetch.
  - Step 2 review detail correctly places Step 2-only surfaces as in-scope.
TDD Plan:
  RED: Write `test_review_detail_stage_aware_buckets.py` asserting that a persisted Step 1 ERC structured review detail response has `b2_part2_scientific_proposal` in an `out_of_scope` bucket (not `not_reviewed`). Run → fails.
  GREEN: Implement stage-aware bucket logic in review-detail assembly using `stage_scope_leaf_ids` → test passes.
  REFACTOR: Confirm no live call-config fetch occurs inside the detail projection; mock-free assertion confirms this.
Verification Steps:
  - `pytest backend/tests/unit/test_review_detail_stage_aware_buckets.py -v` → passes.
  - Integration: fetch review-detail for a stored Step 1 ERC review → Step 2-only surfaces appear as `out_of_scope`.
Risks:
  - Existing `visible_not_reviewed_node_logical_ids` logic may be tightly coupled; this task must not refactor that field for all review types — only extend ERC structured-review detail.

---

### [x] Task 8 — Frontend: enforce stage-eligible ERC leaf display and carry explicit `review_stage` in submission

Goal: Update the ERC structured-review submit surface to (a) show only stage-eligible ERC proposal leaves from the Task 2 derived metadata, (b) carry explicit `review_stage` selection in the submission payload, and (c) display stage-aware boundary information from the Task 7 review-detail projection.
Slice: frontend-surface
User Stories: US1, US2
PRD Requirements: FR1, FR4, FR11, FR12
Depends on: Task 2, Task 3, Task 7
Enables: Task 9
Parallelizable: no
Files to modify:
  Must touch files:
    - ERC structured-review submit component/page — resolve path with `find frontend/src -name "*erc*" -o -name "*structured-review*" | grep -v node_modules` before editing; likely under `frontend/src/app/(erc-structured-review)/` or equivalent
  May touch files:
    - Shared `isNodeEligibleForStage()` helper if it still references a stale, non-derived stage source
    - Review-detail rendering component for stage-aware boundary display
  Out of scope: compliance warnings redesign (DS4), visual polish beyond stage-accurate surface display, single-node review path
Stop if:
  - The frontend cannot consume derived stage metadata without introducing a new peer-authored ERC mapping in the frontend codebase → surface as blocker.
  - Fixing `isNodeEligibleForStage()` would affect non-ERC call types non-trivially → isolate fix to ERC or surface as blocker.
Session boundary after: yes
Acceptance Criteria:
  - Selecting ERC Step 1 renders only Step 1-eligible ERC proposal surfaces; `b2_part2_scientific_proposal` is absent.
  - Selecting ERC Step 2 renders the full eligible Step 2 ERC surface set.
  - Submit payload carries `review_stage` explicitly (not defaulted or coerced client-side).
  - Review detail for a Step 1 ERC review displays `b2_part2_scientific_proposal` as out of scope.
TDD Plan:
  RED: Write `erc-structured-review.test.tsx` asserting rendering the ERC Step 1 submit view does not render a node for `b2_part2_scientific_proposal`. Run → fails if current view shows it.
  GREEN: Bind node visibility to derived stage-eligible metadata → test passes.
  REFACTOR: Remove any hardcoded ERC stage conditionals in the frontend submission handler; verify `review_stage` passes through unmodified.
Verification Steps:
  - `npm test -- --testPathPattern=erc-structured-review` → all assertions pass.
  - Manual/smoke: ERC Step 1 submit view → `b2_part2_scientific_proposal` node absent.
  - Manual/smoke: ERC Step 2 submit view → `b2_part2_scientific_proposal` node present.
Risks:
  - `isNodeEligibleForStage()` may be called in non-ERC contexts; changes must be scoped or the helper must accept an explicit stage-truth source argument.

---

### [x] Task 9 — Verification matrix: end-to-end proof, all FR14 blocking tests, and audit-disposition ledger

Goal: Implement all blocking automated test coverage from FR14, add at least one representative end-to-end proof spanning submit → validation → activation → persistence → review-detail for ERC structured review, and produce the audit-disposition ledger and baseline-SHA scope proof required by FR15/FR16 before any readiness or ship recommendation.
Slice: verification
User Stories: US2, US4
PRD Requirements: FR14, FR15, FR16
Depends on: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
Enables: none (terminal task)
Parallelizable: no
Files to modify:
  Must touch files:
    - `backend/tests/integration/test_erc_structured_review_e2e.py` (new or updated E2E integration test covering all seven FR14 proof items)
  May touch files:
    - `frontend/src/` — frontend E2E or integration test for submit + review-detail boundary if not already covered by Task 8
    - `docs/walkthroughs/walkthrough-WF-0070-erc-structured-review-step-gating.md` — scope-proof evidence section (baseline SHA, audit-disposition ledger)
  Out of scope: new product features, scope widening beyond the ERC structured-review trust-closure slice, single-node review path
Stop if:
  - Any FR14 blocking item cannot be covered without modifying the single-node review path → surface as blocker (FR17).
  - Baseline SHA cannot be established because the branch is not anchored to a stable commit range → block ship recommendation until resolved (FR15).
Session boundary after: yes
Acceptance Criteria:
  All seven FR14 blocking proof items have a corresponding passing automated test or explicit end-to-end verification record:
  1. Step 1 happy path (submit + validate + activate + persist + review-detail).
  2. Step 1 with Step 2 node mismatch → fail-closed with explicit offending ids.
  3. Step 1 review-detail boundary proof: `b2_part2_scientific_proposal` is `out_of_scope`, not `not_reviewed`.
  4. Step 2 happy path.
  5. Invalid-stage fail-closed proof at BFF and backend boundaries.
  6. Idempotency and payload-hash parity proof after boundary hardening.
  7. Explicit review-evidence verification for the activated stage scope (`stage_scope_leaf_ids` present and correct).
  - At least one representative E2E test spans all five layers: submit → validation → activation → persistence → review-detail.
  - Scope proof anchored to an explicit baseline SHA or commit range.
  - Audit-disposition ledger in walkthrough closes every blocking finding and either closes or explicitly rejects each justified non-blocking finding with rationale.
TDD Plan:
  RED: Write `test_erc_structured_review_e2e.py` asserting all seven FR14 proof items in sequence. Run → any not-yet-implemented path fails.
  GREEN: Confirm all Tasks 1–8 are implemented; E2E test passes end-to-end.
  REFACTOR: Deduplicate any unit tests superseded by the E2E proof; update ledger.
Verification Steps:
  - `pytest backend/tests/ -k "erc" -v` → all ERC-related test files pass.
  - `pytest backend/tests/integration/test_erc_structured_review_e2e.py -v` → all seven FR14 items pass.
  - `git log --oneline main...HEAD` → baseline SHA documented in walkthrough.
  - Audit-disposition ledger in walkthrough: every blocking finding closed, every justified non-blocking finding accepted or explicitly rejected with rationale.
Risks:
  - If any earlier task introduced a regression not caught by its own test, the E2E test will surface it → treat as STOP condition and fix in the appropriate earlier task before re-running.
  - Worktree-only verification without a committed baseline SHA invalidates the proceed recommendation (FR15).

---

## Changelog

- v0.1 (2026-03-09): Initial task breakdown from PRD v0.3.
- v0.2 (2026-03-09): Applied Part B review findings (all non-blocking): added Task 1+2 to Task 9 Depends on (SF1); added empty-submitted_leaf_ids edge case to Task 4 AC (SF2); replaced Task 8 Must-touch glob placeholder with resolve-before-edit instruction (SF3); named concrete expectation-builder file for Task 5 May touch (SF4); annotated Task 4 as tracer-bullet (SF5).
- v0.3 (2026-03-10): Adversarial harden pass: explicitly added backend missing `review_stage` -> 422 requirement to Task 4 AC (closing FR5 missing-stage default hole), and added idempotency parity test case to Task 4 TDD plan (closing FR13 proof gap). Status changed to Approved for Implementation.
