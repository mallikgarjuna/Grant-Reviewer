<!-- docs/brainstorms/completed/brainstorm-WF-0062-erc-cog-2026-contract-model-correction.md -->
# WF-0062 — ERC CoG 2026 Contract Model Correction

Artifact: brainstorm
Version: v0.1
Status: Completed
Last Updated: 2026-03-07

Type: feature

## Preflight Checklist

### Step 1 — Long-Form Problem Intake

- [backend/data/calls/canonical/erc/erc_cog_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_cog_2026_full.yaml) was still on the older container-as-surface shape while [erc_stg_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_stg_2026_full.yaml) had already been corrected in WF-0060.
- That mismatch was no longer defensible because the 2026 CoG application form shares the same Part A/B, B1/B2, and Resources placement as StG.
- The requested correction is source-first and narrow: re-author canonical CoG so it matches the official form structure while preserving CoG-specific nuance in expectations and guidance.

## Repo Reality Snapshot (Read-Only) (2026-03-07)

- The current CoG canonical file modeled `b1` and `b2` as expectation-bearing surfaces and left `resources_time_commitment` outside the corrected Part A / Budget grouping.
- Existing repo tests already included CoG dry-run, DB ingest, and structured API happy-path seams, but some API proofs were still pinned to old CoG node IDs.
- The correct implementation boundary is small: canonical YAML, source manifest, memory note, and stale CoG proof tests. No frontend/runtime redesign is justified here.

## Source Grounding

Accepted source set for this run:

- `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-COG-2026/af_he-erc-cog_en.pdf`
- `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-COG-2026/guide-for-peer-reviewers_he-erc-stg-cog_en.pdf`
- `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-COG-2026/wp_horizon-erc-2026_en.pdf`

Source-backed facts:

- The CoG application form places `Section C. Resources (Maximum 8000 characters allowed)` under `Part A -> 3 - Budget`.
- `Part B1` contains `Proposal summary`, `Part I of the Scientific Proposal`, and `Curriculum vitae and Track Record`.
- `Part B2` contains `Part II of the Scientific Proposal` and is not evaluated in Step 1.
- The Work Programme keeps the same Excellence evaluation-element wording across StG and CoG, but CoG-specific framing expects evidence of research independence and a 40% PI time commitment on the ERC-funded project.

## Corrected Hierarchy Proposal

```text
erc_cog_2026_full
- part_a
  - budget
    - resources_time_commitment
- part_b
  - b1
    - proposal_summary
    - b1_part1_scientific_proposal
    - b1_cv_track_record
  - b2
    - b2_part2_scientific_proposal
```

## Critical Semantics

- `part_a`, `budget`, `part_b`, `b1`, and `b2` are structural containers only.
- Reviewable/input-bearing leaves are `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, `b2_part2_scientific_proposal`, and `resources_time_commitment`.
- CoG should mirror the corrected StG structure where the form is shared, but retain CoG-specific nuance in guidance/runtime notes rather than inventing a different hierarchy.
- API proof seams must use the corrected CoG leaf IDs, not the pre-correction CoG split-node IDs.

## MVP Boundary

- In scope: canonical CoG correction, source manifest refresh, memory note for the generalized rule, and proof-seam alignment for existing CoG DB/API checks.
- Out of scope: StG changes, frontend redesign, runtime architecture work, and any new call onboarding.
