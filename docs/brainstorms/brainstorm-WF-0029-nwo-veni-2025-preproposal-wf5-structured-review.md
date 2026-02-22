# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-22

---

## 1. Problem Statement

**Summary:**
- The existing `/reviews` endpoint evaluates a single snippet against one node — researchers cannot get holistic multi-node AI feedback in a single request.
- Cross-node alignment evaluation (e.g., does the `research_idea` align with claims in `academic_profile`?) is impossible with isolated per-node reviews.
- The primary users affected are researchers preparing NWO Veni 2025 pre-proposals who need structured AI feedback on all 3 nodes (`academic_profile`, `key_outputs`, `research_idea`).
- Today, a researcher *could* submit 3 separate single-node reviews, but the feedback is fragmented and misses alignment issues — the core frustration.
- This matters now because the V2 data model (WF-0021), structured endpoint/gating (WF-0027), and compliance engine (WF-0028) are all shipped — this is the next logical layer before the frontend form (WF-6). Deadline pressure adds urgency.
- Hard requirement: if a node's text is missing or empty, evaluation elements that depend on cross-node context must return `NOT_ASSESSABLE` (never fabricate alignment). This is a data integrity and trustworthiness rule from the north star doc.

**Brainstorming Q&A:**

**Q1: What is the primary gap this endpoint fills?**
- A) Researchers currently get AI feedback only on one node at a time — they need holistic per-node feedback in a single request (covers cross-node alignment like `academic_profile` ↔ `research_idea`).
- B) The existing `/reviews` endpoint is too slow / generates poor quality — this replaces it entirely.
- C) The frontend needs multi-node submission to build the structured form (WF-6) — this is purely an API prerequisite.
> Recommendation: A — The core value is holistic multi-node review with cross-node alignment awareness. B is inaccurate (it doesn't replace the legacy endpoint). C is partially true but undersells the product value.
> **Selected: A**

**Q2: Who primarily experiences this problem?**
- A) Researchers preparing NWO Veni 2025 pre-proposals — they can't get structured AI feedback on all 3 nodes at once.
- B) All platform users — every call's review flow would benefit.
- C) Internal team — we can't validate multi-node review quality without this endpoint.
> Recommendation: A — MVP scopes to NWO Veni 2025 specifically. Generalization is a future concern.
> **Selected: A**

**Q3: What happens today without this endpoint?**
- A) Researcher submits 3 separate single-node reviews → gets fragmented feedback → can't detect cross-node alignment issues (e.g., `research_idea` claims not supported by `academic_profile`).
- B) Researcher can't use the app at all for NWO Veni — only legacy single-snippet mode exists.
- C) Researcher gets compliance checks but missing the qualitative LLM-based review entirely.
> Recommendation: A — Today they *could* do 3 single-node reviews, but the feedback would be isolated and miss alignment evaluation. This is the core frustration.
> **Selected: A**

**Q4: Why does this matter now (sequencing justification)?**
- A) The V2 data model (WF-0021), structured endpoint/gating (WF-0027), and compliance engine (WF-0028) are all shipped — this is the next logical layer before the frontend form (WF-6).
- B) NWO Veni 2025 pre-proposal deadline is approaching — researchers need this soon.
- C) Both A and B — technical readiness meets user urgency.
> Recommendation: C — Both the technical stack readiness and the deadline pressure make this the right time.
> **Selected: C**

**Q5: What is the NOT_ASSESSABLE alignment requirement and why is it critical?**
- A) If a node's text is missing or empty, the LLM must return `NOT_ASSESSABLE` for evaluation elements that depend on cross-node context (never fabricate alignment). This is a data integrity rule.
- B) `NOT_ASSESSABLE` is an optional graceful-degradation signal — the LLM should try its best even with missing context and only use it as last resort.
- C) `NOT_ASSESSABLE` applies only to compliance checks (already handled in WF-0028) — the AI review endpoint doesn't need it.
> Recommendation: A — The north star doc is explicit: "Missing context → mark alignment-related evaluation as NOT_ASSESSABLE (never fabricate)." This is a hard requirement for trustworthiness.
> **Selected: A**

