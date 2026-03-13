<!-- docs/tasks/task-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-13

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: accept one valid ERC PoC synthesized companion at the structured-review seam

Goal:
Prove the structured-review path can attempt bounded per-card synthesis for one `ERC-2026-PoC` assessed card after deterministic findings already exist, while keeping deterministic `feedback_text` as the persisted fallback surface.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR6, FR10, FR10A, FR12
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: `pipeline_v1` edits, legacy `ReviewerService`, schema/API/frontend carry-through, persistence model changes, non-`ERC-2026-PoC` rollout
Stop if: proving accepted synthesis requires widening persisted `ReviewCard` fields, mutating deterministic engine outputs, or touching more than these three files
Session boundary after: no
Acceptance Criteria:
- Before the code change, a targeted failing regression such as `test_wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance` proves the current service path returns deterministic cards only and does not yet expose an accepted additive synthesis result at the service/helper seam.
- After the change, the same regression passes by proving one representative `ERC-2026-PoC` assessed card triggers synthesis only after deterministic card generation and accepts a validated per-card synthesized companion/outcome for that card at a service-test-visible seam.
- A paired regression such as `test_wf0078_contract_erc_poc_feedback_text_remains_deterministic` proves persisted `feedback_text` still equals the WF-0077 deterministic guidance even when accepted synthesis exists at the seam.
- The tracer-bullet implementation stays confined to the approved three-file backend slice.
TDD Plan:
- RED: add `test_wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance` and `test_wf0078_contract_erc_poc_feedback_text_remains_deterministic` in `backend/tests/test_structured_reviewer_service.py`; run them before introducing the synthesis helper so they fail against the current deterministic-only path.
- GREEN: add the smallest structured-review synthesis helper plus the narrow `StructuredReviewerService` orchestration needed to attempt one accepted in-scope card synthesis after deterministic findings, while preserving persisted deterministic `feedback_text`.
- REFACTOR: extract tiny seam-owned helper methods or dataclasses only if the service orchestration becomes hard to read inline; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance or wf0078_contract_erc_poc_feedback_text_remains_deterministic"`
- `cd backend && rg -n "wf0078_contract_erc_poc_(tracer_bullet_synthesis_acceptance|feedback_text_remains_deterministic)|structured_review_synthesis_service|feedback_text" app/services/structured_reviewer_service.py app/services/structured_review_synthesis_service.py tests/test_structured_reviewer_service.py`
Risks (if any): The tracer bullet could accidentally overclaim public rollout if the additive result is not clearly labeled as seam-only proof.

### [ ] Task 2 — Fail closed per card for synthesis rejection, timeout, and out-of-scope no-attempt paths

Goal:
Harden the structured-review seam so invalid or unavailable synthesis degrades only the affected card to deterministic WF-0077 guidance, while non-targeted calls/cards never invoke synthesis at all.
Slice: fail-closed-service-hardening
User Stories: US1, US2, US3, US4
PRD Requirements: FR7, FR8, FR10, FR10A, FR11, FR12, FR13
Depends on: 1
Enables: 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: retry queues, product telemetry expansion, schema/API/detail/export/frontend exposure, cross-call enablement beyond `ERC-2026-PoC`
Stop if: fail-closed handling would require engine changes, batch-level review failure for single-card synthesis rejection, or a fourth file to prove non-targeted no-attempt behavior
Session boundary after: yes
Acceptance Criteria:
- Targeted regressions such as `test_wf0078_contract_erc_poc_card_timeout_falls_back`, `test_wf0078_contract_erc_poc_card_malformed_output_falls_back`, `test_wf0078_contract_erc_poc_card_ungrounded_output_falls_back`, and `test_wf0078_contract_all_cards_rejected_review_still_completes` prove synthesis failure degrades only the affected card and never turns a deterministic-success review into a failed review.
- A targeted regression such as `test_wf0078_contract_non_targeted_calls_do_not_attempt_synthesis` proves non-`ERC-2026-PoC` calls/cards do not invoke the synthesis collaborator and do not emit synthesis-specific seam outcomes.
- The service still persists deterministic `feedback_text` only, even when all synthesis attempts reject.
TDD Plan:
- RED: extend `backend/tests/test_structured_reviewer_service.py` with explicit per-card timeout, malformed-output, ungrounded-output, all-cards-rejected, and non-targeted no-attempt regressions; run them before the hardening change and capture failures against the initial tracer-bullet implementation.
- GREEN: add the minimum service/helper rejection handling needed to convert these scenarios into deterministic per-card fallback or no-attempt behavior without widening the public contract.
- REFACTOR: consolidate repeated fallback classification logic only if Task 1 plus Task 2 create duplicated branch handling; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_card_timeout_falls_back or wf0078_contract_erc_poc_card_malformed_output_falls_back or wf0078_contract_erc_poc_card_ungrounded_output_falls_back or wf0078_contract_all_cards_rejected_review_still_completes or wf0078_contract_non_targeted_calls_do_not_attempt_synthesis"`
- `cd backend && rg -n "wf0078_contract_(erc_poc_card_timeout_falls_back|erc_poc_card_malformed_output_falls_back|erc_poc_card_ungrounded_output_falls_back|all_cards_rejected_review_still_completes|non_targeted_calls_do_not_attempt_synthesis)|deterministic_fallback|accepted_synthesis" app/services/structured_reviewer_service.py app/services/structured_review_synthesis_service.py tests/test_structured_reviewer_service.py`
Risks (if any): If rejection handling is too broad, accepted synthesis could silently stop working for valid cards; if too narrow, malformed output could leak past the seam.

