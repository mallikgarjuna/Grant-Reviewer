# WF-0037 — Re-author NWO Vidi 2025 full proposal YAML (official sources)

Artifact: brainstorm
Version: v0.2
Status: Draft
Last Updated: 2026-02-27

---

## Preflight Step 1: Narrative Intake (Interactive)

Current intent:

- Primary goal (now): prove the universal call YAML authoring pipeline works for a second real NWO call (eventually also supports researcher-facing use).
- Stage: full proposal (not pre-proposal), single-stage evaluation (per user; must confirm against official docs).
- Scope boundary: encode evaluable proposal structure (nodes), evaluation criteria/elements, and enforceable content constraints only; include reviewer-relevant guidance only when it directly supports evaluation and is grounded in the official sources.

**Brainstorming Q&A:**

**Q1: What is the primary “pain” WF-0037 is fixing?**
- A) Our call YAML for NWO Vidi full proposal doesn’t exist (or is outdated), so we can’t ingest/evaluate it reliably.
- B) The YAML exists but doesn’t follow updated authoring conventions (sources manifest, reviewer_policy), risking drift and poor traceability.
- C) The YAML is fine; the real issue is frontend or API behavior.
> Recommendation: A — This is the cleanest, falsifiable deliverable and keeps scope in call-definition maintenance rather than product changes.
> **Selected: A**

**Q2: Who is the primary “customer” of this WF output?**
- A) Researchers/applicants using the app to get evaluation-criteria-grounded feedback.
- B) Internal us, to prove the universal YAML authoring pipeline works across calls.
- C) Reviewers/committee members (model reviewer instructions heavily).
> Recommendation: B — Optimizes for creating a second robust, source-grounded call definition under the universal conventions; researcher UX benefits later.
> **Selected: B (then eventually A)**

**Q3: What “stage model” should the YAML encode for Vidi?**
- A) Single stage only, unless the official docs clearly define multiple steps.
- B) Always encode STEP_1 + STEP_2 for future-proofing.
- C) No stages; treat stage as app-level only.
> Recommendation: A — Don’t invent stages. Encode what the funder defines, and keep runtime honest.
> **Selected: A (single-stage full proposal; must confirm in sources)**

**Q4: What is your strict scope boundary for what goes into the call YAML?**
- A) Only: proposal structure (nodes), evaluation criteria/elements, and enforceable content constraints.
- B) Include lots of help text/guidelines even if not enforceable.
- C) Encode everything in the docs (process/eligibility/deadlines/budget rules).
> Recommendation: A — Matches repo scope rules and keeps YAML legally/operationally defensible.
> **Selected: A (plus reviewer-relevant, source-grounded guidance that directly supports evaluation)**

**Q5: Definition of “done” for WF-0037 Phase 0 output?**
- A) Source-gated: official docs uploaded, clear plan for YAML + reviewer_policy, and a verification plan (dry-run ingest + DB/API preflight).
- B) A complete YAML fully authored and merged.
- C) A brainstorm only, no verification plan.
> Recommendation: A — Prevents authoring from memory and sets up a deterministic verification loop.
> **Selected: A**

## Preflight Step 2: Repo Reality Snapshot (Read-Only) (2026-02-27)

- No existing NWO Vidi call YAML is present in `backend/data/calls/nwo/`; only Veni preproposal exists (canonical + legacy archive).
- The repo has an explicit authoring SSOT: `docs/workflow/call-yaml-authoring-workflow.md` with gated steps (source confirmation, nodes, criteria/elements, mapping, guidance/compliance, then generation).
- Source traceability manifests live in `backend/data/calls/sources/` and are already used for ERC StG 2026 and NWO Veni 2025 preproposal; we should follow the same pattern for Vidi.
- V2 schema supports `reviewer_policy` with deterministic enforcement modes (`PROMPT_ONLY`, `POST_CHECK`, `BLOCKING`) and validates `forbidden_terms` when enforcement is post-check/blocking.
- Universal form work (WF-0035) has an explicit acceptance gate: “Veni + 1 additional official flat-supported structured call” (Vidi selected as the candidate), so we should preserve flat-only feasibility when authoring Vidi nodes.

Key open questions this snapshot suggests:

- What is the exact canonical call code + filename that matches `{agency}_{program}_{year}_{stage}.yaml` without leaking brittle numbering?
- What are the official sources for: (1) proposal structure (application form/template) and (2) evaluation criteria/procedure (reviewer guidance / criteria chapter)?
- Are there domain/pilot variants that introduce per-domain word limits or node differences (like Veni `science_enw`)?
- Does Vidi explicitly prohibit bibliometrics/venue-prestige language (needs `reviewer_policy` parity), and where is it stated?
- Are there hard word limits / item limits per section that are actually enforceable with current compliance engine capabilities?

---

## Section 1: Problem Statement (Interactive)

Decisions:

