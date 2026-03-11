<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-11

---

## Section 1 — Phase 0 Gate Inputs

- User requested a dedicated WF for onboarding `ERC-2026-PoC` into PeerLens and explicitly constrained the first step to Phase 0 gate only.
- User confirmed this should be treated as call onboarding and activation, not broad platform feature work.
- User stated `ERC-2026-PoC` does not yet exist in the repo as a canonical call.
- User stated the likely path is new call authoring plus dry-run validation plus DB ingest plus API exposure plus smoke test, not major frontend rework.

## Section 2 — Source Documents Provided

- Application form template:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/af_he-erc-poc_en.pdf`
  - Part B template and drafting instructions are in this file.
- Evaluation criteria and elements:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/wp_horizon-erc-2026_en.pdf`
  - The relevant PoC evaluation material is anchored in section `2.1.6.1 Evaluation Criterion`.
- Applicant guidance:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/information-for-applicants_he-erc-poc_en.pdf`
  - This guidance states there is one evaluation step for PoC, so stage-specific reuse from other ERC calls must not be assumed.

## Section 3 — Phase 0 Decisions Promoted To Brainstorm

- Proposed WF ID: `WF-0073`
- Slug: `erc-poc-2026-call-onboarding`
- Phase 0 gate recommendation before source upload: no-go for implementation until clean workflow boundary and official sources existed.
- After source upload, official-source blocker is cleared for planning and later YAML authoring.
- Recommended execution order: docs-only planning, then call YAML plus source-manifest onboarding, then ingest/exposure/structured-review verification.
- Proceed remains blocked unless every required verification item has explicit pass/fail evidence and every review finding has a closure or explicit rejection rationale.
