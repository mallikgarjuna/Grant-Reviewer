# WF-0044 — P1 #12: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-02

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer Bullet: Canonical CoG v2 ingest path

Goal:
Deliver a tracer bullet proving `erc_cog_2026_full` can be authored in canonical v2 format, traced to sources, and validated via ingest dry-run.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR6
Depends on: none
Enables: Task 2, Task 6
Parallelizable: no
Files to modify:
- `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
- `backend/data/calls/legacy/erc/erc_cog_2026_full_official.yaml`
- `backend/data/calls/sources/erc_cog_2026_full.sources.md`
- `backend/tests/test_ingest_call_dry_run.py`
Acceptance Criteria:
- Canonical file `erc_cog_2026_full.yaml` exists and is v2-valid (no mixed v1 keys).
- Legacy mirror `erc_cog_2026_full_official.yaml` is refreshed for traceability parity only (no behavior expansion).
- Source manifest includes both source classes (application form + evaluation criteria elements) with required metadata fields.
- Manifest entries include both origin context and copied-local path under `backend/data/calls/source_files/WF-0044/...`.
- Dry-run ingest test explicitly validates `erc_cog_2026_full`.
TDD Plan: RED: add failing dry-run test case in `test_ingest_call_dry_run.py` for missing/non-valid CoG file; GREEN: author YAML + manifest to make dry-run pass; REFACTOR: normalize comments/ordering in YAML for deterministic diffs.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k erc_cog_2026_full`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run`
Risks (if any):
- Existing legacy CoG wording may contain v1-era naming that needs careful minimal-change normalization.

### [x] Task 2 — CoG real ingest + structured API acceptance

Goal:
Prove primary acceptance path: local DB ingest succeeds and one structured review API request returns review cards for `erc_cog_2026_full`.
Slice: acceptance-e2e
User Stories: US2
PRD Requirements: FR6, FR10
Depends on: Task 1
Enables: Task 9
Parallelizable: no
Files to modify:
- `backend/tests/test_ingest_call_v2_db.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- DB ingest test includes `erc_cog_2026_full` success coverage.
- Structured API test posts `call_code=erc_cog_2026_full` (via seeded call id lookup) and asserts non-empty review cards on happy path.
TDD Plan: RED: add failing DB/API acceptance tests for CoG; GREEN: seed/fixture adjustments required for CoG path to pass; REFACTOR: reduce fixture duplication between API and ingest tests.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_v2_db.py -k erc_cog_2026_full`
- `cd backend && uv run pytest tests/test_api.py -k "structured_review and erc_cog_2026_full"`
Risks (if any):
- Local DB fixture setup may need additional canonical call seed ordering.

### [x] Task 3 — Minimal-change refresh: NWO Veni call + manifest

Goal:
Apply source-grounded minimal corrections to `nwo_veni_2025_preproposal` and refresh its manifest metadata without node-id churn.
Slice: baseline-refresh-veni
User Stories: US1, US3
PRD Requirements: FR2, FR5, FR6, FR13
Depends on: Task 1
Enables: Task 9
Parallelizable: yes
Files to modify:
- `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
- `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`
Acceptance Criteria:
- YAML updates are source-proven only; no unnecessary structure rewrites.
- Manifest has required fields (`Path`, `SHA256`, `Used for`, source URL/page or provenance note, provided/downloaded date).
- Manifest records both source origin and local copied path for WF-0044 source-gate traceability.
- Any node-id change (if unavoidable) includes explicit decision-log reference note in task implementation artifacts.
TDD Plan: RED: add/update failing case in `tests/test_ingest_call_dry_run.py` for `nwo_veni_2025_preproposal`; GREEN: apply minimal corrections until dry-run passes; REFACTOR: tighten comments for traceability without changing semantics.
Verification Steps:
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
Risks (if any):
- Hidden ID drift from manual edits can break downstream expectations.

### [x] Task 4 — Minimal-change refresh: NWO Vidi call + manifest