---

## 2. Desired Outcome

**Summary:**
- Primary measurable outcome: a researcher submits all 3 nodes in one request and receives per-node AI feedback cards with alignment awareness.
- Behavior change: researchers shift from fragmented per-node reviews to holistic all-at-once submission with alignment-aware feedback.
- MVP "good enough": endpoint accepts 3-node payload, runs per-node LLM review using V2 expectations/criteria/elements, returns per-node feedback cards + overall summary. Alignment-dependent elements respect `NOT_ASSESSABLE`. Response is persisted for review history.
- After this ships: unblocks WF-6 (frontend structured form) + enables structured-vs-single review quality comparison for prompt tuning.
- Response structure: per-node feedback cards (reuse existing `ReviewCard` model shape), grouped under each node, plus overall review summary. Each card maps to a `NodeExpectation`.

**Brainstorming Q&A:**

**Q1: What is the primary measurable outcome after this endpoint exists?**
- A) A researcher can submit all 3 nodes in one request and receive per-node AI feedback cards with alignment awareness — measured by "structured review request → per-node feedback returned."
- B) All calls (not just NWO Veni) can use multi-node review — measured by "number of calls with structured review coverage."
- C) Review quality improves measurably vs. single-node reviews — measured by user satisfaction or feedback accuracy scores.
> Recommendation: A — This is the MVP outcome: submit 3 nodes, get per-node feedback. B generalizes beyond scope. C is aspirational but not measurable at this phase.
> **Selected: A**

**Q2: What behavior change do we expect from researchers?**
- A) Researchers shift from submitting nodes individually (or skipping review entirely) to submitting all 3 nodes together and using the per-node + alignment feedback to iterate on their draft.
- B) Researchers stop using single-node review entirely — the new endpoint replaces the old flow.
- C) No behavior change — this is backend-only plumbing for WF-6's frontend form.
> Recommendation: A — The behavior shift is "fragmented 1-by-1" → "holistic all-at-once." B is too aggressive (legacy flow stays for other calls). C undersells the user impact.
> **Selected: A**

**Q3: What does "good enough" look like for MVP?**
- A) Endpoint accepts the 3-node payload, runs per-node LLM review using V2 expectations/criteria/elements, returns per-node feedback cards + an overall summary. Alignment-dependent elements respect `NOT_ASSESSABLE`. Response is persisted.
- B) Same as A, but also generates a cross-node "alignment report" as a separate section in the response.
- C) Same as A, but without persistence — stateless review-on-the-fly, no DB storage.
> Recommendation: A — Persistence is important for review history (WF-0014, already shipped). Cross-node alignment report (B) adds complexity for later. Stateless (C) breaks review history UX.
> **Selected: A**

**Q4: What becomes possible after this ships?**
- A) The frontend structured form (WF-6) can call this endpoint to provide the full review experience — this unblocks the next chunk.
- B) We can start comparing structured review quality to single-node review quality, informing prompt tuning.
- C) Both A and B.
> Recommendation: C — The main unlock is WF-6 (frontend form), but quality comparison becomes a valuable side benefit. Both are real outcomes.
> **Selected: C**

**Q5: How should the response be structured?**
- A) Per-node feedback cards (same shape as current `ReviewCard` model) grouped under each node, plus an overall review summary. Each card maps to a `NodeExpectation`.
- B) A single flat list of feedback cards across all nodes, with a `node_logical_id` tag on each card.
- C) A completely new response schema decoupled from the existing `ReviewCard`/`Review` models.
> Recommendation: A — Reuse existing card structure, group by node, add overall summary. Preserves compatibility with existing review detail rendering (WF-0016). B loses grouping structure. C adds unnecessary complexity.
> **Selected: A**

