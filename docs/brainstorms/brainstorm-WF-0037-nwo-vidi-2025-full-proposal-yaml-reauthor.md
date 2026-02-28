# WF-0037 — Re-author NWO Vidi 2025 full proposal YAML (official sources)

Artifact: brainstorm
Version: v0.7
Status: Draft
Last Updated: 2026-02-28

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

---

## Section 4: Rough Idea Exploration (Interactive)

Decisions:

- Model **full proposal only** in this WF (do not encode the entire pre-proposal + full-proposal pipeline here).
- Proposal nodes: include evaluable **narrative** sections only (summary, research narrative, impact). Exclude administrative and mechanics by default.
- Budget justification: include **only if** the official evaluation criteria explicitly assess feasibility/resources/budget as a reviewable concern; otherwise exclude from proposal nodes.
- Multi-domain scheme: keep one YAML; add domain notes only; add per-domain constraints only if the schema can represent them honestly from sources.
- Enforceable constraints posture: encode deterministic constraints only (word limits / explicit max items). Do not pretend we can enforce fonts/margins/layout.

**Brainstorming Q&A:**

**Q1: Single “full proposal call” vs encoding the whole Vidi pipeline (pre-proposal + full proposal)**
- A) Model full proposal only.
- B) Model both pre-proposal + full proposal as STEP_1/STEP_2 stages in one YAML.
- C) Create two separate call YAMLs: pre-proposal + full proposal.
> Recommendation: A — Matches the initiative (“Vidi 2025 full proposal”) and avoids turning this WF into a multi-stage workflow rebuild.
> **Selected: A**

**Q2: Which DOCX sections become `proposal_nodes` (narrative content only)**
- A) Include narrative sections only: scientific summary, public summary (EN), research description, impact; exclude administrative/budget/literature list as nodes.
- B) Also include “Budget justification” as a node (if evaluated).
- C) Include everything in the form as nodes.
> Recommendation: A — Preserves YAML scope; budget may be added only if explicitly evaluated in the call’s criteria.
> **Selected: A (and B only if budget justification is evaluated)**

**Q3: How to handle the multi-domain nature (AES/TTW, SSH/SGW, ENW)**
- A) Keep one call YAML; encode domain differences as `funding_call.domain_notes` only, and only add per-domain constraints if the schema can represent them honestly.
- B) Split into 3 call YAMLs (one per domain).
- C) Add domain branching everywhere even if it requires schema work.
> Recommendation: A — Keeps the universal call flow consistent; only encode branching when the source requires it.
> **Selected: A**

**Q4: Literature list: do we treat `Vidi 2025_literature_list.docx` as a source?**
- A) No, unless the PDF explicitly says it is an official annex that affects evaluable structure/limits/evaluation; otherwise ignore it for YAML authoring.
- B) Yes, include it in the manifest and use it for guidance_text only.
- C) Yes, include it and make it a proposal node.
> Recommendation: A — Keeps the source gate defensible; do not import “extra” docs unless officially referenced.
> **Selected: A**

**Q5: “Enforceable constraints” posture (given our compliance engine limits)**
- A) Encode deterministic constraints only (word limits, explicit max items) and keep the rest as guidance_text; do not pretend we can enforce fonts/margins/page layout.
- B) Encode all formatting requirements as compliance_rules WARNING/ERROR anyway.
- C) Don’t encode constraints; guidance_text only.
> Recommendation: A — Honest enforcement prevents false confidence while still providing useful guardrails to applicants.
> **Selected: A**

---

## Section 5: Constraints (Interactive)

Decisions:

- Timebox: 1–2 days once we move from ideation into authoring/verification.
- Guidance strictness: default strict (only evaluation-tied or enforceable-constraint-tied guidance, source-grounded). If we want broader “explanatory notes” guidance, we should only add it if it can live in a clearly separated field (not mixed into evaluable guidance); schema support for that separation is currently unclear and may require a follow-on.
- Deadline handling: store `datetime_local` + `timezone` exactly as in the official sources (no conversion).
- Nested structure: encode true nesting, but keep depth conservative (<=4–5). If depth reaches >=5, stop and ask for explicit user guidance before proceeding.
- Budget justification node: exclude by default; include only if official criteria explicitly assess feasibility/resources/budget, and keep it narrow.

**Brainstorming Q&A:**

**Q1: Timebox for WF-0037 execution (once we leave ideation)?**
- A) 1–2 days (tight YAML-only maintenance).
- B) 1 week.
- C) No timebox.
> Recommendation: A — Keeps this WF from turning into a product initiative; it should be a fast, source-grounded definition + verification pass.
> **Selected: A**