### [ ] Task 3 — Lock the additive synthesis input/output contract and raw-reason exclusion in helper tests

Goal:
Prove the synthesis helper accepts only approved same-card context, excludes raw machine `reason`, and rejects ambiguous or contract-breaking outputs before the service can treat them as accepted synthesis.
Slice: helper-contract-hardening
User Stories: US1, US2, US3
PRD Requirements: FR5, FR6, FR7, FR9, FR13, FR14
Depends on: 1
Enables: 4
Parallelizable: yes
Files to modify:
Must touch files:
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_review_synthesis_service.py`
May touch files:
- `none`
Out of scope: service orchestration rewrites already proven in Tasks 1-2, prompt changes that require full-call/full-submission context, frontend copy work
Stop if: the helper contract cannot be proven without introducing a fourth-file schema/API surface, or if honest grounding checks need unrelated-card context the PRD forbids
Session boundary after: yes
Acceptance Criteria:
- Targeted helper regressions such as `test_wf0078_contract_prompt_payload_excludes_raw_reason`, `test_wf0078_contract_prompt_payload_uses_same_card_context_only`, and `test_wf0078_contract_rejects_ambiguous_or_mismatched_output` prove prompt construction stays within the approved boundary and output validation rejects ambiguous or unrelated-card synthesis.
- Helper tests prove accepted output requires deterministic card identity, same-card node context, relevant evaluation criteria/elements, WF-0077 deterministic guidance, approved subordinate-prompt context, and a bounded excerpt from the same submitted node text.
- Helper tests prove rejected output is dropped rather than partially surfaced.
TDD Plan:
- RED: create `backend/tests/test_structured_review_synthesis_service.py` with explicit payload-boundary and output-validation regressions; run them before helper hardening so they fail on missing exclusions/validation.
- GREEN: implement the smallest helper-level builders/validators needed to pass the new contract tests while preserving the Task 1 seam shape.
- REFACTOR: extract tiny private validators only if the helper starts repeating field checks across prompt-build and response-parse logic; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_review_synthesis_service.py -k "wf0078_contract_prompt_payload_excludes_raw_reason or wf0078_contract_prompt_payload_uses_same_card_context_only or wf0078_contract_rejects_ambiguous_or_mismatched_output"`
- `cd backend && rg -n "wf0078_contract_(prompt_payload_excludes_raw_reason|prompt_payload_uses_same_card_context_only|rejects_ambiguous_or_mismatched_output)|raw machine|same-card|subordinate" app/services/structured_review_synthesis_service.py tests/test_structured_review_synthesis_service.py`
Risks (if any): Prompt-boundary drift here would look harmless in service tests while still reintroducing audit-only machine traces into LLM inputs.

### [ ] Task 4 — Conditional carry-through check; otherwise close as explicit backend-only seam proof

