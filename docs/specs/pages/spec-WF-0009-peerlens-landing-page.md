# WF-0009 — PeerLens Landing Page Spec

Artifact: spec
Version: v0.5
Status: Ready for PRD
Last Updated: 2026-02-14

## 1. Purpose

Provide a high-trust, conversion-focused landing page that positions PeerLens as a safe "pre-reviewer" for grant proposals. It aims to validate the value proposition (review-criteria-aligned feedback) and drive user sign-ups (`/sign-in`) without over-promising capabilities.

## 2. User / System Context

- **User**: New researchers, PIs, postdocs, and fellowship applicants drafting grant proposals (specifically NWO Veni, ERC Starting, MSCA PF).
- **Situation**: User is in the drafting or polishing phase, feeling anxious about arbitrary rejection or "Reviewer #2" critique.
- **System**: Public-facing static page serving as the entry point to the application.

## 3. Core Behavior

- **Hero Section**: Immediately frames the problem (reviewer compliance) and offers a solution (pre-review check).
- **Static Demo**: Interactive-looking but static tabs showing (a) a short snippet, (b) review-criteria findings, (c) a concrete “suggested fix” (may include a short micro-rewrite), and (d) an example readiness score.
- **Readiness Score (Example)**: Visualizes a “65/100” style score to make the value tangible; labeled as an example (not computed on-landing).
- **Trust Signals**: Emphasize “review-criteria-aligned” (vs generic) and link to `/privacy` for data handling details (avoid over-specific claims on the landing page).
- **Demo Label (Exact)**: “Examples only. Sign in to get feedback on your proposal text.” + “Export your review. Delete your data anytime. See Privacy.”
- **Call to Action**: Directs users to "Check My Draft Now" (which leads to Sign In/Sign Up).

## 4. In Scope

- **Public Landing Page (`/`)**:
    - **Nav**: Logo, "Privacy", "Sign In" button.
    - **Hero**: Headline, Subhead, "Check My Draft Now" CTA, text-only “Supported calls” line: “NWO Veni · ERC Starting · MSCA PF”.
    - **Problem/Agitation**: Section highlighting "Reviewer #2" anxiety.
    - **Solution/Demo**: 3 static tabs (NWO Veni, ERC Starting, MSCA PF) showing snippet -> 3–5 feedback cards (criterion + finding + suggested fix) -> example readiness score + “Examples only” label near the demo.
    - **Benefits**: 3 key value props (Readiness Score, Compliance Check, Time Saved).
    - **How It Works**: 3-step visual guide (Sign in -> Select call/section + paste snippet -> Get review).
    - **Social Proof (Text-Only)**: “Supported calls” ticker/list (NWO Veni, ERC Starting, MSCA PF). No funder logos in MVP.
    - **FAQ**: accordion addressing: (1) “Is this generic AI?”, (2) “Why do I need to sign in?”, (3) “What should I paste?”, (4) “How is my data handled?” (links to `/privacy`), (5) “Can I delete my data?”
    - **Footer**: Privacy link only + Copyright.
- **Routing**: `CTA` clicks -> `/sign-in`.

## 4.1 Static Demo Content (Locked for MVP)

All demo content below is **static example content** (no user text; no backend calls). Each tab shows:
- **Snippet** (80–120 words)
- **4 feedback cards** (criterion + finding + suggested fix + micro-rewrite example)
- **Readiness Score (Example)** (0–100)

### Tab: NWO Veni

**Snippet (Example)**
“This project tests why early-career researchers (ECRs) struggle to form cross-lab collaborations despite strong incentives to do so. We combine (1) a survey of ECRs across three Dutch universities (target n≈250) to quantify perceived barriers, with (2) 24 semi-structured interviews to explain the highest-impact barriers in depth. We will triangulate findings into a practical ‘collaboration checklist’ for PIs and research support offices, and validate it via a small pilot workshop. Deliverables include an open interview guide, an anonymized codebook, and a short policy brief.”

**Feedback Cards (Example)**
1) **Criterion**: Feasibility / Work plan  
   **Finding**: Key activities are listed, but sequencing and decision points are missing.  
   **Suggested fix**: Add a simple work plan with milestones, dependencies, and a clear “done” definition per step.  
   **Micro-rewrite (Example)**: “Months 1–2: finalize instruments + ethics; Months 3–4: launch survey (n≈250) and close at ≥200 responses; Months 5–7: run 24 interviews (8 per site); Months 8–9: dual-code transcripts (κ ≥ 0.7) and resolve disagreements; Months 10–12: synthesize checklist + pilot workshop + brief.”
2) **Criterion**: Methodology  
   **Finding**: The link from data → checklist is implicit, so reviewers can’t judge rigor.  
   **Suggested fix**: Specify analysis steps and what the checklist contains (structure, criteria, evidence).  
   **Micro-rewrite (Example)**: “We will run thematic analysis with a pre-registered codebook, then convert the top 6 barriers into checklist items with (a) an ‘early warning’ indicator, (b) a concrete action, and (c) a short evidence note citing survey + interview support.”
