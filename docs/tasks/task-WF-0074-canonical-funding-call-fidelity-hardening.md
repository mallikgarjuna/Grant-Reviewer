<!-- docs/tasks/task-WF-0074-canonical-funding-call-fidelity-hardening.md -->
# WF-0074 — Canonical Funding Call Fidelity Hardening

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-11

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Schema contract and legacy-flat compatibility

Goal:
Add the typed subordinate-prompt schema surface under evaluation elements while preserving the explicit compatibility posture for existing flat canonical YAMLs.
Slice: schema-compat
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR6, FR10, FR12
Depends on: none
Enables: 2, 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/call_definitions_v2.py`
- `backend/tests/test_call_definitions_v2_schema.py`
May touch files:
- `none`
Out of scope: template authoring, canonical proof-call edits, docs/checklist updates, runtime snapshot or engine contract changes
Stop if: adding subordinate prompts would force a runtime contract change or make existing flat canonical YAMLs invalid outside the explicitly documented temporary compatibility posture
Session boundary after: no
Acceptance Criteria:
- `CallDefinitionV2` gains a typed per-item subordinate-prompt shape with stable `id`, non-empty prompt content, and required source-traceability metadata.
- Validation rejects anonymous string lists, duplicate subordinate-prompt IDs within one evaluation element, empty prompt content, and missing required traceability fields.
- At least one existing real flat canonical YAML regression target still validates unchanged to prove the temporary compatibility posture remains intact.
TDD Plan:
- RED: add `test_wf0074_schema_accepts_typed_subordinate_prompts_and_legacy_flat_yaml` and `test_wf0074_schema_rejects_malformed_subordinate_prompt_items` in `backend/tests/test_call_definitions_v2_schema.py`.
- GREEN: implement the smallest `CallDefinitionV2` schema/validator change that admits the typed subordinate-prompt structure while preserving legacy flat YAML validity.
- REFACTOR: extract a tiny subordinate-prompt payload helper only if the new schema tests become repetitive.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_definitions_v2_schema.py -k "wf0074_schema_accepts_typed_subordinate_prompts_and_legacy_flat_yaml or wf0074_schema_rejects_malformed_subordinate_prompt_items"`
- `cd backend && rg -n "subordinate|prompt|traceability|legacy flat" tests/test_call_definitions_v2_schema.py app/schemas/call_definitions_v2.py`
Risks (if any): A loose schema can normalize anonymous nested prose and make future authoring look structured without actually preserving source-grounded fidelity.

### [ ] Task 2 — Tracer bullet: one real proof-call with dry-run validation

Goal:
Re-author one real canonical YAML proof-call to use the new subordinate-prompt structure and prove it validates through the existing dry-run seam without widening into runtime-consumption work.
Slice: tracer-bullet
User Stories: US1, US3
PRD Requirements: FR2, FR6, FR8, FR9, FR10, FR11
Depends on: 1
Enables: 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
- `backend/tests/test_ingest_call_dry_run.py`
May touch files:
- `none`
Out of scope: activating subordinate prompts in `structured_reviewer_service`, changing `backend/app/engine/contracts.py`, or widening into multi-call migration work
Stop if: `erc_poc_2026_full.yaml` cannot validate with subordinate prompts without changing the activated snapshot / engine contract seam beyond the PRD's explicit inspection-only boundary
Session boundary after: yes
Acceptance Criteria:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` demonstrates subordinate official prompts on at least one evaluation element using the new typed item shape.
- Dry-run validation proves the real proof-call remains ingestable under the updated schema.
- Task verification explicitly proves the runtime seam boundary is unchanged by showing the activated snapshot still carries only `schema_version` and `expectations`.
TDD Plan:
- RED: add `test_wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: make the smallest source-grounded edits to `erc_poc_2026_full.yaml` needed for the proof-call to validate under dry-run with subordinate prompts.
- REFACTOR: keep proof-call subordinate-prompt examples inline unless a second proof artifact becomes necessary, which is out of scope for this WF.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run`
- `cd backend && rg -n "call_config_snapshot =|schema_version|expectations" app/services/structured_reviewer_service.py app/engine/contracts.py app/engine/review_request_validator.py`
Risks (if any): A proof-call can falsely imply end-to-end review impact unless the task records that representability is proven while runtime consumption remains unchanged.

### [ ] Task 3 — Template default for subordinate-prompt fidelity

Goal:
Make the starter YAML teach subordinate-prompt preservation by default and prove the example shape remains valid under the updated schema.
Slice: template-default
User Stories: US1
PRD Requirements: FR3, FR10, FR11
Depends on: 1
Enables: 4
Parallelizable: yes
Files to modify:
Must touch files:
- `backend/data/calls/templates/call_definition_v2_template.yaml`
- `backend/tests/test_call_definitions_v2_schema.py`
May touch files:
- `none`
Out of scope: proof-call edits, docs/checklist wording, compatibility-policy changes, runtime seam changes
Stop if: keeping the template valid would require relaxing the subordinate-prompt schema contract introduced in Task 1
Session boundary after: no
Acceptance Criteria:
- The starter template includes at least one evaluation element encoded with subordinate prompt fidelity instead of only a flattened description.
- Template guidance makes the subordinate-prompt structure the copy-forward default when official source prompts exist.
- Validation coverage proves a minimally concretized template payload remains schema-valid.
TDD Plan:
- RED: add `test_wf0074_template_demonstrates_subordinate_prompt_default` in `backend/tests/test_call_definitions_v2_schema.py`.
- GREEN: update the template with the minimal valid subordinate-prompt example needed to teach the new shape by default.
- REFACTOR: keep template hydration logic test-local unless another template validation seam appears in-scope.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_definitions_v2_schema.py -k "wf0074_template_demonstrates_subordinate_prompt_default"`
- `cd backend && rg -n "subordinate|prompt|source_hint|evaluation_elements" data/calls/templates/call_definition_v2_template.yaml`
Risks (if any): If the template stays flatter than the schema allows, future authors will keep copying the lossy pattern even after the contract is hardened.

