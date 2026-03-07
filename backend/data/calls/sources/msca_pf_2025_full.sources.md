<!-- backend/data/calls/sources/msca_pf_2025_full.sources.md -->
# MSCA-PF-2025 Full Proposal YAML Source Manifest

Artifact: source-manifest
WF: WF-0061
Last Updated: 2026-03-07

## Purpose
Traceability manifest for `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`.

## Required Official Source Classes

1) **Application Form (HE MSCA PF)**
- Path (origin): `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/af_he-msca-pf_en.pdf`
- SHA256: `011e650c11118ced01ef2cd78bd7fdd1c2d7ef7c884a3c4e7d3ffae154c7c2c7`
- Used for:
  - Proposal structure and application structure (Part A, Part B1, Part B2) and hierarchy.
  - Part B1 page-limit constraint (`max 10 pages` for Sections 1-3).
  - Part B2 structural sections (`4` to `8`) and CV indicative length guidance.
  - Section headings and proposal-node labels aligned with template wording.
- Source URL / provenance note: User-uploaded local source for WF-0061 on 2026-03-07.
- Provided/Downloaded date: `2026-03-07`

2) **Evaluation Form (HE MSCA) + Work Programme award-criteria confirmation**
- Path (origin): `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/ef_he-msca_en.pdf`
- SHA256: `f7478ef7f1eac4c327c62489b66f0c8531ee890917671442846027f329bfbd2c`
- Used for:
  - Evaluation criteria/elements framing for Excellence, Impact, and Quality and efficiency of implementation.
  - Scoring scale and threshold context used as non-enforceable reviewer guidance.
- Source URL / provenance note: User-uploaded local source for WF-0061 on 2026-03-07.
- Provided/Downloaded date: `2026-03-07`

- Path (origin): `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/wp-2-msca-actions_horizon-2023-2024_en.pdf`
- SHA256: `dd1209675abd79075768093ea277ddf0afe2985f489a5514f8f219d5902fbacf`
- Used for:
  - Authoritative wording of MSCA Postdoctoral Fellowships award criteria/elements and weighting (`Excellence 50%`, `Impact 30%`, `Quality and efficiency of implementation 20%`).
  - Confirmation of page-limit rule (`10 pages`, excluding annexes) and evaluation-threshold context (`70%`).
- Source URL / provenance note: User-uploaded local source for WF-0061 on 2026-03-07.
- Provided/Downloaded date: `2026-03-07`

## Supplemental Sources (Semantic Clarification Only)

1) **Guide for applicants (MSCA PF 2025)**
- Path (origin): `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/Guide for applicants_MSCA PF 2025.pdf`
- SHA256: `de3e3efdc0934b365cab42e07746b7e2b1e791fedeac4b09c0e503229ed0226c`
- Used for:
  - Clarifying semantic guidance text in proposal-node descriptions where template labels are brief.
  - Cross-checking wording consistency for Part B drafting guidance.
- Source URL / provenance note: User-uploaded local source for WF-0061 on 2026-03-07.
- Provided/Downloaded date: `2026-03-07`

## Notes
- This manifest intentionally anchors WF-0061 to one call only: `MSCA-PF-2025`.
- Runtime proof seam for WF-0061 is backend `POST /api/structured-review` only.
