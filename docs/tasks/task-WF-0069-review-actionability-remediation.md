<!-- docs/tasks/task-WF-0069-review-actionability-remediation.md -->
# WF-0069 — Review Actionability Remediation

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-09

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: prove the narrowest actionable-feedback seam for one NWO stress case

Goal:
Prove the smallest viable backend seam can emit at least one concrete revision move without breaking explicit missing-context handling for NWO `wf0068_nwo_actionability_prioritization_stress`, starting from the primary evaluator / compatibility / pipeline seams implicated by the approved artifacts and using a service-layer reroute only if the tracer evidence shows those seams cannot preserve actionable feedback truthfully on their own.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR3, FR4, FR5, FR6, FR7, FR8
Depends on: none
Enables: 2, 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/app/engine/findings/evaluator.py`
- `backend/app/engine/compat/review_card_mapper.py`
- `backend/app/services/structured_reviewer_service.py`
Out of scope: ERC/MSCA rollout, review-detail ordering, DB schema changes, prompt/schema rewrites, generic wording cleanup, changing more than one primary implementation seam before the first seam is disproven
Stop if: one NWO tracer bullet still cannot produce a truthful actionable assessed card without adding new persistence fields, changing non-target calls, or widening into prompt/schema work before one primary seam is proven insufficient; if the tracer needs concurrent evaluator + mapper + service changes, stop and split the planning instead of widening Task 1
Session boundary after: no
Acceptance Criteria:
- The tracer proof is grounded to the exact WF-0068 target `wf0068_nwo_actionability_prioritization_stress` and its submitted-node context, not only to synthetic service fixtures.
- The tracer proves whether the current failure is closed by one primary implementation seam (`evaluator`, `review_card_mapper`, or `structured_reviewer_service`) rather than assuming a service-layer reroute up front.
- The NWO tracer path persists at least one `AssessmentStatus.ASSESSED` card whose feedback is concrete revision guidance rather than `content_evaluated` or other flat status text.
- Existing fail-closed `NOT_ASSESSABLE` cards for missing cross-node context remain explicit and are not rewritten into fabricated advice.
- If Task 1 uses `structured_reviewer_service.py`, the task records in test intent and implementation comments why an evaluator-only or mapper-only change was insufficient for the exact tracer case.
- The change is scoped to the locked NWO/ERC/MSCA remediation wedge and does not alter behavior for unrelated calls.
- The tracer proof stays within the structured-review backend seam; no API/UI work is required for this task to pass.
TDD Plan: RED in `backend/tests/test_structured_reviewer_service.py` with `test_wf0069_wf0068_nwo_actionability_prioritization_stress_proves_narrowest_actionable_seam`; GREEN in exactly one of `backend/app/engine/findings/evaluator.py`, `backend/app/engine/compat/review_card_mapper.py`, or `backend/app/services/structured_reviewer_service.py`; REFACTOR `skip` unless a small helper is needed to keep the chosen seam readable after the tracer passes.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0069_wf0068_nwo_actionability_prioritization_stress_proves_narrowest_actionable_seam"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "structured_pipeline_v1_not_assessable_cards_for_missing_context"`
Risks (if any): The tracer may prove that actionable text is available upstream but still hidden later by review-detail ordering, which is why this task stops at the smallest backend seam only and fails closed if it cannot isolate one primary change surface.

### [x] Task 2 — Extend the actionable-review seam across the locked ERC/MSCA wedge without call drift

Goal:
Roll the Task 1-proven seam out to `erc_stg_2026_full` and `MSCA-PF-2025` only, so all three WF-0068 stress calls can produce actionable assessed cards while preserving the same fail-closed missing-context boundary and without introducing a second primary remediation seam.
Slice: wedge-rollout
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR11
Depends on: 1
Enables: 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- the Task 1-proven implementation seam
- `backend/tests/test_api.py`
Out of scope: new funding-program support, broader trust-surface work, launch-floor ops, generic prompt tuning
Stop if: making ERC/MSCA pass requires widening the seam beyond the locked wedge, changing unrelated structured-review flows, introducing non-deterministic LLM behavior outside the existing stub-backed path, or adding a second primary implementation seam that Task 1 did not justify
Session boundary after: no
Acceptance Criteria:
- The structured-review path emits actionable assessed cards for the NWO, ERC, and MSCA WF-0068 stress targets under the same primary implementation seam proven in Task 1.
- Missing-context and insufficient-evidence states remain explicit for all three calls and are not downgraded to normal success cards.
- Representative baseline paths for the same three calls still complete without regressing into failures or empty-card output.
- If cross-call rollout exposes a second primary seam, the task fails closed and records that Task 1’s chosen seam was insufficient rather than silently widening implementation scope.
- No broader call coverage or cross-workflow surface area is introduced.
TDD Plan: RED in `backend/tests/test_structured_reviewer_service.py` with exact ERC/MSCA stress regressions plus baseline non-regression checks for the six named WF-0068 item IDs; GREEN in the Task 1-proven implementation seam; REFACTOR by extracting a narrow locked-call guard/helper only if the proven seam becomes repetitive across the three locked calls.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0069_erc_actionability"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0069_msca_actionability"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0069_baseline_non_regression"`
Risks (if any): The backend seam may close actionability while still leaving prioritization weak at the review-detail output surface if assessed cards are rendered behind fail-closed context-gap cards.