---

## 3. Target User / Actor

**Summary:**
- Primary user: researchers preparing NWO Veni 2025 pre-proposals (mediated by the frontend).
- Current behavior: researchers either skip PeerLens for NWO Veni entirely or misuse the legacy single-snippet mode for one section — the structured flow doesn't exist yet.
- Frustration: fragmented feedback (each node reviewed in isolation, missing alignment) + compliance-only without qualitative review (sees word limit violations but not "your research idea doesn't leverage claimed strengths").
- This endpoint is researcher-facing only in MVP. No internal/admin user interaction.
- Partial submission is supported: researcher can submit 2 of 3 nodes. Missing nodes get `NOT_ASSESSABLE` for alignment-dependent elements; present nodes still receive per-node feedback.

**Brainstorming Q&A:**

**Q1: Who is the primary user of this endpoint?**
- A) Researchers preparing NWO Veni 2025 pre-proposals (via the frontend structured form that will call this API).
- B) The frontend application itself — the researcher never calls the API directly; the BFF/frontend is the consumer.
- C) Internal QA / prompt-tuning team — they need it to validate multi-node review quality before exposing to researchers.
> Recommendation: A — The researcher is the ultimate user, even though the frontend mediates. B is technically correct but misses the "who benefits" framing. C is a secondary use case.
> **Selected: A**

**Q2: What is the researcher's current behavior?**
- A) They write their 3-section pre-proposal in a word processor, then paste one section at a time into PeerLens for single-node review, losing cross-section context.
- B) They don't use PeerLens for NWO Veni at all yet — there's no structured flow, so they skip it or use only the legacy single-snippet mode for one section.
- C) They rely on peer review from colleagues/supervisors and don't use AI tools at all.
> Recommendation: B — Most realistic for MVP launch. The structured flow doesn't exist yet. A assumes adoption of per-node flow (unlikely). C ignores PeerLens users entirely.
> **Selected: B**

**Q3: What frustration does the current state create?**
- A) Feedback is fragmented — each node is reviewed in isolation, so the researcher can't tell if their `research_idea` aligns with strengths claimed in `academic_profile`.
- B) Compliance checks exist (WF-0028) but qualitative AI feedback is missing — the researcher sees "you violated a word limit" but not "your research idea doesn't leverage the strengths you described."
- C) Both A and B — fragmented feedback + compliance-only without qualitative review.
> Recommendation: C — Both frustrations are real and complementary. A captures the alignment gap. B captures the compliance-vs-quality gap. Together they paint the full picture.
> **Selected: C**

**Q4: Does this endpoint serve any internal/admin users?**
- A) No — this is purely researcher-facing (mediated by frontend). Admin/internal users don't interact with this endpoint.
- B) Yes — the internal team will use it for prompt quality testing and tuning before researcher-facing launch.
- C) Not in MVP — but a future admin dashboard might consume review analytics from persisted structured reviews.
> Recommendation: A — MVP scope is researcher-facing only. Internal prompt tuning (B) can use scripts/CLI. Future admin dashboards (C) are out of scope.
> **Selected: A**

**Q5: Should partial submission be supported (e.g., researcher submits only 2 of 3 nodes)?**
- A) Yes — partial submission is valid. Missing nodes get `NOT_ASSESSABLE` for alignment-dependent elements, and present nodes still get per-node feedback.
- B) No — all 3 nodes must be submitted. The whole point is holistic review; partial defeats the purpose.
- C) Yes for the API, but the frontend should discourage it (soft warning, not hard block).
> Recommendation: A — Partial submission is realistic: a researcher might want feedback on 2 nodes while still drafting the 3rd. The `NOT_ASSESSABLE` mechanism handles this gracefully. B is too rigid. C adds unnecessary frontend complexity for MVP.
> **Selected: A**

---

## 4. Rough Idea Exploration

