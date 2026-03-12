<!-- docs/tasks/task-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-12

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: fail-closed page-43 coverage proof

Goal:
Add a replayable proof seam that classifies ERC PoC subordinate-prompt coverage as `absent_by_source`, `fully_encoded`, or `partially_encoded`, and proves the current real proof-call fails closed while `1.b` and `1.c` remain incomplete.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR3, FR4, FR5, FR6
Depends on: none
Enables: 2, 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_call_subordinate_prompt_coverage.py`
May touch files:
- `none`
Out of scope: editing the canonical YAML itself, runtime-consumption changes, repo-wide flat-call policy tightening
Stop if: the proof seam cannot classify exact source-to-YAML coverage for the real ERC PoC call without introducing a broader schema/runtime abstraction or relying on synthetic fixture-only evidence
Session boundary after: no
Acceptance Criteria:
- A targeted executable proof derives or encodes the official page-43 expectation set for `1.a`, `1.b`, and `1.c` and maps each expected prompt to an exact YAML prompt ID or path in the real ERC PoC call.
- The proof reports `partially_encoded` for the current real proof-call state and does not allow `absent_by_source` for `1.a`, `1.b`, or `1.c`.
- At least one negative case proves that omitting an official `1.b` or `1.c` prompt from an otherwise valid payload fails closed.
TDD Plan:
- RED: add `backend/tests/test_call_subordinate_prompt_coverage.py` with a failing classification test against `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` plus a negative omitted-prompt case.
- GREEN: keep the proof seam test-local unless one tiny helper is strictly required to avoid duplicated classification logic.
- REFACTOR: extract a small expectation-ledger helper only if the coverage assertions become unreadable inside one test module.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075"`
- `cd backend && rg -n "partially_encoded|fully_encoded|absent_by_source|page 43|1.a|1.b|1.c" tests/test_call_subordinate_prompt_coverage.py`
Risks (if any): A count-only or fixture-only proof would still allow the real proof-call to look complete without source-grounded identity checks.

### [ ] Task 2 — Complete the ERC PoC canonical YAML and preserve runtime-boundary honesty

Goal:
Finish the real proof-call by encoding the official page-43 subordinate prompts under `1.b` and `1.c`, then prove dry-run ingest and canonical persistence succeed without claiming runtime consumption.
Slice: canonical-completion
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR4, FR8
Depends on: 1
Enables: 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
- `backend/tests/test_ingest_call_dry_run.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: broad ERC runtime redesign, changing the activated snapshot beyond `schema_version` plus `expectations`, flat-call compatibility policy changes
Stop if: completing `1.b` and `1.c` would require widening the runtime snapshot seam or changing non-ERC proof-call artifacts
Session boundary after: yes
Acceptance Criteria:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` preserves the official page-43 subordinate prompts across `1.a`, `1.b`, and `1.c` with stable prompt IDs and page-43 source traceability metadata.
- Dry-run validation proves the completed real call remains ingestable and the canonical JSON includes subordinate prompts for all three page-43 elements.
- Runtime-boundary proof remains explicit: the structured-review snapshot still exposes only `schema_version` and `expectations`, even though canonical persistence now includes all subordinate prompts.
TDD Plan:
- RED: extend the new coverage proof and existing dry-run/runtime-boundary tests so they fail until `1.b` and `1.c` are encoded in the real YAML.
- GREEN: make the narrowest source-grounded YAML edits needed for full page-43 completion and update the existing dry-run/runtime-boundary assertions.
- REFACTOR: keep prompt IDs and traceability strings inline in the canonical YAML unless duplication across tests becomes unmanageable.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075"`
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run`
Risks (if any): Filling the YAML without preserving the runtime-boundary proof would invite an overclaim that canonical fidelity already changes structured-review generation.

### [ ] Task 3 — Clarify authoring/checklist semantics for absent vs partial vs complete

Goal:
Apply only the narrow corrective wording needed so repo guidance explicitly distinguishes `absent_by_source` from `partially_encoded` for new or re-authored proof-calls, without reopening WF-0074 mechanism or compatibility posture.
Slice: authoring-contract
User Stories: US2, US3
PRD Requirements: FR5, FR7, FR8
Depends on: 1, 2
Enables: 4
Parallelizable: no
Files to modify:
Must touch files:
- `docs/call-yaml/authoring-workflow.md`
- `docs/call-yaml/onboarding-checklist.md`
- `backend/tests/test_call_yaml_authoring_contract.py`
May touch files:
- `none`
Out of scope: repo-wide migration requirements, schema redesign, runtime-consumption claims, broad documentation rewrites
Stop if: the clarification would require weakening WF-0074's temporary compatibility posture or editing more than the two existing authoring-governance docs plus the contract test
Session boundary after: no
Acceptance Criteria:
- The workflow and checklist make it explicit that when source prompts exist, partial preservation is not equivalent to source-grounded absence.
- The wording keeps existing flat canonical YAMLs temporarily compatible unless separately re-approved, while still requiring the ERC PoC proof-call to become fully encoded.
- Contract tests fail closed on any wording that blurs absent-by-source, partially encoded, and fully encoded states or overclaims runtime-consumption impact.
TDD Plan:
- RED: extend `backend/tests/test_call_yaml_authoring_contract.py` with WF-0075 assertions for the three-state distinction and the preserved expectations-only runtime boundary.
- GREEN: add the smallest wording change needed in the authoring workflow and onboarding checklist.
- REFACTOR: keep the contract checks string-based unless the existing test file becomes too repetitive.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0075"`
- `rg -n "absent|partial|complete|subordinate prompts|runtime-consumption impact|temporarily compatible" docs/call-yaml/authoring-workflow.md docs/call-yaml/onboarding-checklist.md`
Risks (if any): Leaving the three-state rule implicit would let a later closeout reuse WF-0074 wording while still treating a partial real proof-call as complete.