### [ ] Task 3 — Reorder targeted review detail output so the highest-value actionable cards surface first

Goal:
Prove and, only if still needed after Task 2, enforce the smallest output seam needed for prioritization by ensuring targeted structured-review detail responses surface assessed submitted-node cards ahead of fail-closed missing-context cards for the locked NWO/ERC/MSCA wedge, without hiding or deleting the fail-closed cards.
Slice: output-ordering
User Stories: US1, US3, US4
PRD Requirements: FR2, FR3, FR4, FR5, FR6, FR8, FR9, FR12, FR13
Depends on: 2
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
May touch files:
- `backend/main.py`
- `backend/app/repositories/review_repository.py`
Out of scope: UI redesign, card copy polish, untargeted review-detail sorting changes, adding new API fields unless ordering alone proves insufficient
Stop if: fixing ordering would require a broader trust-surface redesign rather than a narrow targeted sort rule; if the existing detail surface already passes after Task 2, keep this task as a verified-no-op implementation plus a new regression test in `backend/tests/test_api.py`
Session boundary after: yes
Acceptance Criteria:
- Task 3 executes as implementation work only when Task 2 evidence still shows prioritization failure on the researcher-facing review-detail surface for the exact three WF-0068 stress IDs; otherwise it closes as a verified-no-op regression guard.
- For the three targeted stress cases, review detail output places assessed actionable cards for the submitted snippet ahead of fail-closed context-gap cards.
- Fail-closed cards remain visible and explicitly marked as non-assessable; they are reordered, not dropped or rewritten.
- Untargeted calls and legacy review-detail ordering remain unchanged.
- Ordering stays deterministic for equal-priority cards by preserving stable submitted-node / expectation order after the targeted assessed-first rule is applied.
TDD Plan: RED in `backend/tests/test_api.py` with a WF-0069 targeted review-detail ordering regression plus one untargeted legacy ordering guard; GREEN in `backend/main.py` (and `backend/app/repositories/review_repository.py` only if needed); REFACTOR `skip` unless the targeted ordering rule needs a dedicated helper for clarity.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0069_review_detail_orders_assessed_cards_before_context_gaps"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0069_review_detail_legacy_ordering_guard"`
Risks (if any): A sorting fix that is not call-scoped could silently change trusted review-detail behavior outside the approved wedge.

### [ ] Task 4 — Add deterministic WF-0069 replay evaluation for exact stress, baseline, and fail-closed gates

Goal:
Create one fail-closed replay/evaluation seam that regenerates fresh WF-0069 outputs for the exact WF-0068 stress and baseline item IDs, then scores those regenerated outputs against the closure contract so implementation proof cannot reuse stale pre-remediation evidence.
Slice: replay-evidence
User Stories: US2, US4
PRD Requirements: FR7, FR8, FR9, FR10, FR11, FR13, FR14
Depends on: 3
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/scripts/evaluate_wf_0069_actionability.py`
- `backend/tests/test_evaluate_wf_0069_actionability.py`
- `backend/tests/fixtures/wf_0069_actionability_cases.json`
May touch files:
- `none`
Out of scope: new sample-data generation, broader quality dashboards, rollout telemetry, replacing the approved WF-0068 evidence bundle
Stop if: the evaluator cannot consume the approved WF-0068 evidence/raw-output item IDs directly, or closure would require inventing a new unstated rubric outside `revision_actionability` and `prioritization_quality`
Session boundary after: no
Acceptance Criteria:
- The evaluator regenerates fresh outputs for the exact stress IDs `wf0068_nwo_actionability_prioritization_stress`, `wf0068_erc_actionability_prioritization_stress`, and `wf0068_msca_actionability_prioritization_stress` plus the three representative baseline IDs through the changed WF-0069 seam.
- The evaluator fails closed unless each regenerated stress item passes both `revision_actionability` and `prioritization_quality`, each regenerated baseline item stays at or above its WF-0068 floor, and fail-closed missing-context behavior remains explicit.
- Tests cover passing, failing, tie-handling, and fabricated-advice/fail-closed regression cases.
- The evaluator output is machine-readable and suitable for direct inclusion in the walkthrough closure artifact.
TDD Plan: RED in `backend/tests/test_evaluate_wf_0069_actionability.py` using `backend/tests/fixtures/wf_0069_actionability_cases.json` for stress pass/fail, baseline floor, tie-handling, and fail-closed cases; GREEN in `backend/scripts/evaluate_wf_0069_actionability.py`; REFACTOR by centralizing allowed dimension/result enums once the closure cases pass.
Verification Steps:
- `cd backend && uv run pytest tests/test_evaluate_wf_0069_actionability.py`
- `cd backend && uv run python scripts/evaluate_wf_0069_actionability.py --batch ../docs/walkthroughs/evidence/WF-0068/snippet-batch.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json --output /tmp/wf_0069_actionability_eval.json`
Risks (if any): If the evaluator drifts from the named WF-0068 IDs or dimensions, it can create false closure with a prettier but non-traceable proof path.