**Summary:**
- Implementation direction: new `/api/structured-review` endpoint, separate from legacy `/reviews`. Accepts multi-node payload, iterates per node using existing `ReviewerService`, persists as one `Review` record with grouped `ReviewCard` sets.
- LLM invocation: per-node sequential using existing prompt builder/parser. The existing `build_review_prompt()` functions with V2 data (reads from same `NodeExpectation` records). Prompt quality tuning is parked separately (P2 #7).
- Persistence: one `Review` record per structured submission, with `review_type` field to distinguish `"single"` vs `"structured"`.
- Overall summary: **skipped for MVP** — return per-node cards only. LLM-generated holistic summary is deferred (parked).
- `NOT_ASSESSABLE`: per-card granularity. Each `ReviewCard` includes an `assessable` status. Cards for alignment-dependent elements with missing context show `not_assessable` with explanation.

**Parked for future:**
- 🅿️ Single mega-prompt strategy (Q2 option B) → P2 #5.
- 🅿️ LLM-generated overall summary (Q4 option A) → P2 #6.
- 🅿️ Prompt revision for V2 expectations structure → P2 #7.

**Brainstorming Q&A:**

**Q1: What is the simplest implementation direction for the new endpoint?**
- A) New `/api/structured-review` endpoint — separate from legacy `/reviews`. Accepts multi-node payload, iterates using existing `ReviewerService.generate_review()` per node, wraps results in grouped response. One `Review` record persisted.
- B) Extend existing `/reviews` endpoint — add optional `nodes[]` array to `CreateReviewRequest`.
- C) New endpoint with parallel LLM strategy — single mega-prompt containing all nodes, parse structured multi-node response.
> Recommendation: A — Cleanest separation of concerns. B muddies the existing contract. C is riskier (new prompt format + parsing) and can be an optimization later.
> **Selected: A**

**Q2: How should the LLM be invoked — once per node or once for all nodes?**
- A) Per-node sequential — call LLM once per submitted node using existing prompt builder. Simple, predictable, reuses all existing logic.
- B) Single mega-prompt — send all nodes + expectations in one LLM call, get structured JSON response. More efficient but requires new prompt template and parser.
- C) Per-node parallel — same as A but concurrent. Faster but risks rate limiting and complex error handling.
> Recommendation: A — Per-node sequential is the MVP safe path. Reuses entire existing pipeline without change. B requires new prompt engineering and risks regressions. C is a valid optimization for later.
> **Selected: A** — User noted preference for B as a future optimization (P2 #5). User also flagged prompt revision concern — resolved: existing prompt functions with V2 data; quality tuning parked as P2 #7.

**Q3: How should persistence work for structured reviews?**
- A) One `Review` record per structured submission, with `ReviewCard` records grouped by node. Existing `Review` model gets optional `review_type` field (`"single"` vs `"structured"`).
- B) One `Review` record per node — 3 separate reviews linked by shared `batch_id`.
- C) New `StructuredReview` table — separate persistence model.
> Recommendation: A — One Review per submission is cleanest. B fragments review history UX (3 reviews where user expects 1). C adds unnecessary schema complexity.
> **Selected: A**

**Q4: Should the overall summary be LLM-generated or derived from per-node results?**
- A) LLM-generated — additional LLM call synthesizing holistic summary across all nodes.
- B) Algorithmically derived — compute rating as average/weighted score, template-based summary.
- C) Skip overall summary for MVP — return per-node cards only.
> Recommendation: C — Per-node feedback cards are the core value. A adds extra LLM call + new prompt + latency. B would feel mechanical. Skipping keeps scope tight and shippable.
> **Selected: C** — User noted preference for A as a future enhancement (parked).

