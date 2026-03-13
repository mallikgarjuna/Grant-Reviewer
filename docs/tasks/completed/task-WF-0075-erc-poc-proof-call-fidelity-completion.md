<!-- docs/tasks/completed/task-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: task
Version: v0.4
Status: Done
Last Updated: 2026-03-12

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: fail-closed page-43 coverage proof

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
- The proof also includes one explicit positive `absent_by_source` example for an element outside the page-43 subordinate-prompt scope so all three states are demonstrated, not inferred.
- At least one negative case proves that omitting an official `1.b` or `1.c` prompt from an otherwise valid payload fails closed.
TDD Plan:
- RED: add `backend/tests/test_call_subordinate_prompt_coverage.py` with a failing classification test against `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`, one positive `absent_by_source` case, and a negative omitted-prompt case.
- GREEN: keep the proof seam test-local unless one tiny helper is strictly required to avoid duplicated classification logic.
- REFACTOR: extract a small expectation-ledger helper only if the coverage assertions become unreadable inside one test module.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075"`
- `cd backend && rg -n "partially_encoded|fully_encoded|absent_by_source|page 43|1.a|1.b|1.c" tests/test_call_subordinate_prompt_coverage.py`
Risks (if any): A count-only or fixture-only proof would still allow the real proof-call to look complete without source-grounded identity checks.

### [x] Task 2 — Complete the ERC PoC canonical YAML and prove proof-call closure

Goal:
Finish the real proof-call by encoding the official page-43 subordinate prompts under `1.b` and `1.c`, then prove the real call reaches full page-43 coverage and still passes dry-run ingest without claiming runtime consumption.
Slice: canonical-completion
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR4
Depends on: 1
Enables: 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
- `backend/tests/test_call_subordinate_prompt_coverage.py`
- `backend/tests/test_ingest_call_dry_run.py`
May touch files:
- `none`
Out of scope: canonical-persistence reproof, broad ERC runtime redesign, changing the activated snapshot beyond `schema_version` plus `expectations`, flat-call compatibility policy changes
Stop if: completing `1.b` and `1.c` would require widening the runtime snapshot seam, changing non-ERC proof-call artifacts, or introducing a fourth required file
Session boundary after: yes
Acceptance Criteria:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` preserves the official page-43 subordinate prompts across `1.a`, `1.b`, and `1.c` with stable prompt IDs and page-43 source traceability metadata.
- The fail-closed coverage proof flips from `partially_encoded` to `fully_encoded` for the real ERC PoC proof-call and still reports exact YAML prompt IDs or paths for every official page-43 prompt.
- Dry-run validation proves the completed real call remains ingestable.
TDD Plan:
- RED: extend the new coverage proof and existing dry-run test so they fail until `1.b` and `1.c` are encoded in the real YAML.
- GREEN: make the narrowest source-grounded YAML edits needed for full page-43 completion and update the coverage/dry-run assertions.
- REFACTOR: keep prompt IDs and traceability strings inline in the canonical YAML unless duplication across tests becomes unmanageable.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075"`
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run`
Risks (if any): Reusing dry-run alone as completeness evidence would fail closed incorrectly; source-to-YAML coverage proof must remain the primary completion seam.

### [x] Task 3 — Re-prove runtime-boundary honesty after proof-call completion

Goal:
Re-run the existing runtime-boundary seam after Task 2 so WF-0075 explicitly preserves WF-0074 honesty that structured-review runtime activation still exposes only `schema_version` plus `expectations`.
Slice: runtime-boundary
User Stories: US3
PRD Requirements: FR8
Depends on: 2
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: runtime snapshot expansion, docs/governance wording changes, repo-wide migration requirements
Stop if: preserving runtime-boundary honesty would require widening the activated snapshot seam or changing runtime-consumption behavior
Session boundary after: no
Acceptance Criteria:
- `backend/tests/test_structured_reviewer_service.py` still proves the structured-review runtime snapshot remains limited to `schema_version` plus `expectations` after the ERC PoC proof-call becomes fully encoded.
- Verification makes no claim that subordinate prompts are runtime-consumed for review generation.
TDD Plan:
- RED: tighten the existing runtime-boundary regression so it would fail if Task 2 accidentally broadens the activated snapshot seam.
- GREEN: keep or minimally update the assertion surface needed to re-prove the expectations-only runtime boundary.
- REFACTOR: keep the proof in the existing runtime test seam; do not create a second runtime-boundary surface.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only"`
- `cd backend && rg -n "call_config_snapshot =|schema_version|expectations" app/services/structured_reviewer_service.py app/engine/contracts.py app/engine/review_request_validator.py`
Risks (if any): If runtime-boundary proof is skipped after YAML completion, later closeout could overclaim review-generation impact from authoring-only fidelity work.

