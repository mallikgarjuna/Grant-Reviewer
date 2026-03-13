<!-- docs/tasks/completed/task-WF-0076-subordinate-prompt-runtime-consumption.md -->
# WF-0076 — Subordinate Prompt Runtime Consumption

Artifact: task
Version: v0.3
Status: Done
Last Updated: 2026-03-12

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: carry ERC PoC subordinate prompts into the activated expectation payload

Goal:
Project official ERC PoC subordinate prompts from `CallDefinition.canonical_json` onto the live activated expectation payload for the first `poc_idea_innovation` runtime slice, without reopening WF-0074 authoring/governance or broadening the snapshot beyond the smallest additive seam.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR3A, FR10, FR11
Depends on: none
Enables: 2, 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/engine/contracts.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: evaluator `reason` changes, prompt-builder work, new persistence fields, multi-call rollout, docs/governance rewrites
Stop if: canonical subordinate-prompt lookup cannot be derived from the existing `NodeExpectation` to evaluation-element identity already present in the service/runtime path, or if the first live slice would require widening beyond an additive expectation-level child payload
Session boundary after: no
Acceptance Criteria:
- The activated runtime snapshot for the ERC PoC `poc_idea_innovation` path includes an additive expectation-level `subordinate_prompts` payload only where canonical source prompts exist.
- Each carried subordinate prompt preserves stable official prompt ID and prompt text, with source locator metadata included only if needed for deterministic proof.
- The proof remains sourced from the active call definition already ingested in `CallDefinition.canonical_json`, not from a hardcoded test-only table or parallel persistence seam.
- The service proof must include one in-test source perturbation that changes the active call definition's subordinate-prompt payload and proves the activated expectation payload follows that change, so a hardcoded parallel map fails closed.
- Existing calls that do not surface canonical subordinate prompts through this seam remain valid without making `subordinate_prompts` mandatory everywhere.
- The tracer verification hook is renamed away from the old expectations-only WF-0074 selector so Task 1 cannot accidentally pass by exercising the superseded boundary proof.
TDD Plan:
- RED: extend `backend/tests/test_structured_reviewer_service.py` so the existing ERC PoC runtime-boundary test fails once it expects canonical subordinate prompts to appear on the activated expectation payload for `poc_idea_innovation`, and add a paired source-perturbation assertion that would fail if the service used a hardcoded prompt map instead of live `CallDefinition.canonical_json`.
- GREEN: implement the smallest service-to-contract projection needed to attach canonical subordinate prompts to activated expectations and keep non-ERC or flat-compat paths valid without fabricated data.
- REFACTOR: extract one tiny helper inside `structured_reviewer_service.py` only if the canonical lookup logic becomes unreadable inline.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0076"`
- `cd backend && rg -n "subordinate_prompts|call_config_snapshot|expectations" app/services/structured_reviewer_service.py app/engine/contracts.py tests/test_structured_reviewer_service.py`
Risks (if any): If the service carries prompts by a new parallel map instead of existing evaluation-element identity, the proof would look green while bypassing the approved canonical source seam.

### [x] Task 2 — Harden the request contract and validator for the additive payload