**Q5: How should `NOT_ASSESSABLE` be surfaced in the response?**
- A) Per-card field — each `ReviewCard` includes `assessable` status. Cards for alignment-dependent elements with missing context have `not_assessable` with explanation.
- B) Omit unassessable cards entirely — add top-level `skipped_elements[]` list.
- C) Per-node level — mark entire node as `NOT_ASSESSABLE` if text is empty.
> Recommendation: A — Per-card granularity is most informative. B hides information. C is too coarse (some elements within a node may be assessable even if cross-node alignment isn't).
> **Selected: A**

---

## 5. Constraints

**Summary:**
- Time constraint: tight — this is the last backend prerequisite before WF-6. Target 1–2 days.
- Technical constraint: `ReviewerService` is synchronous (uses `ThreadPoolExecutor`). New endpoint stays synchronous — no async refactor.
- Dependencies: V2 data model (WF-0021), structured config (WF-0027), compliance engine (WF-0028) are all merged to `main` (satisfied). Must verify NWO Veni YAML has complete `evaluation_criteria` + `evaluation_elements` for all 3 nodes.
- Quota: structured review counts as 1 "review" against daily quota (not 3 LLM calls). Researcher submitted one review.
- No new external dependencies. Pure internal wiring: new endpoint + schema + persistence.

**Brainstorming Q&A:**

**Q1: What is the time constraint for this WF?**
- A) Tight — last backend prerequisite before WF-6 (frontend form). Ship within 1–2 days.
- B) Moderate — target 3–5 days, allowing thorough prompt revision and testing.
- C) Flexible — no hard deadline; quality over speed.
> Recommendation: A — The WF chain (WF-2 → WF-3 → WF-4 → WF-5 → WF-6) is sequential. WF-6 is blocked on this. Tight scope, ship fast.
> **Selected: A**

**Q2: What technical constraints exist from the current stack?**
- A) `ReviewerService` is synchronous (uses `ThreadPoolExecutor` for LLM calls). New endpoint must remain synchronous — no async refactor in scope.
- B) `ReviewerService` needs async refactor first.
- C) No significant technical constraints.
> Recommendation: A — Existing `ReviewerService.generate_review()` runs LLM calls in `ThreadPoolExecutor` with timeout. Structured endpoint reuses this pattern. Async refactoring (B) is out of scope.
> **Selected: A**

**Q3: What are the dependencies (must-have before starting implementation)?**
- A) V2 data model (WF-0021), structured config (WF-0027), and compliance engine (WF-0028) must all be merged to `main`. All three are shipped (Done).
- B) NWO Veni YAML must contain valid V2 `evaluation_criteria` and `evaluation_elements` for all 3 nodes.
- C) Both A and B.
> Recommendation: C — Both required. A is satisfied. B needs verification — confirm ingested YAML has complete evaluation data for all 3 nodes.
> **Selected: C**

**Q4: Are there LLM cost/rate-limiting constraints to consider?**
- A) Yes — structured review makes 3 LLM calls per submission. Daily quota should count it as 1 "review" (not 3).
- B) Yes — 3 calls triples cost. Each structured review should count as 3 against daily quota.
- C) No — current limits are sufficient; no changes needed.
> Recommendation: A — From researcher's perspective, they submitted one review. Counting as 3 would halve effective quota and feel punitive. Cost increase is manageable for MVP.
> **Selected: A**

**Q5: Does this endpoint have any external dependencies?**
- A) No new external dependencies. Uses existing OpenAI client, DB, models. Only new: endpoint, response schema, persistence.
- B) May need new LLM model/endpoint for better structured output handling.
- C) Need new prompt testing framework to validate quality.
> Recommendation: A — Zero new external deps. Pure internal wiring. B and C are future concerns, not blockers.
> **Selected: A**

---

## 6. Risks / Unknowns

