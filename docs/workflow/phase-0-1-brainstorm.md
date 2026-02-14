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

## Required Inputs

- docs/brainstorm/brainstorm-WF-XXXX-<slug>.md
- docs/templates/brainstorm-template.md
- docs/index.md (to understand project phase)
- Any relevant previous WF artifacts (if related)

---

## Core Facilitation Rules

1. Work section-by-section.
2. Ask max 5 important questions per section.
3. For each question:
   - Provide 2–3 structured options.
   - Provide one recommended option (clearly labeled).
4. Require explicit user selection or custom answer.
5. Challenge vague answers.
6. Avoid implementation details.
7. Avoid architecture design.
8. After each section:
   - Summarize decisions clearly.
   - Update brainstorm file.
9. Do NOT overwrite previous brainstorm content.
   - Append refinements or clarifications.
10. Keep all thinking aligned with MVP.

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

Wait for user selection before continuing.

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

Wait for selection.
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
- @docs/brainstorm/brainstorm-WF-XXXX-<slug>.md
- @docs/templates/brainstorm-template.md
- @docs/index.md

Instruction:

"Run an interactive, context-aware brainstorming session.
Provide 2–3 options per question.
Label one recommended option.
Wait for my selection before proceeding.
Update the brainstorm file incrementally."