### [x] Task 4 — Conditional authoring/checklist clarification for three-state semantics

Execution outcome: skipped on 2026-03-12 because Tasks 1-3 already provide unambiguous executable proof for `absent_by_source`, `partially_encoded`, and `fully_encoded` without reopening WF-0074 governance surfaces.

Goal:
Apply only if Tasks 1-3 show executable proof still leaves ambiguity between `absent_by_source`, `partially_encoded`, and `fully_encoded` for proof-call closure.
Slice: authoring-contract
User Stories: US2, US3
PRD Requirements: FR5, FR7, FR8
Depends on: 1, 2, 3
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/call-yaml/authoring-workflow.md`
- `docs/call-yaml/onboarding-checklist.md`
- `backend/tests/test_call_yaml_authoring_contract.py`
May touch files:
- `none`
Out of scope: repo-wide migration requirements, schema redesign, runtime-consumption claims, broad documentation rewrites
Stop if: Tasks 1-3 already provide unambiguous executable proof, or the clarification would require weakening WF-0074's temporary compatibility posture or editing more than the two existing authoring-governance docs plus the contract test
Session boundary after: no
Acceptance Criteria:
- The workflow and checklist make it explicit, only if still needed, that when source prompts exist, partial preservation is not equivalent to source-grounded absence.
- Any wording change keeps existing flat canonical YAMLs temporarily compatible unless separately re-approved, while still requiring the ERC PoC proof-call to become fully encoded.
- Contract tests fail closed on any wording that blurs absent-by-source, partially encoded, and fully encoded states or overclaims runtime-consumption impact.
TDD Plan:
- RED: extend `backend/tests/test_call_yaml_authoring_contract.py` with WF-0075 assertions for the three-state distinction and preserved expectations-only runtime boundary only if Tasks 1-3 expose ambiguity not closed by executable proof.
- GREEN: add the smallest wording change needed in the authoring workflow and onboarding checklist.
- REFACTOR: keep the contract checks string-based unless the existing test file becomes too repetitive.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0075"`
- `rg -n "absent|partial|complete|subordinate prompts|runtime-consumption impact|temporarily compatible" docs/call-yaml/authoring-workflow.md docs/call-yaml/onboarding-checklist.md`
Risks (if any): Making this task unconditional would reopen WF-0074 governance even when executable proof already closes the ambiguity.

### [x] Task 5 — Conditional durable governance and baseline-anchored closure evidence

Execution outcome: skipped on 2026-03-12 because Task 4 was not needed, so no residual governance gap remained that required changes to `docs/logs/decisions.md` or `docs/memory/domain/project_docs.md`.

