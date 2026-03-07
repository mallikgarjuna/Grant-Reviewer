<!-- docs/tasks/task-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-07

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Fail-closed MSCA upload gate on the ingest seam

Goal:
Freeze the Phase 3 authoring gate in executable form so `MSCA-PF-2025` cannot be treated as valid ingest progress without a complete per-call manifest covering both required official source classes, while locking the MVP proof seam to backend `/api/structured-review` only.
Slice: source-gate
User Stories: US1, US2, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR13
Depends on: none
Enables: 2, 3, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/scripts/ingest_call.py`
- `backend/tests/test_ingest_call_dry_run.py`
- `backend/data/calls/README.md`
May touch files:
- `docs/call-yaml/onboarding-checklist.md`
Out of scope: substantive `MSCA-PF-2025` YAML authoring, frontend/BFF work, generic multi-call source-governance framework
Stop if: enforcing the gate would require a repo-wide onboarding redesign instead of a call-specific fail-closed check for `MSCA-PF-2025`
Session boundary after: no
Acceptance Criteria:
- `MSCA-PF-2025` dry-run or ingest attempts fail closed when `backend/data/calls/sources/msca_pf_2025_full.sources.md` is missing or does not prove both required official source classes with durable hash metadata.
- Existing canonical calls continue to dry-run and ingest unchanged.
- Repo guidance for call YAML explicitly states that WF-0061 runtime proof is limited to backend `/api/structured-review`, not frontend or multi-surface proof.
TDD Plan:
- RED: add `wf0061_contract_ingest_blocks_msca_pf_2025_without_two_uploaded_sources` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: implement the smallest `ingest_call.py` manifest gate needed to reject incomplete `MSCA-PF-2025` source provenance before dry-run/ingest success is reported.
- REFACTOR: tighten README/onboarding wording only if the new gate semantics are otherwise ambiguous.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_ingest_blocks_msca_pf_2025_without_two_uploaded_sources"`
- `cd backend && rg -n "MSCA-PF-2025|/api/structured-review|sources.md" scripts/ingest_call.py data/calls/README.md`
Risks (if any): A weak manifest check could create fake “source-gated” progress while still allowing speculative MSCA authoring to pass as valid.

### [x] Task 2 — Source-grounded MSCA manifest and canonical dry-run

Goal:
After the official `MSCA-PF-2025` source documents are uploaded in Phase 3, author the per-call manifest and canonical YAML from those exact sources and prove deterministic dry-run validation on the real artifact.
Slice: canonical-authoring
User Stories: US1, US2, US3
PRD Requirements: FR2, FR3, FR4, FR5, FR6, FR7
Depends on: 1
Enables: 3, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`
- `backend/data/calls/sources/msca_pf_2025_full.sources.md`
- `backend/tests/test_ingest_call_dry_run.py`
May touch files:
- `backend/data/calls/README.md`
Out of scope: second-call authoring, placeholder criteria/elements, frontend form modeling
Stop if: the official `MSCA-PF-2025` narrative/application-structure source and evaluation criteria/elements source have not both been uploaded and accepted for this run
Session boundary after: no
Acceptance Criteria:
- `backend/data/calls/sources/msca_pf_2025_full.sources.md` records the accepted official source set with provenance notes, usage labels, and SHA256 hashes.
- `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml` contains only source-grounded structure, evaluation criteria/elements, and enforceable constraints for `MSCA-PF-2025`.
- Dry-run validation passes deterministically for the new canonical file with no speculative placeholders.
TDD Plan:
- RED: add `wf0061_contract_msca_pf_2025_dry_run_passes_with_uploaded_sources` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: author the minimal real `MSCA-PF-2025` manifest and canonical YAML needed to satisfy the uploaded sources and existing v2 schema.
- REFACTOR: normalize manifest wording or YAML comments only if traceability becomes hard to audit.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_msca_pf_2025_dry_run_passes_with_uploaded_sources"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/msca/msca_pf_2025_full.yaml --dry-run`
- `cd backend && rg -n "SHA256|Used for|MSCA" data/calls/sources/msca_pf_2025_full.sources.md`
Risks (if any): MSCA source documents may blur structure and evaluation evidence boundaries; the task must fail closed rather than infer missing details.