**Summary:**
- Most fragile assumption: 3 sequential LLM calls = 3× latency (15–45 seconds per structured review). This is the biggest latency risk. Accepted for MVP; the mega-prompt optimization (P2 #5) directly mitigates this.
- Must validate early: (1) confirm NWO Veni YAML has complete `evaluation_criteria` + `evaluation_elements` for all 3 nodes, and (2) smoke-test `ReviewerService.generate_review()` against each node using V2 data.
- Rework risk: existing `Review` has single `node_id` FK and `ReviewCard` has no node-level grouping. Structured reviews need schema additions: multi-node association + per-card node tagging. Must plan for this from the start.
- Latency strategy: accept synchronous 15–45s for MVP. Frontend (WF-6) will need a loading spinner. Safety net: existing `ThreadPoolExecutor` timeout per LLM call.
- Conflict risk: minimal. New endpoint is separate URL/schema but shares `ReviewerService`. Good test coverage on shared service is the mitigation.

**Brainstorming Q&A:**

**Q1: What assumption is most fragile?**
- A) Existing `ReviewerService.generate_review()` called per-node in a loop = 3× latency. Three sequential LLM calls could mean 15–45 seconds per structured review.
- B) V2 `NodeExpectation` / `EvaluationCriterion` data may be incomplete for all 3 NWO Veni nodes.
- C) Partial submission (2 of 3 nodes) `NOT_ASSESSABLE` path hasn't been tested.
> Recommendation: A — Three sequential LLM calls is the biggest latency risk. Known tradeoff for MVP but needs clear timeout strategy.
> **Selected: A**

**Q2: What must be validated early (before writing endpoint code)?**
- A) Run `ReviewerService.generate_review()` against each NWO Veni node to confirm valid output from V2 data.
- B) Verify NWO Veni YAML has `evaluation_criteria` + `evaluation_elements` for all 3 nodes.
- C) Both A and B.
> Recommendation: C — B is a quick check (inspect DB or YAML). A is the smoke test. Both should happen before writing the new endpoint.
> **Selected: C**

**Q3: What could cause rework?**
- A) `ReviewCard` model doesn't support grouping cards by node within a single `Review`. May need `node_logical_id` column.
- B) `ReviewerService` signature ties a review to a single `node_id` (UUID FK). Structured reviews need to reference multiple nodes.
- C) Both A and B — current single-node data model may resist multi-node extension.
> Recommendation: C — Both are real risks. Need: (1) multi-node association for `Review`, (2) per-card node tagging on `ReviewCard`. Manageable but must be in the plan from the start.
> **Selected: C**

**Q4: What is the latency risk and how should we handle it?**
- A) Accept 15–45 second response time for MVP. Document it. Frontend (WF-6) needs loading state but no async polling.
- B) Add async processing + polling to avoid long-blocking requests.
- C) Hard timeout (30s) and fail fast if any LLM call exceeds it.
> Recommendation: A — Synchronous is simpler for MVP. Existing single-node review is already synchronous with `ThreadPoolExecutor` timeout. WF-6 needs "processing" spinner. Async (B) is overengineering for MVP.
> **Selected: A** — User noted this latency risk strengthens the case for the previously parked mega-prompt optimization (P2 #5), which would reduce 3 LLM calls to 1.

**Q5: Is there a risk of the new endpoint conflicting with the existing `/reviews` flow?**
- A) No — completely separate endpoint. Different URL, schema, code path.
- B) Yes — shared `ReviewerService` means a bug could affect single-node reviews.
- C) Minimal — shared service code, but endpoint separation reduces conflict risk. Good test coverage is the mitigation.
> Recommendation: C — They share `ReviewerService.generate_review()`, so a regression there would affect both. But endpoint separation minimizes collision. Good test coverage mitigates.
> **Selected: C**

---

## 7. MVP Definition

