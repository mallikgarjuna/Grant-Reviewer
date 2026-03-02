# WF-0044 — P1 #12: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration

Artifact: brainstorm-qna
Version: v0.0
Status: Not started
Last Updated: 2026-03-02

## Preflight — Intake (2026-03-02)

User accepted the recommended “Long-Form Problem Intake (free-form)” as-is.

Clarifications locked before WF minting:

- Q1 (legacy CoG): Selected A — keep `erc_cog_2026_full_official` as a legacy mirror file; re-author its content from official sources for traceability parity with canonical.
- Q2 (NWO Vidi app form sources): Selected A — allow official `.docx` as the application-form source; assessment criteria remain PDF.

## Section 1 — Problem Statement (2026-03-02)

**Q1: Where should uploaded official source documents live for traceability in this WF?**
- A) External absolute paths (like prior `.sources.md` files), just record path + SHA256.
- B) Copy into repo under `backend/data/calls/source_files/WF-0044/<call_code>/...` and reference those paths + SHA256.
- C) Hybrid: keep originals external, but also store a copy in-repo for each file used (reference both paths + SHA256).
 > Recommendation: C (max defensibility) or B (simpler, portable).
 > **Selected: C**

**Q2: What exactly is the “validation baseline/preflight” we must pass for the 3 baseline calls?**
- A) Schema validate only (Pydantic), no ingest.
- B) `cd backend && uv run python scripts/ingest_call.py ... --dry-run` for each baseline call.
- C) Dry-run + real DB ingest (non-prod local DB) for each baseline call.
 > Recommendation: B as baseline; add C if needed.
 > **Selected: C** (user note: “maybe Dry-run + real DB ingest?”)

**Q3: For ERC calls, what counts as “assessment-criteria source PDFs” per the upload gate?**
- A) Work Programme PDF only (if it contains criteria/elements).
- B) Reviewer Guide PDF only.
- C) Both Work Programme + Reviewer Guide PDFs.
 > Recommendation: C (criteria/elements + enforceable reviewer-policy constraints).
 > **Selected: C**

**Q4: For each call, do you want one combined traceability manifest or separate manifests per source type?**
- A) One manifest per call at `backend/data/calls/sources/<call>.sources.md` listing both app-form + criteria.
- B) Two manifests per call: `<call>.application.sources.md` and `<call>.criteria.sources.md`.
 > Recommendation: A (matches existing repo pattern).
 > **Selected: A**

**Q5: Order of work inside the WF (after Phase 0), given the hard upload gate?**
- A) Start with primary target ERC CoG migration first, then re-author baseline calls.
- B) First prove baseline preflight passes for existing canonical YAMLs (dry-run + ingest), then start CoG migration + re-authoring.
- C) Re-author baseline calls first (from uploaded sources), then do CoG migration.
 > Recommendation: B.
 > **Selected: B**

## Section 2 — Desired Outcome (2026-03-02)

**Q1: What is the minimum “canonical v2 migration done” signal for `erc_cog_2026_full`?**
- A) YAML exists + `ingest_call.py --dry-run` passes.
- B) Dry-run passes + real DB ingest succeeds into local non-prod DB.
- C) DB ingest succeeds + we can run at least 1 structured review request end-to-end locally using that call code.
 > Recommendation: B.
 > **Selected: A + B + C** (treat as staged DoD: A/B as required gates; C as final acceptance for WF completion)

**Q2: For the “baseline calls” (`nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`), what are we allowed to change?**
- A) No YAML changes allowed; only validate current state.
- B) YAML changes allowed only to fix validation/ingest breakage; otherwise keep content stable.
- C) Full re-author from official sources even if it changes node IDs/elements, as long as it validates.
 > Recommendation: B.
 > **Selected: B** (with additional constraint: keep compatibility with the universal structured review engine outputs/contracts)

**Q3: Node ID stability constraint for re-authoring (baseline calls):**
- A) Keep all existing `proposal_nodes[*].id` stable unless an ID is clearly wrong.
- B) IDs may change freely if more “official aligned”.
- C) Keep IDs stable, but allow adding new nodes/elements as needed.
 > Recommendation: A.
 > **Selected: A**

**Q4: Traceability “minimum required fields” for each `.sources.md` in this WF:**
- A) `Path` + `SHA256` + `Used for` mapping only.
- B) A + add “official URL” (or source page) and `Downloaded/Provided date`.
- C) B + page/section citations for every mapped YAML field.
 > Recommendation: B.
 > **Selected: B**

**Q5: Source-file handling: do you want the local copied sources (`backend/data/calls/source_files/WF-0044/...`) committed to git?**
- A) Yes, commit them.
- B) No, keep them gitignored; manifests still record SHA256 + local path, and external/original context when available.
- C) Commit only small text sources; ignore PDFs/DOCX.
 > Recommendation: B.
 > **Selected: B**
