<!-- docs/tasks/completed/task-WF-0077-structured-review-deterministic-researcher-guidance.md -->
# WF-0077 — Structured Review Deterministic Researcher Guidance

Artifact: task
Version: v0.4
Status: Done
Last Updated: 2026-03-13

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: rewrite one ERC PoC assessed card into deterministic researcher guidance

Goal:
Prove the end-to-end `ERC-2026-PoC` structured-review path can move one assessed card from WF-0076 prompt-list output to concise deterministic revision guidance without widening beyond `StructuredReviewerService` and its service tests.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR4, FR7, FR8, FR9, FR12
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: evaluator changes, mapper changes, legacy `ReviewerService`, frontend edits, new API fields, OpenAI/LLM work, non-`ERC-2026-PoC` rollout
Stop if: producing honest imperative guidance requires evaluator or mapper changes, the service cannot preserve raw machine `reason` while changing `feedback_text`, or the slice would require touching more than these two files
Session boundary after: no
Acceptance Criteria:
- Before the service edit, a targeted failing regression such as `test_wf0077_contract_erc_poc_actionable_guidance` proves the current `ERC-2026-PoC` assessed-card output is still question-shaped or prompt-list-shaped.
- After the service edit, the same targeted regression passes with concise deterministic revision guidance grounded only in the evaluation element label and canonical subordinate-prompt text already carried by the service path.
- A separate targeted regression such as `test_wf0077_contract_erc_poc_reason_passthrough` proves the mocked raw machine reason/source string remains unchanged while the service derives researcher-facing `feedback_text`, with no new persisted or API-exposed `reason` field added in this slice.
- The implementation stays confined to `StructuredReviewerService` plus `backend/tests/test_structured_reviewer_service.py`.
TDD Plan:
- RED: add `test_wf0077_contract_erc_poc_actionable_guidance` in `backend/tests/test_structured_reviewer_service.py` for one representative `ERC-2026-PoC` assessed card; run it before the service edit and capture the failing output showing `feedback_text` still mirrors WF-0076 subordinate-prompt/question output.
- GREEN: implement the narrowest `StructuredReviewerService` guidance rewrite needed to make `test_wf0077_contract_erc_poc_actionable_guidance` pass, then add or keep `test_wf0077_contract_erc_poc_reason_passthrough` proving the mocked machine reason/source string remains unchanged.
- REFACTOR: extract one tiny helper inside `structured_reviewer_service.py` only if the rewrite logic becomes hard to read inline; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_actionable_guidance"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_reason_passthrough"`
- `cd backend && rg -n "wf0077_contract_erc_poc_(actionable_guidance|reason_passthrough)|ERC-2026-PoC|feedback_text|reason" app/services/structured_reviewer_service.py tests/test_structured_reviewer_service.py`
Risks (if any): A vague rewrite could look more readable while still fabricating advice not grounded in the canonical subordinate-prompt source.

### [x] Task 2 — Fail closed on weak source surfaces and protect non-targeted calls

Goal:
Harden the same backend seam so deterministic guidance only applies when `ERC-2026-PoC` source prompts support an honest rewrite, while all non-targeted calls and weak-source cases keep existing deterministic behavior.
Slice: fail-closed-hardening
User Stories: US1, US2, US3
PRD Requirements: FR5, FR6, FR10, FR11, FR12
Depends on: 1
Enables: 3
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: frontend rendering changes, evaluator fallbacks, new persistence, broad call-code expansion, docs-only closure pretending to verify behavior
Stop if: honest fallback handling would require a third backend file, if non-targeted-call safety cannot be proven from service tests alone, or if the only remaining issue is frontend presentation mismatch
Session boundary after: yes
Acceptance Criteria:
- `test_wf0077_contract_non_targeted_passthrough` proves non-`ERC-2026-PoC` calls keep their current deterministic `feedback_text`.
- `test_wf0077_contract_erc_poc_fallback_missing_source`, `test_wf0077_contract_erc_poc_fallback_unresolved_prompt`, and `test_wf0077_contract_erc_poc_fallback_duplicate_source` prove missing, unresolved, duplicated into unusable surfaces, or otherwise weak subordinate-prompt inputs fall back to the existing WF-0076-style prompt rendering instead of invented guidance.
- The implementation remains bounded to the same two files and does not widen the transform beyond the approved `ERC-2026-PoC` slice.
TDD Plan:
- RED: extend `backend/tests/test_structured_reviewer_service.py` with `test_wf0077_contract_non_targeted_passthrough`, `test_wf0077_contract_erc_poc_fallback_missing_source`, `test_wf0077_contract_erc_poc_fallback_unresolved_prompt`, and `test_wf0077_contract_erc_poc_fallback_duplicate_source`; each should fail if the service fabricates stronger guidance instead of preserving WF-0076 fallback output.
- GREEN: add the minimum fail-closed guards inside `StructuredReviewerService` to pass those regressions while leaving existing non-targeted behavior untouched.
- REFACTOR: consolidate helper branching only if Task 1 plus Task 2 logic duplicates source-usability checks; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_non_targeted_passthrough or wf0077_contract_erc_poc_fallback_missing_source or wf0077_contract_erc_poc_fallback_unresolved_prompt or wf0077_contract_erc_poc_fallback_duplicate_source"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0076 or wf0077_contract_"`
- `cd backend && rg -n "wf0077_contract_(non_targeted_passthrough|erc_poc_fallback_missing_source|erc_poc_fallback_unresolved_prompt|erc_poc_fallback_duplicate_source)|WF0076|ERC-2026-PoC" app/services/structured_reviewer_service.py tests/test_structured_reviewer_service.py`
Risks (if any): If weak-source detection is too permissive, Phase 3 could silently replace honest prompt fallback with overconfident guidance text.

