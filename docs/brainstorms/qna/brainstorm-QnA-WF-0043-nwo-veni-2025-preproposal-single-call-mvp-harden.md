# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-01

---

## Section 1 — Problem Statement

**Brainstorming Q&A:**

**Q1: Which single flow is *the* hardening target for WF-0043?**
- A) `POST /api/structured-review` (structured multi-node; universal submit path).
- B) `POST /reviews` (legacy single-snippet path).
- C) Both flows (but still single-call: `nwo_veni_2025_preproposal`).
 > Recommendation: A — this is the single-call MVP path introduced/strengthened in WF-0041 and is the highest regression-risk surface (call-driven submit + policy + persistence + idempotency). B is important historically, but hardening it first does not directly protect the new “single-call MVP” surface. C is broader and risks losing atomic scope.
 > **Selected: A**

**Q2: What’s the primary “trust” failure we’re preventing?**
- A) Contract drift: error codes/statuses/idempotency/persistence semantics change.
- B) Reviewer-policy enforcement drift: blocking/post-check/prompt-only behavior changes.
- C) Output quality drift: review cards become less useful (prompt/model issues).
 > Recommendation: A — most falsifiable and launch-critical. We can explicitly cover B as a sub-slice of the contract suite, but “quality drift” is hard to make deterministic without adding brittle golden outputs.
 > **Selected: A**

**Q3: For execution-time failures (timeout, LLM failure, response validation failure, policy blocking), what’s the required contract?**
- A) Persist a Review with `status=FAILED` + stable `overall_summary`; return `200` with `{review_id, status}`.
- B) Return an API error (4xx/5xx) and do not persist a Review.
- C) Persist the Review but still return an API error.
 > Recommendation: A — aligns with current runtime behavior and supports `/app/reviews` rendering (review exists even when execution fails). B/C would change semantics and break the “persistence first, then status update” model.
 > **Selected: A**
 > Clarification (2026-03-01): “validation failure” here refers to service/engine execution/contract validation *after* a Review row exists (i.e., failures that surface as `ReviewStatus=FAILED` + `overall_summary`). Endpoint-level request validation errors (e.g., missing `Idempotency-Key`, unknown node IDs, stage mismatch) return API errors and must not create a Review.

**Q4: What form should the “regression hardening” take (no new tooling)?**
- A) Add/extend deterministic `pytest` contract tests (API + service seams) with a stubbed LLM client.
- B) Add only doc/checklist verification steps (no new tests).
- C) Add only fixtures/matrices (no new assertions).
 > Recommendation: A — tests are the only durable regression guard. Docs alone drift; fixtures without assertions don’t prevent changes.
 > **Selected: A**

**Q5: What is the “deterministic verification bundle” for this WF?**
- A) A documented checklist + exact `pytest` commands (subset) to run for this call.
- B) A versioned fixture matrix (inputs/expected outcomes) consumed by tests.
- C) Both A + B.
 > Recommendation: C — gives fast human verification plus machine-enforced regression safety.
 > **Selected: C**

---

## Section 2 — Desired Outcome

**Brainstorming Q&A:**

**Q1: What is the success metric for “no contract drift” for `POST /api/structured-review`?**
- A) Add an explicit API contract test suite covering the top error+success scenarios + idempotency replay/mismatch.
- B) Only assert “no exceptions” + “review created” for a couple cases.
- C) Only document the contract; don’t assert it in tests.
 > Recommendation: A — contract drift is only prevented when asserted; lightweight “smoke” tests don’t lock semantics.
 > **Selected: A** (user: “go with recommendations”)

**Q2: Which idempotency behaviors must be explicitly locked for this WF?**
- A) (1) same key + same payload returns same `{review_id, status}`; (2) same key + different payload returns `IDEMPOTENCY_PAYLOAD_MISMATCH`; (3) key expiry reuse is allowed after TTL.
- B) Only (1) and (2); ignore TTL reuse semantics.
- C) Only (2) (payload mismatch), since that’s the high-risk part.
 > Recommendation: A — TTL reuse and replay behavior are subtle regression surfaces that can break UX and create duplicate persisted reviews if changed.
 > **Selected: A** (user: “go with recommendations”)

**Q3: Which reviewer-policy enforcement outcomes must be deterministic and testable (for this call)?**
- A) Verify `BLOCKING` leads to a persisted `FAILED` review with a policy-blocking failure summary; `POST_CHECK` yields warnings surfaced in the persisted review summary; `PROMPT_ONLY` is included in the prompt but never blocks.
- B) Only verify `BLOCKING` (don’t assert post-check/prompt-only behavior).
- C) Only verify prompt contains policy (don’t assert any enforcement behavior).
 > Recommendation: A — even if the primary flow hardening is `POST /api/structured-review`, policy enforcement is a key “trust” lever for this call and should be regression-locked via deterministic tests around the single-snippet execution seam.
 > **Selected: A** (user: “go with recommendations”)

