<!-- docs/tasks/task-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-13

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: accept one valid ERC PoC synthesized companion at the structured-review seam

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
- The accepted additive seam result is carried through a narrow typed helper result owned by `structured_review_synthesis_service.py`, not ad hoc dict mutation on persisted `ReviewCard` objects.
- The tracer-bullet implementation stays confined to the approved three-file backend slice.
TDD Plan:
- RED: add `test_wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance` and `test_wf0078_contract_erc_poc_feedback_text_remains_deterministic` in `backend/tests/test_structured_reviewer_service.py`; run them before introducing the synthesis helper so they fail against the current deterministic-only path.
- GREEN: add the smallest structured-review synthesis helper plus the narrow `StructuredReviewerService` orchestration needed to attempt one accepted in-scope card synthesis after deterministic findings, while preserving persisted deterministic `feedback_text`.
- REFACTOR: extract tiny seam-owned helper methods or dataclasses only if the service orchestration becomes hard to read inline; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance or wf0078_contract_erc_poc_feedback_text_remains_deterministic"`
- `cd backend && rg -n "wf0078_contract_erc_poc_(tracer_bullet_synthesis_acceptance|feedback_text_remains_deterministic)|structured_review_synthesis_service|feedback_text" app/services/structured_reviewer_service.py app/services/structured_review_synthesis_service.py tests/test_structured_reviewer_service.py`
Risks (if any): The tracer bullet could accidentally overclaim public rollout if the additive result is not clearly labeled as seam-only proof.

### [x] Task 2 — Fail closed per card for synthesis rejection and whole-review deterministic completion

Goal:
Harden the structured-review seam so invalid or unavailable synthesis degrades only the affected card to deterministic WF-0077 guidance and never turns a deterministic-success review into a failed review.
Slice: fail-closed-service-hardening
User Stories: US1, US2, US3, US4
PRD Requirements: FR7, FR8, FR11, FR12, FR13
Depends on: 1
Enables: 3, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: retry queues, product telemetry expansion, schema/API/detail/export/frontend exposure, cross-call enablement beyond `ERC-2026-PoC`
Stop if: fail-closed handling would require engine changes, batch-level review failure for single-card synthesis rejection, or persistence/API carry-through to prove fallback honesty
Session boundary after: yes
Acceptance Criteria:
- Targeted regressions such as `test_wf0078_contract_erc_poc_card_timeout_falls_back`, `test_wf0078_contract_erc_poc_card_client_error_falls_back`, `test_wf0078_contract_erc_poc_card_malformed_output_falls_back`, `test_wf0078_contract_erc_poc_card_ungrounded_output_falls_back`, and `test_wf0078_contract_all_cards_rejected_review_still_completes` prove synthesis failure degrades only the affected card and never turns a deterministic-success review into a failed review.
- The service still persists deterministic `feedback_text` only, even when all synthesis attempts reject.
TDD Plan:
- RED: extend `backend/tests/test_structured_reviewer_service.py` with explicit per-card timeout, client-error, malformed-output, ungrounded-output, and all-cards-rejected regressions; run them before the hardening change and capture failures against the initial tracer-bullet implementation.
- GREEN: add the minimum service/helper rejection handling needed to convert these scenarios into deterministic per-card fallback behavior without widening the public contract.
- REFACTOR: consolidate repeated fallback classification logic only if Task 1 plus Task 2 create duplicated branch handling; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_card_timeout_falls_back or wf0078_contract_erc_poc_card_client_error_falls_back or wf0078_contract_erc_poc_card_malformed_output_falls_back or wf0078_contract_erc_poc_card_ungrounded_output_falls_back or wf0078_contract_all_cards_rejected_review_still_completes"`
- `cd backend && rg -n "wf0078_contract_(erc_poc_card_timeout_falls_back|erc_poc_card_client_error_falls_back|erc_poc_card_malformed_output_falls_back|erc_poc_card_ungrounded_output_falls_back|all_cards_rejected_review_still_completes)|deterministic_fallback|accepted_synthesis" app/services/structured_reviewer_service.py app/services/structured_review_synthesis_service.py tests/test_structured_reviewer_service.py`
Risks (if any): If rejection handling is too broad, accepted synthesis could silently stop working for valid cards; if too narrow, malformed output could leak past the seam.

### [x] Task 3 — Prove the real service-emitted prompt payload stays inside the approved boundary