### [x] Task 3 — Conditional frontend necessity check; otherwise close as explicit backend-only skip

Goal:
Confirm the current review page still renders `card.feedback_text` directly so WF-0077 can finish backend-only, and only open a separate frontend follow-on if backend proof reveals a real UI truthfulness gap.
Slice: conditional-ui-necessity
User Stories: US1, US3
PRD Requirements: FR13, FR14
Depends on: 1, 2
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `none`
May touch files:
- `none`
Out of scope: proactive frontend polish, card regrouping, copy refresh, styling changes, implementation work without backend proof of necessity
Stop if: Tasks 1-2 backend proof is green and the page still renders `card.feedback_text` directly, because this task should then close as an explicit skip rather than create unnecessary work
Session boundary after: yes
Acceptance Criteria:
- Phase 3 cites the existing direct `card.feedback_text` render path as sufficient closure when backend proof shows no remaining UI truthfulness gap.
- If a real render mismatch appears, stop and author a new bounded follow-on task instead of editing frontend code under WF-0077's backend MVP slice.
- No implementation claim is made without an audit disposition covering the backend-only skip or the newly opened follow-on.
TDD Plan:
- N/A for the default skip path; if backend proof exposes a real frontend mismatch, stop and create a new bounded follow-on task before editing code.
Verification Steps:
- `rg -n "feedback_text" frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `git diff --name-only main...HEAD`
Risks (if any): Treating this conditional check as implicit could let Phase 3 claim backend-only sufficiency without citing the current render path.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Current-baseline proof | `StructuredReviewerService` assessed-card presentation | `backend/tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_actionable_guidance"` | targeted `ERC-2026-PoC` card initially proves prompt-list/question-shaped output before the service fix | `pass` | 2026-03-13 RED pytest: `1 failed, 29 deselected` with `Address the following evaluation element prompts:` output | required RED starting point captured before the service edit |
| Narrow seam proof | service code review + targeted regression | `git diff -- backend/app/services/structured_reviewer_service.py backend/tests/test_structured_reviewer_service.py` | change stays in the approved backend service seam | `pass` | implementation commits `99eb344` and `12ee6f9`; code diff limited to the approved backend files | frontend/task-proof docs updated only during closeout |
| Raw machine reason preservation | targeted service regression | `backend/tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_reason_passthrough"` | mocked machine reason/source string stays unchanged while returned `feedback_text` changes, without adding a new persisted/API `reason` field in this slice | `pass` | 2026-03-13 pytest selector: `1 passed, 33 deselected` | keeps proof honest within the approved backend seam |
| Deterministic guidance proof | targeted service regression | `backend/tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_actionable_guidance"` | targeted assessed cards emit concise deterministic revision guidance | `pass` | 2026-03-13 pytest selector: `1 passed, 33 deselected` | paired with the RED evidence above |
| Non-targeted call safety | targeted service regression | `backend/tests/test_structured_reviewer_service.py -k "wf0077_contract_non_targeted_passthrough"` | non-`ERC-2026-PoC` calls keep current deterministic behavior | `pass` | 2026-03-13 WF-0077 fallback selector bundle: `4 passed, 30 deselected` | bounded rollout proof |
| Fallback honesty proof | targeted service regression | `backend/tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_fallback_missing_source or wf0077_contract_erc_poc_fallback_unresolved_prompt or wf0077_contract_erc_poc_fallback_duplicate_source"` | weak/unusable prompt surfaces preserve WF-0076-style fallback instead of invented guidance | `pass` | 2026-03-13 WF-0077 fallback selector bundle: `4 passed, 30 deselected` | duplicate-source case now fails closed by dropping unusable duplicate IDs from the runtime prompt surface |
| Optional frontend necessity check | render-path citation or new follow-on task | `rg -n "feedback_text" frontend/src/app/app/reviews/[reviewId]/page.tsx` | explicit skip is allowed only if backend proof is green and the page still renders `card.feedback_text` directly | `pass` | `frontend/src/app/app/reviews/[reviewId]/page.tsx:110` and `:1044` render `card.feedback_text` directly | explicit backend-only skip accepted |
| Atomic slice proof | finalized task review | task artifact review | first implementation slice stays within two backend files and no task exceeds the approved seam | `pass` | Task 1/2 implementation confined to `backend/app/services/structured_reviewer_service.py` and `backend/tests/test_structured_reviewer_service.py`; Task 3 closed as no-edit skip | planning-level guard preserved |
| Audit disposition | findings-closure ledger | Phase 2/3 ledger | every blocking finding closes and every non-blocking finding closes or is rejected with rationale | `pass` | walkthrough ledger + `docs/logs/decisions.md` closeout entry | proceed no longer blocked |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 1 overclaimed raw machine `reason` preservation as if the two-file service seam could prove a separate persisted audit surface, even though current `ReviewCard`/API payloads do not expose that field | non-blocking | narrow the task and matrix wording to a service-local invariant: the mocked machine reason/source string remains unchanged while guidance is derived into `feedback_text`, with no new persisted/API field in this slice | closed | closed in v0.2 |
| Phase 2.2 task review | Task 2 weak-source fallback coverage did not name the duplicated/unusable subordinate-prompt surface called out by the PRD | non-blocking | make duplicate/unusable prompt-surface coverage explicit in Task 2 acceptance and RED plan | closed | closed in v0.2 |
| Phase 2.2 task review | Task 3 still read like latent frontend implementation scope instead of a pure backend-only skip-or-escalate guard | non-blocking | set `May touch files` to `none`, narrow verification to the live render path, and require a new follow-on task before any frontend edits | closed | closed in v0.2 |
| 2026-03-13 fail-closed adversarial review | Task 1 mixed RED baseline evidence with post-fix GREEN assertions, making the first slice non-executable as written | blocking | split Task 1 acceptance/TDD/matrix wording into explicit RED capture plus separate post-fix guidance and reason-preservation proofs | closed | closed in v0.3 |
| 2026-03-13 fail-closed adversarial review | Verification commands used fuzzy/shared `-k` filters, so matrix rows could not produce row-specific pass/fail evidence for ship decisions | blocking | replace fuzzy filters with deterministic `wf0077_contract_*` selector contracts and point each matrix row at a distinct evidence surface | closed | closed in v0.3 |

## Changelog

- v0.1 (2026-03-13): Initial task breakdown from PRD.
- v0.2 (2026-03-13): Applied Part B feedback by narrowing raw-machine-reason proof to the approved two-file seam, making duplicate weak-source fallback explicit, and converting the frontend check into a skip-or-escalate guard before marking the plan ready for implementation.
- v0.3 (2026-03-13): Split Task 1 RED versus GREEN proof expectations, replaced fuzzy verification filters with deterministic `wf0077_contract_*` selectors, and tightened the matrix evidence pointers for fail-closed closure.
- v0.4 (2026-03-13): Marked Tasks 1-3 complete after implementation, recorded passing verification evidence for every matrix row, and closed the backend-only frontend-necessity check as an explicit skip.