### [x] Task 3 — Tracer bullet: local ingest plus backend structured-review proof

Goal:
Use the real ingested `MSCA-PF-2025` call as the earliest end-to-end tracer bullet by proving the selected MVP seam, backend `/api/structured-review`, works with the canonical artifact and no frontend/BFF dependency.
Slice: tracer-bullet
User Stories: US1, US3, US4
PRD Requirements: FR6, FR7, FR8, FR8a, FR8b, FR9, FR9a, FR13
Depends on: 2
Enables: 4, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/main.py`
- `backend/app/services/structured_reviewer_service.py`
Out of scope: frontend universal-submit changes, BFF proxy changes, multi-surface runtime proof
Stop if: the real `MSCA-PF-2025` ingest reveals that backend `/api/structured-review` cannot be used without coordinated frontend/BFF or other multi-surface expansion
Session boundary after: yes
Acceptance Criteria:
- Local ingest of `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml` succeeds and makes the new call available to backend structured review.
- One deterministic backend proof exercises `MSCA-PF-2025` through `/api/structured-review` using the real canonical artifact, not a synthetic stand-in.
- Proof evidence captures the exercised seam, the canonical artifact path/code, and the deterministic pass/fail result.
TDD Plan:
- RED: add `wf0061_contract_structured_api_tracer_accepts_real_msca_pf_2025_call` in `backend/tests/test_api.py` and `wf0061_contract_structured_service_uses_real_msca_pf_2025_snapshot` in `backend/tests/test_structured_reviewer_service.py`.
- GREEN: implement only the minimum backend route/service change required for the ingested MSCA call to pass through the selected proof seam.
- REFACTOR: extract a tiny backend helper only if proof-evidence assembly or call-resolution logic is duplicated.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0061_contract_structured_api_tracer_accepts_real_msca_pf_2025_call"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_structured_service_uses_real_msca_pf_2025_snapshot"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/msca/msca_pf_2025_full.yaml`
Risks (if any): The new call may validate yet still expose backend assumptions about currently ingested call families; that is acceptable only if the fix stays on one narrow backend seam.

### [x] Task 4 — Narrow backend compatibility seam or explicit no-fix proof

Goal:
If Task 3 exposes an MSCA-specific backend incompatibility, constrain the fix to one narrow seam and codify the resulting invariant; if no fix is needed, codify that no-fix outcome with a deterministic regression.
Slice: backend-compat
User Stories: US3, US4
PRD Requirements: FR10, FR11, FR11a, FR12
Depends on: 3
Enables: 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/main.py`
Out of scope: generalized multi-call abstractions, frontend/BFF proof wiring, cross-call hardening unrelated to `MSCA-PF-2025`
Stop if: the smallest viable fix spans more than one major product surface or requires changes beyond one narrow backend seam
Session boundary after: no
Acceptance Criteria:
- Any compatibility change remains confined to one narrow backend seam directly required by `MSCA-PF-2025`.
- Regression coverage proves the seam remains stable for existing structured-review behavior.
- If no production-code fix is required, the new regression explicitly proves the existing seam already satisfies the MSCA contract.
TDD Plan:
- RED: add `wf0061_contract_msca_backend_compatibility_stays_single_seam` in `backend/tests/test_structured_reviewer_service.py`.
- GREEN: apply only the minimum backend seam change required by Task 3 findings, or add the no-fix regression assertions if Task 3 already passes cleanly.
- REFACTOR: collapse any MSCA-only branch into a smaller helper or inline guard if the seam becomes hard to audit.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_msca_backend_compatibility_stays_single_seam"`
- `cd backend && rg -n "msca|MSCA|wf0061" app/services/structured_reviewer_service.py main.py tests/test_structured_reviewer_service.py`
Risks (if any): A seemingly “small” fix can silently become cross-call hardening if the task does not assert the single-seam boundary.

### [x] Task 5 — Ordered-gate and blocker-boundary closure contracts

