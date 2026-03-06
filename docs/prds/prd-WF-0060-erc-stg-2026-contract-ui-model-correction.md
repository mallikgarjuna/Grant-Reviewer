<!-- docs/prds/prd-WF-0060-erc-stg-2026-contract-ui-model-correction.md -->
# WF-0060 — ERC StG 2026 Contract/UI Model Correction PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-06

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher submitting ERC StG 2026 content, I want the product to use the official source-grounded hierarchy, so that editable fields, section grouping, and submission behavior match the real application form.
- US2: As a researcher reading review results, I want review detail coverage and ordering to reflect the corrected leaf-node contract, so that feedback is traceable to the sections I actually submitted.
- US3: As a product owner, I want the ERC correction to preserve runtime compatibility for legacy WF-0059-era records where possible, so that the contract fix does not silently corrupt existing review detail behavior.
- US4: As an engineer maintaining the ERC proof path, I want invalid WF-0059 container-node assumptions replaced with leaf-node expectations and tests, so that future work builds on the corrected source-first model.

## Deferred Stories (Not in MVP)

- DS1: Generalized redesign of all call hierarchies or universal container semantics beyond the minimum required to correct ERC StG 2026.
- DS2: Re-authoring other agency calls unless required as a narrowly scoped compatibility control.
- DS3: Review UX redesign beyond the leaf-node coverage, compatibility-note, and ordering behavior forced by this correction.
- DS4: New ingestion authoring tools, migration dashboards, or broad telemetry redesign.

## 1. In Scope

- Correct `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml` so structural containers (`part_a`, `budget`, `part_b`, `b1`, `b2`) stop behaving like applicant-entered or directly reviewable surfaces. (US1, US4)
- Move `resources_time_commitment` under `part_a -> budget` while keeping it a Step 2 reviewable leaf. (US1, US2, US4)
- Preserve `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, and `b2_part2_scientific_proposal` as the ERC StG 2026 input-bearing/reviewable leaf nodes. (US1, US2, US4)
- Add ingestion/runtime container semantics so structural nodes render as grouping only and are excluded from editable/reviewable submitted-node sets. (US1, US2)
- Update submit flow behavior so only leaf nodes are submitted, persisted, and used for reviewed/not-reviewed coverage. (US1, US2, US4)
- Define explicit compatibility handling for legacy WF-0059-era persisted records that reference deprecated container submissions such as `b1` or `b2`. (US2, US3)
- Re-baseline review detail semantics so persisted submitted-node coverage, reviewed/not-reviewed grouping, and zero-card coverage operate on corrected leaf nodes. (US2, US3, US4)
- Replace invalid WF-0059 tests and assumptions that encoded container-as-surface behavior. (US3, US4)

## 2. Out of Scope

- Correcting non-ERC calls or introducing a platform-wide hierarchy rewrite. (DS1, DS2)
- Splitting ERC Part I or Part II into finer applicant-facing subnodes without new official source evidence. (DS1)
- Broad redesign of review history, reviewer prompts, ingestion authoring UX, or evaluation pipeline architecture. (DS3, DS4)
- Optimistic migration that converts ambiguous legacy container submissions into proven reviewed leaf coverage without supporting payload evidence. (DS3)

## 3. User / System Flow

### Happy path

1. Maintainer updates the canonical ERC StG 2026 YAML to the source-grounded hierarchy where structural containers group leaves but do not carry direct expectations or applicant-entered text. (US1, US4)
2. Ingestion/runtime loads the corrected hierarchy and marks structural nodes as non-editable grouping nodes while exposing only the real content-bearing leaves to submit and review surfaces. (US1)
3. Researcher opens the ERC StG 2026 submit flow and sees grouped sections for Part A / Budget and Part B / B1 / B2, but can enter content only into the five corrected leaf nodes. (US1)
4. Submit flow sends only the leaf-node payload and persisted submitted-node logical IDs for `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, `b2_part2_scientific_proposal`, and `resources_time_commitment` as applicable. (US1, US2)
5. Review creation persists submitted-node coverage in a form that preserves zero-card submitted leaves and remains usable by review detail without inferring coverage from container nodes. (US2, US3)
6. Researcher opens review detail and sees ordering, grouping, reviewed/not-reviewed coverage, and any compatibility annotations derived from the corrected leaf-node contract and persisted review-linked data. (US2, US3)
7. Engineers replace deprecated WF-0059 container-node tests with corrected leaf-node tests and compatibility cases, keeping future regressions anchored to the new contract. (US4)

