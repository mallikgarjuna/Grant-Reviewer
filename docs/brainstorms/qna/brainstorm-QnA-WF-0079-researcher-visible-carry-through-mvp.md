<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md -->
# WF-0079 — Researcher-Visible Carry-Through MVP

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-13

Type: feature

---

## Preflight Step 1 — Long-Form Problem Intake

Source: user-provided initiative brief in chat on 2026-03-13.

- WF-0077 made deterministic researcher-facing guidance the visible fallback surface for the structured `/app` review path.
- WF-0078 added a bounded additive synthesis seam downstream of `pipeline_v1`, but intentionally closed as backend-only seam proof.
- Accepted synthesized companion output currently exists only via in-memory `last_synthesis_requests` / `last_synthesis_results` in `backend/app/services/structured_reviewer_service.py`.
- The researcher-visible review page still renders persisted deterministic `ReviewCard.feedback_text`, so the product still looks effectively unchanged to researchers.
- The active structured-review runtime must remain deterministic-first and fail-closed per card.

## Preflight Step 2 — Repo Reality Snapshot

- `StructuredReviewerService` already attempts bounded additive synthesis after deterministic card generation.
- `StructuredReviewSynthesisService` already exposes typed accepted/rejected synthesis results.
- `ReviewCard` persistence does not yet store additive synthesis.
- Review-detail repository/API mapping returns only deterministic `feedback_text`.
- `/app/reviews/[reviewId]` renders and exports only deterministic `feedback_text`.

## Section 1 — Problem Statement

**Q1: What exact ship claim should WF-0079 be allowed to make?**
- A) `/app/reviews/[reviewId]` detail page only shows deterministic baseline plus accepted synthesized companion when present. Exports/history remain unchanged for MVP.
- B) Detail page plus text export both show the additive companion in MVP.
- C) Detail page, exports, and review history/list all carry synthesis in MVP.
> Recommendation: A — it is the narrowest truthful production slice. B is dismissed because it widens scope to a second read surface too early. C is dismissed because it overreaches far beyond the minimum honest rollout.
> **Selected: A**

**Q2: What should count as researcher-visible carry-through for this WF?**
- A) Persist companion data, expose it on the review detail API, and render it on `/app/reviews/[reviewId]`; no other surfaces.
- B) Keep persistence out, derive companion text on read from transient or recomputed seams.
- C) Render synthesized text by replacing `feedback_text` in the frontend only.
> Recommendation: A — this is the smallest honest end-to-end contract. B is dismissed because it is not durable and breaks read truth. C is dismissed because it hides deterministic fallback truth and creates a fake rollout.
> **Selected: A**

**Q3: What is the safest storage boundary for the additive companion?**
- A) Add nullable companion/provenance fields directly on `ReviewCard`.
- B) Store a review-level JSON blob keyed by card identity.
- C) Keep it in a separate new table for synthesis artifacts.
> Recommendation: A — it is the narrowest, most readable MVP contract and makes backward compatibility obvious. B is dismissed because it increases hidden coupling to read mapping. C is dismissed because it adds platform shape beyond the MVP need.
> **Selected: A**

**Q4: How should the page present deterministic versus additive text?**
- A) Deterministic `feedback_text` remains the main baseline block, with synthesized companion rendered as a clearly labeled secondary section when present.
- B) Synthesized companion becomes the primary visible text and deterministic feedback is collapsed behind a toggle.
- C) Merge both into one combined text block.
> Recommendation: A — it preserves deterministic truth and makes additive scope explicit. B is dismissed because it over-promotes synthesis. C is dismissed because it obscures fallback boundaries.
> **Selected: A**

**Q5: Should this be planned as one WF or a tiny 2-WF split?**
- A) One WF for the review-detail MVP, with internal task splitting and explicit deferral of exports/history.
- B) Two WFs: first persistence/API/backend carry-through, second frontend visibility.
- C) Two WFs: first detail page, second exports/history/history-list.
> Recommendation: A — the detail flow is one user-visible truth contract across four seams. B is dismissed because the first WF still could not claim user-visible success. C is dismissed because exports/history are easier and safer to defer inside this same WF.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What should the MVP change for the researcher?**
- A) The review detail page shows deterministic feedback as baseline and accepted synthesized companion when available.
- B) The detail page hides deterministic feedback when synthesis exists.
- C) The detail page shows only a global review-level synthesis.
> Recommendation: A — it matches the requested truth contract. B and C are dismissed because they either erase fallback truth or break per-card grounding.
> **Selected: A**

**Q2: What should happen when synthesis is absent for a card?**
- A) Render deterministic-only content with no broken additive placeholder.
- B) Show an empty synthesis shell so users know the feature exists.
- C) Treat the review as partially failed.
> Recommendation: A — it keeps missing synthesis harmless and backward compatible. B and C are dismissed because they misframe a valid deterministic-only state as a defect.
> **Selected: A**

