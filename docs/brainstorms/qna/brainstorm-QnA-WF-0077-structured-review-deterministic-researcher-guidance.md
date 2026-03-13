<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md -->
# WF-0077 — Structured Review Deterministic Researcher Guidance

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-13

## Preflight Step 1 — Long-Form Problem Intake

### Q1: What exact product defect is still open after WF-0076?
- A) Raw machine subordinate-prompt IDs still leak to the UI.
- B) The structured path is readable now, but still feels like a checklist instead of revision guidance.
- C) The structured path is missing canonical subordinate prompts entirely.
> Recommendation: B. A was largely closed by WF-0076 for ERC-2026-PoC, and C is false because the canonical subordinate prompts already exist and are now rendered. The remaining gap is actionability for researchers.
> Selected: B (user-provided direction)

### Q2: Which runtime path is in scope for this WF?
- A) The current structured `/app` path through `StructuredReviewerService` and `pipeline_v1`.
- B) The legacy OpenAI-backed `ReviewerService` path.
- C) Both paths together for consistency.
> Recommendation: A. B and C widen scope into a different behavior model and would hide whether deterministic guidance is actually sufficient.
> Selected: A (user-provided direction)

### Q3: What kind of improvement is explicitly allowed?
- A) Deterministic researcher-facing guidance grounded in existing evaluation criteria/elements and subordinate prompts.
- B) OpenAI-backed synthesis layered onto structured review.
- C) A broad mixed deterministic + LLM redesign.
> Recommendation: A. B and C are separate initiatives with different contracts, dependencies, and failure modes.
> Selected: A (user-provided direction)

## Preflight Step 2 — Repo Reality Snapshot

- `StructuredReviewerService._resolve_feedback_text_for_card` is already the place where machine-oriented feedback becomes user-facing copy for bounded calls.
- `evaluate_expectations` and `map_findings_to_review_cards` are lower-level, call-agnostic seams that should keep machine semantics stable.
- The frontend review page renders `feedback_text` directly, so backend contract quality matters more than frontend wording.
- Existing WF-0069 and WF-0076 tests already prove the service seam can carry deterministic actionability and subordinate-prompt presentation logic.
- The most likely MVP can stay within `backend/app/services/structured_reviewer_service.py` and `backend/tests/test_structured_reviewer_service.py`, with frontend changes deferred unless proven necessary.

## Section 1 — Problem Statement

### Q1: Which seam is currently failing the researcher-facing promise?
- A) The evaluator, because it still emits machine `reason` values.
- B) The service presentation seam, because it stops at readable prompt display rather than revision guidance.
- C) The frontend, because it renders the returned text too literally.
> Recommendation: B. A must stay machine-oriented for audit, and C is downstream of the backend contract. The failure is that the service chooses a prompt-list presentation instead of guidance.
> Selected: B

### Q2: What is the adversarial risk of changing evaluator or mapper instead?
- A) Minimal risk; those are cleaner central places.
- B) Hidden coupling across all calls and possible audit-contract regression.
- C) No risk if tests are updated.
> Recommendation: B. Those seams are generic and machine-signal oriented, so changing them would widen behavior and risk cross-call regressions.
> Selected: B

## Section 2 — Desired Outcome

### Q1: What should the output feel like after this WF?
- A) A cleaner list of review questions.
- B) Deterministic revision guidance telling the researcher what to strengthen or clarify.
- C) A synthesized paragraph with nuanced coaching.
> Recommendation: B. A does not solve the product gap, and C is future LLM-synthesis work.
> Selected: B

### Q2: What is the strongest bounded success signal?
- A) The UI looks more polished.
- B) Targeted assessed cards contain concise imperative guidance instead of raw machine text or question lists.
- C) More cards are produced.
> Recommendation: B. A is cosmetic and C is unrelated to usefulness.
> Selected: B

## Section 3 — Target User / Actor

### Q1: Who is the primary beneficiary?
- A) Researchers revising proposal sections in `/app`.
- B) Internal admins auditing traces.
- C) Prompt engineers tuning the legacy review path.
> Recommendation: A. B matters for boundary preservation, but the user value of this WF is researcher-facing revision help.
> Selected: A

## Section 4 — Rough Idea Exploration

