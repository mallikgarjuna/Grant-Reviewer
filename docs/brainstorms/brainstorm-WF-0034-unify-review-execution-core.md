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

**Section 5 summary (decisions):**
- Hard boundary: strict “no behavior change” across HTTP semantics, idempotency, and persistence.
- Endpoint-specific must remain: DTOs + idempotency semantics + persistence differences.
- Retries/timeouts: preserve current behavior first; introduce a seam for later standardization.
- Telemetry: add standardized hooks in a non-invasive way (can be no-op initially).
- Test mode constraint: keep `LLM_MODE=stub` behavior identical; ensure coverage for both endpoints in stub.

**Brainstorming Q&A:**

**Q1: What is the hard “no behavior change” boundary for WF-0034?**
- A) Strict: identical status codes + error codes/messages, idempotency behavior, DB side effects, and card persistence rules.
- B) Contracts identical, but internal retry/timeout behavior may change.
- C) User-visible behavior only; backend internals can change.
> Recommendation: A — This is a refactor WF; strict parity is the safest guardrail and keeps review scope narrow.
> **Selected: A**

**Q2: What must remain endpoint-specific (explicitly) even after shared-core extraction?**
- A) Request/response DTOs + idempotency semantics + persistence differences (snippet vs structured payload, NOT_ASSESSABLE handling).
- B) Only DTOs; everything else can be shared.
- C) Keep persistence shared; DTOs + validation stay endpoint-specific.
> Recommendation: A — DTOs and persistence semantics differ materially today; forcing them into shared code early increases regression risk.
> **Selected: A**

**Q3: How should retries/timeouts be handled in the shared-core (initially)?**
- A) Preserve existing timeout behavior; add a shared wrapper seam but default to current values/behavior.
- B) Introduce a standardized retry policy now.
- C) Remove timeouts from services and let infra handle it.
> Recommendation: A — Changing retries/timeouts changes behavior (latency/error patterns). Create a seam first; standardize later.
> **Selected: A**

**Q4: Telemetry constraint (initially)?**
- A) Add standardized hooks (structured logs/metrics/tracing) but keep them no-op or non-invasive to avoid behavior change.
- B) Implement full telemetry stack changes in this WF.
- C) Defer telemetry entirely.
> Recommendation: A — Add the seam now with low risk; full telemetry adoption can be a separate WF if needed.
> **Selected: A**

**Q5: Any constraints around LLM-mode and test mode?**
- A) Must keep `LLM_MODE=stub` behavior identical and ensure tests cover both endpoints under stub.
- B) It’s okay if stub behavior changes as long as prod works.
- C) Remove stub mode and rely on recorded cassettes.
> Recommendation: A — Stub mode is a core regression safety net; refactors should not break deterministic test execution.
> **Selected: A**

## 6. Risks / Unknowns

User instruction for remaining sections (2026-02-26): default to the recommended option unless overridden.

**Section 6 summary (decisions):**
- Biggest risk is accidental behavior change (error mapping, persistence ordering, idempotency edge cases).
- Second risk is creating a shared-core abstraction that’s either too shallow (doesn’t prevent drift) or too deep (couples endpoint-specific semantics).
- Validation/policy seams must be deterministic and testable; avoid “hidden” exceptions that differ by endpoint.
- Telemetry and retry seams should not change execution timing or failure modes in the initial refactor.
- Regression prevention depends on strong parity tests and controlled rollout (one endpoint at a time).

**Brainstorming Q&A:**

**Q1: What is the most fragile assumption in this refactor?**
- A) We can extract shared execution without changing any externally observable behavior (including persistence side effects). (Recommended)
- B) The main risk is only code organization; behavior won’t change if tests pass.
- C) Small behavior changes are acceptable as long as response models don’t change.
> Recommendation: A — The refactor crosses execution, validation, and persistence boundaries; subtle changes are easy to introduce without strict parity framing.
> **Selected: A**

