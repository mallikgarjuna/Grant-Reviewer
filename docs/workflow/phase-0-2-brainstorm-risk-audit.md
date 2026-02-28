# Phase 0.2 — Brainstorm Risk Audit (Review Gate, No Edits)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-0-2-brainstorm-risk-audit.md.
Do NOT modify any files while executing this phase.

---

## Purpose

Run a critical risk audit of the brainstorm artifact produced in Phase 0.1.

Mindset shift:
- Take off the “obedient agent” hat.
- Put on a Senior Principal Software Architect/Engineer hat.
- Assume the brainstorm will be used to generate a PRD and tasks; your job is to prevent avoidable rework.

---

## Inputs Required

- The brainstorm artifact path (e.g., `docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`)
- The brainstorm Q&A transcript path (e.g., `docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md`)
- `docs/index.md` (to confirm WF/slug/phase)

## Phase Gate & Completion

- **START**: Ensure the brainstorm being audited is **saved and committed** so findings map to a stable artifact version.
- **FINISH**: This is a no-edit review phase; if no files changed, there is nothing to commit for this phase.

---

## Rules (Strict)

1. **No edits**: Do not modify any files in this part.
2. **Be adversarial**: Treat ambiguity as a defect.
3. **Preserve scope**: Do not propose new initiatives; only tighten *this* brainstorm.
4. **Output must be actionable**: each finding includes an exact suggested edit to the brainstorm.
5. **Classify findings**: Blocking vs Non-blocking.
6. If blocking issues exist:
   - Ask the user up to 5 clarification questions.
   - Each question must include 2–3 options + one recommended option.
   - Wait for answers before Part C.

---

## Audit Checklist (Use as headings)

### 1) Scope + Problem Clarity
- Is the problem statement precise and falsifiable?
- Are “shared vs endpoint-specific” boundaries explicit?
- Are non-goals explicit enough to prevent scope creep?

### 2) Contract Safety
- Are external API contracts explicitly preserved (DTOs, error codes/semantics)?
- Are idempotency semantics called out per endpoint (including payload-hash mismatch behavior)?
- Are persistence side effects explicitly constrained?
- Is it unambiguous that the **brainstorm is SSOT for contracts**, and the Q&A transcript is **rationale only**?
- Are any contracts/requirements present only in Q&A (split-brain risk)?
- Is there an explicit “Open Questions / Deferred” list so the brainstorm doesn’t imply false completeness?

### 3) Shared-Core Boundary Quality
- Is the proposed shared-core *deep enough* to prevent drift?
- Is it *not too deep* (i.e., it doesn’t force shared persistence/DTO semantics)?
- Does it name the shared concerns clearly (policy injection, LLM call seam, validation, post-checks, telemetry, retries/timeouts seam)?

### 4) Migration Strategy Soundness
- Is migration incremental and reversible?
- Is “no behavior change first” enforceable with tests?
- Does it specify endpoint flip order and parity verification?

### 5) Testing Seams + Regression Prevention
- Are there explicit seams (shared-core service tests + endpoint API tests)?
- Are parity assertions defined (what must match)?
- Are failure modes and edge cases enumerated (timeouts, validation ordering, policy violations)?

---

## Output Format (Required)

Print:

1. `Reviewed artifact: <path> @ <version>`
2. `Reviewed Q&A: <path> @ <version>`
3. **Blocking findings** (if any): list with:
   - Finding
   - Why it matters
   - Exact brainstorm edit to apply (copy-pasteable)
4. **Non-blocking findings** (if any): same format
5. **Clarification Questions** (only if blocking findings exist):
   - Up to 5, each with 2–3 options + recommended option
