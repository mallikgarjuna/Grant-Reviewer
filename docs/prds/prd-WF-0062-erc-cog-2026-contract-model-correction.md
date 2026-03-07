<!-- docs/prds/prd-WF-0062-erc-cog-2026-contract-model-correction.md -->
# WF-0062 — ERC CoG 2026 Contract Model Correction

Artifact: prd
Version: v0.1
Status: Completed
Last Updated: 2026-03-07

Type: feature

## 0. User Stories (MVP)

- US1: As a maintainer, I want `erc_cog_2026_full` to reflect the official 2026 CoG form structure, so the canonical contract stays source-grounded and consistent with the corrected StG model.
- US2: As a maintainer, I want CoG-specific guidance to preserve PI independence and 40% time-commitment nuance without inventing a different hierarchy from the official form.
- US3: As an engineer, I want existing CoG DB/API proof seams to target the corrected leaf IDs, so verification exercises the real contract rather than stale node names.

## 1. In Scope

- Re-author [erc_cog_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_cog_2026_full.yaml) to the corrected Part A/B, B1/B2, and Resources hierarchy.
- Refresh [erc_cog_2026_full.sources.md](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/sources/erc_cog_2026_full.sources.md) to match the accepted source set for this run.
- Record the generalized CoG/StG structure rule in memory.
- Align CoG DB/API proof seams in [test_api.py](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_api.py) to the corrected leaf IDs.
- Close ship-gate compatibility gaps for legacy CoG persisted review coverage and corrected CoG read surfaces.

## 2. Out of Scope

- Any new runtime feature work, frontend work, or multi-call expansion.
- Re-authoring StG again.
- Broad ERC policy redesign beyond what the uploaded sources justify.

## 3. Functional Requirements

- FR1: CoG canonical structure must place `resources_time_commitment` under `part_a -> budget`.
- FR2: `part_a`, `budget`, `part_b`, `b1`, and `b2` must be structural containers only.
- FR3: Reviewable/input-bearing leaves must be `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, `b2_part2_scientific_proposal`, and `resources_time_commitment`.
- FR4: CoG-specific nuance must remain in guidance/runtime notes for PI independence and 40% PI project time commitment.
- FR5: Existing CoG DB/API proof seams must pass against the corrected leaf-node contract.
- FR6: Pre-correction persisted CoG review payloads must resolve to corrected reviewed-leaf coverage in review detail while preserving legacy IDs as compatibility metadata.
- FR7: CoG tree and metadata read APIs must expose the corrected hierarchy and leaf review stages.

## 4. Testing Decisions

- Dry-run ingest is necessary but insufficient.
- Minimum verification must include:
  - dry-run ingest
  - DB-backed ingest
  - structured-review API happy path
  - structured reviewer-policy API proof seam
  - persisted legacy CoG review-detail compatibility proof
  - CoG tree/metadata read-surface proofs
