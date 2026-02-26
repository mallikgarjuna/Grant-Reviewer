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

**Section 1 summary (decisions):**
- Scope the problem as drift/duplication between the two create endpoints (not new features).
- Primary pain: engineering maintenance + duplicated bugfixes.
- Key failure mode: behavior drift (one endpoint gets fixes, the other lags).
- Timing: do it now to prevent future divergence.
- Strict “no behavior change first” for safety and reviewability.

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

**Section 2 summary (decisions):**
- Create a shared internal execution pipeline that returns a normalized “execution result”; endpoints adapt to their own DTOs/persistence semantics.
- Share policy injection + policy post-checks + response validation first (highest ROI, lowest behavior risk).
- Migrate incrementally, flipping one endpoint at a time with parity checks.
- Define success as golden parity across API semantics, idempotency, and persistence side effects.
- Use both endpoint-level API tests and service-level shared-core tests with deterministic LLM stubs/fixtures.

**Brainstorming Q&A:**

**Q1: What is the shared “execution core” output we want to converge on (internally), while keeping external contracts separate?**
- A) A shared internal pipeline function that returns a normalized “review execution result” (status, cards, summary, logs/telemetry hooks), and each endpoint adapts it to its DTO/persistence needs.
- B) A shared service class that both endpoints call directly, with branching inside for single vs multi.
- C) Share only helpers (prompt/policy/validation) and keep orchestration separate.
> Recommendation: A — It maximizes shared behavior while preserving endpoint-specific contracts and persistence semantics. B risks a “god service” with branching and ambiguous ownership. C is too shallow and doesn’t prevent orchestration drift.
> **Selected: A**

**Q2: Which concerns must be shared first (highest ROI, lowest behavior risk)?**
- A) Policy injection + post-checks + response validation (schema/expectations).
- B) LLM call wrapper (timeouts/retries) + parsing + error mapping.
- C) Telemetry + tracing + structured logs.
> Recommendation: A — These are the most likely to drift and the easiest to make deterministic/parity-safe. B/C are valuable but can change behavior/observability expectations if introduced prematurely.
> **Selected: A**

**Q3: What is the migration strategy for WF-0034?**
- A) Incremental refactor: introduce shared pipeline behind an internal switch; keep behavior identical; flip one endpoint at a time; compare outputs in tests.
- B) Big-bang: refactor both endpoints to the new core in one PR.
- C) Only refactor structured endpoint first; leave `/reviews` untouched.
> Recommendation: A — Incremental flips reduce blast radius and make regressions attributable. Big-bang increases review and rollback risk. C leaves half the drift risk in place.
> **Selected: A**

**Q4: What is the success definition for “no behavior change first”?**
- A) Golden-contract parity tests: same API status codes/errors, same idempotency semantics, same persistence side effects, same card counts/fields for both endpoints.
- B) Only API shape parity; persistence/logging may change.
- C) Only “end user experience” parity; backend internals can change.
> Recommendation: A — This is the tightest safety rail: it explicitly constrains the refactor to internal structure while guarding against subtle regressions.
> **Selected: A**

**Q5: What testing seam do we rely on to prevent regressions across both endpoints?**
- A) Keep endpoint-level API tests + add service-level tests around the shared core using a stub LLM client and deterministic fixtures.
- B) Only API tests (end-to-end) are enough.
- C) Only service-level tests; reduce API test coverage.
> Recommendation: A — API tests protect external contracts; shared-core tests protect internal equivalence and allow faster iteration without full-stack setup.
> **Selected: A**

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
