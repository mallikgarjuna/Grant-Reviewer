# WF-0034 — Unify review service execution core

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-02-26

---

## Repo Reality Snapshot (Read-Only) (2026-02-26)

- Both endpoints (`POST /reviews`, `POST /api/structured-review`) are implemented in `backend/main.py`.
- Both endpoints implement similar idempotency-key enforcement and quota gating, then delegate into a service.
- `POST /reviews` uses `ReviewerService.generate_review(...)`; structured uses `StructuredReviewerService.generate_structured_review(...)`.
- Both services build prompts via `build_review_prompt(...)`, call the LLM via `generate_with_timeout(...)`, parse via `parse_llm_response(...)`, and apply reviewer-policy checks.
- There are API tests in `backend/tests/test_api.py` covering both endpoints (including signed-header helpers and structured-review coverage).

Key questions this snapshot suggests:
- What is the “shared core” contract (input/output) that’s stable across single-node and multi-node flows?
- Where should shared concerns live (policy injection, retries/timeouts, validation, telemetry) without coupling endpoint DTOs?
- What are the “must-not-change” behaviors (error codes, idempotency semantics, persistence side effects) for each endpoint?
- What testing seams/golden tests do we need before refactoring to prevent drift/regressions?

---

## 1. Problem Statement

We currently maintain two synchronous “create review” execution paths:

- `POST /reviews` (single-node)
- `POST /api/structured-review` (multi-node)

They share many concerns (policy injection, LLM call, response validation, post-checks) but are implemented separately, increasing drift risk and duplicating fixes.

**Brainstorming Q&A:**

**Q1: What’s the primary problem we’re solving with this WF?**
- A) Reduce duplication/drift between `/reviews` and `/api/structured-review` while keeping both stable.
- B) Reduce latency/cost of LLM calls.
- C) Enable new features (async/polling, richer outputs).
> Recommendation: A — The WF goal is internal consolidation without changing external contracts. B/C may be future wins, but bundling them now increases behavior-change and scope risk.
> **Selected: A**

**Q2: Who primarily feels the pain today?**
- A) Backend engineers maintaining/fixing review execution code.
- B) End users seeing inconsistent errors/behavior.
- C) Both equally.
> Recommendation: A — The immediate pain is duplicated code paths and higher maintenance overhead. User-facing improvements should be downstream of eliminating drift.
> **Selected: A**

**Q3: What’s the clearest “bad outcome” we want to prevent?**
- A) A fix/policy/validation change lands in one endpoint but not the other (behavior drift).
- B) The system can’t scale to more calls/nodes.
- C) The database model becomes too complex.
> Recommendation: A — Drift is the direct cost of duplication and the most likely near-term failure mode while both endpoints evolve.
> **Selected: A**

**Q4: Why do this now (2026-02-26) instead of later?**
- A) Both endpoints are active; divergence risk increases with every change—refactor before more feature work.
- B) Wait until we do async structured reviews.
- C) Wait until universal form work stabilizes.
> Recommendation: A — Shared-core extraction is easiest before additional features amplify differences and make refactors riskier.
> **Selected: A**

**Q5: How strict is “no behavior change first”?**
- A) Strict parity: same HTTP semantics, error codes, idempotency behavior, and persistence side effects; only internal refactor.
- B) Contracts stay the same, but allow minor timeout/retry/telemetry behavior shifts.
- C) Allow output/error changes if they’re improvements.
> Recommendation: A — Locking parity reduces migration risk and makes refactoring reviewable with high confidence; any behavior change can be an explicit follow-on.
> **Selected: A**

## 2. Desired Outcome

(Pending — to be filled via interactive Q&A.)

## 3. Target User / Actor

(Pending — to be filled via interactive Q&A.)

## 4. Rough Idea (Unstructured Thinking)

(Pending — to be filled via interactive Q&A.)

## 5. Constraints

(Pending — to be filled via interactive Q&A.)

## 6. Risks / Unknowns

(Pending — to be filled via interactive Q&A.)

## 7. MVP Definition

(Pending — to be filled via interactive Q&A.)

## 8. Explicit Non-Goals

(Pending — to be filled via interactive Q&A.)
