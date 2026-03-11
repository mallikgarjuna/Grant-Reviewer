<!-- docs/brainstorms/brainstorm-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-11

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0073-erc-poc-2026-call-onboarding.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for WF-0073 scope and delivery boundaries.
- The Q&A transcript is rationale only; new contracts must be promoted here before later phases.
- This WF is a one-call onboarding and activation workflow, not a platform-expansion workflow.

## 1. Problem Statement

- PeerLens does not yet contain a canonical `ERC-2026-PoC` call, even though the current architecture already supports multi-call exposure, structured call config, and ERC-style staged review behavior.
- Researchers need this call available before the ERC Proof of Concept 2026 deadline on 2026-03-17.
- The safest path is to onboard this one call through existing authoring, ingest, and exposure seams rather than widen scope into new frontend or platform work.

Contract notes / non-obvious constraints:
- Launch claims for this WF must stay bounded to one new call and direct repo evidence.
- Official-source grounding is mandatory before substantive authoring.

## 2. Desired Outcome

- `ERC-2026-PoC` exists as one source-grounded canonical call in the repo.
- The call validates cleanly, ingests cleanly, appears through the current call exposure path, and passes one minimal smoke verification through the intended product path.
- Any code change made during implementation is the smallest compatibility fix required to expose this call safely.

Contract notes / non-obvious constraints:
- Docs-only planning is allowed before implementation; YAML authoring is not.
- This WF is not done at dry-run only; ingest and smoke evidence are required.

## 3. Target User / Actor

- Primary actor: internal operator/developer onboarding one funding call into PeerLens.
- Secondary actor: researchers who need `ERC-2026-PoC` to be selectable in the existing PeerLens submission flow before the deadline.

## 4. Rough Idea (Unstructured Thinking)

- Reuse the existing ERC canonical calls as structural reference points, especially `erc_stg_2026_full` and `erc_cog_2026_full`.
- Use the uploaded official ERC PoC 2026 documents as the authoring basis:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/af_he-erc-poc_en.pdf`
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/wp_horizon-erc-2026_en.pdf`
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/information-for-applicants_he-erc-poc_en.pdf`
- Keep the workflow in four narrow slices: docs-only planning, call YAML onboarding, ingest plus smoke verification, optional product copy cleanup only if repo evidence shows it is needed.

## 5. Constraints

- Hard scope: one call only, `ERC-2026-PoC`.
- Hard date constraint: researchers need this before 2026-03-17.
- Do not widen into new agencies, generic onboarding framework work, landing-page work, or broad frontend redesign.
- Respect the representative proof baseline already used by the repo: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- Use researcher-facing term `evaluation criteria/elements`, not `rubric`.

Contract notes / non-obvious constraints:
- The likely implementation path is new call authoring plus dry-run validation plus DB ingest plus API exposure plus smoke test.
- Frontend/backend code changes are conditional, not assumed.

## 6. Risks / Unknowns

- The biggest schedule risk is discovering a hidden activation seam too late, given the short runway to 2026-03-17.
- The biggest scope risk is turning a one-call onboarding into broader platform work.
- There may be ERC PoC-specific structure or stage semantics that differ materially from existing ERC StG/CoG patterns and need source-led confirmation during planning.

Contract notes / non-obvious constraints:
- If onboarding this call appears to require broad product changes, stop and re-scope rather than absorb the work implicitly.
- The application structure image is helpful but optional if the PDF sources are sufficient.

## Open Questions / Deferred

- Whether any call-specific activation seam beyond YAML plus ingest is actually needed should be answered in planning, not assumed now.
- Optional product copy updates are deferred unless implementation evidence shows the call needs explicit naming or visibility adjustments.

## 7. MVP Definition

- Smallest valid slice:
  - source-grounded ERC PoC 2026 manifest,
  - one canonical ERC PoC 2026 YAML,
  - successful dry-run validation,
  - successful ingest,
  - successful call exposure check,
  - one smoke verification proving researchers can use the call through the current architecture.

## 8. Explicit Non-Goals

- New agencies or program families.
- Broad platform feature work.
- Landing-page or marketing work.
- Major frontend redesign.
- Re-authoring existing canonical calls unless a direct compatibility fix is strictly required for this one call.