3) **Criterion**: Risk management  
   **Finding**: Recruitment and response-rate risks are not mitigated.  
   **Suggested fix**: Add a fallback recruitment plan and a minimum viable sample threshold.  
   **Micro-rewrite (Example)**: “If survey responses are <150 by week 3, we will add two partner institutions and targeted outreach via graduate schools; interviews proceed once we have ≥18 participants spanning all three sites, with a maximum of 30 to avoid scope creep.”
4) **Criterion**: Impact / Relevance  
   **Finding**: The “policy brief” deliverable is mentioned, but adoption and success metrics are unclear.  
   **Suggested fix**: Tie outputs to specific users and define how you’ll test usefulness.  
   **Micro-rewrite (Example)**: “Primary users are PIs and research support offices; we will evaluate usefulness via a pilot workshop (n≈20) and a pre/post measure of ‘confidence in collaboration planning’, plus qualitative feedback on which checklist items are most actionable.”

**Readiness Score (Example)**: 64/100

### Tab: ERC Starting

**Snippet (Example)**
“I will develop a high-risk, high-gain framework for learning causal, clinician-auditable representations from multimodal hospital data (images + notes). The core hypothesis is that enforcing explicit, testable links between textual evidence and visual features reduces shortcut learning and improves out-of-distribution reliability. WP1 derives the theory and constraints; WP2 implements the model and evaluation suite; WP3 validates robustness on two independent hospital cohorts with prospectively-defined failure tests (shifted protocols, rare subgroups). Deliverables include open-source code, a reproducible benchmark, and a methods paper.”

**Feedback Cards (Example)**
1) **Criterion**: Scientific ambition  
   **Finding**: Novelty is implied, but the “breakthrough” mechanism isn’t crisply stated.  
   **Suggested fix**: State what is fundamentally new and the specific limitation it addresses.  
   **Micro-rewrite (Example)**: “Unlike black-box fusion, we introduce evidence-linked constraints that require the model’s prediction to be supported by aligned note concepts and image regions, directly targeting known failure modes from spurious correlations in multimodal learning.”
2) **Criterion**: Methodological soundness  
   **Finding**: The evaluation plan lacks hard “stress tests” and leakage safeguards.  
   **Suggested fix**: Define split strategy, leakage checks, and failure tests aligned to the hypothesis.  
   **Micro-rewrite (Example)**: “We will use patient-level temporal holdout and cross-site transfer; we will run leakage audits (near-duplicate images, templated notes) and report calibration + subgroup performance, plus pre-registered shift tests (protocol changes, rare subgroups) to quantify out-of-distribution robustness.”
3) **Criterion**: Feasibility / Resources  
   **Finding**: Dependencies (data access approvals, compute) are not explicitly managed.  
   **Suggested fix**: Declare gating dependencies and fallback plans (method + data).  
   **Micro-rewrite (Example)**: “Data access approvals are completed by Month 2; training uses 4×A100-equivalent for ≤96 hours per experiment; if compute is constrained we use parameter-efficient tuning and precomputed embeddings, and we prioritize WP2 evaluation deliverables to de-risk WP3.”
4) **Criterion**: Impact pathway  
   **Finding**: Impact is described at a high level without a concrete decision context.  
   **Suggested fix**: Tie to a specific clinical task and measurable decision-relevant endpoints.  
   **Micro-rewrite (Example)**: “We target triage prioritization for acute findings; success is measured by calibration and recall at fixed precision under distribution shift, plus a small reader study quantifying whether the evidence-linked outputs change clinician confidence and time-to-decision.”

**Readiness Score (Example)**: 67/100

### Tab: MSCA PF

**Snippet (Example)**
“This MSCA Postdoctoral Fellowship will strengthen my expertise in causal inference and open science while delivering a comparative evaluation of two education policies using linked administrative datasets. At the host institution I will receive structured training in synthetic controls, event studies, and reproducible workflows (pre-registration, versioned pipelines), with a secondment to a policy unit to learn evidence translation. The research will produce two first-author papers and a reusable analysis toolkit. I will communicate results via a stakeholder brief, a public explainer, and open materials (code + documentation) aligned to EU open science practices.”

**Feedback Cards (Example)**
1) **Criterion**: Training / Skills development  
   **Finding**: Training is credible, but the skills-to-output mapping is not explicit.  
   **Suggested fix**: Map each skill gap to an activity, a mentor, and a concrete artifact.  
   **Micro-rewrite (Example)**: “Skill gap: synthetic controls; Activity: host short course (Month 2) + supervised replication (Months 3–4); Mentor: Dr. X; Artifact: preregistered analysis plan + reproducible pipeline template to reuse across WPs.”
2) **Criterion**: Research plan quality  
   **Finding**: The identification strategy is suggested but not testable as written.  
   **Suggested fix**: State the counterfactual, core assumptions, and diagnostics.  
   **Micro-rewrite (Example)**: “We estimate the effect of Policy A on dropout rates using staggered adoption; identification assumes parallel pre-trends, tested via event-study diagnostics and placebo policies, with robustness checks using synthetic controls for treated regions.”
