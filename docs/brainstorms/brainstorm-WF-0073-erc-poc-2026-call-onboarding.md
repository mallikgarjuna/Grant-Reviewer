<!-- docs/brainstorms/brainstorm-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-11

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0073-erc-poc-2026-call-onboarding.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for WF-0073 scope and delivery boundaries.
- The Q&A transcript is rationale only; new contracts must be promoted here before later phases.
- This WF is a one-call onboarding and activation workflow for `ERC-2026-PoC`, not a platform-expansion, cross-call-proof, or product-copy workflow.

## 1. Problem Statement

- PeerLens does not yet contain a canonical `ERC-2026-PoC` call even though the current repo already supports source-gated call authoring, ingest, call exposure, and v1 structured review.
- Researchers need this call available before the first ERC PoC 2026 cut-off on 2026-03-17.
- The official applicant guidance states there is one evaluation step for PoC; this WF must therefore default to single-step onboarding and must not assume `STEP_1` / `STEP_2` stage behavior from other ERC calls unless Phase 1 proves a narrower call-specific seam is truly required.
- The safest path is to onboard this one call through existing authoring, ingest, exposure, and `POST /api/structured-review` seams rather than widen scope into new frontend or platform work.

Contract notes / non-obvious constraints:
- Launch claims for this WF must stay bounded to one new call and direct repo evidence.
- Official-source grounding is mandatory before substantive authoring.
- Any claim about stage-specific activation, split visibility/reviewability opt-in, or extra product-surface work is a defect unless it is explicitly proven necessary for `ERC-2026-PoC`.

## 2. Desired Outcome

- `ERC-2026-PoC` exists as one source-grounded canonical call in the repo.
- The onboarding artifact set is explicit and fail-closed:
  - canonical YAML at `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
  - source traceability manifest at `backend/data/calls/sources/erc_poc_2026_full.sources.md`
- The source manifest records the official proposal-structure source and official evaluation-criteria/elements source with durable `SHA256` metadata and explicit `Used for` traceability.
- The call validates cleanly, ingests cleanly, appears through the current call exposure path, and passes at least one `POST /api/structured-review` smoke verification through the intended product path.
- Any code change made during implementation is the smallest compatibility fix required to expose this call safely.

Contract notes / non-obvious constraints:
- Docs-only planning is allowed before implementation; YAML authoring is not.
- This WF is not done at dry-run only; manifest, ingest, exposure, and structured-review smoke evidence are all required.
- If the filename contract above proves incorrect during Phase 1, stop and correct the artifact before authoring rather than silently drifting.

## 3. Target User / Actor

- Primary actor: internal operator/developer onboarding one funding call into PeerLens.
- Secondary actor: researchers who need `ERC-2026-PoC` to be selectable in the existing PeerLens submission flow before the cut-off.

## 4. Rough Idea (Unstructured Thinking)

- Reuse existing ERC canonical calls only as structural reference points for authoring discipline, especially `erc_stg_2026_full` and `erc_cog_2026_full`; do not inherit their stage semantics without source proof.
- Use the uploaded official ERC PoC 2026 documents as the authoring basis:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/af_he-erc-poc_en.pdf`
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/wp_horizon-erc-2026_en.pdf`
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-PoC-2026/information-for-applicants_he-erc-poc_en.pdf`
- Keep the workflow in three narrow slices only:
  - docs-only planning,
  - call YAML plus source-manifest onboarding,
  - ingest, exposure, and structured-review verification.

## 5. Constraints

- Hard scope: one call only, `ERC-2026-PoC`.
- Hard date constraint: researchers need this before 2026-03-17.
- Do not widen into new agencies, generic onboarding framework work, landing-page work, broad frontend redesign, or cross-call verification expansion.
- Use researcher-facing term `evaluation criteria/elements`, not `rubric`.
- Follow the repo onboarding gate explicitly:
  - official proposal-structure source present,
  - official evaluation-criteria/elements source present,
  - source manifest present before counting authoring as valid,
  - dry-run ingest passes,
  - DB ingest passes,
  - call appears in calls listing APIs and node metadata APIs,
  - at least one `POST /api/structured-review` smoke request succeeds for this call.

Contract notes / non-obvious constraints:
- Frontend/backend code changes are conditional, not assumed.
- Default runtime posture is no special split-role opt-in and no special stage activation beyond what the official PoC sources require.
- If later planning proposes a call-specific activation seam, it must stay localized to config/activation boundaries and carry targeted regression tests.

## 6. Risks / Unknowns

- The biggest schedule risk is discovering a hidden compatibility seam too late, given the short runway to 2026-03-17.
- The biggest scope risk is turning a one-call onboarding into broader platform work.
- There may be ERC PoC-specific structure, validation, or exposure details that differ materially from existing ERC StG/CoG patterns and need source-led confirmation during planning.
- There is a verification risk if the workflow stops at YAML or ingest and overclaims readiness without structured-review evidence.

Contract notes / non-obvious constraints:
- If onboarding this call appears to require broad product changes, stop and re-scope rather than absorb the work implicitly.
- The application structure image or reviewer guide may assist planning, but the mandatory source classes remain proposal structure plus evaluation criteria/elements.

## Open Questions / Deferred

- Whether `ERC-2026-PoC` can remain a standard single-step, non-split call with no extra activation seam after source-grounded planning.
- Whether any narrow compatibility fix is required for exposure or structured-review smoke; if yes, it must be documented and tested as part of this WF.

## 7. MVP Definition

- Smallest valid slice:
  - source-grounded `erc_poc_2026_full.sources.md`,
  - one canonical `erc_poc_2026_full.yaml`,
  - successful dry-run validation,
  - successful ingest,
  - successful calls-listing and node-metadata exposure checks,
  - one successful `POST /api/structured-review` smoke verification,
  - recorded pass/fail evidence for every verification item.

## Verification / Proceed Gate

- No proceed recommendation is valid without explicit pass/fail evidence for dry-run, ingest, exposure, and structured-review smoke steps.
- Evidence must identify the exact command, endpoint, or artifact used for each verification item.
- Any blocking finding raised during review must be closed before a proceed recommendation.
- Any non-blocking finding must be either closed or explicitly rejected with rationale before a proceed recommendation.
- If any required verification item is missing, skipped without rationale, or failing, the workflow remains blocked.

## 8. Explicit Non-Goals

- New agencies or program families.
- Broad platform feature work.
- Landing-page, marketing, or optional product-copy cleanup.
- Major frontend redesign.
- Cross-call representative-proof work from other WFs.
- Re-authoring existing canonical calls unless a direct compatibility fix is strictly required for this one call.