- Use the provided Vidi DOCX (structure + enforceable limits) and PDF (evaluation criteria/procedure) as SSOT sources for authoring.
- Canonical code and filename: `nwo_vidi_2025_full_proposal` → `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`.
- Include deadlines inside YAML (schema-supported; must be copied from official sources only).
- Encode true structure even if nested (`children`), even though WF-0035 flat-only universal form will hard-block nested calls for now.
- Do not update `docs/workflow/call-yaml-authoring-workflow.md` with call-specific content during WF-0037; only add generalizable workflow rules when warranted.

**Brainstorming Q&A:**

**Q1: Source Gate Confirmation (SSOT)**
- A) Yes: treat the provided DOCX (structure) + PDF (evaluation criteria/procedure) as SSOT; provide any missing annexes if we discover a gap.
- B) Yes, but only the PDF is SSOT; the DOCX is “help text”.
- C) Not yet; wait for a page/section list first.
> Recommendation: A — Minimizes ambiguity: structure comes from the form; evaluation logic comes from the call PDF; this matches the authoring SSOT workflow.
> **Selected: A**

**Q2: Canonical Call Code + Filename**
- A) `nwo_vidi_2025_full_proposal` and filename `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`.
- B) `nwo_vidi_2025_fullproposal` (avoid underscores in stage).
- C) Custom code (specify).
> Recommendation: A — Matches repo naming convention `{agency}_{program}_{year}_{stage}.yaml` and keeps the stage explicit.
> **Selected: A**

**Q3: Deadlines In YAML**
- A) Yes: include the key submission deadline(s) in `funding_call.deadlines`, clearly labeled, strictly copied from official sources.
- B) No: keep deadlines out of YAML entirely.
- C) Yes, but only a single `submission_deadline` key.
> Recommendation: A — Schema supports deadlines and we already use it (e.g., NWO Veni); it’s useful metadata and low risk if source-grounded.
> **Selected: A**

**Q4: Proposal Node Shape If The Real Call Is Nested**
- A) Encode the true structure (including nesting via `children`), even if WF-0035 universal form will hard-block it for now.
- B) Force-flatten to keep it “flat-supported” for WF-0035.
- C) Dual-author: “true nested” + “flat shim” YAML.
> Recommendation: A — Don’t falsify the call structure to satisfy a temporary frontend limitation; keep the universal flow honest and handle recursion separately.
> **Selected: A**

**Q5: Update The Living Authoring Spec (`docs/workflow/call-yaml-authoring-workflow.md`)**
- A) Update only with generalizable workflow rules we learn here (no call-specific facts), and link to example YAML/manifests.
- B) Also add a short “NWO patterns” note (still generic).
- C) Do not update it during WF-0037; defer spec updates to a dedicated WF.
> Recommendation: A — Keeps SSOT lean while still letting us improve the workflow when we learn something reusable.
> **Selected: A**

---

## Section 2: Desired Outcome (Interactive)

Decisions:

- “Shipped output” for this WF includes the authored YAML + traceability manifest + passing validations (not brainstorm-only).
- Assume no legacy Vidi YAML exists; create a new canonical file (if we discover a legacy later, we will archive it as `*_legacy.yaml`).
- Verification required before “ready”: both `--dry-run` ingest and DB/API preflight smoke-test.
- Include `reviewer_policy` where Vidi official sources justify it, following the same enforcement posture as Veni (PROMPT_ONLY vs POST_CHECK vs BLOCKING based on clarity).
- Treat `Vidi 2025_literature_list.docx` as out-of-scope unless the official call PDF explicitly references it as an official annex that affects structure/limits/evaluation.

**Brainstorming Q&A:**

**Q1: What is the minimum “shipped output” for WF-0037 (beyond brainstorm clarity)?**
- A) A fully authored V2 call YAML + `sources.md` manifest + `--dry-run` ingest passes.
- B) Same as A, plus DB ingest and API smoke-test is executed now.
- C) Brainstorm-only; YAML authoring happens in Phase 1+.
> Recommendation: A — Phase 0 should converge on a falsifiable deliverable and verification plan; DB/API smoke-test is still required, but it can be executed once the YAML exists.
> **Selected: A**

**Q2: Do we archive any “legacy Vidi YAML” if it exists?**
- A) No legacy exists; this is a new file.
- B) If legacy exists, archive to `*_legacy.yaml` and keep canonical stable.
- C) Overwrite any existing file in-place without archive.
> Recommendation: A — No evidence of an existing Vidi YAML in-repo; if one is found later, we should switch to (B) rather than overwrite.
> **Selected: A**

**Q3: What verification is required before we consider YAML “ready to be used by the app”?**
- A) Both: dry-run ingest + DB/API smoke-test (`/calls`, `/calls/{id}/nodes`, `/api/public/calls/{code}/config`, `/api/public/calls/{code}/nodes/metadata`).
- B) Dry-run ingest only.
- C) DB/API smoke-test only.
> Recommendation: A — Dry-run validates schema and references; DB/API preflight validates runtime shape and prevents frontend rework.
> **Selected: A**