### Q1: Where should deterministic guidance generation live first?
- A) In `backend/app/services/structured_reviewer_service.py`.
- B) In `backend/app/engine/compat/review_card_mapper.py`.
- C) In `frontend/src/app/app/reviews/[reviewId]/page.tsx`.
> Recommendation: A. The service already owns bounded user-facing transforms; B is too broad, and C is too late in the contract.
> Selected: A

### Q2: What is the narrowest safe implementation pattern?
- A) Replace raw machine reasons everywhere with new guidance strings.
- B) Add a call-scoped deterministic transform at the service seam that converts prompt-list output into short revision guidance while leaving raw machine reasons intact elsewhere.
- C) Introduce a new guidance engine abstraction across the pipeline.
> Recommendation: B. A breaks traceability boundaries and C is unnecessary architecture for a bounded MVP.
> Selected: B

### Q3: How should the work split to respect the 3-file limit?
- A) One backend test file, one backend service file, and only add a frontend file if backend proof shows a remaining UI gap.
- B) Touch backend evaluator, mapper, service, tests, and frontend together.
- C) Start in the frontend and backfill backend later.
> Recommendation: A. It preserves a tight task boundary and keeps the first slice testable.
> Selected: A

### Q4: What should happen if subordinate-prompt text is missing or too weak to support honest imperative guidance?
- A) Fabricate the most likely researcher guidance anyway so every card sounds equally actionable.
- B) Preserve the existing WF-0076 prompt rendering and unresolved-ID fallback for that card, and only emit stronger guidance where the source text supports it.
- C) Fail the whole review request.
> Recommendation: B. A would invent semantics and break traceability honesty, while C widens a presentation issue into a runtime failure. The bounded deterministic rule is to improve guidance only where the canonical prompt surface can support it honestly.
> Selected: B

## Section 5 — Constraints

### Q1: Which constraints are mandatory?
- A) Preserve raw machine `reason`, preserve fail-closed behavior, no OpenAI/LLM calls, use evaluation criteria/elements terminology.
- B) Only preserve UI behavior.
- C) None, because this is just presentation.
> Recommendation: A. The product boundary here is exactly what makes the work safe.
> Selected: A

## Section 6 — Risks / Unknowns

### Q1: What is the biggest failure mode?
- A) Guidance sounds nicer but is still not actionable.
- B) The backend tests become slower.
- C) The frontend still uses the old font stack.
> Recommendation: A. The core risk is pseudo-improvement: better copy shape without stronger revision value.
> Selected: A

### Q2: What future-work confusion must be prevented now?
- A) Confusing deterministic guidance transformation with future LLM synthesis.
- B) Confusing this WF with CSS cleanup.
- C) Confusing this WF with call-definition ingestion.
> Recommendation: A. That distinction drives both seam choice and proof standard.
> Selected: A

## Section 7 — MVP Definition

### Q1: What is the smallest honest MVP?
- A) Improve `feedback_text` generation at the service seam with TDD and stop unless a frontend gap remains.
- B) Deliver a full cross-call guidance engine plus UI rewrite.
- C) Add LLM synthesis for one call.
> Recommendation: A. B and C expand beyond the bounded deterministic objective.
> Selected: A

### Q1b: How should Phase 1 treat reuse beyond ERC-2026-PoC?
- A) Treat multi-call reuse as already approved because the service seam is shared.
- B) Keep ERC-2026-PoC as the only approved MVP slice; any widening requires explicit later-phase approval and regression proof.
- C) Decide during implementation based on convenience.
> Recommendation: B. The current artifact approves a bounded proof slice, not silent widening. Shared seam location is not approval to broaden call scope.
> Selected: B

### Q2: Why is this a separate WF from future LLM synthesis?
- A) Because the code owners are different.
- B) Because deterministic guidance and LLM synthesis have different contracts, tests, failure modes, rollback paths, and scope.
- C) Because OpenAI is unavailable.
> Recommendation: B. Even if OpenAI were available, the workflow should remain separate for architectural and verification reasons.
> Selected: B

## Section 8 — Explicit Non-Goals

### Q1: What must be deferred?
- A) Any OpenAI-backed synthesis, legacy review-path work, or engine-wide feedback redesign.
- B) The structured service seam.
- C) Existing traceability requirements.
> Recommendation: A. B is the MVP seam, and C is a hard invariant, not a deferrable feature.
> Selected: A