Goal:
Fail closed on malformed expectation-level subordinate prompts while keeping the widened runtime contract digest-safe and additive.
Slice: contract-hardening
User Stories: US1, US3
PRD Requirements: FR2, FR3, FR4, FR8, FR11
Depends on: 1
Enables: 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
May touch files:
- `backend/app/engine/contracts.py`
Out of scope: service lookup logic, evaluator `reason` behavior, review-card prose changes, non-runtime authoring surfaces
Stop if: malformed subordinate-prompt rejection would require making unrelated snapshot sections mandatory or introducing a second contract representation outside the existing request validator
Session boundary after: no
Acceptance Criteria:
- Request validation accepts the additive expectation-level `subordinate_prompts` shape without requiring unrelated snapshot fields.
- Canonical digesting remains stable for valid subordinate-prompt carriage.
- Malformed subordinate-prompt items fail closed deterministically, including missing required fields and duplicate subordinate-prompt IDs within one activated expectation.
- An otherwise valid activated payload without subordinate-prompt carriage still validates so the later negative runtime proof can remove carriage without becoming an invalid-contract proof instead.
TDD Plan:
- RED: add targeted contract tests in `backend/tests/engine/test_review_request_contracts.py` covering valid additive subordinate-prompt carriage, malformed item rejection, duplicate prompt-ID rejection, and the no-carriage-but-still-valid negative setup.
- GREEN: implement the narrowest validator and contract checks needed to pass those tests while keeping the snapshot additive.
- REFACTOR: keep contract validation close to the existing request-validation seam; do not introduce a second normalization layer.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "subordinate_prompt or activated_expectation"`
- `cd backend && uv run pytest tests/test_review_request_validator.py`
- `cd backend && rg -n "subordinate_prompts|digest|Duplicate" app/engine/review_request_validator.py app/engine/contracts.py tests/engine/test_review_request_contracts.py`
Risks (if any): If the negative case becomes a schema-invalid payload instead of a valid no-carriage payload, WF-0076 would overclaim runtime proof while only proving schema rejection.

### [x] Task 3 — Prove subordinate prompts change live evaluator output and disappear without carriage

Goal:
Use the smallest active execution seam to prove subordinate prompts influence structured-review behavior on the ERC PoC `poc_idea_innovation` path by changing evaluator-produced finding `reason`, then prove that signal disappears when carriage is removed from an otherwise valid request.
Slice: runtime-consumption
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR8, FR9, FR10, FR12
Depends on: 2
Enables: 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/engine/findings/evaluator.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: prompt-builder routing, broad `pipeline_v1` redesign, subjective review-card quality scoring, non-ERC runtime claims
Stop if: changing finding `reason` for the active path would require new snapshot sections outside activated expectations, or if the only available proof surface is a non-active prompt-building seam
Session boundary after: yes
Acceptance Criteria:
- One deterministic ERC PoC live-path test shows evaluator-produced finding `reason` now carries official subordinate-prompt signal for the chosen `poc_idea_innovation` expectation path.
- A paired negative live-path test proves the signal disappears when `subordinate_prompts` carriage is removed from an otherwise valid activated payload.
- Where multiple official subordinate prompts exist for the chosen expectation path, the proof keeps their stable prompt IDs distinguishable in the evaluator signal instead of collapsing them into one indistinguishable summary string.
- One explicit output-level proof, separate from the raw evaluator-finding assertion, proves the live surfaced artifact for the same expectation path now carries at least one previously omitted official subordinate-prompt signal in deterministic review-card feedback or another already-active execution surface.
- The service-level ERC PoC runtime test proves the live structured-review path reaches the new evaluator proof without reopening broader runtime scope.
- Verification continues to cite the existing ERC PoC page-43 coverage proof so WF-0075 proof-call completeness remains preserved rather than redefined here.
TDD Plan:
- RED: add a targeted `backend/tests/test_review_engine_pipeline_v1.py` expectation-evaluation test, a paired no-carriage negative case, one assertion that multiple carried prompt IDs stay distinguishable for the chosen ERC PoC expectation path, and one separate output-level assertion that deterministic review-card feedback (or another already-active surfaced artifact) now retains the official subordinate-prompt signal; then tighten `backend/tests/test_structured_reviewer_service.py` so ERC PoC runtime execution must expose the new signal.
- GREEN: implement the smallest evaluator change that derives a deterministic `reason` signal from activated expectation-level subordinate prompts on the live path.
- REFACTOR: keep the signal format terse and source-grounded; extract a helper only if the evaluator would otherwise duplicate prompt-formatting logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0076 or subordinate_prompt"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0076"`
- `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075_real_erc_poc_page_43_proof_call_is_fully_encoded"`
Risks (if any): If the new signal is only asserted at review-card prose level, the proof can pass despite evaluator behavior remaining generic and non-source-grounded.

### [x] Task 4 — Conditional boundary/governance clarification only if executable proof leaves ambiguity