Goal:
Prove `StructuredReviewerService` emits only approved same-card synthesis inputs, excludes raw machine `reason`, and never attempts synthesis for non-targeted calls/cards.
Slice: service-payload-boundary
User Stories: US1, US2, US3, US4
PRD Requirements: FR5, FR9, FR10, FR10A, FR13, FR14
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: helper-only parser validation already deferred to Task 4, prompt changes that require full-call/full-submission context, frontend copy work
Stop if: proving the emitted payload boundary would require widening persisted/API surfaces, or if honest gating needs unrelated-card context the PRD forbids
Session boundary after: yes
Acceptance Criteria:
- Targeted service regressions such as `test_wf0078_contract_emitted_payload_excludes_raw_reason`, `test_wf0078_contract_emitted_payload_uses_same_card_context_only`, `test_wf0078_contract_emitted_payload_excludes_full_call_and_legacy_artifacts`, and `test_wf0078_contract_non_targeted_calls_do_not_attempt_synthesis` prove the real helper request emitted by `StructuredReviewerService` excludes raw machine `reason`, full-submission scope, full call-definition payloads, legacy review artifacts, unrelated findings, and out-of-scope call/card attempts.
- Service tests prove the emitted helper request carries deterministic card identity, same-card node context, relevant evaluation criteria/elements, WF-0077 deterministic guidance, approved subordinate-prompt context, and only a bounded excerpt from the same submitted node text.
- Service tests prove non-`ERC-2026-PoC` calls/cards do not invoke the helper and do not emit synthesis-specific seam outcomes.
TDD Plan:
- RED: extend `backend/tests/test_structured_reviewer_service.py` with explicit emitted-payload, full-call/legacy-artifact exclusion, and non-targeted no-attempt regressions; run them before the service-boundary hardening so they fail on missing exclusions or missing gating.
- GREEN: implement the smallest service/helper payload builder changes needed to pass the new boundary regressions while preserving Tasks 1-2 fallback behavior.
- REFACTOR: extract tiny private payload-builder helpers only if the service starts duplicating same-card boundary logic; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0078_contract_emitted_payload_excludes_raw_reason or wf0078_contract_emitted_payload_uses_same_card_context_only or wf0078_contract_emitted_payload_excludes_full_call_and_legacy_artifacts or wf0078_contract_non_targeted_calls_do_not_attempt_synthesis"`
- `cd backend && rg -n "wf0078_contract_(emitted_payload_excludes_raw_reason|emitted_payload_uses_same_card_context_only|emitted_payload_excludes_full_call_and_legacy_artifacts|non_targeted_calls_do_not_attempt_synthesis)|raw_reason|legacy|call_definition|same-card|subordinate|ERC-2026-PoC" app/services/structured_reviewer_service.py app/services/structured_review_synthesis_service.py tests/test_structured_reviewer_service.py`
Risks (if any): If the service-level payload boundary is not tested directly, helper-level validation can look correct while the live seam still leaks audit-only context into prompts.

### [x] Task 4 — Lock helper output validation for wrong-element, ambiguous-card, and malformed synthesis