Goal:
Apply source-grounded minimal corrections to `nwo_vidi_2025_full_proposal` and refresh its manifest metadata.
Slice: baseline-refresh-vidi
User Stories: US1, US3
PRD Requirements: FR2, FR5, FR6, FR13
Depends on: Task 1
Enables: Task 9
Parallelizable: yes
Files to modify:
- `backend/data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml`
- `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`
Acceptance Criteria:
- YAML reflects only source-backed corrections.
- Manifest is complete with required traceability metadata and dual-path context.
- Node IDs remain stable unless explicitly justified and mapped.
TDD Plan: RED: add/update failing case in `tests/test_ingest_call_dry_run.py` for `nwo_vidi_2025_full_proposal`; GREEN: apply minimal corrections until ingest succeeds; REFACTOR: remove redundant wording while preserving behavior.
Verification Steps:
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run`
Risks (if any):
- Over-editing this mature baseline could regress prompt/node assumptions.

### [x] Task 5 — Minimal-change refresh: ERC StG call + manifest

Goal:
Apply source-grounded minimal corrections to `erc_stg_2026_full` and refresh its manifest metadata.
Slice: baseline-refresh-stg
User Stories: US1, US3
PRD Requirements: FR2, FR5, FR6, FR13
Depends on: Task 1
Enables: Task 9
Parallelizable: yes
Files to modify:
- `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
- `backend/data/calls/sources/erc_stg_2026_full.sources.md`
Acceptance Criteria:
- YAML changes remain minimal-change and source-grounded.
- Manifest includes required fields and updated provenance/hash metadata.
- Manifest explicitly captures dual-path traceability (source origin + local copied path).
- Node IDs stay stable unless explicitly governed with mapping notes.
TDD Plan: RED: add/update failing case in `tests/test_ingest_call_dry_run.py` for `erc_stg_2026_full`; GREEN: apply minimal corrections until dry-run passes; REFACTOR: clean source comments for consistency.
Verification Steps:
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run`
Risks (if any):
- Step-scoped guidance text is sensitive; accidental scope drift can affect policy behavior.

### [x] Task 6 — Structured pipeline: apply reviewer_policy scope at runtime

Goal:
Ensure structured pipeline v1 resolves and applies call-definition `reviewer_policy` by stage/node scope for each submitted node.
Slice: policy-runtime-scope
User Stories: US4
PRD Requirements: FR7, FR8, FR9
Depends on: Task 1
Enables: Task 7, Task 8
Parallelizable: no
Files to modify:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/reviewer_policy.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Structured service resolves applicable policy rules per node/stage using call definition data.
- `PROMPT_ONLY` rules influence prompt path only (no deterministic warn/block side effects).
- Existing `nwo_veni_2025_preproposal` structured contract behavior is unchanged.
TDD Plan: RED: add failing structured-service tests for stage/node filtering and prompt-only behavior; GREEN: wire policy extraction/filtering into structured path; REFACTOR: deduplicate rule-selection logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k reviewer_policy`
- `cd backend && uv run pytest tests/test_reviewer_policy.py`
Risks (if any):
- Diverging policy-selection logic from single-snippet path can create inconsistent behavior.

### [x] Task 7 — Structured pipeline: deterministic POST_CHECK/BLOCKING enforcement

Goal:
Implement deterministic post-generation enforcement in structured pipeline v1 for `POST_CHECK` warnings and `BLOCKING` failures with no partial cards.
Slice: policy-enforcement-contract
User Stories: US4
PRD Requirements: FR7, FR11, FR14
Depends on: Task 6
Enables: Task 8, Task 9
Parallelizable: no
Files to modify:
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_review_execution_core.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- `POST_CHECK` violations complete with deterministic warning signal.
- `BLOCKING` violations return stable blocking-failure category and no review cards.
- Deterministic WF-0044 selector naming (`wf0044_policy_<surface>_<case_id>`) is used in new/updated tests.
TDD Plan: RED: add failing API/core tests for POST_CHECK and BLOCKING outcomes (including empty cards assertion); GREEN: enforce deterministic failure/warning mapping in structured execution path; REFACTOR: centralize summary convention constants used by tests.
Verification Steps:
- `cd backend && uv run pytest -k wf0044_policy_`
- `cd backend && uv run pytest tests/test_api.py -k "structured_review and policy"`
Risks (if any):
- If enforcement occurs after persistence, partial-card leakage can violate contract.

### [ ] Task 8 — Contract matrix fixture update for WF-0044 policy selectors

Goal:
Add WF-0044 policy contract fixture cases covering `PROMPT_ONLY`, `POST_CHECK`, and `BLOCKING` for structured surface.
Slice: policy-matrix
User Stories: US4
PRD Requirements: FR7, FR11, FR14
Depends on: Task 7
Enables: Task 9
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/wf_0044_policy_matrix.yaml`
- `backend/tests/test_review_execution_core.py`
Acceptance Criteria:
- Fixture contains WF-0044-targeted case IDs/selectors and expected conventions for all 3 modes.
- Tests assert no-card payload behavior for blocking failure cases.
TDD Plan: RED: introduce failing matrix cases named with `wf0044_policy_...`; GREEN: add dedicated WF-0044 fixture + loader updates to satisfy new cases; REFACTOR: keep fixture schema aligned with existing matrix conventions.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_execution_core.py -k wf0044_policy_`
Risks (if any):
- Reusing the WF-0043 fixture file can cause accidental collisions in selector IDs.

### [ ] Task 9 — Verification sweep + retention lifecycle notes

Goal:
Run and document WF-0044 verification bundle and finalize retention/lifecycle notes for local source copies.
Slice: verification-and-retention
User Stories: US1, US2, US3, US4
PRD Requirements: FR6, FR10, FR12
Depends on: Task 2, Task 3, Task 4, Task 5, Task 7, Task 8
Enables: none
Parallelizable: no
Files to modify:
- `backend/data/calls/README.md`
- `docs/walkthroughs/walkthrough-WF-0044-call-yaml-source-gated-migration.md`
Acceptance Criteria:
- Verification checklist commands for all scoped calls and `pytest -k wf0044_policy_` are recorded with expected pass criteria.
- Source retention rule (keep through WF completion/review, then secure-store or purge after manifest/hash verification) is documented in repo artifacts.
TDD Plan: N/A (documentation + verification capture task)
Verification Steps:
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run`
- `cd backend && uv run pytest -k wf0044_policy_`
Risks (if any):
- Verification commands may be environment-sensitive if local DB is not running.

## Changelog

- v0.1 (2026-03-02): Initial task breakdown from PRD.
- v0.2 (2026-03-02): Applied Phase 2.2 review edits (FR3 dual-path traceability explicitness, dedicated WF-0044 policy matrix fixture, clearer RED test targets); marked Ready for Implementation.
- v0.3 (2026-03-02): Applied adversarial-pass delta by adding explicit legacy CoG mirror parity coverage (FR5) to tracer-bullet task; kept Ready for Implementation.
