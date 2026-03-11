<!-- docs/tasks/task-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-11

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Source-grounded PoC manifest

Goal:
Author the fail-closed source manifest for `ERC-2026-PoC` from the approved official files so later YAML authoring cannot drift from the accepted structure and evaluation criteria/elements sources.
Slice: source-manifest
User Stories: US1
PRD Requirements: FR1, FR2, FR5, FR6, FR7, FR8, FR13, FR14
Depends on: none
Enables: 2, 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/sources/erc_poc_2026_full.sources.md`
- `backend/tests/test_ingest_call_dry_run.py`
May touch files:
- `docs/logs/decisions.md`
Out of scope: canonical YAML authoring, ingest/runtime code, generic manifest enforcement for all calls
Stop if: any required official source file, section locator, or `SHA256` value cannot be resolved from the approved ERC PoC source set
Session boundary after: no
Acceptance Criteria:
- The manifest records the PoC proposal/application-structure source and the PoC evaluation criteria/elements source with explicit `Used for` traceability and `SHA256` metadata.
- The manifest notes the applicant guidance as a cross-check source without replacing the ERC work programme as the primary evaluation criteria/elements authority.
- The manifest preserves one-call scope and names only `ERC-2026-PoC` authoring targets.
- Regression coverage proves the manifest gate fails closed when a required source class, `SHA256`, or `Used for` field is missing for `ERC-2026-PoC`.
TDD Plan:
- RED: add `wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: author the minimal manifest content and manifest-gate assertions needed for dry-run validation to reject incomplete PoC source traceability.
- REFACTOR: keep manifest fixtures inline unless a second PoC traceability case makes extraction materially clearer.
Verification Steps:
- `sha256sum /home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/af_he-erc-poc_en.pdf /home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/wp_horizon-erc-2026_en.pdf /home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/information-for-applicants_he-erc-poc_en.pdf`
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability"`
- `cd backend && rg -n "SHA256|Used for|ERC-2026-PoC|evaluation criteria|proposal structure" data/calls/sources/erc_poc_2026_full.sources.md`
Risks (if any): A weak manifest can create fake progress by allowing speculative YAML authoring to look source-grounded.

### [ ] Task 2 — Tracer bullet: canonical YAML plus dry-run validation

Goal:
Author the smallest source-grounded canonical `ERC-2026-PoC` call definition and prove it survives existing dry-run validation before any DB ingest or runtime proof is attempted.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR13, FR14
Depends on: 1
Enables: 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
- `backend/data/calls/sources/erc_poc_2026_full.sources.md`
- `backend/tests/test_ingest_call_dry_run.py`
May touch files:
- `backend/data/calls/README.md`
Out of scope: DB ingest, public API exposure proof, structured-review runtime changes
Stop if: dry-run reveals that `ERC-2026-PoC` cannot validate without changing runtime behavior or borrowing unsupported ERC stage semantics
Session boundary after: yes
Acceptance Criteria:
- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` models a single-step `ERC-2026-PoC` call with only evaluable narrative content, official evaluation criteria/elements, and enforceable constraints.
- Dry-run succeeds for `erc_poc_2026_full.yaml` with no unresolved expectation references and no unsupported split-role opt-in by default.
- Regression coverage proves the dry-run contract for the new PoC artifact and protects against accidental stage-semantics inheritance.
TDD Plan:
- RED: add `wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml` in `backend/tests/test_ingest_call_dry_run.py`.
- GREEN: author the minimal manifest-backed canonical YAML needed for `ERC-2026-PoC` to validate through the existing ingest dry-run seam.
- REFACTOR: tighten YAML comments or dry-run assertions only if PoC source-traceability is otherwise hard to audit.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml"`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run`
- `cd backend && rg -n "ERC-2026-PoC|single-step|breakthrough innovation potential|approach and methodology|strategic leadership" data/calls/canonical/erc/erc_poc_2026_full.yaml`
Risks (if any): PoC source details can be subtly overfit to existing ERC StG/CoG patterns unless the task explicitly fails closed on unsupported stage reuse.

### [ ] Task 3 — Activate the call and prove exposure seams

Goal:
Ingest the real PoC call into the target DB and prove it appears through the existing listing and node-metadata seams without widening scope beyond one call.
Slice: activation-exposure
User Stories: US2
PRD Requirements: FR1, FR9, FR10, FR11, FR13, FR14
Depends on: 2
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_ingest_call_v2_db.py`
- `backend/tests/test_api.py`
- `backend/tests/test_call_nodes_metadata_api.py`
May touch files:
- `backend/main.py`
- `backend/app/services/node_metadata_service.py`
Out of scope: frontend form rendering work, BFF changes, generic ERC activation cleanup unrelated to `ERC-2026-PoC`
Stop if: making `ERC-2026-PoC` appear in `/calls` and `/api/public/calls/{call_logical_id}/nodes/metadata` would require changes across multiple product surfaces instead of one call-local activation seam
Session boundary after: yes
Acceptance Criteria:
- DB ingest of `erc_poc_2026_full.yaml` succeeds in the target environment.
- `/calls` includes `ERC-2026-PoC` after ingest and the node-metadata endpoint resolves PoC node metadata for the authored logical IDs.
- If any activation/exposure fix is needed, it stays localized to the smallest backend seam required for this one call.
TDD Plan:
- RED: add `wf0073_contract_erc_poc_2026_ingest_exposes_call_listing` in `backend/tests/test_api.py`, `wf0073_contract_erc_poc_2026_node_metadata_exposes_authored_nodes` in `backend/tests/test_call_nodes_metadata_api.py`, and `wf0073_contract_erc_poc_2026_db_ingest_persists_single_step_call` in `backend/tests/test_ingest_call_v2_db.py`.
- GREEN: implement only the minimum ingest or exposure seam change required for the ingested PoC call to appear through the existing backend APIs, while asserting the ingested PoC call does not inherit unsupported multi-step ERC stage behavior.
- REFACTOR: extract a tiny call-seeding helper only if PoC setup is duplicated across the three backend test files.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_v2_db.py -k "wf0073_contract_erc_poc_2026_db_ingest_persists_single_step_call"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0073_contract_erc_poc_2026_ingest_exposes_call_listing"`
- `cd backend && uv run pytest tests/test_call_nodes_metadata_api.py -k "wf0073_contract_erc_poc_2026_node_metadata_exposes_authored_nodes"`
Risks (if any): Exposure can fail even when dry-run passes because the DB projection and API surfaces read ingested state, not raw YAML.