Goal:
Prove the synthesis helper rejects wrong-element, ambiguous-card, and malformed outputs before the service can classify them as accepted synthesis.
Slice: helper-output-validation
User Stories: US1, US2, US3
PRD Requirements: FR6, FR7, FR13, FR14
Depends on: 1, 3
Enables: 5
Parallelizable: yes
Files to modify:
Must touch files:
- `backend/app/services/structured_review_synthesis_service.py`
- `backend/tests/test_structured_review_synthesis_service.py`
May touch files:
- `none`
Out of scope: service orchestration changes already covered by Tasks 1-3, persistence/API propagation, frontend copy edits
Stop if: helper validation cannot reject wrong-element or ambiguous-card output without a fourth-file schema/API change, because that would mean the seam contract is underspecified
Session boundary after: yes
Acceptance Criteria:
- Targeted helper regressions such as `test_wf0078_contract_rejects_wrong_element_output`, `test_wf0078_contract_rejects_ambiguous_or_mismatched_output`, and `test_wf0078_contract_rejects_malformed_output` prove the helper drops invalid synthesis before acceptance.
- Helper tests prove rejected output is dropped rather than partially surfaced.
- Helper tests keep the additive contract narrow and deterministic-card-anchored.
TDD Plan:
- RED: create `backend/tests/test_structured_review_synthesis_service.py` with explicit wrong-element, ambiguous-card, and malformed-output regressions; run them before helper hardening so they fail on missing validation.
- GREEN: implement the smallest helper-level validators needed to pass the new output-rejection tests while preserving the Task 1 typed seam contract.
- REFACTOR: extract tiny private validators only if output validation repeats field checks across parse paths; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_review_synthesis_service.py -k "wf0078_contract_rejects_wrong_element_output or wf0078_contract_rejects_ambiguous_or_mismatched_output or wf0078_contract_rejects_malformed_output"`
- `cd backend && rg -n "wf0078_contract_(rejects_wrong_element_output|rejects_ambiguous_or_mismatched_output|rejects_malformed_output)|wrong_element|ambiguous|malformed" app/services/structured_review_synthesis_service.py tests/test_structured_review_synthesis_service.py`
Risks (if any): If helper validation accepts a wrong-element payload, synthesis could present unsupported evaluation-criteria/elements advice as if it were grounded.

### [ ] Task 5 — Conditional carry-through check; otherwise close as explicit backend-only seam proof

Goal:
Confirm WF-0078 can close honestly at the backend seam without implying persistence/API/review-detail/export/frontend rollout, and open a separate dependent slice only if that broader carry-through is truly required.
Slice: carry-through-decision-gate
User Stories: US1, US4
PRD Requirements: FR6, FR10A, FR11, FR12
Depends on: 2, 3, 4
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
- Phase 3 cites concrete proof that accepted/rejected synthesis is currently a backend seam concern only and that persisted `ReviewCard` storage, repository reads, API/review-detail, export, and frontend surfaces still read deterministic `feedback_text` unless a new dependent slice is opened.
- If broader researcher-visible rollout is required, Phase 3 must stop and author a new dependent follow-on task instead of widening WF-0078 implementation under this plan.
- No implementation claim is made without an explicit audit disposition covering either the backend-only skip or the newly opened dependent slice.
TDD Plan:
- N/A for the default skip path; if a real carry-through need is proven, stop and author a bounded follow-on task before editing code.
Verification Steps:
- `rg -n "class ReviewCard|feedback_text|create_review_cards_batch|get_review_cards_with_criteria|ReviewCardSummary|ReviewDetailResponse|export" backend/app/models/domain.py backend/app/repositories/review_repository.py backend/app/schemas/api.py backend/main.py frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `git diff --name-only -- docs/tasks/task-WF-0078-structured-review-grounded-llm-synthesis.md docs/index.md`
Risks (if any): Without an explicit stop/skip gate, Phase 3 could quietly smuggle API or frontend scope into a backend seam-proof WF.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | 1 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance or wf0078_contract_erc_poc_feedback_text_remains_deterministic"` | synthesis happens only after deterministic cards exist and persisted `feedback_text` remains deterministic | `fail` | required | must prove `pipeline_v1` remains unchanged as the findings source |
| Narrow seam proof | 1 | `git diff -- backend/app/services/structured_reviewer_service.py backend/app/services/structured_review_synthesis_service.py backend/tests/test_structured_reviewer_service.py` | first slice stays at the structured-review seam only | `fail` | required | no execution-core, mapper, or legacy-path widening |
| Partial-card degradation proof | 2 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_erc_poc_card_timeout_falls_back or wf0078_contract_erc_poc_card_client_error_falls_back or wf0078_contract_erc_poc_card_malformed_output_falls_back or wf0078_contract_erc_poc_card_ungrounded_output_falls_back"` | rejected synthesis degrades only the affected card for timeout, client-error, malformed, and ungrounded paths | `fail` | required | card-level fail-closed behavior |
| Whole-review deterministic success proof | 2 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_all_cards_rejected_review_still_completes"` | review still completes when all synthesis rejects | `fail` | required | deterministic fallback remains sufficient |
| Non-targeted no-attempt proof | 3 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_non_targeted_calls_do_not_attempt_synthesis"` | out-of-scope calls/cards do not invoke synthesis or emit seam outcomes | `fail` | required | protects `ERC-2026-PoC`-only rollout |
| Prompt-boundary proof | 3 | `backend/tests/test_structured_reviewer_service.py -k "wf0078_contract_emitted_payload_excludes_raw_reason or wf0078_contract_emitted_payload_uses_same_card_context_only or wf0078_contract_emitted_payload_excludes_full_call_and_legacy_artifacts"` | service-emitted helper input excludes raw machine `reason`, full-submission scope, full call-definition payloads, legacy review artifacts, and unrelated findings | `fail` | required | approved same-card context only |
| Output-validation proof | 4 | `backend/tests/test_structured_review_synthesis_service.py -k "wf0078_contract_rejects_wrong_element_output or wf0078_contract_rejects_ambiguous_or_mismatched_output or wf0078_contract_rejects_malformed_output"` | wrong-element, malformed, or mismatched output is rejected before acceptance | `fail` | required | no partial surfacing of rejected output |
| Backend-only seam-proof compatibility | 5 | `rg -n "class ReviewCard|feedback_text|create_review_cards_batch|get_review_cards_with_criteria|ReviewCardSummary|ReviewDetailResponse|export" backend/app/models/domain.py backend/app/repositories/review_repository.py backend/app/schemas/api.py backend/main.py frontend/src/app/app/reviews/[reviewId]/page.tsx` | persisted storage plus user-visible read surfaces still depend on deterministic `feedback_text`, so backend-only proof can close honestly if explicitly documented | `fail` | required | open a follow-on instead of widening silently |
| Dependent carry-through trigger proof | 5 | task/audit disposition | any API/frontend/persistence carry-through is opened only as an explicit dependent slice | `fail` | required | no implied rollout |
| Scope-boundary proof | 1, 2, 3, 4, 5 | `git diff --name-only main...HEAD` | no widening into `pipeline_v1`, legacy `/reviews`, or unrelated call families | `fail` | required | review gate must check range before proceed |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 3 proved prompt-boundary rules only at the helper layer, leaving the real service-emitted payload unverified against FR5/FR9 | blocking | split service-emitted payload proof into a dedicated three-file Task 3 and move helper-only output validation to Task 4 | closed | preserves 3-file slices while closing the hidden-coupling gap |
| Phase 2.2 task review | Task 2 did not name the wrong-evaluation-element rejection case explicitly | non-blocking | add `test_wf0078_contract_rejects_wrong_element_output` in Task 4 and its verification-matrix row | closed | makes the PRD edge case auditable |
| Phase 2.2 task review | Task 4 carry-through check under-described review-detail/export read-surface risk | non-blocking | strengthen Task 5 acceptance and verification to cite persistence/API/review-detail/export/frontend surfaces explicitly | closed | keeps backend-only seam closure honest |
| Phase 2.2 task review | Task 1 did not name the intended typed seam contract for accepted additive synthesis | non-blocking | require a narrow typed helper result in Task 1 acceptance criteria | closed | reduces ad hoc dict/private-attr drift |
| Continuation review | Task 2 omitted explicit client-error fallback proof even though the approved brainstorm/PRD require fail-closed handling for client errors, not just timeouts or malformed output | blocking | add `test_wf0078_contract_erc_poc_card_client_error_falls_back` to Task 2 acceptance, TDD, and verification matrix coverage | closed | closes a real fail-closed hole before implementation starts |
| Continuation review | Task 3 did not explicitly prove the emitted service payload excludes full call-definition material and legacy review artifacts, leaving FR5 passable by narrower same-card assertions alone | blocking | add a dedicated service regression for full-call/legacy-artifact exclusion and expand Task 3 verification selectors accordingly | closed | prevents hidden prompt-scope drift behind the helper seam |
| Continuation review | Task 5 verified API/review-detail/export surfaces only, but not persisted `ReviewCard` storage or repository reads, so backend-only closure could be overstated | non-blocking | extend Task 5 acceptance and verification to inspect model and repository seams alongside API/frontend reads | closed | makes the backend-only closure claim auditable end-to-end |

## Changelog

- v0.1 (2026-03-13): Initial task breakdown from PRD.
- v0.2 (2026-03-13): Applied Part B feedback by splitting service-emitted payload proof from helper output validation, adding explicit wrong-element rejection coverage, strengthening the carry-through gate to include review-detail/export read surfaces, and requiring a typed seam-owned additive result before marking the plan ready for implementation.
- v0.3 (2026-03-13): Applied continuation review hardening by adding explicit client-error fail-closed coverage, requiring service-level proof that prompt payloads exclude full-call and legacy review artifacts, and expanding the backend-only closure check to inspect persisted `ReviewCard` storage and repository reads.