Goal:
Apply a minimal durable-governance clarification only if Tasks 1-3 still leave unresolved ambiguity about WF-0074/WF-0075 prior truth, compatibility posture, or WF-0076 runtime-proof boundaries.
Execution note (2026-03-12): Skipped by condition; executable proof from Tasks 1-3 was sufficient and unambiguous.
Slice: conditional-closure
User Stories: US3
PRD Requirements: FR10, FR11, FR12
Depends on: 1, 2, 3
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/logs/decisions.md`
- `docs/memory/domain/project_docs.md`
- `backend/tests/test_call_yaml_authoring_contract.py`
May touch files:
- `none`
Out of scope: unconditional docs churn, new runtime code, reopening WF-0074 authoring/governance mechanisms, broad product claims
Stop if: executable proof from Tasks 1-3 is already unambiguous, or if clarification would require more than these three files
Session boundary after: yes
Acceptance Criteria:
- This task is skipped unless executable proof shows a real ambiguity that cannot be closed by code/tests alone.
- If executed, the updates preserve explicit prior truth that WF-0074 solved authoring/governance and WF-0075 solved ERC PoC proof-call completeness, while WF-0076 solves only runtime consumption.
- Any added contract test fails closed on the exact ambiguity found and does not invent a broader governance requirement.
TDD Plan:
- RED: only if needed, add one narrow docs-contract test in `backend/tests/test_call_yaml_authoring_contract.py` that reproduces the residual ambiguity found after Tasks 1-3.
- GREEN: update only the minimum durable-governance surfaces needed to close that specific ambiguity.
- REFACTOR: skip unless a residual ambiguity exists.
Verification Steps:
- If executed: `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0076"`
- `rg -n "WF-0074|WF-0075|WF-0076|runtime consumption|prior truth|compatibility" docs/logs/decisions.md docs/memory/domain/project_docs.md`
Risks (if any): Making this unconditional would reopen prior-truth governance scope and violate the PRD's narrow runtime-only boundary.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Runtime discard-seam closure | structured-review activation snapshot | `backend/tests/test_structured_reviewer_service.py -k "wf0076"` | ERC PoC activated expectations carry canonical subordinate prompts where available | `fail` (default until executed) | pytest output in `backend/tests/test_structured_reviewer_service.py` | must prove the live service seam no longer drops them |
| Canonical source lookup proof | service projection from `CallDefinition.canonical_json` | `backend/tests/test_structured_reviewer_service.py -k "wf0076"` | carried prompts are sourced from existing canonical call-definition JSON through expectation/evaluation-element identity | `fail` (default until executed) | pytest output + captured snapshot assertions in `backend/tests/test_structured_reviewer_service.py` | no hardcoded parallel seam |
| Additive contract acceptance | request validator | `backend/tests/engine/test_review_request_contracts.py -k "subordinate_prompt"` | additive expectation-level subordinate-prompt payload validates and digests deterministically | `fail` (default until executed) | pytest output in `backend/tests/engine/test_review_request_contracts.py` | unrelated snapshot fields remain optional |
| Malformed-payload rejection | request validator | `backend/tests/engine/test_review_request_contracts.py -k "subordinate_prompt"` | malformed subordinate-prompt items and duplicate prompt IDs fail closed | `fail` (default until executed) | pytest output in `backend/tests/engine/test_review_request_contracts.py` | required fail-closed contract row |
| Runtime consumption proof | evaluator live path | `backend/tests/test_review_engine_pipeline_v1.py -k "wf0076"` | evaluator-produced finding `reason` carries official subordinate-prompt signal for one ERC PoC expectation path | `fail` (default until executed) | pytest output in `backend/tests/test_review_engine_pipeline_v1.py` | stronger than snapshot-only proof |
| Negative live-path proof | evaluator live path without carriage | `backend/tests/test_review_engine_pipeline_v1.py -k "wf0076"` | removing subordinate-prompt carriage from an otherwise valid payload removes the official signal | `fail` (default until executed) | pytest output in `backend/tests/test_review_engine_pipeline_v1.py` | positive-only proof is insufficient |
| Output-level improvement proof | deterministic surfaced runtime artifact | `backend/tests/test_review_engine_pipeline_v1.py -k "wf0076"` | deterministic review-card feedback or another already-active surfaced artifact carries at least one previously omitted official subordinate-prompt signal for the chosen expectation path | `fail` (default until executed) | pytest output in `backend/tests/test_review_engine_pipeline_v1.py` and/or `backend/tests/test_structured_reviewer_service.py` | keep separate from the raw evaluator-finding row |
| ERC PoC proof-call preservation | real proof-call coverage regression | `backend/tests/test_call_subordinate_prompt_coverage.py -k "wf0075_real_erc_poc_page_43_proof_call_is_fully_encoded"` | WF-0075 page-43 completeness remains fully encoded while WF-0076 changes runtime consumption only | `fail` (default until executed) | pytest output in `backend/tests/test_call_subordinate_prompt_coverage.py` | preserves prior truth instead of re-solving it |
| WF-0074 compatibility posture | representative no-carriage validation path | `backend/tests/engine/test_review_request_contracts.py -k "subordinate_prompt"` | valid payloads without subordinate-prompt carriage still validate, preserving additive compatibility posture | `fail` (default until executed) | pytest output in `backend/tests/engine/test_review_request_contracts.py` | do not silently make carriage universal |
| Boundary honesty | scope proof plus prior-artifact citations | `git diff --name-only main...HEAD` plus approved WF-0074/WF-0075 artifact citations | closure language stays limited to runtime consumption and does not reopen authoring/governance or proof-call completeness | `fail` (default until executed) | closeout artifact with cited PRD/task evidence | required before proceed/ship |
| Audit disposition | findings-closure ledger | Phase 2/3 closeout ledger | every blocking finding is closed and every justified non-blocking finding is closed or rejected with rationale | `fail` (default until executed) | task or walkthrough audit ledger | fail-closed closure gate |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 1 verification still referenced the superseded expectations-only WF-0074 selector, which could let the tracer step pass against the wrong proof seam | non-blocking | narrow Task 1 acceptance and verification to WF-0076-specific selectors only | closed | closed in v0.2 |
| Phase 2.2 task review | Task 3 did not explicitly require multiple carried subordinate prompts to remain distinguishable in the evaluator proof signal | non-blocking | add a specific acceptance and RED assertion for stable prompt-ID distinguishability | closed | closed in v0.2 |
| Phase 2.2 task review | Task 4's verification command looked unconditional even though the task is intentionally conditional | non-blocking | mark the pytest command as conditional execution only | closed | closed in v0.2 |
| Phase 2.2 task review | The verification matrix dropped the PRD-required output-level improvement proof row, which could let Phase 3 ship without explicit pass/fail evidence for operationalized improvement | blocking | add a distinct Task 3 acceptance/TDD requirement and verification-matrix row for deterministic surfaced-artifact proof | closed | closed in v0.3 |
| Phase 2.2 task review | Task 1's canonical-source lookup proof could still pass with a hardcoded parallel map because it did not require a source-perturbation assertion against live `CallDefinition.canonical_json` | blocking | strengthen Task 1 acceptance/TDD so the service test mutates the active source payload and proves the activated expectation payload follows it | closed | closed in v0.3 |
| Phase 2.2 task review | Task 2 verification omitted the shared validator suite even though the task changes `review_request_validator.py` and the strict request contract | non-blocking | add a targeted `backend/tests/test_review_request_validator.py` verification run alongside the engine contract suite | closed | closed in v0.3 |

## Changelog

- v0.1 (2026-03-12): Initial task breakdown from PRD.
- v0.2 (2026-03-12): Applied Part B feedback by tightening the Task 1 verification hook, making Task 3 preserve distinguishable prompt identity in the live proof, and making Task 4's conditional verification explicit before marking the plan ready for implementation.
- v0.3 (2026-03-12): Restored the missing output-level improvement proof row, strengthened Task 1 with a source-perturbation proof against live `CallDefinition.canonical_json`, and widened Task 2 verification to include the shared validator suite.