### Failure path A — legacy container submission record

1. Review detail loads a WF-0059-era review whose persisted submitted-node list includes deprecated container IDs such as `b1` or `b2`. (US2, US3)
2. System treats those IDs as ambiguous legacy evidence, does not auto-expand them into reviewed leaf coverage, and renders an explicit compatibility note where needed. (US2, US3)
3. Coverage accounting remains deterministic and does not falsely claim reviewed leaf coverage that cannot be proven from persisted data. (US2, US3)

### Failure path B — runtime still treats container nodes as input-bearing

1. Ingestion or submit/runtime logic encounters a structural node flagged as editable/reviewable after the YAML correction. (US1, US4)
2. Validation or runtime guards fail closed at the touched seam rather than silently reintroducing container-as-surface behavior. (US1, US4)
3. Tests prove only leaf nodes can be submitted or counted as reviewed in the corrected ERC path. (US4)

### Failure path C — moved resources node or zero-card leaf disappears from coverage

1. A researcher submits `resources_time_commitment` under the corrected `part_a -> budget` location or submits another leaf that later emits zero review cards. (US1, US2)
2. Persisted submitted-node coverage still records that leaf and review detail shows it in the correct structural group with deterministic reviewed/not-reviewed semantics. (US2, US3)
3. No fallback to top-level legacy placement or cards-only inference hides the submitted leaf. (US2, US3)

## 4. Functional Requirements

- FR1 (US1, US4): The source of truth for ERC StG 2026 must be the official-source-grounded hierarchy approved in the WF-0060 brainstorm, not the WF-0059 proof-call shape.
- FR2 (US1, US4): Structural nodes `part_a`, `budget`, `part_b`, `b1`, and `b2` must be modeled as structural containers only and must not be applicant-editable or directly reviewable.
- FR3 (US1, US2, US4): `resources_time_commitment` must move under `part_a -> budget` while preserving its logical leaf identity and Step 2 reviewability.
- FR4 (US1, US2, US4): The ERC StG 2026 input-bearing/reviewable leaves in MVP are exactly `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, `b2_part2_scientific_proposal`, and `resources_time_commitment`.
- FR5 (US1): Ingestion/runtime must expose explicit container semantics so structural nodes render as grouping-only surfaces and are excluded from editable/reviewable submission sets.
- FR6 (US1, US2): Submit flow must collect, validate, and transmit only leaf-node content for the corrected ERC hierarchy.
- FR7 (US2, US3): Review persistence must preserve submitted leaf-node coverage even when a submitted leaf emits zero review cards.
- FR8 (US2, US3): Review detail grouping, ordering, reviewed/not-reviewed coverage, and submitted-node traceability must derive from persisted review-linked data plus corrected call metadata, not deprecated container assumptions.
- FR9 (US2, US3): Legacy WF-0059-era `b1`/`b2` submitted-node references must be treated as ambiguous compatibility-era evidence and must not be auto-expanded into reviewed leaf coverage without proof.
- FR10 (US2, US3): Legacy top-level `resources_time_commitment` references must resolve to the corrected moved leaf without changing the logical leaf ID exposed to downstream consumers.
- FR11 (US2, US3): Review detail must surface explicit compatibility-state semantics when legacy submitted-node evidence is ambiguous or deprecated.
- FR12 (US3, US4): WF-0059 tests, fixtures, and assertions that treat `b1` or `b2` as editable/reviewable surfaces must be replaced with leaf-node and compatibility-aware coverage.
- FR13 (US4): The corrected ERC contract must fail closed against any expectation mapping or submit/review path that still assigns direct expectations to structural containers.
- FR14 (US1, US2, US3): Part I and Part II scientific proposal surfaces must remain whole-node leaves in MVP unless new official source evidence authorizes further subdivision.
- FR15 (US1, US2, US4): The correction must remain source-first and narrow: only the minimum ingestion/runtime, submit, persistence, review-detail, and test-seam changes required by the ERC fix are in scope.

## 5. Data & API Contracts

### 5.1 Canonical call contract

- The canonical YAML for ERC StG 2026 must encode structural-only containers separately from input-bearing/reviewable leaves. (US1, US4, FR1, FR2, FR4)
- Container nodes must have semantics that downstream readers can interpret as grouping-only rather than expectation-bearing surfaces. (US1, FR2, FR5)
- `resources_time_commitment` must appear under `part_a -> budget` in canonical structure while keeping the logical leaf ID stable for persistence and compatibility handling. (US1, US2, FR3, FR10)
- Leaf nodes must carry stage/reviewability semantics aligned to source evidence: `proposal_summary`, `b1_part1_scientific_proposal`, and `b1_cv_track_record` are reviewable in both steps; `b2_part2_scientific_proposal` and `resources_time_commitment` are Step 2 only. (US1, US2, FR4)

### 5.2 Ingestion/runtime and submit contract

- Runtime normalization must preserve structural grouping nodes for rendering/order while producing a submittable leaf-node set that excludes containers. (US1, FR5, FR6)
- Submit payloads for ERC StG 2026 must be keyed by corrected leaf logical IDs only; container logical IDs are invalid at the contract boundary. (US1, US4, FR5, FR6, FR13)
- Validation must fail closed if a structural container is passed as submitted content or as a direct reviewable node. (US1, US4, FR5, FR13)
- Persisted submitted-node coverage must record corrected leaf-node IDs independently of whether downstream review cards were emitted. (US2, US3, FR7, FR8)

### 5.3 Legacy compatibility contract

- Legacy persisted submitted-node IDs `b1` and `b2` must be interpreted as deprecated ambiguous container-era evidence. (US2, US3, FR9, FR11)
- Ambiguous legacy container evidence may drive compatibility messaging or scoped legacy grouping behavior, but must not count as proven reviewed coverage for individual leaf nodes without companion evidence. (US2, US3, FR9, FR11)
- Legacy persisted `resources_time_commitment` references must map to the corrected leaf under `part_a -> budget` for display and coverage continuity. (US2, US3, FR10)

### 5.4 Review-detail state transitions

- `Corrected leaf submission` -> `persisted leaf submitted-node coverage` -> `review detail grouped by corrected hierarchy` is the standard ERC StG 2026 path. (US1, US2, FR6, FR7, FR8)
- `Legacy container submission evidence` -> `compatibility-note render` -> `non-optimistic coverage accounting` is the required compatibility path. (US2, US3, FR9, FR11)
- `submitted leaf with zero emitted cards` -> `review detail still shows submitted reviewed leaf` is required coverage behavior. (US2, US3, FR7, FR8)
- `container logical ID submitted at runtime after correction` -> `deterministic validation/runtime failure` is the fail-closed behavior. (US1, US4, FR5, FR13)

## 6. Components / Modules

- `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
  - Canonical ERC contract seam to correct first. (FR1, FR2, FR3, FR4, FR14)