3) **Criterion**: Dissemination & communication  
   **Finding**: Dissemination is broad, but not scheduled or audience-specific.  
   **Suggested fix**: Specify channels, cadence, and outputs per audience.  
   **Micro-rewrite (Example)**: “Academic: two submissions (Months 12 and 22); Policy: 2-page brief after each WP; Public: one explainer per milestone with a plain-language summary and a short methods appendix.”
4) **Criterion**: Career development  
   **Finding**: The career plan needs concrete independence signals and mentoring cadence.  
   **Suggested fix**: Add measurable milestones (papers, talks, grant prep) and mentoring structure.  
   **Micro-rewrite (Example)**: “Independence signals include two first-author papers, one invited seminar, and a maintained toolkit repo; mentoring includes monthly check-ins and a structured grant-writing sprint (Month 18) targeting a follow-on fellowship or starter grant.”

**Readiness Score (Example)**: 62/100

## 5. Out of Scope

- **Real Interactive Demo**: No actual text processing or backend analysis on the landing page (signed-out).
- **Blog / Content Hub**: No `/blog` or dynamic content pages in this phase.
- **Pricing Page**: No standalone pricing page; likely single tier or free tier focus for now.
- **Dark Mode**: MVP is Light Mode only.
- **User Accounts/Dashboard**: This spec covers the *landing page* entry point, not the dashboard itself (covered in separate specs).

## 6. Data & Dependencies

- **Assets**:
    - Logo files (PeerLens wordmark).
    - Icons (Lucide React).
- **Routing**: Needs access to application routing to link to `/sign-in` and `/privacy`.
- **Theme**: Uses `globals.css` variables (`--primary`, `--surface`, etc.) defined in Brand Guidelines.

## 7. Edge Considerations

- **Mobile Responsiveness**: complex demo tabs must stack or simplify on mobile.
- **Performance**: High Lighthouse score required (static generation preferred).
- **Privacy Trust**: Avoid over-specific privacy promises on landing; include a short reassurance + link to `/privacy` near CTAs.

## 8. Desktop Wireframe (ASCII)

```text
+---------------------------------------------------------------+
|  PeerLens                                     [ Sign In ]     |
+---------------------------------------------------------------+
|                                                               |
|           Review-criteria-aligned feedback for                |
|               your grant writing.                             |
|                                                               |
|               [ Check My Draft Now ]                          |
|                                                               |
|      Supported calls: NWO Veni · ERC Starting · MSCA PF        |
|                                                               |
+---------------------------------------------------------------+
|  [ SUPPORTED CALLS (TEXT): NWO Veni ... ERC Starting ... ]     |
+---------------------------------------------------------------+
|                                                               |
|  Problem: "Reviewer #2" is arbitrary.                         |
|  Solution: Pre-validate against review criteria.              |
|                                                               |
+---------------------------------------------------------------+
|  [ Demo Tabs: NWO Veni | ERC Starting | MSCA PF ]             |
|                                                               |
|  +-------------------------------------------------------+    |
|  |  Snippet: "The methodology utilizes..."               |    |
|  |                                                       |    |
|  |  [!] Criterion: Implementation (Weight 20%)           |    |
|  |      "Too vague on risk management."                  |    |
|  |      -> Suggested fix: Add mitigation table.          |    |
|  |                                                       |    |
|  |  Readiness Score: [====== 65/100 ]                    |    |
|  +-------------------------------------------------------+    |
|                                                               |
+---------------------------------------------------------------+
|  Benefits:                                                    |
|  [ Icon ] Readiness Score   [ Icon ] Compliance Check         |
|  [ Icon ] Time Saved                                          |
+---------------------------------------------------------------+
|  How It Works:                                                |
|  1. Sign in                                                   |
|  2. Select call/section + paste snippet                        |
|  3. Get review                                                |
+---------------------------------------------------------------+
|  FAQ:                                                         |
|  + Is this generic AI? (No, grounded in review criteria)      |
|  + How is my data handled? (See Privacy)                      |
+---------------------------------------------------------------+
|            [ Check My Draft Now ]                             |
+---------------------------------------------------------------+
|  PeerLens 2026 | Privacy                                      |
+---------------------------------------------------------------+
```

## Changelog

- v0.1 (2026-02-14): Initial spec from brainstorm (WF-0009).
- v0.2 (2026-02-14): Applied review edits (removed "rubric").
- v0.3 (2026-02-14): Remove “Watch Demo”, text-only social proof, footer privacy-only, and soften landing-page privacy claims (link to `/privacy`).
- v0.4 (2026-02-14): Lock static demo content for NWO Veni / ERC Starting / MSCA PF (micro-rewrite examples + example readiness scores).
- v0.5 (2026-02-14): Rewrite demo snippets/cards to be more grant-proposal-realistic (kept structure and locked requirements).