**Q3: What should remain the authoritative visible truth?**
- A) Deterministic `feedback_text`.
- B) The synthesized companion when present.
- C) A merged hybrid string.
> Recommendation: A — it preserves the approved trust model. B and C are dismissed because they blur deterministic authority.
> **Selected: A**

**Q4: What should count as honest ship readiness?**
- A) Persistence + API/read path + frontend rendering are all coherent end to end.
- B) Backend persistence exists even if the page does not render it yet.
- C) Frontend renders mock additive content from a local seam.
> Recommendation: A — anything less would be an overclaim. B and C are dismissed because they leave the user-visible contract incomplete.
> **Selected: A**

**Q5: What should be explicitly deferred by default?**
- A) Exports and review history/list surfaces.
- B) Backward compatibility handling.
- C) Fail-closed behavior.
> Recommendation: A — it keeps the MVP tight without compromising correctness. B and C are dismissed because they are required for any honest rollout.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary user of this workflow?**
- A) Researchers viewing structured review details in `/app`.
- B) Internal maintainers only.
- C) Users of the legacy review path.
> Recommendation: A — this workflow exists to close a researcher-visible product gap. B and C are dismissed because they are secondary or out of scope.
> **Selected: A**

**Q2: Which secondary actor must the design protect?**
- A) Maintainers preserving deterministic traceability and fail-closed semantics.
- B) Marketing owners seeking broader AI claims.
- C) Prompt writers seeking more model freedom.
> Recommendation: A — maintainers own the trust boundary. B and C are dismissed because they encourage scope drift.
> **Selected: A**

**Q3: What user burden are we reducing?**
- A) Turning grounded findings into clearer revision guidance without losing traceability.
- B) Teaching users the backend runtime architecture.
- C) Unifying all review surfaces at once.
> Recommendation: A — it matches the narrow product pain. B and C are dismissed because they do not define the MVP.
> **Selected: A**

**Q4: Which terminology rule matters in the rendered experience?**
- A) Use evaluation criteria/elements terminology.
- B) Allow mixed rubric language.
- C) Let the UI vary language based on context.
> Recommendation: A — it aligns with canonical product language. B and C are dismissed because they reintroduce terminology drift.
> **Selected: A**

**Q5: Which path is explicitly not the user target?**
- A) Legacy `/reviews` surfaces and generalized AI coach behavior.
- B) The structured detail page.
- C) Existing deterministic fallback states.
> Recommendation: A — it preserves scope. B and C are dismissed because they are central to this MVP.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest credible implementation direction?**
- A) Persist optional accepted synthesized companion fields on review cards and read/render them on review detail.
- B) Recompute synthesis on every read.
- C) Concatenate synthesis into `feedback_text`.
> Recommendation: A — it is stable, truthful, and backward compatible. B is dismissed because it makes reads probabilistic. C is dismissed because it collapses additive and deterministic truth.
> **Selected: A**

**Q2: What is the safest public card contract shape?**
- A) Keep `feedback_text` unchanged and add optional additive companion plus minimal provenance/state.
- B) Replace `feedback_text` entirely.
- C) Expose internal rejection taxonomy directly.
> Recommendation: A — it is the narrowest safe contract. B is dismissed because it breaks fallback truth. C is dismissed because it leaks internal mechanics without product need.
> **Selected: A**

**Q3: Which surfaces are definitely in scope?**
- A) Persistence, repository/read path, detail API, and review-detail rendering.
- B) Frontend only.
- C) Backend only.
> Recommendation: A — this is one end-to-end truth contract. B and C are dismissed because each leaves the ship claim incomplete.
> **Selected: A**

**Q4: Which surfaces are definitely out of scope unless proven necessary later?**
- A) Exports and review history/list.
- B) Backward compatibility.
- C) Per-card fail-closed behavior.
> Recommendation: A — they are the safest deferment. B and C are dismissed because they are core constraints.
> **Selected: A**

**Q5: What mixed-state behavior should MVP support?**
- A) Some cards show companions while other cards in the same review remain deterministic-only.
- B) All cards must either all show synthesis or none do.
- C) The page should hide cards without synthesis.
> Recommendation: A — it matches the per-card fail-closed invariant. B and C are dismissed because they falsely elevate additive behavior over deterministic truth.
> **Selected: A**

## Section 5 — Constraints

**Q1: What must remain deterministic SSOT?**
- A) `pipeline_v1` findings, ratings, and traceability.
- B) The persisted companion text.
- C) Frontend presentation state.
> Recommendation: A — it is non-negotiable. B and C are dismissed because they are downstream artifacts.
> **Selected: A**