Goal:
Lock the workflow’s core safety invariants so runtime proof cannot count before upload/validation/ingest succeed for the same artifact, and broad multi-surface proof candidates fail as blockers instead of sliding into scope.
Slice: closure-guard
User Stories: US2, US3, US4
PRD Requirements: FR8a, FR8b, FR9, FR9a, FR10, FR11, FR11a, FR12
Depends on: 3, 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_ingest_call_dry_run.py`
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/main.py`
- `backend/scripts/ingest_call.py`
Out of scope: new proof orchestration framework, frontend blocker handling, generic governance automation
Stop if: proving ordered gates or blocker boundaries requires introducing a second runtime proof surface or a repo-wide workflow engine
Session boundary after: yes
Acceptance Criteria:
- Automated coverage proves runtime proof is invalid when upload-gate, validation, or ingest has not passed for the same `MSCA-PF-2025` artifact.
- Automated coverage proves a proof candidate that would require multiple major surfaces is treated as a blocker/escalation condition rather than normal MVP work.
- Verification remains scoped to `MSCA-PF-2025` and the chosen backend structured-review seam.
TDD Plan:
- RED: add `wf0061_contract_runtime_proof_requires_upload_validate_ingest_order` in `backend/tests/test_api.py`, `wf0061_contract_multisurface_proof_candidate_stops_for_rescope` in `backend/tests/test_structured_reviewer_service.py`, and `wf0061_contract_ingest_gate_blocks_runtime_credit_without_uploaded_msca_manifest` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: add only the minimal assertions and guard logic required to enforce ordered proof acceptance and blocker surfacing for the selected seam.
- REFACTOR: trim duplicated WF-0061 setup/helpers across the three backend test files if closure selectors become noisy.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0061_contract_runtime_proof_requires_upload_validate_ingest_order"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_multisurface_proof_candidate_stops_for_rescope"`
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_ingest_gate_blocks_runtime_credit_without_uploaded_msca_manifest"`
Risks (if any): Without explicit ordered-gate and blocker selectors, Phase 3 can claim success from a passing tracer while still violating the WF’s core scope and evidence rules.

### [ ] Task 6 — Walkthrough evidence for the one-call proof claim

Goal:
Capture the final WF-0061 evidence bundle so completion claims stay traceable to one landed canonical call, one manifest, one selected runtime seam, and any narrow compatibility seam actually used.
Slice: evidence
User Stories: US1, US3, US4
PRD Requirements: FR8a, FR9, FR12, FR13
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0061-real-call-data-expansion-single-call.md`
May touch files:
- `docs/index.md`
- `docs/logs/decisions.md`
Out of scope: new product claims, multi-call marketing copy, unrelated workflow cleanups
Stop if: the recorded evidence would need to claim frontend/BFF coverage, a second call, or a broader platform redesign to present `WF-0061` as complete
Session boundary after: yes
Acceptance Criteria:
- The walkthrough records the exact canonical artifact path `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`, the exact manifest path `backend/data/calls/sources/msca_pf_2025_full.sources.md`, the selected proof seam, verification commands, and deterministic outcomes used for `WF-0061`.
- If a compatibility seam was touched, the walkthrough names that seam and the regression evidence proving it remained narrow.
- Success language is limited to landing one new promised canonical call, `MSCA-PF-2025`.
TDD Plan: N/A
Verification Steps:
- `rg -n "MSCA-PF-2025|/api/structured-review|one new promised canonical call" docs/walkthroughs/walkthrough-WF-0061-real-call-data-expansion-single-call.md`
- `git diff -- docs/walkthroughs/walkthrough-WF-0061-real-call-data-expansion-single-call.md`
Risks (if any): Evidence wording can drift into vague “MSCA support” claims unless the walkthrough stays pinned to the one-call proof claim.

## Changelog

- v0.1 (2026-03-07): Initial task breakdown from PRD.
- v0.2 (2026-03-07): Hardened deterministic verification selectors, reduced Task 3 must-touch scope, tightened walkthrough artifact traceability, and marked Ready for Implementation.
