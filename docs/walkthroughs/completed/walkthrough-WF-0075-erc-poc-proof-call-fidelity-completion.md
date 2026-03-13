<!-- docs/walkthroughs/completed/walkthrough-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: walkthrough
Version: v0.1
Status: Done
Last Updated: 2026-03-12

## Scope Summary
- Complete the real ERC PoC proof-call so page-43 subordinate prompts are fully encoded across `1.a`, `1.b`, and `1.c`.
- Preserve WF-0074's expectations-only runtime boundary while proving source-to-YAML coverage fails closed.
- Keep follow-on doc/governance widening conditional; Tasks 4-5 were skipped because Tasks 1-3 closed the ambiguity directly.

## Phase 3 Progress
- Task 1 added a dedicated coverage proof seam in [backend/tests/test_call_subordinate_prompt_coverage.py](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_call_subordinate_prompt_coverage.py) that classifies `absent_by_source`, `partially_encoded`, and `fully_encoded` against the real ERC PoC artifact.
- Task 2 completed [backend/data/calls/canonical/erc/erc_poc_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_poc_2026_full.yaml) for `1.b` and `1.c` and extended dry-run coverage in [backend/tests/test_ingest_call_dry_run.py](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_ingest_call_dry_run.py).
- Task 3 re-proved that structured-review runtime activation still emits only `schema_version` plus `expectations` in [backend/tests/test_structured_reviewer_service.py](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_structured_reviewer_service.py).
- Task 4 and Task 5 were skipped per the approved task contract because no residual ambiguity remained after the executable proof landed.
- This audit pass closed the stale workflow-state gap by updating active WF status surfaces out of pre-implementation state.

## Verification Evidence

| Proof item | Command or test ID | Result | Notes |
| :--- | :--- | :--- | :--- |
| Page-43 source-to-YAML coverage | `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -q` | pass | `3 passed`; includes full-coverage proof, explicit absent-by-source example, and omitted-prompt negative case. |
| ERC PoC dry-run ingest | `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -q -k 'wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run or wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml'` | pass | `2 passed, 10 deselected`; confirms the completed proof-call still dry-runs cleanly. |
| Runtime-boundary honesty | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -q -k 'wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only or wf0073_contract_structured_service_keeps_erc_poc_2026_single_step_activation'` | pass | `2 passed, 24 deselected`; proves persisted subordinate prompts do not widen the runtime snapshot seam. |
| Baseline-anchored scope proof | `git diff --name-only main...HEAD` | pass | Changed files remain within the WF-0075 proof-call, test, and workflow-artifact boundary. |
| WF-0074 boundary preservation | `AD 74.3`, `AD 74.4`, and `WF-0074 planning/execution must preserve durable decision/memory guidance` | pass | WF-0075 preserves temporary flat-call compatibility and the expectations-only runtime boundary. |
| Conditional authoring/governance follow-ons | Task 4 / Task 5 execution outcome | skipped | Skipped by design because Tasks 1-3 provided sufficient executable proof without reopening WF-0074 governance surfaces. |

## Commit Trail
- `461134a` — Task 1: tracer-bullet coverage proof
- `9532fa1` — Task 2: complete ERC PoC page-43 prompts
- `86a2741` — Task 3: preserve runtime boundary proof

## Audit-Disposition Ledger

| ID | Type | Severity | Disposition |
| :--- | :--- | :--- | :--- |
| DI-1 | Documentation state | blocking | Fixed by updating active WF status surfaces so the task, walkthrough, and registry no longer present WF-0075 as pre-Phase-3 work. |

## Remaining Risks
- The verification pass was targeted to WF-0075 selectors; a full backend suite was not rerun in this audit.
- The walkthrough now closes Phase 3 evidence honestly, but ship remains user-gated.

## Ship Recommendation
- Phase 3 status: complete.
- Ship gate: pending explicit user approval.