### [ ] Task 4 — Durable governance and baseline-anchored closure evidence

Goal:
Record WF-0075's narrow corrective boundary and fail-closed closure contract in durable governance surfaces so future closure cannot drop the three-state proof, `main...HEAD` scope proof, or audit-disposition gate.
Slice: durable-governance
User Stories: US2, US3
PRD Requirements: FR7, FR9, FR10
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
Out of scope: revisiting WF-0074 mechanism/governance decisions beyond a narrow corrective clarification, runtime implementation changes, walkthrough closeout content
Stop if: preserving the fail-closed closure gate would require broader governance-surface expansion beyond the existing decision log, project-doc memory file, and docs contract test
Session boundary after: yes
Acceptance Criteria:
- `docs/logs/decisions.md` records that WF-0075 completes the ERC PoC proof-call without reopening WF-0074, and that partial page-43 coverage must fail closed for the real proof-call.
- `docs/memory/domain/project_docs.md` records that WF-0075 closure must include `main...HEAD` scope proof plus a named audit-disposition artifact before any proceed or ship recommendation.
- Contract tests prove the durable-governance wording preserves temporary flat-call compatibility, the expectations-only runtime seam, and the three-state fail-closed closure rule.
TDD Plan:
- RED: extend `backend/tests/test_call_yaml_authoring_contract.py` with WF-0075 durable-governance assertions covering partial-coverage failure, baseline-anchored scope proof, and audit-disposition closure.
- GREEN: update the decision log and project-doc memory file with the narrowest approved-policy wording needed to preserve FR7/FR9/FR10 outside transient task/chat context.
- REFACTOR: reuse the existing string-fragment assertion helper instead of introducing a new docs-testing abstraction.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0075"`
- `rg -n "WF-0075|partial|main...HEAD|audit-disposition|temporarily compatible|expectations-only" docs/logs/decisions.md docs/memory/domain/project_docs.md`
- `git diff --name-only main...HEAD`
Risks (if any): If the closure gate stays only in the PRD or task plan, later implementation can appear complete while silently dropping the required scope-proof and audit-disposition evidence.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Page-43 source-to-YAML coverage | fail-closed coverage proof | `tests/test_call_subordinate_prompt_coverage.py` | every official page-43 subordinate prompt for `1.a`, `1.b`, and `1.c` maps to an exact YAML prompt ID/path | `fail` (default until executed) | pytest output in `backend/tests/test_call_subordinate_prompt_coverage.py` | count-only proof is insufficient |
| Partial-vs-complete negative proof | fail-closed coverage proof | `tests/test_call_subordinate_prompt_coverage.py` omitted-prompt case | omission of an official `1.b` or `1.c` prompt yields `partially_encoded` and fails closure | `fail` (default until executed) | pytest output in `backend/tests/test_call_subordinate_prompt_coverage.py` | required negative MVP case |
| Absent/complete/partial distinction | classification contract | `tests/test_call_subordinate_prompt_coverage.py` | elements with no source prompts may be `absent_by_source`; page-43 ERC PoC elements may not | `fail` (default until executed) | pytest output + expectation ledger in `backend/tests/test_call_subordinate_prompt_coverage.py` | three-state seam must be explicit |
| ERC PoC proof-call completion | dry-run ingest | `uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run` | completed ERC PoC call ingests successfully with page-43 subordinate prompts across `1.a`, `1.b`, and `1.c` | `fail` (default until executed) | dry-run stdout + pytest output in `backend/tests/test_ingest_call_dry_run.py` | real proof-call only |
| Runtime-boundary honesty | structured-review snapshot inspection | `test_wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only` | canonical JSON preserves subordinate prompts while runtime snapshot remains limited to `schema_version` plus `expectations` | `fail` (default until executed) | pytest output in `backend/tests/test_structured_reviewer_service.py` | no runtime-consumption claim allowed |
| Authoring/checklist three-state guard | docs contract test | `backend/tests/test_call_yaml_authoring_contract.py -k "wf0075"` | authoring docs distinguish absent vs partial vs complete and preserve temporary compatibility posture | `fail` (default until executed) | pytest output + doc diff | corrective wording only if needed |
| WF-0074 boundary preservation | durable governance docs | `backend/tests/test_call_yaml_authoring_contract.py -k "wf0075"` | WF-0075 records a narrow corrective clarification without reopening WF-0074 mechanism/governance or tightening flat-call compatibility globally | `fail` (default until executed) | pytest output + doc diff in `docs/logs/decisions.md` and `docs/memory/domain/project_docs.md` | prior truth must remain explicit |
| Baseline-anchored scope proof | branch diff ledger | `git diff --name-only main...HEAD` | changed-file surface stays inside the approved WF-0075 boundary | `fail` (default until executed) | `main...HEAD` diff output cited in closeout artifact | required before proceed/ship |
| Audit disposition | named findings ledger | closure artifact ledger | every blocking finding is closed and every justified non-blocking finding is closed or rejected with rationale before any proceed/ship recommendation | `fail` (default until executed) | named audit-disposition artifact | fail-closed ship gate |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | none yet | none | complete Part B review before revising to ready state | open | placeholder until Part B |

## Changelog

- v0.1 (2026-03-12): Initial task breakdown from PRD.
