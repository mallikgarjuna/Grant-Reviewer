# Phase 0.1 — Interactive Brainstorm (Iterative + Context-Aware)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-0-1-brainstorm.md.
Do NOT modify this file during execution.

---

## Purpose

Run a structured, interactive brainstorming session.

This phase:

- Is iterative (can be invoked multiple times).
- Must consider:
  - Current project status
  - Previous brainstorming content (if any)
- Must provide structured decision options.
- Must provide recommendations.
- Must require explicit user selection.
- Must update brainstorm file incrementally.

This is NOT auto-generation.

---

## Preflight Checklist (Steps 1–3)

Before running the section-by-section brainstorm flow, do this short preflight to ensure you and the user share the same reality and vocabulary.

### Step 1 — Long-Form Problem Intake (User Narrative)

Ask the user for a long, detailed description (free-form) covering:

- The problem/pain and who experiences it
- Concrete examples (inputs/outputs, current vs desired behavior)
- Constraints (time, UX, data, compliance), non-goals
- Any solution ideas they’re considering (including “maybe universalize it”)

Do not “solve” anything yet. Treat this as raw material you will tighten during the interview.

### Step 2 — Repo Reality Snapshot (Timeboxed, Read-Only, Non-Architectural)

Purpose: lightly ground the brainstorm in the current repo state so you can:

- Verify any critical assertions the user made (“we already have X”, “this is hardcoded”, “we have only one example”, etc.)
- Avoid premature universalization when there aren’t enough real exemplars
- Ask sharper questions and steer toward an MVP that is least likely to overfit

Rules:

- Timebox: 5–10 minutes.
- Read-only: do not edit files.
- Non-architectural: do not propose modules, data models, or implementation plans here.
- Output: a 5-bullet “repo snapshot” summary + 3–5 key open questions this snapshot suggests.

Suggested inputs to scan (pick only what’s relevant):

- `docs/index.md` (active initiatives + related artifacts)
- `docs/workflow/README.md` (phase meanings / constraints)
- Any existing PRDs/tasks/brainstorms that look adjacent
- A quick `rg` over likely terms to find existing seams and hardcoded paths

Optional (recommended): append a short section to the brainstorm artifact:

- `## Repo Reality Snapshot (Read-Only)` with date + 5 bullets

### Step 3 — Relentless Interview to Shared Understanding

Now run the structured brainstorm sections below.

Goal: walk down the decision tree one dependency at a time until you can state the MVP, its boundaries, and its highest-risk unknowns without ambiguity.

---

## Required Inputs

- docs/brainstorms/brainstorm-WF-XXXX-<slug>.md
- docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md
- docs/templates/brainstorm-template.md
- docs/index.md (to understand project phase)
- Any relevant previous WF artifacts (if related)

---

## Phase Gate — Commit Previous Phase

Before running Phase 0.1, ensure Phase 0.0 outputs are **saved and committed** on the WF branch:

- Baseline WF artifacts exist (brainstorm/prd/task/walkthrough placeholders).
- `docs/index.md` has the WF row.

---

## Phase Completion — Commit This Phase

After completing a Phase 0.1 brainstorm session:

- Ensure your brainstorm artifact edits are **saved and committed** before moving to Phase 1.

---

## Core Facilitation Rules

0. Run the **Preflight Checklist (Steps 1–3)** above before Section 1.
1. Work section-by-section.
2. Ask **exactly 5** important questions per section (unless fewer are genuinely needed).
3. Ask questions **in a single batch** (5 at a time), not one-by-one.
4. For each question:
   - Provide 2–3 structured options.
   - Provide one recommended option (clearly labeled).
5. Require explicit user selection or custom answer **for each question in the batch**.
   - Preferred answer format: `Q1:A, Q2:C, Q3:custom..., Q4:B, Q5:A`
   - When presenting an interactive batch, end your message with a single copy-pasteable line listing the recommended selections in that same format (e.g., `Recommended: Q1:A, Q2:B, Q3:A, Q4:C, Q5:A`).
