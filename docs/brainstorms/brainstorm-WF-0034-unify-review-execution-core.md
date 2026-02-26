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

**Section 3 summary (decisions):**
- Primary actor: backend engineers maintaining review execution.
- Secondary actor: frontend engineers relying on stable contracts/error semantics.
- Frontend constraint: no contract changes (including error-code semantics).
- Backend constraint: a single shared place for policy/validation/timeouts to avoid drift.
- Ops constraint: standardize telemetry hooks in a no-behavior-change way (can start as no-op).

**Brainstorming Q&A:**

**Q1: Who is the primary “user” of this workflow output (the refactor) day-to-day?**
- A) Backend engineers working on review execution/features/bugfixes.
- B) Frontend engineers integrating submission flows.
- C) SRE/ops monitoring reliability.
> Recommendation: A — This WF is primarily about reducing backend maintenance cost and drift risk; frontend/ops benefits are downstream.
> **Selected: A**

**Q2: Who is the secondary actor we should optimize for (explicitly, but not primary)?**
- A) Frontend engineers (predictable errors/contracts).
- B) SRE/ops (telemetry + incident response).
- C) End users (perceived latency and clarity).
> Recommendation: A — The main risk of a refactor is contract drift; making frontend expectations explicit helps prevent accidental behavior changes.
> **Selected: A**

**Q3: What is the strongest constraint from the frontend actor perspective?**
- A) No contract changes (same endpoints, same error codes/semantics).
- B) Faster responses / fewer timeouts.
- C) More detailed structured response shapes.
> Recommendation: A — Contract stability is a hard gate for safe incremental refactors. B/C are valuable but belong in later behavior-changing WFs.
> **Selected: A**

**Q4: What is the strongest constraint from the backend actor perspective?**
- A) One place to implement/verify policy + validation + retries/timeouts to avoid drift.
- B) Maximum flexibility to experiment with new LLM prompting strategies.
- C) Simplify DB writes even if behavior changes slightly.
> Recommendation: A — This directly targets the drift problem and produces the most leverage for future work.
> **Selected: A**

**Q5: What is the strongest constraint from the ops actor perspective (if any)?**
- A) Add/standardize telemetry hooks without changing behavior (can be no-op initially).
- B) Introduce retries/backoff globally even if it changes latency.
- C) Defer ops concerns entirely to a future WF.
> Recommendation: A — Establishing standardized hooks now creates a seam for later improvements without forcing behavior changes.
> **Selected: A**

## 4. Rough Idea (Unstructured Thinking)

**Section 4 summary (decisions):**
- Extract a new shared internal module (e.g., `backend/app/services/review_execution_core.py`) used by both services.
- Define a shared-core internal input contract at the “node execution” level (call/stage/node_logical_id/text + lookup context), not endpoint DTOs.
- Shared-core responsibility (first cut): prechecks + policy selection/injection + prompt build + LLM call + parse + validation + policy post-checks; return normalized result; avoid direct DB writes.
- Keep endpoint/service-specific persistence separate (snippet vs structured payload, NOT_ASSESSABLE cards, review_type differences).
- Refactor sequence: helper extraction + parity tests first, then consolidate orchestration into shared-core; flip one endpoint at a time.

**Brainstorming Q&A:**

**Q1: Where should the shared internal execution pipeline live?**
- A) New internal module, e.g. `backend/app/services/review_execution_core.py`, imported by both `reviewer_service.py` and `structured_reviewer_service.py`.
- B) Keep it inside `reviewer_service.py` and import from structured.
- C) Put it in `backend/main.py` next to the routes.
> Recommendation: A — A dedicated module creates a clean “shared core” seam without making either service the de facto owner, and keeps route handlers thin.
> **Selected: A**

**Q2: What is the shared-core input contract (internal), at the right abstraction level?**
- A) `call_id`, `review_stage`, `node_logical_id`, `node_text`, plus context needed for policy + expectations lookup.
- B) Pass full endpoint DTOs into the core and branch.
- C) Pass raw DB models only (node/expectations already fetched).
> Recommendation: A — It’s stable across endpoints and avoids coupling core logic to external DTOs, while still being concrete enough to be testable and deterministic.
> **Selected: A**

**Q3: What should the shared-core be responsible for (first cut)?**
- A) Deterministic prechecks + policy rule selection + prompt build + LLM call + parse + validation + policy post-checks; return normalized result (no direct DB writes).
- B) Everything including DB writes (create review, cards, snippets).
- C) Only LLM call + parsing; leave validation/policy to callers.
> Recommendation: A — This captures the drift-prone “execution pipeline” while keeping DB side effects endpoint-owned, preserving no-behavior-change constraints.
> **Selected: A**

**Q4: How should endpoint-specific persistence stay separate?**
- A) Each endpoint/service remains responsible for DB writes (snippet vs structured payload, NOT_ASSESSABLE cards, review_type, etc.), using the shared-core result.
- B) Core writes everything; endpoints just adapt DTOs.
- C) Create a third “persistence service” that both call.
> Recommendation: A — It keeps the shared-core purely “execution” and avoids entangling storage semantics that differ across endpoints.
> **Selected: A**

**Q5: What is the “no behavior change” refactor sequence (high level)?**
- A) First extract helpers behind the same public service methods (no signature changes), add parity tests, then consolidate orchestration into shared-core, then flip structured, then flip single.
- B) Immediately rewrite both services around the new core.
- C) Only refactor one endpoint; leave the other duplicated.
> Recommendation: A — It’s the safest incremental route: you establish tests, then move logic behind a seam, then flip one endpoint at a time.
> **Selected: A**

## 5. Constraints

(Pending — to be filled via interactive Q&A.)

## 6. Risks / Unknowns

(Pending — to be filled via interactive Q&A.)

## 7. MVP Definition

(Pending — to be filled via interactive Q&A.)

## 8. Explicit Non-Goals

(Pending — to be filled via interactive Q&A.)
