# Sources Manifest — NWO Vidi 2025 Full Proposal

Traceability manifest for `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`.

## Source Files (Official)

1. **Vidi full proposal form (structure + embedded explanatory notes / constraints)**
   - Filename: `Vidi-2025-Full-proposal-form.docx`
   - Local path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Vidi-2025/Full-proposal/Vidi-2025-Full-proposal-form.docx`
   - SHA256: `2c0fae7da27eec6001c85ebbd23b338e4a659b7c5d4d4c23eec414ff5e2e7919`

2. **Call for Proposals (evaluation procedure + criteria + DORA policy + deadlines)**
   - Filename: `Call-for-Proposals-Vidi-2025_Eng.pdf`
   - Local path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Vidi-2025/Full-proposal/Call-for-Proposals-Vidi-2025_Eng.pdf`
   - SHA256: `0ca64071d011268eea1c9a3a6aa3de52f0a8f16b2ed480ca8e24fe1e5de5c026`

## Not Used (Present Locally)

- `Vidi 2025_literature_list.docx` is not used unless the Call PDF explicitly references it as an official annex that changes evaluable structure/limits/evaluation.

## Mapping: Sources → YAML Fields

### Funding call metadata

- `funding_call.title`, `funding_call.stage`, `funding_call.language`:
  - Derived from Call PDF cover/title context + form header.

- `funding_call.deadlines.full_proposal_submission`:
  - Call PDF Chapter 1 (deadline statement: full proposal submission).

### Proposal nodes (structure + constraints)

- `proposal_nodes.scientific_summary` (`source_section: "1b"`):
  - Form: notes for scientific summary (max 300 words).

- `proposal_nodes.public_summary_en` (`source_section: "1c"`):
  - Form: public summary (English) word-count guidance (50–100 words).
  - Dutch public summary is explicitly excluded from `proposal_nodes` (see brainstorm guardrail).

- `proposal_nodes.research_proposal` (`source_section: "2a"`):
  - Form: "Description of proposed research" constraints (max 4000 words; no more than 8 pages).

- `proposal_nodes.impact` (`source_section: "2b"`):
  - Form: "Scientific and/or societal impact" constraints (max 1000 words; no more than 2 pages).

### Evaluation criteria/elements

- `evaluation_criteria.*`:
  - Call PDF Chapter 4.3.2 (Substantive assessment criteria for the full proposal):
    - Quality and innovative character of the research proposal (75%).
    - Scientific and/or societal impact (25%).
  - AES-only note about user committee composition/involvement is intentionally deferred from evaluable elements in this YAML until domain gating exists (see WF-0037 PRD v0.2, Edge Cases/Deferred Stories).

### Reviewer policy

- `reviewer_policy.*`:
  - Call PDF Chapter 4.1 (DORA): avoid Journal Impact Factor / h-index, broad definition of output, applicants not allowed to mention bibliometrics.
  - Call PDF Chapter 4 (assessment procedure) inclusion/bias note: avoid barriers due to background, gender, etc.