**Summary:**
- MVP must include: new `POST /api/structured-review` endpoint, per-node LLM review using existing `ReviewerService`, persistence as one `Review` record, review history integration, and `NOT_ASSESSABLE` handling.
- **Critical**: cross-node alignment evaluation elements (e.g., `elem_cv_idea_alignment`) require the prompt for a node to include context from other submitted nodes. This is NOT a separate "alignment report" — it's passing cross-node text into each per-node prompt so the LLM can evaluate alignment elements. This IS in-scope for MVP.
- Excluded from MVP: LLM-generated overall summary (P2 #6), mega-prompt optimization (P2 #5), prompt quality tuning (P2 #7), async polling, frontend changes.
- Minimum schema change: add `review_type` to `Review` model + `node_logical_id` to `ReviewCard` model. No new tables.
- Single-node structured submissions are valid (≥1 node). `review_type` is always `"structured"`.

**Brainstorming Q&A:**

**Q1: If limited to 2 days, what must exist?**
- A) New `POST /api/structured-review` endpoint: accepts multi-node payload, loops per node, calls `ReviewerService`, returns per-node cards. Persisted as one `Review`.
- B) Same as A, plus `NOT_ASSESSABLE` handling for missing/empty node text on alignment-dependent elements.
- C) Same as B, plus full integration with review history listing (structured review shows up in `/reviews`).
> Recommendation: C — All three needed for functional MVP. A is core. B is a hard requirement (north star). C is necessary for review history UX.
> **Selected: C**

**Q2: What can explicitly wait (not in this WF)?**
- A) LLM-generated overall summary (P2 #6), mega-prompt optimization (P2 #5), prompt quality tuning (P2 #7).
- B) Frontend form (WF-6 — separate WF).
- C) Both A and B.
> Recommendation: C — All of A's items are parked. WF-6 is a separate WF by design. This WF is backend-only.
> **Selected: C**

**Q3: What must NOT be included in MVP?**
- A) No async polling — synchronous only.
- B) No cross-node alignment report — per-node cards only. **BUT** cross-node alignment *evaluation* IS in-scope: the prompt for alignment-dependent elements (e.g., `elem_cv_idea_alignment` on `research_idea`) must include text from related nodes (e.g., `academic_profile`) as context so the LLM can evaluate alignment.
- C) No frontend changes — backend endpoint + schema + persistence only.
- D) All of A, B, and C.
> Recommendation: D — Async, alignment report, and frontend are excluded. But user correctly flagged that cross-node alignment *evaluation* within per-node prompts is required — `elem_cv_idea_alignment` needs both `academic_profile` and `research_idea` text (confirmed by YAML `runtime_notes`). This is in-scope (prompt-level concern, not a new report).
> **Selected: D** — With critical clarification: "no alignment report" ≠ "no alignment evaluation." Cross-node context in prompts is required.

**Q4: What is the minimum schema change?**
- A) Add `review_type` to `Review` model (`"single"` or `"structured"`). Add `node_logical_id` to `ReviewCard` (nullable). No new tables.
- B) Create new `StructuredReviewNode` junction table.
- C) No schema changes — store as JSON in existing metadata field.
> Recommendation: A — Minimal and backward-compatible. B adds complexity. C is fragile and hard to query.
> **Selected: A**

**Q5: How should the endpoint handle a single-node structured submission?**
- A) Treat same as multi-node — return one node group with cards. `review_type` is still `"structured"`.
- B) Reject — require at least 2 nodes.
- C) Auto-detect: if 1 node, route to legacy; if 2+, use structured.
> Recommendation: A — Simplest and most consistent. No special-casing, no silent routing.
> **Selected: A**

---

## 8. Explicit Non-Goals