Goal:
Apply only if Task 4 proves a real governance gap remains; record WF-0075's narrow corrective boundary and fail-closed closure contract in durable governance surfaces so future closure cannot drop the three-state proof, `main...HEAD` scope proof, or audit-disposition gate.
Slice: durable-governance
User Stories: US2, US3
PRD Requirements: FR7, FR9, FR10
Depends on: 4
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
Stop if: Task 4 is skipped because no governance gap remains, or preserving the fail-closed closure gate would require broader governance-surface expansion beyond the existing decision log, project-doc memory file, and docs contract test
Session boundary after: yes
Acceptance Criteria:
- `docs/logs/decisions.md` records that WF-0075 completes the ERC PoC proof-call without reopening WF-0074, and that partial page-43 coverage must fail closed for the real proof-call.
- `docs/memory/domain/project_docs.md` records that WF-0075 closure must include `main...HEAD` scope proof plus a named audit-disposition artifact before any proceed or ship recommendation.
- `main...HEAD` scope proof is paired with explicit citations to `AD 74.3`, `AD 74.4`, and `WF-0074 planning/execution must preserve durable decision/memory guidance` for compatibility posture, proof-call policy, and runtime-boundary honesty.
- Contract tests prove the durable-governance wording preserves temporary flat-call compatibility, the expectations-only runtime seam, and the three-state fail-closed closure rule.
TDD Plan:
- RED: extend `backend/tests/test_call_yaml_authoring_contract.py` with WF-0075 durable-governance assertions covering partial-coverage failure, baseline-anchored scope proof, and audit-disposition closure only if Task 4 proves durable-governance wording is still required.
- GREEN: update the decision log and project-doc memory file with the narrowest approved-policy wording needed to preserve FR7/FR9/FR10 outside transient task/chat context.
- REFACTOR: reuse the existing string-fragment assertion helper instead of introducing a new docs-testing abstraction.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0075"`
- `rg -n "WF-0075|partial|main...HEAD|audit-disposition|temporarily compatible|expectations-only" docs/logs/decisions.md docs/memory/domain/project_docs.md`
- `git diff --name-only main...HEAD`
- `cd backend && rg -n "AD 74.3|AD 74.4|WF-0074 planning/execution must preserve durable decision/memory guidance" docs/logs/decisions.md docs/memory/domain/project_docs.md`
Risks (if any): If the closure gate stays only in the PRD or task plan, later implementation can appear complete while silently dropping the required scope-proof and audit-disposition evidence.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Page-43 source-to-YAML coverage | fail-closed coverage proof | `tests/test_call_subordinate_prompt_coverage.py` | every official page-43 subordinate prompt for `1.a`, `1.b`, and `1.c` maps to an exact YAML prompt ID/path | `fail` (default until executed) | pytest output in `backend/tests/test_call_subordinate_prompt_coverage.py` | count-only proof is insufficient |
| Partial-vs-complete negative proof | fail-closed coverage proof | `tests/test_call_subordinate_prompt_coverage.py` omitted-prompt case | omission of an official `1.b` or `1.c` prompt yields `partially_encoded` and fails closure | `fail` (default until executed) | pytest output in `backend/tests/test_call_subordinate_prompt_coverage.py` | required negative MVP case |
| Absent/complete/partial distinction | classification contract | `tests/test_call_subordinate_prompt_coverage.py` | elements with no source prompts may be `absent_by_source`; page-43 ERC PoC elements may not, and all three states are proven explicitly | `fail` (default until executed) | pytest output + expectation ledger in `backend/tests/test_call_subordinate_prompt_coverage.py` | three-state seam must be explicit |
| ERC PoC proof-call completion | dry-run ingest | `uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run` | completed ERC PoC call ingests successfully with page-43 subordinate prompts across `1.a`, `1.b`, and `1.c` | `fail` (default until executed) | dry-run stdout + pytest output in `backend/tests/test_ingest_call_dry_run.py` | real proof-call only |
| Runtime-boundary honesty | structured-review snapshot inspection | `test_wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only` | runtime snapshot remains limited to `schema_version` plus `expectations` after proof-call completion | `fail` (default until executed) | pytest output in `backend/tests/test_structured_reviewer_service.py` | no runtime-consumption claim allowed |
| Authoring/checklist three-state guard | docs contract test | `backend/tests/test_call_yaml_authoring_contract.py -k "wf0075"` | if executable proof leaves ambiguity, authoring docs distinguish absent vs partial vs complete and preserve temporary compatibility posture | `fail` (default until executed) | pytest output + doc diff, or explicit skip rationale | corrective wording only if needed |
| WF-0074 boundary preservation | durable governance docs | `backend/tests/test_call_yaml_authoring_contract.py -k "wf0075"` | if a governance gap remains, WF-0075 records a narrow corrective clarification without reopening WF-0074 mechanism/governance or tightening flat-call compatibility globally | `fail` (default until executed) | pytest output + doc diff in `docs/logs/decisions.md` and `docs/memory/domain/project_docs.md`, or explicit skip rationale | prior truth must remain explicit |
| Baseline-anchored scope proof | branch diff ledger | `git diff --name-only main...HEAD` + WF-0074 boundary citations | changed-file surface stays inside the approved WF-0075 boundary and cites the preserved WF-0074 compatibility/runtime boundary artifacts | `fail` (default until executed) | `main...HEAD` diff output + cited `docs/logs/decisions.md` / `docs/memory/domain/project_docs.md` refs in closeout artifact | required before proceed/ship |
| Audit disposition | named findings ledger | closure artifact ledger | every blocking finding is closed and every justified non-blocking finding is closed or rejected with rationale before any proceed/ship recommendation | `fail` (default until executed) | named audit-disposition artifact | fail-closed ship gate |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 2 file boundary omitted the coverage-proof test file even though Task 2 verification depends on that proof moving from RED to GREEN | non-blocking | add `backend/tests/test_call_subordinate_prompt_coverage.py` under Task 2 `May touch files` | closed | closed in v0.2 |
| Phase 2.2 task review | Task 1 did not require an explicit positive `absent_by_source` proof, leaving the third state too implicit | non-blocking | add one positive absent-by-source acceptance/TDD obligation and tighten the verification-matrix row | closed | closed in v0.2 |
| Phase 2.2 task review | Task 4 scope proof relied on raw `main...HEAD` diff text without explicit WF-0074 boundary citations | non-blocking | require boundary-artifact citations in Task 4 acceptance, verification, and matrix wording | closed | closed in v0.2 |
| Phase 2.2 task review | Audit-disposition section was a placeholder instead of a concrete closure ledger | non-blocking | replace the placeholder row with the actual Part B findings and planned closures | closed | closed in v0.2 |
| Fail-closed adversarial review | Task 2 overclaimed canonical persistence and bundled the YAML, coverage proof, dry-run proof, and runtime-boundary regression into an effective 4-file slice | blocking | remove unsupported persistence language, move coverage proof into Task 2 proper, and split runtime-boundary regression into its own atomic task | closed | closed in v0.3 |
| Fail-closed adversarial review | Tasks 3 and 4 made WF-0074 doc/governance edits mandatory even though the approved brainstorm/PRD allow them only if executable proof leaves a real ambiguity | blocking | convert the authoring and durable-governance follow-ons into conditional tasks gated by unresolved ambiguity after Tasks 1-3 | closed | closed in v0.3 |
| Fail-closed adversarial review | Task 5 acceptance referenced only generic WF-0074 boundary categories instead of the explicit approved citation targets already used in verification | non-blocking | align acceptance criteria to cite `AD 74.3`, `AD 74.4`, and the WF-0074 project-doc rule directly | closed | closed in v0.3 |

## Changelog

- v0.1 (2026-03-12): Initial task breakdown from PRD.
- v0.2 (2026-03-12): Applied Part B feedback by making the absent-by-source proof explicit, fixing the Task 2 file boundary, tightening `main...HEAD` scope proof with WF-0074 boundary citations, and replacing the audit-ledger placeholder with closed findings.
- v0.3 (2026-03-12): Removed unsupported persistence scope from Task 2, split runtime-boundary reproof into its own atomic slice to satisfy the 3-file limit, and made doc/governance follow-ons conditional so WF-0074 is only reopened if executable proof leaves a real ambiguity.
- v0.4 (2026-03-12): Marked Phase 3 tasks complete after targeted verification and walkthrough closeout evidence were recorded.
