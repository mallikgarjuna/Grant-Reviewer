# NWO Veni 2025 Pre-proposal YAML Source Manifest

Artifact: source-manifest
WF: WF-0036
Last Updated: 2026-02-26

## Purpose
Traceability manifest for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.

## Source Files

1) **Pre-proposal form (DOCX)**
- Path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Veni-2026/veni_pre-proposal_form_2025.docx`
- SHA256: `90c8d81e5ed5994ff739a46e34d8b89cbdb00143f5a44551b4e6afc501c288c9`
- Used for:
  - Proposal-node structure (2a Academic profile, 2b Key outputs, 3 Research idea).
  - Word limits and domain-specific pilot (`science_enw` 500 words for research idea; otherwise 100).
  - Key-output constraints and formatting guidance (max 10; references/URLs rules; prohibited indicator lists).

2) **Call for Proposals (PDF)**
- Path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Veni-2026/Call for Proposals Veni 2025_EN_0.pdf`
- SHA256: `24dfa9fa7cc594a0f519d62b3fd179f43e46fbc10e06275e00f2e319e667ff2e`
- Used for:
  - Assessment procedure overview (Chapter 4).
  - DORA policy and prohibited bibliometric indicators (Section 4.1).
  - Pre-proposal substantive assessment criterion and bullets (Section 4.3.1).
  - Deadlines for pre-proposal and proposal phases (Sections 1.3 / 4.2.16).

## Notes
- The runtime currently enforces word limits deterministically via whitespace tokenization and does not implement “excludes” semantics (e.g., excluding references/URLs). Such exclusions are stored as guidance text and notes, not as enforceable parsing logic.
