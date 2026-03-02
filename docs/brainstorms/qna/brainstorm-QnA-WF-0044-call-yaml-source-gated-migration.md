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

## Section 3 — Target User / Actor (2026-03-02)

**Q1: Who is the primary actor for WF-0044 execution?**
- A) Internal developer/operator maintaining call YAML + ingestion + tests.
- B) Researcher using the product UI.
- C) Mixed: internal operator + researcher-facing documentation as an output.
 > Recommendation: A.
 > **Selected: A**

**Q2: Who supplies the official source documents (per the hard upload gate)?**
- A) User uploads per call (application-form docs + assessment-criteria PDFs); authoring only after upload + traceability reference.
- B) Agent may fetch official sources from the web if user provides URLs.
- C) Hybrid: user uploads some, agent fetches some.
 > Recommendation: A.
 > **Selected: A**

**Q3: For the “real DB ingest” validation, what environment should we treat as the target?**
- A) Local Postgres dev DB.
- B) SQLite local file DB.
- C) Disposable Docker Postgres used only for this WF verification.
 > Recommendation: A.
 > **Selected: A**

**Q4: For the “run 1 structured review end-to-end locally” acceptance, what counts as E2E?**
- A) Call the FastAPI endpoint locally (API-level contract).
- B) Call the internal service function directly (unit-level).
- C) Either is fine.
 > Recommendation: A.
 > **Selected: A**

**Q5: Who is the intended consumer of traceability manifests (`backend/data/calls/sources/*.sources.md`)?**
- A) Internal engineering only, but written defensibly (path, hash, mapping, dates).
- B) External audit-grade with full page/section citations for each YAML mapping.
- C) Minimal internal notes only.
 > Recommendation: A.
 > **Selected: A**

## Section 4 — Rough Idea Exploration (2026-03-02)

**Q1: How should we structure the “upload gate” mechanics in artifacts?**
- A) Add a per-call “Source Gate Checklist” section inside the WF-0044 brainstorm and keep it updated as we go.
- B) Create a dedicated per-call gate file under `docs/workflow_gates/WF-0044/<call>.md`.
- C) Track gates only in commit messages / PR description.
 > Recommendation: A.
 > **Selected: A**

**Q2: Where should the new canonical file for CoG live and what should its id/code be?**
- A) `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml` with `funding_call.id: erc_cog_2026_full` and `funding_call.code: erc_cog_2026_full`.
- B) `canonical/erc/erc_cog_2026_full_proposal.yaml` with stage `full_proposal`.
- C) Keep it in `legacy/` first, move later.
 > Recommendation: A.
 > **Selected: A**

**Q3: How do we handle the legacy mirror `erc_cog_2026_full_official.yaml` during re-authoring?**
- A) Re-author content from sources but keep it v1 schema; add/refresh a `.sources.md` manifest for it anyway.
- B) Freeze legacy; only author canonical.
- C) Convert it into v2 as well.
 > Recommendation: A.
 > **Selected: A**

**Q4: “Universal structured review engine compatibility” constraint: what should we treat as the primary contract surface?**
- A) `backend/tests/test_structured_reviewer_service.py` + API tests as the contract; avoid changing baseline call logical IDs that those tests implicitly depend on.
- B) Only schema/ingest are contract; runtime tests are secondary.
- C) Add new contract tests now as part of Phase 0.
 > Recommendation: A.
 > **Selected: A**

**Q5: When re-authoring baseline calls from official sources, what’s the stance if the current canonical YAML conflicts with the sources?**
- A) Prefer minimal-change unless the conflict breaks ingest/schema or is clearly wrong; log discrepancies and defer “perfect alignment” unless required.
- B) Always change YAML to match sources, even if it breaks compatibility.
- C) Split into new call IDs to avoid changing existing ones.
 > Recommendation: A.
 > **Selected: A** (plus: capture any newly discovered info that is critical/useful for the universal structured review engine, without destabilizing existing contracts)

## Section 5 — Constraints (2026-03-02)

**Q1: “Engine-critical info” discovery: where do we record it when sources reveal something we missed originally?**
- A) Append an “Engine-impact notes” section inside the WF-0044 brainstorm only.
- B) Log it in `docs/logs/decisions.md` with a WF-0044 entry + link from brainstorm.
- C) Add it to `docs/memory/` files (when it’s a recurring gotcha/pattern).
 > Recommendation: B (and optionally also summarize in brainstorm).
 > **Selected: B + C**

**Q2: Baseline-call compatibility: are we allowed to change behavior-affecting fields (e.g., `reviewer_policy`, `evaluation_stage`, compliance severities) if sources show they’re wrong?**
- A) Only if needed to make ingestion/validation pass.
- B) Allowed if it improves correctness, but must keep node IDs stable and preserve universal-engine runtime contracts; any behavior changes require explicit notes + verification.
- C) Always update to match sources even if it breaks tests; we’ll fix tests later.
 > Recommendation: B.
 > **Selected: B**

## Note — Runtime Utilization Gap (2026-03-02)

We explicitly tracked that v2 call-definition `reviewer_policy` rules are applied in the single-snippet flow (prompt injection + deterministic forbidden-term post-checks), but structured pipeline v1 does not currently enforce them. WF-0044 scope includes wiring reviewer_policy into structured pipeline v1 so call/agency-specific reviewer constraints affect structured review outputs.

## PART B Clarifications (2026-03-02)

User selected “go with recommendations” for the Part B clarification set:

- Q1: Selected B (traceability refresh + targeted corrections when sources clearly contradict; preserve node IDs; explicit verification notes).
- Q2: Selected A (local Postgres dev DB URL, no Docker).
- Q3: Selected A (one structured-review API request with minimal node payload that returns review cards).
- Q4: Selected B (per call under WF: `backend/data/calls/source_files/WF-0044/<call_code>/...`).
- Q5: Selected A (tag applicability in docs as `[ERC-only]`, `[NWO-only]`, `[General]`).

**Q3: For the upload gate, what is the minimum acceptable “assessment-criteria document(s)” for each call?**
- A) Exactly 1 criteria document per call.
- B) As many as needed, but must include (1) evaluation criteria/elements and (2) any enforceable reviewer-policy constraints; may be 2+ documents of any type (PDF/DOCX/MD/TXT/etc.).
- C) Anything you upload is fine; we won’t gate on content completeness.
 > Recommendation: B.
 > **Selected: B** (explicitly not fixated on PDF file type)

**Q4: Are we allowed to update `docs/call-yaml/authoring-workflow.md` / `docs/call-yaml/guidelines.md` within this WF if sources force new universal patterns?**
- A) No, keep WF limited to call YAMLs only.
- B) Yes, but only small surgical updates (1–10 lines) when we learn something generalizable.
- C) Yes, freely refactor the docs.
 > Recommendation: B.
 > **Selected: B** (note: not all patterns apply to all calls; capture applicability/limits when updating)

**Q5: Strictness of “STOP and ask for uploads before authoring each call YAML”: does “authoring” include creating an empty YAML skeleton/template file?**
- A) Yes: no file creation/edits at all before uploads.
- B) No: we can create skeleton placeholders and TODO blocks, but no substantive content derived from sources until uploads.
- C) Only applies to criteria/elements; structure can be drafted without sources.
 > Recommendation: B.
 > **Selected: B**
