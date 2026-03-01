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
