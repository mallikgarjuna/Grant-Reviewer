<!-- docs/tasks/task-WF-0068-review-quality-evaluation-loop.md -->
# WF-0068 — Review Quality Evaluation Loop

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-08

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Lock the representative batch manifest and frozen baseline skeleton

Goal:
Create the auditable execution scaffold for WF-0068 so Phase 3 starts from a locked 9-snippet batch and one frozen baseline contract instead of ad hoc sampling.
Slice: execution-scaffold
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR8, FR15, FR17
Depends on: none
Enables: 2, 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
- `docs/walkthroughs/evidence/WF-0068/snippet-batch.json`
- `docs/walkthroughs/evidence/WF-0068/baseline.json`
May touch files:
- `none`
Out of scope: generating review outputs, scoring review quality, follow-on remediation ideas, changing the locked call wedge
Stop if: the repo cannot locate approved snippet material for a locked call/role without expanding beyond `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`; record `coverage_status: coverage_gap` with the missing call/role/material blockers in `snippet-batch.json` and the walkthrough, then stop before Task 2
Session boundary after: no
Acceptance Criteria:
- `snippet-batch.json` records a top-level `coverage_status`. When `coverage_status` is `locked`, it contains exactly 9 planned items: 3 per locked call, with one `baseline_representative`, one `traceability_specificity_stress`, and one `actionability_prioritization_stress` role per call.
- If `coverage_status` is `coverage_gap`, `snippet-batch.json` records the missing call/role/material blockers and the walkthrough explicitly marks WF-0068 as blocked from Task 2 until the gap is resolved without widening scope.
- Every planned item records auditable inclusion rationale, snippet identifier, node/section target, stable `batch_order`, and the official source artifact(s) expected to support later judgment.
- `baseline.json` records `baseline_id`, `app_commit_sha`, `app_branch_ref`, `prompt_config_ref`, `model_runtime_ref`, `reviewer_instruction_ref`, `evidence_template_version`, and the fixed 4-state dimension scale.
- The walkthrough records the Phase 3 baseline SHA capture and links the locked batch and baseline artifacts as the only approved inputs for the evaluation run.
TDD Plan: N/A
Verification Steps:
- `cd backend && uv run python - <<'PY'\nimport json\nfrom pathlib import Path\nbatch = json.loads(Path('../docs/walkthroughs/evidence/WF-0068/snippet-batch.json').read_text())\nassert batch['coverage_status'] in {'locked', 'coverage_gap'}\nif batch['coverage_status'] == 'locked':\n    assert len(batch['items']) == 9\n    assert sorted({item['call_id'] for item in batch['items']}) == ['MSCA-PF-2025', 'erc_stg_2026_full', 'nwo_veni_2025_preproposal']\n    roles = {'baseline_representative', 'traceability_specificity_stress', 'actionability_prioritization_stress'}\n    for call_id in ['nwo_veni_2025_preproposal', 'erc_stg_2026_full', 'MSCA-PF-2025']:\n        assert {item['role'] for item in batch['items'] if item['call_id'] == call_id} == roles\n        assert sorted(item['batch_order'] for item in batch['items'] if item['call_id'] == call_id)\nelse:\n    assert batch['coverage_gaps']\nPY`
- `cd backend && uv run python - <<'PY'\nimport json\nfrom pathlib import Path\nbaseline = json.loads(Path('../docs/walkthroughs/evidence/WF-0068/baseline.json').read_text())\nrequired = {'baseline_id', 'app_commit_sha', 'app_branch_ref', 'prompt_config_ref', 'model_runtime_ref', 'reviewer_instruction_ref', 'evidence_template_version', 'dimension_scale'}\nassert required <= set(baseline)\nassert baseline['dimension_scale'] == ['pass', 'weak', 'fail', 'insufficient_evidence']\nPY`
- `rg -n "snippet-batch\\.json|baseline\\.json|phase_3_baseline_sha" docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
Risks (if any): If the batch scaffold is weak, later evidence can look complete while hiding convenience sampling or baseline drift.

### [ ] Task 2 — Tracer bullet: capture locked-batch raw review outputs with a fail-closed runner

Goal:
Prove the evaluation loop can replay the locked batch through an existing non-demo review-generation seam and persist raw outputs without widening into reviewer remediation or product behavior changes.
Slice: tracer-bullet
User Stories: US2, US3
PRD Requirements: FR5, FR7, FR8, FR9, FR10, FR14, FR17
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/scripts/run_review_batch.py`
- `backend/tests/test_run_review_batch.py`
- `backend/tests/fixtures/wf_0068_review_batch.json`
May touch files:
- `none`
Out of scope: prompt tuning, review-card scoring changes, UI changes, batch-summary decisions, adding calls outside the locked wedge
Stop if: replaying the locked batch requires seeded demo state, review-engine contract changes, prompt edits, or a fourth file outside the named runner/test/fixture surface
Session boundary after: no
Acceptance Criteria:
- A new batch runner accepts the locked manifest path and supplied baseline file, replays the batch through an existing non-demo review-generation seam, and emits raw `snippet -> review output` evidence to a caller-specified JSON path without changing reviewer behavior.
- The runner fails closed on wedge drift, missing roles, manifest/baseline reference mismatch, any per-item attempt to override the frozen baseline, or item-count drift from the required `3 x 3` matrix.
- Tests prove one valid locked batch path and at least one fail-closed path for coverage drift and baseline-reference mismatch.
- The runner preserves raw output and provenance fields only; it does not add reviewer judgments or remediation suggestions.
TDD Plan: RED in `backend/tests/test_run_review_batch.py` for a valid locked-batch replay plus fail-closed wedge-drift and baseline-reference mismatch cases; GREEN in `backend/scripts/run_review_batch.py`; REFACTOR by extracting manifest/baseline parsing helpers inside the new runner once tests are green.
Verification Steps:
- `cd backend && uv run pytest tests/test_run_review_batch.py -k "wf0068_batch_runner_persists_locked_batch_outputs"`
- `cd backend && uv run pytest tests/test_run_review_batch.py -k "wf0068_batch_runner_rejects_wedge_drift"`
- `cd backend && uv run pytest tests/test_run_review_batch.py -k "wf0068_batch_runner_rejects_baseline_reference_mismatch"`
- `cd backend && uv run python scripts/run_review_batch.py tests/fixtures/wf_0068_review_batch.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json --output /tmp/wf_0068_raw_review_outputs.json`
- `cd backend && uv run python - <<'PY'\nimport json\nfrom pathlib import Path\nraw_outputs = json.loads(Path('/tmp/wf_0068_raw_review_outputs.json').read_text())\nassert len(raw_outputs['items']) == 9\nassert len({item['baseline_id'] for item in raw_outputs['items']}) == 1\nPY`
Risks (if any): If the runner mutates or interprets review quality instead of only capturing raw outputs, it will collapse the evidence and judgment seams together.