### [ ] Task 4 — Backend structured-review smoke for PoC

Goal:
Prove the MVP runtime seam by exercising `POST /api/structured-review` with a valid `ERC-2026-PoC` payload and capturing deterministic pass/fail evidence.
Slice: structured-review-smoke
User Stories: US3
PRD Requirements: FR1, FR10, FR12, FR13, FR14
Depends on: 3
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
- `backend/tests/fixtures/wf_0073_erc_poc_2026_structured_review.json`
May touch files:
- `backend/main.py`
- `backend/app/services/structured_reviewer_service.py`
Out of scope: frontend/BFF proof, multi-scenario review coverage, generic review-engine redesign
Stop if: a passing PoC smoke request would require widening the runtime proof surface beyond backend `/api/structured-review`
Session boundary after: yes
Acceptance Criteria:
- One valid PoC submission payload aligned to authored node IDs produces a successful structured-review response with no call-contract errors.
- Runtime proof explicitly demonstrates the PoC path remains single-step and does not require staged ERC activation semantics.
- Replayable evidence records the request seam, payload fixture reference, and deterministic outcome for the PoC smoke proof.
- The proof remains explicitly backend-only and does not overclaim browser or BFF coverage.
TDD Plan:
- RED: add `wf0073_contract_structured_api_accepts_erc_poc_2026_payload` in `backend/tests/test_api.py` and `wf0073_contract_structured_service_resolves_erc_poc_2026_snapshot` in `backend/tests/test_structured_reviewer_service.py`.
- RED: add `wf0073_contract_structured_service_keeps_erc_poc_2026_single_step_activation` in `backend/tests/test_structured_reviewer_service.py`.
- GREEN: implement only the minimum backend change required for the real ingested PoC call to pass the structured-review seam, or wire the smoke fixture if no production change is needed.
- REFACTOR: extract a small PoC payload builder or fixture loader only if structured-review setup becomes noisy.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0073_contract_structured_api_accepts_erc_poc_2026_payload"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0073_contract_structured_service_resolves_erc_poc_2026_snapshot"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0073_contract_structured_service_keeps_erc_poc_2026_single_step_activation"`
- `cd backend && rg -n "ERC-2026-PoC|erc_poc_2026|structured-review" tests/test_api.py tests/test_structured_reviewer_service.py tests/fixtures`
Risks (if any): A smoke proof can pass syntactically while still hiding call-resolution drift unless the payload uses the real authored node IDs and ingested call code.

### [ ] Task 5 — Call-local compatibility closure and verification matrix evidence