**Q2: YAML scope strictness for “helpful for LLM to review” guidance**
- A) Strict: only include guidance that is directly tied to an evaluation element or an enforceable constraint, and is grounded in sources.
- B) Medium: include broader “Explanatory Notes” guidance if it helps applicants write better, even if not evaluable.
- C) Loose: include most embedded guidance.
> Recommendation: A — Mixing non-evaluable tips into evaluable guidance blurs what the model should assess. If we want (B), we should do it via a clearly separated field to keep the execution contract honest.
> **Selected: A (+ B only if represented in separate YAML fields, not mixed into evaluable guidance)**

**Q3: Deadline timezone consistency**
- A) Store deadlines exactly as in source (CET/CEST) with `datetime_local` + `timezone` and no conversion.
- B) Convert everything to UTC.
- C) Store as free text only.
> Recommendation: A — Lowest ambiguity and matches the schema intent; avoids implicit conversions that can shift deadlines.
> **Selected: A**

**Q4: Nested structure depth limit**
- A) Allow nesting as needed but keep depth <= 4–5; if deeper (>=5), stop and ask for user input.
- B) Allow arbitrary depth.
- C) Force flat only.
> Recommendation: A — Protects downstream UX/execution complexity while keeping the call definition faithful.
> **Selected: A (ask user if depth >=5)**

**Q5: Budget justification conditional (based on evaluation criteria)**
- A) Default exclude; include only if the official criteria explicitly assess resources/feasibility/budget, and then keep it narrow.
- B) Always include budget justification as a node.
- C) Never include budget justification as a node.
> Recommendation: A — Keeps nodes aligned to what is actually assessed; avoids adding non-evaluable mechanics as narrative nodes.
> **Selected: A**

---

## Section 6: Risks / Unknowns (Interactive)

Decisions:

- Primary authoring risk is mis-identifying what is actually evaluated vs “instructions only”.
- Primary runtime/product risk is that Vidi’s true structure may be nested, so WF-0035 flat-only universal form will hard-block it until recursion ships.
- Despite the PDF describing a pre-proposal + proposal procedure, this WF will model full proposal only (structure from the full-proposal form) and extract only full-proposal-relevant evaluation criteria.
- Traceability must be strict: each evaluation element and any strong guidance/constraint must carry a `source_hint` and be enumerated in `sources.md`.
- If we discover depth >=5 or strong domain-specific differences, we stop and ask explicitly (no guessing).

**Brainstorming Q&A:**

**Q1: Biggest risk to authoring the YAML correctly**
- A) Mis-identifying what is actually evaluated vs “instructions only”, leading to wrong nodes/elements.
- B) Missing/incorrect word/page limits per section.
- C) Incorrectly encoding nested structure depth/order.
> Recommendation: A — If we get “what is assessed” wrong, everything downstream (nodes, mapping, prompts) becomes misleading.
> **Selected: A**

**Q2: Biggest runtime/product risk**
- A) The authored node tree is nested, so WF-0035 universal form won’t accept it yet (hard-block), delaying the “2nd call proof” unless recursion ships.
- B) Review quality drift (model uses bibliometrics/prestige language).
- C) Compliance mismatch (we claim enforceability we don’t have).
> Recommendation: A — This is the most concrete integration risk against current launch sequencing; it can block universal-form validation even if the YAML is correct.
> **Selected: A**

**Q3: How should we handle “single-stage” vs the PDF describing a pre-proposal + proposal procedure?**
- A) Treat this YAML as full proposal only; ignore pre-proposal steps, but use the PDF’s full-proposal evaluation criteria sections.
- B) Reinterpret “single-stage” and encode STEP_1/STEP_2 anyway.
- C) Stop and create separate WFs for pre-proposal vs full proposal.
> Recommendation: A — Keeps scope aligned to the full-proposal form while remaining source-grounded about how full proposals are assessed.
> **Selected: A**

**Q4: Source traceability strictness**
- A) Every evaluation element and any strong guidance/constraint must have a `source_hint` and be listed in `sources.md`.
- B) Only top-level criteria need source hints.
- C) No per-item source hints; just a general manifest.
> Recommendation: A — Prevents “made up” criteria and keeps the universal authoring workflow defensible and maintainable.
> **Selected: A**

**Q5: If we discover depth >=5 or strong domain-specific differences, what is the escalation path?**
- A) Stop and ask you immediately (no guessing), then proceed with your decision.
- B) Make a best guess to keep moving.
- C) Force-flatten/simplify automatically.
> Recommendation: A — Guessing here creates irreversible drift; explicit decisions keep the workflow safe.
> **Selected: A**

---

## Section 7: MVP Definition (Interactive)

Decisions:

- MVP completion means: canonical Vidi full-proposal YAML + source manifest exist, and dry-run ingest passes.
- MVP nodes include only evaluable narrative content (plus minimal metadata like deadlines); budget justification stays conditional on being explicitly evaluated.
- One YAML across domains; use `domain_notes` unless sources mandate enforceable per-domain constraints.
- Include `reviewer_policy` when grounded in the official PDF; enforcement strength matches source clarity.
- Walkthrough records dry-run verification; DB/API preflight is planned (and expected) once YAML exists, but not required to claim MVP completion at the Phase 0 definition level.