### [ ] Task 3 — Add fail-closed validation for the WF-0068 evidence bundle contract

Goal:
Make the evidence bundle machine-checkable before human judgment closure so missing provenance, illegal severity values, or invalid proceed logic fail before the walkthrough can claim readiness.
Slice: evidence-validation
User Stories: US1, US3, US4
PRD Requirements: FR4, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/scripts/validate_wf_0068_evidence_bundle.py`
- `backend/tests/test_validate_wf_0068_evidence_bundle.py`
- `backend/tests/fixtures/wf_0068_evidence_bundle_cases.json`
May touch files:
- `none`
Out of scope: generating the evidence records themselves, changing review-engine output shape, any follow-on implementation WF planning
Stop if: validation requires changing the PRD contract or inferring missing evidence fields from prose instead of rejecting them
Session boundary after: no
Acceptance Criteria:
- The validator rejects missing `app_branch_ref`, missing replayable `official_locator_used`, missing or extra mission-dimension keys, dimension states outside `pass|weak|fail|insufficient_evidence`, illegal severity values outside `high|medium|low`, invalid failure tags, illegal follow-on classes, or absent insufficient-evidence states when declared.
- The validator rejects batch summaries that emit `proceed_to_narrow_follow_on_wf` without a named verification evidence bundle or without repeated categorized evidence across at least 2 reviewed snippets.
- The validator rejects summaries that overstate cross-wedge proof when repeated failures exist only within one locked call and the boundary is not labeled call-specific.
- The validator exposes explicit modes for `records` and `bundle` validation so Phase 3 can verify item-level evidence before writing the final batch decision.
- Tests cover both valid evidence-bundle shape and fail-closed invalid cases tied to the PRD contract.
TDD Plan: RED in `backend/tests/test_validate_wf_0068_evidence_bundle.py` for invalid provenance, dimension-scale, severity, and proceed-threshold cases; GREEN in `backend/scripts/validate_wf_0068_evidence_bundle.py`; REFACTOR by centralizing allowed enums and contract keys into typed constants after the invalid cases pass.
Verification Steps:
- `cd backend && uv run pytest tests/test_validate_wf_0068_evidence_bundle.py -k "wf0068_evidence_bundle_records_require_exact_dimension_scale"`
- `cd backend && uv run pytest tests/test_validate_wf_0068_evidence_bundle.py -k "wf0068_evidence_bundle_bundle_requires_repeated_failure_pattern"`
- `cd backend && uv run python scripts/validate_wf_0068_evidence_bundle.py --mode records tests/fixtures/wf_0068_evidence_bundle_cases.json --case valid_records`
- `cd backend && uv run python scripts/validate_wf_0068_evidence_bundle.py --mode bundle tests/fixtures/wf_0068_evidence_bundle_cases.json --case valid_bundle`
Risks (if any): If contract validation arrives after manual scoring, the workflow can waste time populating evidence that should have been rejected immediately.

### [ ] Task 4 — Record the 9 reviewed items with mission judgments and raw-output traceability

Goal:
Execute the locked batch, preserve every raw output, and complete one evidence record per reviewed item without drifting into remediation proposals.
Slice: evidence-capture
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR4, FR9, FR10, FR11, FR12, FR13, FR14, FR17
Depends on: 2, 3
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/evidence/WF-0068/raw-review-outputs.json`
- `docs/walkthroughs/evidence/WF-0068/evidence-records.json`
- `docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
May touch files:
- `none`
Out of scope: changing prompts/models, rewriting review outputs, deciding a remediation WF, adding extra snippets beyond the locked batch
Stop if: approved official materials referenced by the locked batch are missing from the repo, or the batch baseline changes before all 9 items are complete and the run cannot be cleanly restarted or split
Session boundary after: yes
Acceptance Criteria:
- `raw-review-outputs.json` contains one preserved raw output entry for each of the 9 locked batch items, linked back to the batch and baseline IDs.
- `evidence-records.json` contains one judgment record per item with the five mission dimensions, failure tags, severity, revision-action judgment, follow-on pattern class, official locator, and explicit `insufficient_evidence` handling when needed; unsupported judgments are recorded, not omitted.
- The walkthrough records the fixed review order, notes any fail-closed pauses, and explicitly states that WF-0068 captured evidence only, not remediation.
- The evidence bundle passes the validator before any batch-level decision is written.
TDD Plan: N/A
Verification Steps:
- `cd backend && uv run python scripts/run_review_batch.py ../docs/walkthroughs/evidence/WF-0068/snippet-batch.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json --output ../docs/walkthroughs/evidence/WF-0068/raw-review-outputs.json`
- `cd backend && uv run python scripts/validate_wf_0068_evidence_bundle.py --mode records ../docs/walkthroughs/evidence/WF-0068/evidence-records.json --raw-output ../docs/walkthroughs/evidence/WF-0068/raw-review-outputs.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json`
- `cd backend && uv run python - <<'PY'\nimport json\nfrom pathlib import Path\nrecords = json.loads(Path('../docs/walkthroughs/evidence/WF-0068/evidence-records.json').read_text())\nassert len(records['items']) == 9\nassert all('official_locator_used' in item for item in records['items'])\nPY`
Risks (if any): Manual scoring can silently slip into solutioning unless the walkthrough and evidence records preserve the evaluation-only boundary explicitly.

### [ ] Task 5 — Close the batch summary and prove the follow-on decision stayed bounded

Goal:
Finish WF-0068 with a single batch-level mission result and follow-on decision that is traceable to the validated evidence bundle and does not overclaim beyond the locked wedge.
Slice: decision-closure
User Stories: US3, US4
PRD Requirements: FR14, FR15, FR16, FR17
Depends on: 4
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/evidence/WF-0068/batch-summary.json`
- `docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
May touch files:
- `docs/walkthroughs/evidence/WF-0068/evidence-records.json`
Out of scope: implementing any prompt, engine, UI, contract, or wedge-expansion follow-on work
Stop if: the only available justification for `proceed_to_narrow_follow_on_wf` is a single persuasive example, or the decision boundary cannot be phrased as a repeated failure pattern
Session boundary after: yes
Acceptance Criteria:
- `batch-summary.json` records `batch_id`, `verification_evidence_bundle_ref`, `coverage_status`, `baseline_consistency_status`, `pattern_summary`, `mission_result`, `follow_on_decision`, `decision_rationale`, and `recommended_follow_on_boundary`.
- The summary resolves coverage gaps, mixed baselines, or unsupported judgments as `more_evidence_required` or `inconclusive` instead of optimistic pass claims.
- If repeated failure evidence exists only within one locked call, the summary labels the recommended boundary call-specific and avoids cross-wedge claims.
- The walkthrough closes with explicit verification evidence, the final decision, and a scope note confirming WF-0068 ended at evaluation closure rather than remediation planning.
TDD Plan: N/A
Verification Steps:
- `cd backend && uv run python scripts/validate_wf_0068_evidence_bundle.py --mode bundle ../docs/walkthroughs/evidence/WF-0068/batch-summary.json --records ../docs/walkthroughs/evidence/WF-0068/evidence-records.json --raw-output ../docs/walkthroughs/evidence/WF-0068/raw-review-outputs.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json`
- `cd backend && uv run python - <<'PY'\nimport json\nfrom pathlib import Path\nsummary = json.loads(Path('../docs/walkthroughs/evidence/WF-0068/batch-summary.json').read_text())\nrequired = {'batch_id', 'verification_evidence_bundle_ref', 'coverage_status', 'baseline_consistency_status', 'pattern_summary', 'mission_result', 'follow_on_decision', 'decision_rationale', 'recommended_follow_on_boundary'}\nassert required <= set(summary)\nassert summary['follow_on_decision'] in {'no_follow_on_wf', 'proceed_to_narrow_follow_on_wf', 'more_evidence_required'}\nPY`
- `rg -n "mission_result|follow_on_decision|recommended_follow_on_boundary|no remediation" docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
Risks (if any): A strong narrative summary can still overclaim if the repeated-pattern threshold is not tied back to validated evidence records.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
- v0.2 (2026-03-08): Replaced invalid repo-level Python verification commands with `uv`-backed checks, kept the tracer bullet scoped to runner/test surfaces instead of persisted evidence output, and made validator modes explicit for records versus full-bundle closure; marked Ready for Implementation.
- v0.3 (2026-03-08): Closed fail-closed planning gaps by recording coverage gaps explicitly, removing impossible mixed-baseline task language, requiring non-dry-run raw-output proof, validating exact mission-dimension scoring, and preserving insufficient-evidence records instead of stopping the batch.