**Q2: Where are we most likely to introduce accidental divergence?**
- A) Error mapping + exception handling + edge-case validation ordering. (Recommended)
- B) Prompt text formatting changes.
- C) Logging/telemetry fields.
> Recommendation: A — Error semantics are highly sensitive; reordering checks or changing exception types can change API behavior.
> **Selected: A**

**Q3: What is the biggest abstraction risk for the shared core?**
- A) Core becomes too coupled to endpoint-specific persistence/DTOs, making future changes harder. (Recommended)
- B) Core is too generic and requires lots of boilerplate adapters.
- C) Core doesn’t share enough, so drift continues.
> Recommendation: A — Coupling is the hardest to unwind; we can mitigate B/C with careful boundaries, but coupling can silently creep in.
> **Selected: A**

**Q4: What is the highest-risk integration seam?**
- A) The boundary between “execution result” (parsed/validated findings) and endpoint-specific persistence (review/cards/snippet/structured payload). (Recommended)
- B) The LLM client wrapper.
- C) The prompt builder.
> Recommendation: A — This is where side effects happen; mistakes here are hardest to detect without parity tests.
> **Selected: A**

**Q5: What is the primary mitigation strategy for these risks?**
- A) Add/strengthen parity tests first, then extract core incrementally and flip endpoints one at a time. (Recommended)
- B) Rely on manual testing in the UI.
- C) Refactor quickly, then fix bugs as they appear.
> Recommendation: A — It’s the only approach aligned with “no behavior change first” and reduces blast radius.
> **Selected: A**

## 7. MVP Definition

**Section 7 summary (decisions):**
- MVP is a refactor slice: establish parity tests + introduce shared-core module + migrate orchestration incrementally.
- Shared-core MVP includes: policy injection, LLM call wrapper seam, response parsing/validation, policy post-checks, normalized result object.
- Endpoint-specific MVP includes: preserve DTOs, idempotency semantics, and persistence differences; no endpoint removal.
- Rollout MVP: flip one endpoint at a time with test coverage and clear rollback (revert switch).
- “Good enough” for Phase 0: a concrete, testable boundary and a stepwise migration plan with explicit non-goals.

**Brainstorming Q&A:**

**Q1: If we had to ship in 2–3 days, what must exist?**
- A) Shared-core module + parity tests + one endpoint migrated with no behavior change. (Recommended)
- B) Both endpoints fully migrated + new telemetry and retries.
- C) Just code movement; tests later.
> Recommendation: A — It’s the smallest functional slice that proves the approach while minimizing regression risk.
> **Selected: A**

**Q2: What is the smallest “shared core” slice that delivers value?**
- A) Policy selection/injection + parsing/validation + policy post-checks unified behind a single internal pipeline. (Recommended)
- B) Only unify the LLM client wrapper.
- C) Only unify prompt construction.
> Recommendation: A — This is where drift is most harmful and frequent; unifying only LLM/prompt is less protective.
> **Selected: A**

**Q3: What is explicitly excluded from MVP even if tempting?**
- A) Changing contracts/DTOs, altering retries/timeouts behavior, or changing LLM prompting strategies. (Recommended)
- B) Keeping the legacy endpoint around.
- C) Writing new features on top of the refactor.
> Recommendation: A — These are behavior changes that should be isolated into follow-on WFs.
> **Selected: A**

**Q4: What is the MVP testing bar?**
- A) Keep existing endpoint API tests + add shared-core unit/service tests with stub LLM; add at least one parity-focused test per endpoint. (Recommended)
- B) Manual testing only.
- C) Only shared-core unit tests.
> Recommendation: A — Covers both contract-level and internal-level regression surfaces.
> **Selected: A**

**Q5: What is the MVP migration sequencing?**
- A) Add parity tests → introduce shared-core behind existing service APIs → migrate structured first → migrate single-node next. (Recommended)
- B) Migrate single-node first.
- C) Migrate both simultaneously.
> Recommendation: A — Structured has more complexity and drift risk; migrating it first forces the shared core to handle the harder path.
> **Selected: A**

## 8. Explicit Non-Goals

(Pending — to be filled via interactive Q&A.)
