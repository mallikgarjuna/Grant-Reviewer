# ERC StG 2026 YAML Source Manifest

Artifact: source-manifest
WF: WF-0032
Last Updated: 2026-02-26

## Purpose
Traceability manifest for `backend/data/calls/erc/erc_stg_2026_full.yaml`.

## Source Files

1) **Application Form (Starting Grant)**
- Path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-StG-2026/af_he-erc-stg_en.pdf`
- SHA256: `5c64681088dd19f674618bf382ab0617ae023150fbc5d768d4e90ed199f48c05`
- Used for:
  - Part B1/Part B2 structure and page constraints.
  - Step visibility notes (`Part B1` in Step 1+2, `Part B2` Step 2 only).
  - Section C resources character cap (8000 chars) and Step 2 visibility.
  - Authoring instruction notes (grey-highlight guidance text removal).

2) **Work Programme (Horizon ERC 2026)**
- Path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-COG-2026/wp_horizon-erc-2026_en.pdf`
- SHA256: `36b4558b96db63ec8c07c5683cb04eeb92fbf89d301f9fbc27cc000181031efd`
- Used for:
  - `1.6.1` Excellence as sole evaluation criterion.
  - `1.6.3` Step 1 vs Step 2 evaluation procedure.
  - Footnote definition of complete Research Proposal (Part I + Part II + CV/Track Record + Resources and Time Commitment).
  - `1.6.5` evaluation criteria/elements mapping and stage-specific elements.

3) **Guide for Peer Reviewers (StG/CoG)**
- Path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-COG-2026/guide-for-peer-reviewers_he-erc-stg-cog_en.pdf`
- SHA256: `b11cc47f0e5e478726e179e1a81a30fbaa31b35c41e37369f960d4394e3e4bdb`
- Used for:
  - `2.1 Evaluation Criterion` restatement and procedural-error guardrail.
  - “Reviewers need to observe the following guidelines” for enforceable reviewer-policy rules:
    - no societal-impact criterion usage,
    - no host-institution-standing commentary,
    - no Step 1 resource recommendations,
    - no cross-proposal comparison,
    - no personal-attribute commentary,
    - no ethics/security commentary in scientific scoring,
    - no salary-cut recommendation at Step 2.

## Notes
- Source-derived policy is encoded in `reviewer_policy` in the YAML.
- Scope intentionally excludes panel-operations governance (e.g., COI/confidentiality workflows) from LLM content-scoring logic.