**Summary:**
- Frontend work is out of scope (WF-6).
- Full prompt quality tuning is out of scope (P2 #7). Only minimal cross-node context addition is in-scope (targeted prompt change for alignment-dependent elements).
- Mega-prompt optimization is out of scope (P2 #5).
- Async processing is out of scope. Synchronous for MVP.
- Parallel LLM calls (concurrent per-node) and batch submission of multiple proposals are out of scope (parked).

**Parked for future (from this section):**
- 🅿️ Parallel LLM calls for structured review → P2 #8. (Ref: WF-0029 brainstorm S4 Q2 option C, S8 Q5)
- 🅿️ Batch submission of multiple proposals → P2 #9. (Ref: WF-0029 brainstorm S8 Q5)

**Brainstorming Q&A:**

**Q1: Is frontend work explicitly out of scope?**
- A) Yes — backend-only WF. Frontend structured form is WF-6 (P1 #5 in parking lot). No frontend files touched.
- B) Mostly — but should update BFF proxy to forward structured review requests.
- C) No — should add at least a basic structured review form.
> Recommendation: A — WF-6 is the next WF for frontend. This WF touches only backend. BFF proxy (B) can be part of WF-6.
> **Selected: A**

**Q2: Is prompt quality tuning out of scope?**
- A) Yes — P2 #7 is parked. Existing prompt functions with V2 data.
- B) Partially — need minimal prompt adjustments for cross-node context (needed for alignment evaluation), not a full prompt redesign.
- C) No — prompt tuning is critical for quality and should be in-scope.
> Recommendation: B — Existing prompt functions for single-node review. But alignment-dependent elements need cross-node context in the prompt. This is a minimal, targeted prompt change (add other nodes' text), not full quality tuning (P2 #7).
> **Selected: B**

**Q3: Is the mega-prompt optimization out of scope?**
- A) Yes — P2 #5 is parked. MVP uses per-node sequential calls.
- B) No — the latency risk makes it critical for MVP.
> Recommendation: A — Accepted latency tradeoff for MVP. P2 #5 is the dedicated follow-up.
> **Selected: A**

**Q4: Is async processing out of scope?**
- A) Yes — synchronous only for MVP. Frontend (WF-6) handles loading states.
- B) No — 15–45s sync responses will cause HTTP timeouts.
> Recommendation: A — Existing single-node review is already synchronous (5–15s). Render supports long-running sync requests. If timeouts emerge, async is a follow-up.
> **Selected: A**

**Q5: What tempting features must be explicitly postponed?**
- A) LLM-generated overall summary, mega-prompt, and prompt tuning (already parked as P2 #5–#7).
- B) Parallel LLM calls (S4 Q2 option C) and batch submission of multiple proposals.
- C) Both A and B — all are future WFs or parking lot items.
> Recommendation: C — All tempting but out of scope. A is already parked. B (parallel calls, batch submissions) explicitly noted as non-goals and parked. These may not be needed depending on app evolution — parking preserves the context and rationale for future reference.
> **Selected: C**

---

## Clarification Notes (captured from brainstorm discussion)

### Cross-node alignment evaluation vs. alignment report

| Concept | In scope? | What it means |
|---|---|---|
| Cross-node alignment **evaluation** | ✅ Yes | The prompt for alignment-dependent elements (e.g., `elem_cv_idea_alignment` on `research_idea`) must include text from related nodes (e.g., `academic_profile`) as context, so the LLM can evaluate alignment. This is a prompt-level change. |
| Cross-node alignment **report** | ❌ No | A separate synthesized summary/document comparing nodes. This is a future enhancement (not parked — deemed unnecessary for MVP). |

Confirmed by YAML `runtime_notes` (line 276): _"Alignment elements require both academic_profile and research_idea context."_

### `compliance_rules` vs. `guidance_text` in the review pipeline

| Field | Used where | In review pipeline? |
|---|---|---|
| `guidance_text` | Already in `build_review_prompt()` (prompt_builder.py:76). Included as "Guidance:" in the LLM prompt. | ✅ Yes — in review pipeline |
| `compliance_rules` | Consumed by compliance engine (WF-0028, `/api/check-compliance`). Drives deterministic checks (word limits, prohibited metrics, completeness). | ❌ No — separate deterministic pipeline |

`compliance_rules` are stored in `CallDefinition.canonical_json` (JSONB). They were never part of the LLM review prompt — they're deterministic rules, not qualitative evaluation criteria.