**Brainstorming Q&A:**

**Q1: What is the MVP output of WF-0037 (the smallest “real” completion)?**
- A) Author `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml` + `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`, and `ingest_call.py --dry-run` passes.
- B) Same as A, plus DB ingest + API preflight is executed and recorded in walkthrough.
- C) Only the brainstorm is completed; YAML happens later.
> Recommendation: A — Establishes a source-grounded call definition artifact and a deterministic validation signal without turning Phase 0 into a runtime integration sprint.
> **Selected: A**

**Q2: What is the MVP scope for proposal nodes?**
- A) Only evaluable narrative nodes required for assessment (summary, research narrative, impact), plus minimal required metadata like deadlines.
- B) Include narrative + budget justification always.
- C) Include everything in the form.
> Recommendation: A — Keeps YAML aligned to evaluable narrative content; avoids encoding mechanics as if they were reviewed narrative.
> **Selected: A**

**Q3: What is the MVP treatment of multi-domain differences?**
- A) One YAML; use `domain_notes` only unless the sources mandate different constraints.
- B) Split into one YAML per domain.
- C) Add domain branching everywhere.
> Recommendation: A — Preserves a universal flow and avoids inventing branching logic; escalate only when the sources demand it.
> **Selected: A**

**Q4: What is the MVP stance on `reviewer_policy`?**
- A) Include `reviewer_policy` rules grounded in the PDF (DORA/merits, bibliometrics ban, prestige language, bias/personal-attributes avoidance), with enforcement strength matching source clarity.
- B) PROMPT_ONLY only; no POST_CHECK/BLOCKING.
- C) Skip reviewer_policy.
> Recommendation: A — It’s cheap insurance against known failure modes, but must be grounded in official wording to remain defensible.
> **Selected: A**

**Q5: What is the MVP verification record?**
- A) Walkthrough includes dry-run ingest commands and expected output; DB/API preflight is planned but not executed until YAML exists.
- B) Walkthrough must include DB/API preflight execution now.
- C) No walkthrough needed for MVP.
> Recommendation: A — Walkthrough is required for reproducibility; preflight execution belongs after YAML exists and is still required before frontend reliance.
> **Selected: A**

---

## Phase 0 Risk Audit Edits (Applied) (2026-02-28)

This section incorporates Phase 0.2 (risk audit) findings into the brainstorm so Phase 1 planning does not inherit ambiguity.

### Deadline Encoding Rules (Resolved)

- Deadlines must be copied from the official sources verbatim, including timezone label.
- If sources disagree (e.g., CET vs CEST for April), stop and resolve by citing the authoritative source section/page.
- Policy decision for WF-0037: trust the **Call PDF** for the full proposal submission deadline + timezone if it conflicts with the form.
- Deadline keys must be stable and descriptive (e.g., `full_proposal_submission`), and each entry must include:
  - `datetime_local` (as written)
  - `timezone` (as written)
  - `source_hint` (section/page in the PDF)

### Criteria Extraction Guardrail (Resolved)

The Call PDF describes both pre-proposal and full proposal procedures. For this WF:

- We model the full proposal form only.
- We extract and encode only the evaluation criteria/elements that are applied to the **full proposal**.
- Any pre-proposal-only criteria are explicitly excluded (and noted) to avoid contaminating the full proposal evaluation criteria/elements.
- Criteria extraction source: Chapter 4 “Assessment procedure” and its criteria subsections, explicitly separating pre-proposal vs full proposal applicability.

### Dutch Summary Handling (Resolved)

Decision: exclude "Public summary in Dutch" from `proposal_nodes` (out of evaluable narrative scope). We may optionally surface it as a compliance INFO note to the researcher (submission requirement context), but we will not map evaluation elements to it unless the official criteria explicitly assess it.

### Domain Note (Non-blocking, Explicit)

The official form spans AES/TTW, SSH/SGW, and ENW. Default remains: one YAML with `funding_call.domain_notes`. If required sections or enforceable constraints differ by domain in the official sources, we stop and ask for an explicit decision (split vs explicit branching).

### Cross-WF Sequencing Risk (Non-blocking, Explicit)

WF-0035 currently hard-blocks nested calls. If Vidi YAML is nested, it cannot serve as WF-0035’s “flat 2nd call proof” until recursion ships or we choose a different flat call for that acceptance gate.

### Budget/Feasibility Handling Rule (Resolved)

If full proposal evaluation criteria include “feasibility/resources”:

- Add a narrow narrative node (e.g., “Resources & feasibility”) only if the official form has a corresponding narrative section.
- Otherwise, keep feasibility/resources as an evaluation element mapped to the closest relevant narrative node (do not invent a budget node).