Goal:
Confirm WF-0078 can close honestly at the backend seam without implying persistence/API/review-detail/export/frontend rollout, and open a separate dependent slice only if that broader carry-through is truly required.
Slice: carry-through-decision-gate
User Stories: US1, US4
PRD Requirements: FR6, FR10A, FR11, FR12
Depends on: 2, 3
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `none`
May touch files:
- `none`
Out of scope: proactive schema/API expansion, review-detail UI edits, export changes, walkthrough closeout work
Stop if: Tasks 1-3 already prove honest backend-only seam closure and no real carry-through requirement remains, because this task should then close as an explicit skip rather than create speculative implementation work
Session boundary after: yes
Acceptance Criteria:
- Phase 3 cites concrete proof that accepted/rejected synthesis is currently a backend seam concern only and that persisted/API/frontend surfaces still read deterministic `feedback_text`.
- If broader researcher-visible rollout is required, Phase 3 must stop and author a new dependent follow-on task instead of widening WF-0078 implementation under this plan.
- No implementation claim is made without an explicit audit disposition covering either the backend-only skip or the newly opened dependent slice.
TDD Plan:
- N/A for the default skip path; if a real carry-through need is proven, stop and author a bounded follow-on task before editing code.
Verification Steps:
- `rg -n "class ReviewCardSummary|feedback_text" backend/app/schemas/api.py backend/main.py frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `git diff --name-only -- docs/tasks/task-WF-0078-structured-review-grounded-llm-synthesis.md docs/index.md`
Risks (if any): Without an explicit stop/skip gate, Phase 3 could quietly smuggle API or frontend scope into a backend seam-proof WF.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | 1 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance or wf0078_contract_erc_poc_feedback_text_remains_deterministic"` | synthesis happens only after deterministic cards exist and persisted `feedback_text` remains deterministic | `fail` | required | must prove `pipeline_v1` remains unchanged as the findings source |
| Narrow seam proof | 1 | `git diff -- backend/app/services/structured_reviewer_service.py backend/app/services/structured_review_synthesis_service.py backend/tests/test_structured_reviewer_service.py` | first slice stays at the structured-review seam only | `fail` | required | no execution-core, mapper, or legacy-path widening |
| Partial-card degradation proof | 2 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_card_timeout_falls_back or wf0078_contract_erc_poc_card_malformed_output_falls_back or wf0078_contract_erc_poc_card_ungrounded_output_falls_back"` | rejected synthesis degrades only the affected card | `fail` | required | card-level fail-closed behavior |
| Whole-review deterministic success proof | 2 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_all_cards_rejected_review_still_completes"` | review still completes when all synthesis rejects | `fail` | required | deterministic fallback remains sufficient |
| Non-targeted no-attempt proof | 2 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_non_targeted_calls_do_not_attempt_synthesis"` | out-of-scope calls/cards do not invoke synthesis or emit seam outcomes | `fail` | required | protects `ERC-2026-PoC`-only rollout |
| Prompt-boundary proof | 3 | `backend/tests/test_structured_review_synthesis_service.py -k "wf0078_contract_prompt_payload_excludes_raw_reason or wf0078_contract_prompt_payload_uses_same_card_context_only"` | helper input excludes raw machine `reason`, full-submission scope, and unrelated findings | `fail` | required | approved same-card context only |
| Output-validation proof | 3 | `backend/tests/test_structured_review_synthesis_service.py -k "wf0078_contract_rejects_ambiguous_or_mismatched_output"` | malformed or mismatched output is rejected before acceptance | `fail` | required | no partial surfacing of rejected output |
| Backend-only seam-proof compatibility | 4 | `rg -n "class ReviewCardSummary|feedback_text" backend/app/schemas/api.py backend/main.py frontend/src/app/app/reviews/[reviewId]/page.tsx` | current user-visible surfaces still depend on deterministic `feedback_text`, so backend-only proof can close honestly if explicitly documented | `fail` | required | open a follow-on instead of widening silently |
| Dependent carry-through trigger proof | 4 | task/audit disposition | any API/frontend/persistence carry-through is opened only as an explicit dependent slice | `fail` | required | no implied rollout |
| Scope-boundary proof | 1, 2, 3, 4 | `git diff --name-only main...HEAD` | no widening into `pipeline_v1`, legacy `/reviews`, or unrelated call families | `fail` | required | review gate must check range before proceed |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | pending | pending | revise in Part C if required | open | placeholder until review runs |

## Changelog

- v0.1 (2026-03-13): Initial task breakdown from PRD.