**Q4: What should the “deterministic verification bundle” contain as artifacts?**
- A) `docs/brainstorms/...` appendix: checklist + exact `pytest` commands + “what each test proves”.
- B) A new `docs/guides/...` doc (outside brainstorm artifacts).
- C) Only the tests; no docs bundle.
 > Recommendation: A — keeps WF atomic and ensures the verification bundle is co-located with the initiative SSOT.
 > **Selected: A** (user: “go with recommendations”)

**Q5: What’s the fixture-matrix granularity?**
- A) Small, high-signal matrix: ~8–12 cases (success, key error codes, idempotency replay/mismatch, policy blocking, policy post-check warning, timeout).
- B) Medium matrix: ~20–30 cases (cover most validation branches in the endpoint).
- C) Minimal: 3–5 cases only.
 > Recommendation: A — enough to prevent the most damaging regressions without turning into a full endpoint decision-table project.
 > **Selected: A** (user: “go with recommendations”)

---

## Section 3 — Target User / Actor

**Brainstorming Q&A:**

**Q1: Who is the primary actor for WF-0043?**
- A) Maintainers/engineers (need fast, deterministic regression confidence for a single call).
- B) Operators (need runtime dashboards/alerts/ops playbooks).
- C) Applicants (need UX changes / explanations directly in the UI).
 > Recommendation: A — this WF is explicitly “trust + regression” hardening and should ship as test+verification artifacts without UI/ops scope expansion.
 > **Selected: A** (pre-approved: “go with recommendations”)

**Q2: When should this “verification bundle” be used?**
- A) Pre-merge / pre-release: run locally/CI whenever touching review endpoints, idempotency, call ingestion, or compliance/pipeline logic.
- B) Only during incident response.
- C) Only during call onboarding.
 > Recommendation: A — the whole point is preventing regressions before they reach users.
 > **Selected: A** (pre-approved)

**Q3: What is the user-facing surface we must protect (even though the actor is engineering)?**
- A) `/app/reviews` continues to work because persisted review rows + statuses remain stable.
- B) Only the API response shape; UI can be updated later if needed.
- C) Only internal logging/telemetry.
 > Recommendation: A — preserving persistence semantics is an explicit WF constraint and is the main “trust” surface.
 > **Selected: A** (pre-approved)

**Q4: What “determinism” level is required for tests?**
- A) Fully deterministic: stub LLM responses where relevant; avoid golden natural-language quality assertions.
- B) Semi-deterministic: allow some variability and only assert presence of fields.
- C) Non-deterministic: run against real model and accept drift.
 > Recommendation: A — this is a regression-hardening WF; determinism is mandatory.
 > **Selected: A** (pre-approved)

**Q5: What environment should the bundle assume?**
- A) Standard backend test harness with isolated test DB (`DATABASE_URL` pointing to test DB), no reliance on dev DB.
- B) Ad-hoc local dev DB is acceptable.
- C) No DB required; pure unit tests only.
 > Recommendation: A — persistence/idempotency contracts require DB, and tests must not risk dev DB.
 > **Selected: A** (pre-approved)

---

## Section 4 — Rough Idea Exploration

**Brainstorming Q&A:**

**Q1: What’s the simplest implementation direction that still locks contracts?**
- A) Add a focused “contract suite” around `POST /api/structured-review` + a minimal adjacent suite for policy-enforcement semantics in the single-snippet flow, using deterministic stubs.
- B) Refactor core services first, then add tests later.
- C) Add broad E2E/browser tests.
 > Recommendation: A — harden contracts first without refactor churn or new tooling.
 > **Selected: A** (pre-approved)

**Q2: Where should the fixture matrix live?**
- A) Versioned test fixture (e.g., YAML/JSON) consumed by pytest parametrization.
- B) Inline in tests only.
- C) In docs only.
 > Recommendation: A — fixtures make intent explicit and allow easy case growth without copy/paste.
 > **Selected: A** (pre-approved)

**Q3: What should the contract suite assert (high level)?**
- A) Response codes+error codes; idempotency replay/mismatch; persistence invariants; stable failure summary conventions.
- B) Only success path.
- C) Only internal service behavior.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q4: How do we avoid brittle assertions around review content?**
- A) Assert structural invariants (review exists, status transitions, error codes) and avoid asserting natural-language feedback quality.
- B) Snapshot full response bodies and diff them.
- C) Hardcode expected feedback strings.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q5: How do we keep scope atomic to a single call?**
- A) Ground fixtures exclusively in `nwo_veni_2025_preproposal` call definition + its nodes/constraints/policy rules; no multi-call generalization work.
- B) Generalize into shared multi-call testing infrastructure.
- C) Mix in other canonical calls to “increase confidence”.
 > Recommendation: A — single-call MVP hardening only.
 > **Selected: A** (pre-approved)

---

## Section 5 — Constraints

**Brainstorming Q&A:**