Goal:
Close the workflow with a single evidence bundle that records manifest, dry-run, ingest, exposure, and structured-review proof results, while constraining any discovered fix to a narrow PoC-specific seam.
Slice: evidence-closure
User Stories: US1, US2, US3
PRD Requirements: FR1, FR11, FR12, FR13, FR14
Depends on: 4
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0073-erc-poc-2026-call-onboarding.md`
- `docs/index.md`
- `docs/logs/decisions.md`
May touch files:
- `none`
Out of scope: new product claims beyond one-call onboarding, cross-call hardening, shipping a broader ERC support statement
Stop if: Task 4 still leaves an unresolved compatibility question or the evidence bundle would need to claim unsupported product surfaces
Session boundary after: yes
Acceptance Criteria:
- The walkthrough contains one verification matrix covering manifest, dry-run, DB ingest, `/calls`, `/api/public/calls/{call_logical_id}/nodes/metadata`, and `POST /api/structured-review`, with exact commands/tests, outcomes, and evidence pointers.
- Any compatibility fix is documented as either unnecessary or confined to one narrow backend seam for `ERC-2026-PoC`.
- Completion language stays bounded to getting `ERC-2026-PoC` live through the approved backend seams before the 2026-03-17 cut-off.
- Every walkthrough matrix row resolves from `planned` to explicit `pass`, `fail`, or `skipped` with a replayable evidence reference before any ship recommendation.
TDD Plan: N/A
Verification Steps:
- `rg -n "ERC-2026-PoC|/calls|nodes/metadata|/api/structured-review|verification matrix" docs/walkthroughs/walkthrough-WF-0073-erc-poc-2026-call-onboarding.md`
- `rg -n "Source manifest gate|Dry-run ingest|DB ingest|Call exposure|Node metadata exposure|Structured-review smoke" docs/walkthroughs/walkthrough-WF-0073-erc-poc-2026-call-onboarding.md`
- `rg -n "pass|fail|skipped|wf0073_contract_|erc_poc_2026_full|/api/structured-review|/api/public/calls/.*/nodes/metadata|/calls" docs/walkthroughs/walkthrough-WF-0073-erc-poc-2026-call-onboarding.md`
Risks (if any): Without a single fail-closed evidence bundle, the WF can overclaim readiness from partial proof.

## Verification Matrix

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Source manifest gate | source manifest | `wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability` | manifest rejects missing source class / `SHA256` / `Used for`, and authored manifest satisfies the gate | planned | pytest output for `wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability` + `sha256sum` output | |
| Dry-run ingest | `backend/scripts/ingest_call.py --dry-run` | `uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_poc_2026_full.yaml --dry-run` | dry-run exits 0 with clean summary | planned | pytest output for `wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml` + ingest dry-run stdout | |
| DB ingest | ingest script | `wf0073_contract_erc_poc_2026_db_ingest_persists_single_step_call` | call persists cleanly | planned | pytest output for `wf0073_contract_erc_poc_2026_db_ingest_persists_single_step_call` | |
| Call exposure | `GET /calls` | `wf0073_contract_erc_poc_2026_ingest_exposes_call_listing` | `/calls` includes `ERC-2026-PoC` | planned | pytest output for `wf0073_contract_erc_poc_2026_ingest_exposes_call_listing` | |
| Node metadata exposure | `GET /api/public/calls/{call_logical_id}/nodes/metadata` | `wf0073_contract_erc_poc_2026_node_metadata_exposes_authored_nodes` | metadata endpoint resolves PoC nodes | planned | pytest output for `wf0073_contract_erc_poc_2026_node_metadata_exposes_authored_nodes` | |
| Structured-review smoke | `POST /api/structured-review` | `wf0073_contract_structured_api_accepts_erc_poc_2026_payload` | smoke request succeeds without call-contract errors | planned | pytest output for `wf0073_contract_structured_api_accepts_erc_poc_2026_payload` + fixture `backend/tests/fixtures/wf_0073_erc_poc_2026_structured_review.json` | |

## Changelog

- v0.1 (2026-03-11): Initial task breakdown from PRD.
- v0.2 (2026-03-11): Applied review fixes by anchoring source-hash commands to exact file paths, narrowing the structured-review fixture target to one file, removing code spillover from the evidence-close task, and adding an explicit single-step runtime guard for PoC.
- v0.3 (2026-03-11): Added an explicit fail-closed manifest regression seam to Task 1 and tightened Task 5/matrix evidence requirements to require replayable row-level proof instead of doc-diff closure.
