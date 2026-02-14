export type LandingDemoTabId = "nwo_veni" | "erc_starting" | "msca_pf";

export type LandingDemoCard = {
  criterion: string;
  finding: string;
  suggestedFix: string;
  microRewriteExample: string;
};

export type LandingDemoTab = {
  id: LandingDemoTabId;
  label: string;
  snippet: string;
  cards: [LandingDemoCard, LandingDemoCard, LandingDemoCard, LandingDemoCard];
  readinessScore: number;
};

export const LANDING_DEMO_TABS: readonly LandingDemoTab[] = [
  {
    id: "nwo_veni",
    label: "NWO Veni",
    snippet:
      "This project tests why early-career researchers (ECRs) struggle to form cross-lab collaborations despite strong incentives to do so. We combine (1) a survey of ECRs across three Dutch universities (target n≈250) to quantify perceived barriers, with (2) 24 semi-structured interviews to explain the highest-impact barriers in depth. We will triangulate findings into a practical collaboration checklist for PIs and research support offices, and validate it via a small pilot workshop. Deliverables include an open interview guide, an anonymized codebook, and a short policy brief.",
    cards: [
      {
        criterion: "Feasibility / Work plan",
        finding:
          "Key activities are listed, but sequencing and decision points are missing.",
        suggestedFix:
          "Add a simple work plan with milestones, dependencies, and a clear done definition per step.",
        microRewriteExample:
          "Months 1–2: finalize instruments + ethics; Months 3–4: launch survey (n≈250) and close at ≥200 responses; Months 5–7: run 24 interviews (8 per site); Months 8–9: dual-code transcripts (κ ≥ 0.7) and resolve disagreements; Months 10–12: synthesize checklist + pilot workshop + brief.",
      },
      {
        criterion: "Methodology",
        finding:
          "The link from data to checklist is implicit, so reviewers cannot judge rigor.",
        suggestedFix:
          "Specify analysis steps and what the checklist contains (structure, criteria, evidence).",
        microRewriteExample:
          "We will run thematic analysis with a pre-registered codebook, then convert the top 6 barriers into checklist items with (a) an early warning indicator, (b) a concrete action, and (c) a short evidence note citing survey + interview support.",
      },
      {
        criterion: "Risk management",
        finding: "Recruitment and response-rate risks are not mitigated.",
        suggestedFix:
          "Add a fallback recruitment plan and a minimum viable sample threshold.",
        microRewriteExample:
          "If survey responses are <150 by week 3, we will add two partner institutions and targeted outreach via graduate schools; interviews proceed once we have ≥18 participants spanning all three sites, with a maximum of 30 to avoid scope creep.",
      },
      {
        criterion: "Impact / Relevance",
        finding:
          "The policy brief deliverable is mentioned, but adoption and success metrics are unclear.",
        suggestedFix:
          "Tie outputs to specific users and define how you will test usefulness.",
        microRewriteExample:
          "Primary users are PIs and research support offices; we will evaluate usefulness via a pilot workshop (n≈20) and a pre/post measure of confidence in collaboration planning, plus qualitative feedback on which checklist items are most actionable.",
      },
    ],
    readinessScore: 64,
  },
  {
    id: "erc_starting",
    label: "ERC Starting",
    snippet:
      "I will develop a high-risk, high-gain framework for learning causal, clinician-auditable representations from multimodal hospital data (images + notes). The core hypothesis is that enforcing explicit, testable links between textual evidence and visual features reduces shortcut learning and improves out-of-distribution reliability. WP1 derives the theory and constraints; WP2 implements the model and evaluation suite; WP3 validates robustness on two independent hospital cohorts with prospectively-defined failure tests (shifted protocols, rare subgroups). Deliverables include open-source code, a reproducible benchmark, and a methods paper.",
    cards: [
      {
        criterion: "Scientific ambition",
        finding:
          "Novelty is implied, but the breakthrough mechanism is not crisply stated.",
        suggestedFix:
          "State what is fundamentally new and the specific limitation it addresses.",
        microRewriteExample:
          "Unlike black-box fusion, we introduce evidence-linked constraints that require the model prediction to be supported by aligned note concepts and image regions, directly targeting known failure modes from spurious correlations in multimodal learning.",
      },
      {
        criterion: "Methodological soundness",
        finding:
          "The evaluation plan lacks hard stress tests and leakage safeguards.",
        suggestedFix:
          "Define split strategy, leakage checks, and failure tests aligned to the hypothesis.",
        microRewriteExample:
          "We will use patient-level temporal holdout and cross-site transfer; we will run leakage audits (near-duplicate images, templated notes) and report calibration + subgroup performance, plus pre-registered shift tests (protocol changes, rare subgroups) to quantify out-of-distribution robustness.",
      },
      {
        criterion: "Feasibility / Resources",
        finding: "Dependencies (data access approvals, compute) are not explicitly managed.",
        suggestedFix:
          "Declare gating dependencies and fallback plans (method + data).",
        microRewriteExample:
          "Data access approvals are completed by Month 2; training uses 4×A100-equivalent for ≤96 hours per experiment; if compute is constrained we use parameter-efficient tuning and precomputed embeddings, and we prioritize WP2 evaluation deliverables to de-risk WP3.",
      },
      {
        criterion: "Impact pathway",
        finding:
          "Impact is described at a high level without a concrete decision context.",
        suggestedFix:
          "Tie to a specific clinical task and measurable decision-relevant endpoints.",
        microRewriteExample:
          "We target triage prioritization for acute findings; success is measured by calibration and recall at fixed precision under distribution shift, plus a small reader study quantifying whether the evidence-linked outputs change clinician confidence and time-to-decision.",
      },
    ],
    readinessScore: 67,
  },
  {
    id: "msca_pf",
    label: "MSCA PF",
    snippet:
      "This MSCA Postdoctoral Fellowship will strengthen my expertise in causal inference and open science while delivering a comparative evaluation of two education policies using linked administrative datasets. At the host institution I will receive structured training in synthetic controls, event studies, and reproducible workflows (pre-registration, versioned pipelines), with a secondment to a policy unit to learn evidence translation. The research will produce two first-author papers and a reusable analysis toolkit. I will communicate results via a stakeholder brief, a public explainer, and open materials (code + documentation) aligned to EU open science practices.",
    cards: [
      {
        criterion: "Training / Skills development",
        finding:
          "Training is credible, but the skills-to-output mapping is not explicit.",
        suggestedFix:
          "Map each skill gap to an activity, a mentor, and a concrete artifact.",
        microRewriteExample:
          "Skill gap: synthetic controls; Activity: host short course (Month 2) + supervised replication (Months 3–4); Mentor: Dr. X; Artifact: preregistered analysis plan + reproducible pipeline template to reuse across WPs.",
      },
      {
        criterion: "Research plan quality",
        finding:
          "The identification strategy is suggested but not testable as written.",
        suggestedFix:
          "State the counterfactual, core assumptions, and diagnostics.",
        microRewriteExample:
          "We estimate the effect of Policy A on dropout rates using staggered adoption; identification assumes parallel pre-trends, tested via event-study diagnostics and placebo policies, with robustness checks using synthetic controls for treated regions.",
      },
      {
        criterion: "Dissemination and communication",
        finding:
          "Dissemination is broad, but not scheduled or audience-specific.",
        suggestedFix:
          "Specify channels, cadence, and outputs per audience.",
        microRewriteExample:
          "Academic: two submissions (Months 12 and 22); Policy: 2-page brief after each WP; Public: one explainer per milestone with a plain-language summary and a short methods appendix.",
      },
      {
        criterion: "Career development",
        finding:
          "The career plan needs concrete independence signals and mentoring cadence.",
        suggestedFix:
          "Add measurable milestones (papers, talks, grant prep) and mentoring structure.",
        microRewriteExample:
          "Independence signals include two first-author papers, one invited seminar, and a maintained toolkit repo; mentoring includes monthly check-ins and a structured grant-writing sprint (Month 18) targeting a follow-on fellowship or starter grant.",
      },
    ],
    readinessScore: 62,
  },
];

export const DEFAULT_LANDING_DEMO_TAB_ID: LandingDemoTabId = "nwo_veni";