**Q1: What must not change (hard contracts)?**
- A) API error semantics + idempotency semantics + `/app/reviews` persistence behavior.
- B) Only API response schemas.
- C) Only DB persistence.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q2: What must we avoid adding in this WF?**
- A) New tooling (Playwright/Cypress/etc.), new endpoints, or UX changes.
- B) Only avoid new tooling; endpoints/UI changes are fine.
- C) Only avoid UI changes; new tooling is fine.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q3: What “no behavior change first” posture should the WF take?**
- A) Add tests/verification artifacts first; only then do small refactors if tests prove parity.
- B) Refactor first and rely on existing tests.
- C) Do behavior changes as needed; rely on manual verification.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q4: How should we treat flaky/slow tests?**
- A) Keep the contract suite small and fast; prefer deterministic stubs; timebox “slow integration” cases.
- B) Accept slow suite; it’s fine.
- C) Skip DB tests entirely.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q5: What is the explicit non-goal boundary?**
- A) No multi-call expansion; no new evaluation logic; no change to how findings/cards are generated beyond regression fixes.
- B) Expand to other calls if easy.
- C) Rework the engine to be smarter.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

---

## Section 6 — Risks / Unknowns

**Brainstorming Q&A:**

**Q1: What’s the main risk to “deterministic contract tests”?**
- A) Tests accidentally depend on dev DB / real networked LLM calls, making them flaky or unsafe.
- B) Tests are too small to matter.
- C) Tests become too big and slow.
 > Recommendation: A — enforce isolated DB + stub LLM explicitly.
 > **Selected: A** (pre-approved)

**Q2: What’s the main risk to “preserve persistence semantics”?**
- A) Changing when a Review row is created (before vs after execution) or changing failure representation (API error vs persisted FAILED review) breaks `/app/reviews`.
- B) Only response schema matters.
- C) Only card content matters.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q3: What’s the main idempotency regression risk?**
- A) Duplicate persisted reviews or payload-mismatch behavior changing under race/IntegrityError conflict paths.
- B) Only missing header behavior.
- C) Only TTL behavior.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q4: What’s the main “policy enforcement” risk?**
- A) Enforcement modes drift (blocking vs warning vs prompt-only), or policy coverage silently drops when call-definition shape changes.
- B) Policy doesn’t matter.
- C) Policy should be removed.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q5: What’s the “unknown” we may need to defer?**
- A) TTL-expiry reuse semantics may be tricky to test without time control; document it clearly even if only partially asserted.
- B) Everything is known.
- C) Skip TTL entirely.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

---

## Section 7 — MVP Definition

**Brainstorming Q&A:**

**Q1: What is the smallest shippable slice (2–3 days) that achieves “trust + regression”?**
- A) Add focused contract tests + fixture matrix + docs verification appendix; avoid refactors unless needed to make tests deterministic.
- B) Add docs only.
- C) Add refactors + docs + broad test rewrite.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q2: What must be in the fixture matrix?**
- A) ~8–12 cases covering: success; representative validation errors; idempotency replay/mismatch; persistence on failure; policy enforcement regression cases (single-snippet seam).
- B) Only happy path.
- C) 20–30 cases.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q3: What should we explicitly exclude to keep atomic scope?**
- A) Browser/E2E automation, UI changes, multi-call generalization, prompt “quality” tuning.
- B) Only exclude browser tests.
- C) Don’t exclude; do everything needed.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q4: How should we treat “timeout” cases?**
- A) Cover timeout semantics only where they exist (single-snippet/LLM seam); don’t invent timeouts for deterministic pipeline paths.
- B) Force artificial timeouts everywhere.
- C) Ignore timeouts entirely.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q5: What’s the definition of “done” for this WF?**
- A) One command (or short set) runs the bundle and produces clear pass/fail; tests lock contracts; docs explain what is locked.
- B) Tests exist but are hard to run.
- C) Only docs exist.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

---

## Section 8 — Explicit Non-Goals

**Brainstorming Q&A:**

**Q1: What is explicitly out of scope?**
- A) Any behavior changes to the API/persistence semantics; this WF is regression hardening only unless a regression bug is proven.
- B) Behavior changes are fine.
- C) Replace the engine.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q2: What tooling is explicitly out of scope?**
- A) Playwright/Cypress (or any new browser automation tooling) unless separately approved.
- B) Add Playwright now.
- C) Add both Playwright + Cypress.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q3: What product scope is explicitly out of scope?**
- A) Multi-call expansion and new calls beyond `nwo_veni_2025_preproposal`.
- B) Add one more call if time.
- C) Rework onboarding UX.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q4: What “quality work” is explicitly out of scope?**
- A) Prompt/model tuning and “better feedback wording” work that can’t be tested deterministically.
- B) Do prompt tuning.
- C) Swap models.
 > Recommendation: A.
 > **Selected: A** (pre-approved)

**Q5: What refactor work is explicitly out of scope?**
- A) Large service refactors unrelated to enabling deterministic tests; only allow small refactors strictly in support of the contract suite.
- B) Large refactors are fine.
- C) Rewrite everything.
 > Recommendation: A.
 > **Selected: A** (pre-approved)