### [ ] Task 4 — Authoring workflow and checklist fail closed

Goal:
Update authoring guidance so subordinate official prompts must be preserved when present in source material, while keeping compatibility posture and runtime seam boundary explicit in the docs/checklist contract.
Slice: authoring-contract
User Stories: US2, US3
PRD Requirements: FR4, FR5, FR6, FR7, FR8, FR10, FR11
Depends on: 1, 2, 3
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/call-yaml/authoring-workflow.md`
- `docs/call-yaml/onboarding-checklist.md`
- `backend/tests/test_call_yaml_authoring_contract.py`
May touch files:
- `none`
Out of scope: decision-log or memory-surface expansion, review-engine implementation changes, repo-wide canonical call migration
Stop if: honest closure for this narrow, user-scoped plan would still require `docs/logs/decisions.md` or `docs/memory/domain/project_docs.md`, or if the docs/checklist cannot explain the MVP compatibility posture and seam boundary without widening beyond these two authoring documents
Session boundary after: yes
Acceptance Criteria:
- The workflow states that subordinate official prompts/questions under an evaluation element must be preserved explicitly rather than flattened into summary prose.
- The checklist adds a fail-closed fidelity gate covering prompt presence/absence by source and preserves the temporary compatibility posture for existing flat YAMLs.
- The docs/checklist explicitly state that this WF does not widen the activated snapshot / engine contract seam beyond its current `schema_version` plus `expectations` boundary.
- The task records that decision/memory guidance remains intentionally out of this narrow Phase 2 implementation slice and must trigger a stop/re-plan rather than being silently absorbed.
TDD Plan:
- RED: add `test_wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening` in `backend/tests/test_call_yaml_authoring_contract.py`.
- GREEN: update the workflow and checklist with the minimal wording needed to make prompt preservation, compatibility posture, and seam-boundary claims explicit.
- REFACTOR: keep the docs-contract assertions narrow and string-based unless a reusable documentation contract helper already exists.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening"`
- `rg -n "subordinate|flatten|compatibility|schema_version|expectations" docs/call-yaml/authoring-workflow.md docs/call-yaml/onboarding-checklist.md`
Risks (if any): Guidance can quietly reintroduce flattening or overclaim runtime impact even when the schema and proof-call are correct.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Schema representability | `CallDefinitionV2` model validation | `test_wf0074_schema_accepts_typed_subordinate_prompts_and_legacy_flat_yaml` | typed subordinate prompts validate and one legacy flat YAML still passes | planned | pytest output in `backend/tests/test_call_definitions_v2_schema.py` | compatibility posture must stay explicit |
| Malformed-shape rejection | `CallDefinitionV2` model validation | `test_wf0074_schema_rejects_malformed_subordinate_prompt_items` | malformed subordinate prompt items fail closed | planned | pytest output in `backend/tests/test_call_definitions_v2_schema.py` | duplicate IDs, empty text, and missing traceability must fail |
| Compatibility posture | schema validation regression | `test_wf0074_schema_accepts_typed_subordinate_prompts_and_legacy_flat_yaml` | one legacy flat YAML still validates while the proof-call uses subordinate prompts | planned | pytest output in `backend/tests/test_call_definitions_v2_schema.py` + proof-call dry-run stdout | separates backward compatibility from new-authoring fidelity proof |
| Proof-call example | dry-run ingest | `test_wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run` | `erc_poc_2026_full.yaml` validates with subordinate prompts | planned | pytest output in `backend/tests/test_ingest_call_dry_run.py` + dry-run stdout | one real call only |
| Template fidelity default | starter template | `test_wf0074_template_demonstrates_subordinate_prompt_default` | template teaches subordinate prompts and stays valid when minimally concretized | planned | pytest output in `backend/tests/test_call_definitions_v2_schema.py` | copy-forward default must be lossless |
| Authoring contract hardening | workflow + checklist docs | `test_wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening` | docs/checklist fail closed on flattening and preserve compatibility + seam boundary wording | planned | pytest output in `backend/tests/test_call_yaml_authoring_contract.py` | docs remain the runtime-claim boundary SSOT for this WF |
| Activated seam boundary | runtime snapshot inspection | `rg -n "call_config_snapshot =|schema_version|expectations" app/services/structured_reviewer_service.py app/engine/contracts.py app/engine/review_request_validator.py` | inspection still shows `schema_version` plus `expectations` only | planned | `rg` output against runtime seam files | inspection-only, no runtime code change in this WF |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Make the user-requested exclusion of decision/memory guidance explicit so Phase 3 does not silently drift from the narrow plan | non-blocking | Tighten Task 4 stop boundary and acceptance criteria | closed | closed in v0.2 |
| Phase 2.2 task review | Add a standalone compatibility-posture proof row so backward compatibility remains auditable separately from representability | non-blocking | Extend the verification matrix with a dedicated compatibility row | closed | closed in v0.2 |

## Changelog

- v0.1 (2026-03-11): Initial task breakdown from PRD.
- v0.2 (2026-03-11): Applied review edits by making the narrow governance-scope boundary explicit, adding a standalone compatibility-proof row, and closing the Part B audit ledger findings.