- Call ingestion/runtime normalization seams under `backend/app/`
  - Must preserve grouping metadata while distinguishing structural containers from submittable/reviewable leaves. (FR5, FR13, FR15)
- Submit model and UI seams under `frontend/src/lib/submit/` and `frontend/src/components/submit/`
  - Must render corrected grouping but allow entry/submission only for leaf nodes. (FR5, FR6, FR15)
- Structured-review persistence and detail seams under `backend/app/`
  - Must persist leaf submitted-node coverage, preserve zero-card submitted leaves, and expose compatibility-aware metadata to review detail. (FR7, FR8, FR9, FR10, FR11)
- Review-detail composition seams under `frontend/src/app/app/reviews/`
  - Must render corrected grouping, ordering, coverage, and compatibility notes from persisted review-linked data plus call metadata. (FR8, FR11, FR15)
- WF-0059 regression and compatibility tests across frontend/backend test suites
  - Must remove deprecated container-as-surface assumptions and prove corrected leaf-node behavior. (FR12, FR13)

Design tree / dependencies / ordering:
1. Correct the canonical ERC YAML contract and freeze the leaf/container semantics. (FR1, FR2, FR3, FR4)
2. Thread container-aware semantics through ingestion/runtime so rendering and submission can distinguish grouping nodes from leaves. (FR5, FR13)
3. Update submit/runtime boundaries to accept only corrected leaves and persist submitted-node coverage accordingly. (FR6, FR7)
4. Re-baseline review detail to use corrected leaf-node coverage, grouping, ordering, zero-card handling, and compatibility notes. (FR8, FR9, FR10, FR11)
5. Replace invalid WF-0059 tests/fixtures with leaf-node and compatibility-aware coverage. (FR12, FR15)

Deep module guidance:

- Prefer a small shared contract for `structural container` vs `input-bearing leaf` semantics instead of scattered ERC-only conditionals.
- Keep persisted submitted-node coverage as the public seam for review-detail traceability; do not infer reviewed coverage from emitted cards alone.
- Keep compatibility handling explicit and localized to legacy review-detail/persistence interpretation rather than polluting the corrected canonical contract.

Suggested file-path clusters (coarse only):

- canonical call YAML under `backend/data/calls/canonical/erc/`
- ingestion/runtime and review persistence under `backend/app/`
- submit rendering/modeling under `frontend/src/lib/submit/` and `frontend/src/components/submit/`
- review detail UI under `frontend/src/app/app/reviews/`
- WF-0059/WF-0060 regression coverage under backend/frontend test directories

## 7. Edge Cases

- A structural container still has legacy expectation metadata after the YAML correction; runtime must fail closed instead of preserving invalid review surfaces. (US1, US4, FR2, FR13)
- Submit payload includes `b1` or `b2` after the correction; contract validation must reject it as deprecated container input. (US1, US4, FR5, FR6, FR13)
- Legacy review detail sees only `b1` or `b2` in persisted submitted-node coverage with no companion leaf evidence; UI/API must show compatibility ambiguity without inflating reviewed coverage. (US2, US3, FR9, FR11)
- Legacy review detail sees top-level `resources_time_commitment`; it must still resolve into the corrected Part A / Budget group. (US2, US3, FR10)
- A submitted corrected leaf emits zero review cards; review detail must still mark it as submitted/reviewed according to persisted coverage rules. (US2, US3, FR7, FR8)
- Grouping metadata and review stages disagree after correction; tests must fail on the invariant mismatch rather than allowing stage leakage across steps. (US1, US2, FR4, FR13)
- Review detail order accidentally falls back to deprecated proof-call assumptions when corrected metadata is available; this is a regression and must be blocked by tests. (US2, US4, FR8, FR12)

## 8. Testing Decisions (TDD)

- This workflow is a behavior correction, so implementation must follow RED -> GREEN -> REFACTOR. (US4)
- Public test seams must cover canonical contract loading, submit/runtime leaf filtering, structured-review persistence of submitted-node coverage, and review-detail rendering/coverage semantics. (US1, US2, US3, US4, FR1-FR13)
- Mock only external boundaries. Do not mock the contract logic that distinguishes structural containers from input-bearing leaves or the review-detail logic that computes coverage from persisted submitted-node data. (US2, US4)
- Minimum automated coverage required:
  - canonical YAML/ingestion tests proving container-only vs leaf-node semantics for ERC StG 2026. (US1, US4, FR1-FR5)
  - submit/runtime tests proving only corrected leaves can be entered/submitted and container IDs fail closed. (US1, US4, FR5, FR6, FR13)
  - persistence/review-detail tests proving zero-card submitted leaves still appear in reviewed coverage. (US2, US3, FR7, FR8)
  - legacy compatibility tests proving `b1`/`b2` remain ambiguous evidence and `resources_time_commitment` resolves across the moved location. (US2, US3, FR9, FR10, FR11)
  - regression tests replacing WF-0059 container-node assumptions with corrected leaf-node expectations and ordering assertions. (US3, US4, FR12)
- Verification should include at least one deterministic end-to-end ERC StG 2026 path showing corrected grouping, leaf-only submission, persisted submitted-node coverage, and review detail output. (US1, US2, US4, FR6, FR7, FR8, FR12)

## 9. Telemetry (Minimal)

- Add only minimal diagnostics needed to distinguish corrected leaf-node submissions from deprecated container-node compatibility cases.
- If telemetry is touched, it must make compatibility-note usage and fail-closed container submission rejections observable without redesigning the telemetry system.
- Telemetry is not an MVP deliverable unless required to debug a correctness regression introduced by the correction. (DS4)

## 10. Deferred / Not in MVP

- Universal multi-call hierarchy refactors or platform-wide authoring abstractions.
- Re-modeling other ERC or non-ERC calls.
- UI polish beyond corrected grouping, coverage, and compatibility-state semantics.
- Automatic historical data backfill that claims more reviewed coverage than the stored legacy evidence proves.

## 11. Open Questions (if any)

- None blocking for Phase 1 PRD. The approved brainstorm fixes the hierarchy, leaf semantics, compatibility posture, and replacement direction for WF-0059 assumptions.

## 12. Changelog

- v0.1 (2026-03-06): Initial PRD from brainstorm.
