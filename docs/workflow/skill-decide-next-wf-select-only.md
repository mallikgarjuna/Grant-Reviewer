# SKILL: Decide Next WF (FAST — Selection Only)

Purpose:
Select the next highest-leverage Workflow (WF) to accelerate
PeerLens toward a fast, production-ready MVP.

GOAL:
Use Tim Ferriss DiSSS framework to propose the next best course of action for this project.

This skill ONLY decides:
What to do next.

It does NOT:

- Design tasks
- Plan phases
- Suggest implementation details
- Expand into WF artifacts

After selection, initiate the standard 4-phase WF process separately.

---

## Optimization Target

Maximize:

- End-to-end MVP usability (frontend + backend + DB + production)
- Shipping velocity
- Risk reduction that prevents rework
- Trust and defensibility where MVP-critical

Avoid:

- Premature generalization
- Multi-agency abstractions
- Large refactors
- Cosmetic-only improvements

---

## Mandatory Grounding (SSOT)

Before running DiSS, read:

1. AGENTS.md
2. docs/index.md
3. docs/reference/code_phrases.md
4. docs/guides/workflow-system.md
5. docs/guides/engineering-standards.md
6. docs/guides/knowledge-base.md
7. docs/parking_lot.md
8. backend/app/schemas/call_definitions_v2.py

Do not assume repo state.
Ask for snippets if unclear.

---

# DiSS (FAST — Strategic)

## 1) Deconstruction (Max 10)

List up to 10 concrete, ship-impacting system components across:

- User journey gaps
- Backend reliability risks
- Production readiness gaps
- Trust/defensibility risks
- Admin/YAML ingestion friction
- Technical debt that blocks shipping

Each must be specific and testable.
No vague items like “improve architecture.”

---

## 2) Selection (Top 3)

From the list:

Select the top 3 highest-leverage next moves.

Score each quickly (0–2 each):

- Removes shipping blocker
- Improves end-to-end usability
- Reduces production risk
- Prevents likely rework
- Scope contained (WF-sized)

Total /10.

Provide:

- Candidate
- Score
- 1–2 sentence justification

---

## 3) Sequencing (Strategic Order Only)

Propose the logical execution order of the top 3.

Explain briefly:
Why #1 must precede #2 and #3.

Do NOT design tasks.
Do NOT outline phases.
Do NOT propose file changes.

End with:

**Recommended Next WF:**
<Clear one-sentence objective>

---

# Sanity Filter (Must Pass ≥3)

Before finalizing #1, confirm YES to at least 3:

- Improves the MVP happy path
- Reduces production instability risk
- Reduces false-confidence or trust risk
- Prevents architectural backtracking
- Has clear boundaries

If fewer than 3 YES → wrong WF.

---

# Output Format (Strict)

A) Status Snapshot (3–5 bullets grounded in SSOT)
B) Deconstruction (max 10)
C) Top 3 + score + justification
D) Strategic order
E) Recommended Next WF (one sentence)

No tasks.
No implementation.
No scope expansion.
END.