### [ ] Task 5 — Produce the WF-0069 closure artifact with scope proof and audit disposition ledger

Goal:
Finish WF-0069 with one walkthrough closure artifact that records exact replay evidence, baseline-anchored scope proof, and audit disposition, so the workflow cannot be marked ready or shipped on implied closure.
Slice: closure-artifact
User Stories: US2, US4
PRD Requirements: FR7, FR8, FR9, FR10, FR11, FR14
Depends on: 4
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0069-review-actionability-remediation.md`
May touch files:
- `docs/index.md`
Out of scope: new implementation work, follow-on roadmap creation, ship recommendations without replay evidence, repo-wide diff summaries
Stop if: the walkthrough cannot name the exact WF-0068 item IDs rechecked, the deterministic commands run, the baseline SHA/commit range used for scope proof, and a disposition for every justified finding/comment
Session boundary after: yes
Acceptance Criteria:
- The walkthrough records the closure baseline SHA or commit range, exact replay commands, and pass/fail results for all three stress items, all three baseline items, and the fail-closed guard.
- The walkthrough includes a scope-proof section showing only justified files changed for the chosen remediation slice.
- The walkthrough includes an audit-disposition ledger covering every blocking finding and every justified non-blocking finding/comment, each marked `closed` or `rejected_with_rationale`.
- The walkthrough states an explicit ship/proceed recommendation status, and that status remains blocked unless the Task 4 replay output is pass, the fail-closed guard passes, and the audit-disposition ledger is fully resolved.
- `docs/index.md` is updated only when the walkthrough evidence supports the intended WF readiness state.
TDD Plan: N/A
Verification Steps:
- `rg -n "wf0068_nwo_actionability_prioritization_stress|wf0068_erc_actionability_prioritization_stress|wf0068_msca_actionability_prioritization_stress" docs/walkthroughs/walkthrough-WF-0069-review-actionability-remediation.md`
- `rg -n "scope proof|audit-disposition|rejected_with_rationale|closed" docs/walkthroughs/walkthrough-WF-0069-review-actionability-remediation.md`
- `git diff --name-only <baseline_sha>...HEAD`
Risks (if any): Without explicit scope proof and audit disposition, Phase 3 could appear successful while still hiding widened scope or unresolved review findings.

## Changelog

- v0.1 (2026-03-09): Initial task breakdown from PRD.
- v0.2 (2026-03-09): Tightened tracer tests to the exact WF-0068 item IDs, made review-detail ordering deterministic even for verified-no-op cases, and switched replay closure to regenerated WF-0069 outputs; marked Ready for Implementation.
- v0.3 (2026-03-09): Removed the presupposed service-layer reroute, forced single-seam proof before rollout, gated review-detail ordering on post-Task-2 evidence, and required an explicit blocked/pass ship recommendation in closure evidence.