6. Challenge vague answers.
7. Avoid implementation details.
8. Avoid architecture design.
9. After each section:
   - Summarize decisions clearly as a bulleted list (not a paragraph).
   - Record the explicit Q&A block in the Brainstorm Q&A artifact (`docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md`).
   - In the main brainstorm, add a single link line: `Full Q&A transcript: <path> (Section N)`.
   - Treat the **main brainstorm as SSOT for contracts/decisions**; the Q&A transcript is rationale only.
     - If a Q&A block reveals a new contract or contradicts the brainstorm summary, promote the contract into the brainstorm and log it (do not let “truth” live only in Q&A).
   - For each major decision summarized in the brainstorm, add 1–3 “Contract Notes / Non-obvious constraints” bullets (with a link to the relevant Q&A section header).
   - Maintain an explicit “Open Questions / Deferred” list in the brainstorm so deferred items aren’t lost.
   - The Q&A block **must** include:
     - The **full question text** (not just a label).
     - **All options** (A, B, C, etc.) with their descriptions.
     - The **model's recommendation** with reasoning: why the recommended option is preferred **and** why the alternatives are dismissed.
     - The **user's selected answer** (or custom answer).
   - This preserves the full reasoning chain for traceability and future reference.
   - Example format:
     ```
     **Brainstorming Q&A:**

     **Q1: What is the primary gap this endpoint fills?**
     - A) Option A description.
     - B) Option B description.
     - C) Option C description.
      > Recommendation: A — Rationale for why A is preferred. B is dismissed because… C is partially true but…
      > **Selected: A**
     ```
   - Update brainstorm file.
   - Update Brainstorm Q&A file.
10. Do NOT overwrite previous brainstorm content.
   - Append refinements or clarifications.
11. Keep all thinking aligned with MVP.

---

## Iterative Session Behavior

If brainstorm file already contains content:

- First summarize existing understanding.
- Identify gaps or weak areas.
- Ask targeted refinement questions.
- Do NOT restart from scratch.

Brainstorm sessions can be run multiple times until clarity is achieved.

---

## Structured Brainstorm Flow

Proceed in this order:

---

### Section 1 — Problem Statement

Ask up to 5 key questions.

For each question:

Example format:

Q1: Who primarily experiences this problem?

Option A: All users
Option B: New users only
Option C: Power users

Recommendation: Option B (more focused, clearer MVP)

Ask all 5 questions in one batch and wait for answers to all 5 before continuing.

After final answer:
Summarize final Problem Definition.
Update brainstorm file.

---

### Section 2 — Desired Outcome

Ask:

- What measurable change defines success?
- What behavior change do we expect?
- What would make this “good enough” for MVP?

Provide structured options + recommendation for each.

Ask 5 questions in one batch and wait for answers to all 5.
Summarize.
Update file.

---

### Section 3 — Target User / Actor

Ask:

- Is this for:
  - A) All users
  - B) A specific segment
  - C) Internal admin only

Provide recommendation.

Continue with up to 4 more key clarifying questions.

Summarize.
Update file.

---

### Section 4 — Rough Idea Exploration

Ask:

- What is the simplest implementation direction?

Provide 2–3 variants.
Label tradeoffs.
Provide recommended direction.

Challenge over-complex ideas.

Summarize.
Update file.

---

### Section 5 — Constraints

Ask:

- Time constraint?
- Technical constraint?
- External dependencies?

Provide options + recommendation.
Summarize.
Update file.

---

### Section 6 — Risks / Unknowns

Ask:

- What assumption is most fragile?
- What must be validated early?
- What could cause rework?

Provide structured options + recommendation.

Summarize.
Update file.

---

### Section 7 — MVP Definition

Force clarity:

Ask:

- If limited to 3 days, what must exist?
- What can explicitly wait?
- What must NOT be included?

Provide options + recommendation.

Tighten scope aggressively.

Summarize.
Update file.

---

### Section 8 — Explicit Non-Goals

Ask:

- What tempting feature must be postponed?
- What belongs to a future WF?

Summarize.
Update file.

---

## Completion Criteria

Brainstorm phase is complete when:

- Problem is precise.
- Target user is defined.
- MVP scope is tight.
- Non-goals are explicit.
- No architecture decisions were made.
- No API design exists.

Set:

Status: Draft Complete

Wait for user signal before Phase 1.

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-0-1-brainstorm.md
- @docs/brainstorms/brainstorm-WF-XXXX-<slug>.md
- @docs/templates/brainstorm-template.md
- @docs/index.md

Instruction:

"Run an interactive, context-aware brainstorming session.
Provide 2–3 options per question.
Label one recommended option.
Wait for my selection before proceeding.
Update the brainstorm file incrementally."

---

## Stop Condition

Stop when I say the brainstorm is “good enough” for PRD generation (or if I explicitly pause the workflow).

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 1.1 (generate PRD v0.1): `@docs/workflow/phase-1-1-prd-generate.md`
   - **Provide an explicit, copy-pasteable prompt block** for the user to start this phase.
2. Continue Phase 0.1 brainstorming to resolve remaining unknowns (update the brainstorm file; do not generate a PRD yet).