**Q2: What must remain the fallback truth?**
- A) Deterministic `feedback_text`.
- B) Synthesized companion text.
- C) A generic unavailable message.
> Recommendation: A — it preserves truthful degradation. B and C are dismissed because they are not authoritative review content.
> **Selected: A**

**Q3: How should additive synthesis be separated?**
- A) Separate persisted/API/UI fields, clearly labeled as additive.
- B) Inline merged into deterministic text.
- C) Hidden unless a debug flag is set.
> Recommendation: A — it makes the boundary visible and auditable. B and C are dismissed because they either blur truth or fail the user-visible mission.
> **Selected: A**

**Q4: What backward-compatibility rule must hold?**
- A) Existing reviews with no synthesis data must still read and render cleanly.
- B) Only newly created reviews need to work.
- C) Old reviews can show errors until migrated manually.
> Recommendation: A — it is essential for a production rollout. B and C are dismissed because they create broken history.
> **Selected: A**

**Q5: What execution discipline must planning preserve?**
- A) Split implementation into atomic tasks of three files or fewer and use TDD for behavior changes.
- B) Bundle the whole vertical slice at once for speed.
- C) Skip RED tests for migrations and read paths.
> Recommendation: A — it aligns with AGENTS.md and keeps risk contained. B and C are dismissed because they weaken control over a cross-layer change.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the highest hidden-coupling risk?**
- A) Choosing a persistence shape that silently forces wider read/API/frontend churn.
- B) The page label wording.
- C) The current branch name.
> Recommendation: A — it directly affects scope and safety. B and C are dismissed because they are low-impact.
> **Selected: A**

**Q2: What is the biggest product honesty risk?**
- A) Making synthesis look authoritative or deterministic.
- B) Rendering deterministic feedback too clearly.
- C) Being too explicit about additive separation.
> Recommendation: A — this is the trust failure to avoid. B and C are dismissed because clarity is a benefit here.
> **Selected: A**

**Q3: What is the main backward-compatibility risk?**
- A) Assuming every card or review has synthesis data.
- B) Keeping old deterministic cards working.
- C) Supporting deterministic-only rendering.
> Recommendation: A — this is where read/UI bugs will show up. B and C are dismissed because they are the desired stable behavior.
> **Selected: A**

**Q4: What is the main scope-creep risk?**
- A) Pulling exports/history into MVP without proof they are necessary.
- B) Keeping scope limited to detail view.
- C) Preserving one WF with internal task splits.
> Recommendation: A — it is the likeliest avoidable widening. B and C are dismissed because they are the chosen constraint.
> **Selected: A**

**Q5: What should planning prove before any ship recommendation?**
- A) Mixed-state verification for accepted companion, absent companion, and deterministic-only legacy reviews.
- B) Only the happy path with accepted synthesis.
- C) Only schema migration success.
> Recommendation: A — it is the minimum honest evidence. B and C are dismissed because they leave real user states unproven.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: What exact surface is the MVP?**
- A) Structured review detail at `/app/reviews/[reviewId]`.
- B) All review read surfaces.
- C) The submit flow plus detail plus exports.
> Recommendation: A — it is the narrowest researcher-visible slice. B and C are dismissed because they widen the WF unnecessarily.
> **Selected: A**

**Q2: Which implementation order is safest?**
- A) Persistence contract, then read/API carry-through, then frontend rendering, then end-to-end verification.
- B) Frontend first, backend later.
- C) API first without deciding persistence.
> Recommendation: A — it follows data truth from storage to UI. B and C are dismissed because they encourage temporary or misleading states.
> **Selected: A**

**Q3: Are exports/history in MVP?**
- A) No, defer them unless planning proves they are required for truthful detail-page shipping.
- B) Yes, include both by default.
- C) Include exports but not history.
> Recommendation: A — it keeps the MVP tight and honest. B and C are dismissed because they add surfaces without first proving necessity.
> **Selected: A**

**Q4: What should the public response contract expose at minimum?**
- A) Deterministic `feedback_text` plus optional additive companion data for the same card.
- B) Only synthesized companion when available.
- C) Internal seam diagnostics.
> Recommendation: A — it is the narrowest safe card contract. B and C are dismissed because they either hide fallback truth or expose internal mechanics.
> **Selected: A**

**Q5: Should this remain one WF?**
- A) Yes, one WF with explicit internal task sequencing.
- B) No, split backend carry-through from frontend visibility.
- C) No, split detail view from detail export.
> Recommendation: A — the user-visible truth contract spans all required seams, while task-level splitting is enough to keep execution safe. B and C are dismissed because they would create awkward partial-closure states.
> **Selected: A**