**Q4: Should we include `reviewer_policy` for Vidi in this WF?**
- A) Yes: mirror the pattern from Veni where Vidi sources justify it (bibliometrics ban, prestige language, DORA/merits, bias avoidance).
- B) Only include PROMPT_ONLY guidance; skip POST_CHECK/BLOCKING enforcement.
- C) Skip reviewer_policy entirely for Vidi.
> Recommendation: A — This is low-effort, high-impact quality control when (and only when) grounded in official wording; enforcement level should match clarity of the source.
> **Selected: A**

**Q5: Should we incorporate the extra file present in the folder (`Vidi 2025_literature_list.docx`) as an official source?**
- A) Not unless the Call PDF explicitly references it as a required/official annex affecting structure/limits/evaluation.
- B) Yes, include it automatically as a source.
- C) Use it only for guidance_text, never for constraints/evaluation mapping.
> Recommendation: A — Keeps the source gate legally defensible and avoids “helpful but unofficial” content bleeding into evaluable structure.
> **Selected: A**

---

## Sources (Confirmed, Local) (2026-02-27)

SSOT inputs (provided in-workflow):

- Structure (DOCX): `Vidi-2025-Full-proposal-form.docx`
  - Local path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Vidi-2025/Full-proposal/Vidi-2025-Full-proposal-form.docx`
  - SHA256: `2c0fae7da27eec6001c85ebbd23b338e4a659b7c5d4d4c23eec414ff5e2e7919`
- Evaluation criteria/procedure (PDF): `Call-for-Proposals-Vidi-2025_Eng.pdf`
  - Local path: `/home/mgurram/Projects/Non-Github/PeerLens_proj/NWO-Vidi-2025/Full-proposal/Call-for-Proposals-Vidi-2025_Eng.pdf`
  - SHA256: `0ca64071d011268eea1c9a3a6aa3de52f0a8f16b2ed480ca8e24fe1e5de5c026`

Non-SSOT candidate file in the same folder:

- `Vidi 2025_literature_list.docx` (ignore unless the call PDF explicitly references it as an official annex that affects evaluable structure/limits/evaluation).

---

## Section 3: Target User / Actor (Interactive)

Decisions:

- Primary UI reader for guidance is the researcher/applicant; keep guidance text researcher-facing and submission-practical.
- English-only for YAML labels and guidance (sources are English).
- Do not add domain/pilot scaffolding unless the official Vidi sources explicitly define variants.
- Author nodes at section-level granularity aligned to evaluable chunks (few nodes), optimized for paste-first behavior.
- Source gate approved: we may now open/extract from the official Vidi DOCX+PDF to draft nodes/criteria.

**Brainstorming Q&A:**

**Q1: Who is the primary “reader” of the YAML-authored guidance (guidance_text, constraint notes, reviewer_policy instruction)?**
- A) Researchers/applicants (write in second-person “you”, practical, submission-focused).
- B) Reviewers (write like panel guidance; more formal evaluation framing).
- C) Both (dual-voice; risk: bloated/unclear).
> Recommendation: A — The product UI is researcher-facing; reviewer behavior is mediated by the model. Keep guidance usable for the submitter.
> **Selected: A**

**Q2: What language should we target for node labels/guidance in YAML?**
- A) English only (since sources are English; keep consistent).
- B) Bilingual (English + Dutch).
- C) English now, add localization later (store only English in YAML for now anyway).
> Recommendation: A — Keeps authoring grounded in the provided sources and avoids premature localization complexity.
> **Selected: A**

**Q3: Do we assume domain/pilot variants exist for Vidi (affecting constraints/word limits or nodes)?**
- A) Assume single default (no domain branching) unless the official docs explicitly define variants.
- B) Proactively add `domain_id` scaffolding even if unclear.
- C) Force the user to select a domain in UI always.
> Recommendation: A — Avoid inventing branching logic. If variants exist, encode them explicitly from source text.
> **Selected: A**

**Q4: How should we size proposal nodes for the expected user behavior in the app?**
- A) Section-level nodes aligned to evaluable chunks (few nodes; user pastes per major section).
- B) Very granular subsection nodes (many nodes; heavier UX).
- C) One giant full-proposal node (legacy-style).
> Recommendation: A — Balances structure with usability and keeps the “universal call flow” feasible without making the UI a wizard.
> **Selected: A**

**Q5: Source-gate execution: may I now open and extract from the two official files you listed (DOCX+PDF) to draft nodes/criteria?**
- A) Yes, you can open and extract from both now.
- B) Yes, but only extract structure from DOCX; wait before using the PDF.
- C) Not yet; list exactly which pages/sections first.
> Recommendation: A — We need both structure and evaluation criteria grounded in the official sources to proceed.
> **Selected: A**
