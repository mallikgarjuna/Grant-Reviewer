<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-14

## Preflight Step 1 — Long-Form Problem Intake

Source: user kickoff prompt for WF-0080.

- The workflow must create canonical artifacts for a production MVP launch wedge researchers can actually use.
- Scope is locked to one explicit call wedge, one happy-path submit-to-detail flow, and one review-detail experience.
- Additive seams are preferred over replacement seams, and a new persistence hierarchy is disallowed unless a concrete launch blocker proves it necessary.
- Phase 1 claims must become Phase 2-verifiable boundaries.
- Launch guardrails must be classified into `must ship in WF-0080` vs deferred follow-on work.
- Closure must require usefulness evidence from 5–10 researcher sessions.

## Preflight Step 2 — Repo Reality Snapshot

- Verified the structured-review entry path through the BFF submit route and `StructuredReviewerService.generate_structured_review_pipeline_v1`.
- Verified existing backend launch-adjacent gates in `backend/main.py`: `REVIEWS_DISABLED` and `QUOTA_EXCEEDED`.
- Verified the review-detail BFF normalizes and preserves optional trust fields such as `synthesized_companion_text`.
- Verified the review-detail page already contains retry UX and a deterministic-only export action that explicitly excludes additive companion guidance.
- Verified the structured-review service already contains single-call conditional seams, especially around `ERC-2026-PoC`, which is a likely wedge candidate but not yet approved in this brainstorm.

## Section 1 — Problem Statement

**Q1: Which exact call should WF-0080 lock as the launch wedge?**
- A) `ERC-2026-PoC`
  - Strongest existing single-call seam in current structured-review service and additive behavior.
- B) `MSCA-PF-2025`
  - Already used as a proof call in review-detail trust surfaces, but less obviously aligned to the current additive seams.
- C) `nwo_veni_2025_preproposal`
  - Historically important, but more likely to reopen older assumptions and cross-call drift.
> Recommendation: A — it appears to be the narrowest additive seam already present in the repo. B is less clearly aligned to the current single-call conditional behavior. C risks reopening legacy assumptions and broadening the wedge.
> **Selected: A**

**Q2: What is the primary launch-blocking problem we are solving first?**
- A) Researchers can submit, but the resulting review-detail experience is not yet trustworthy/useful enough to revise from.
- B) Researchers cannot reliably complete the submit-to-detail flow without confusion around waiting, retry, and failure states.
- C) Both are equal first-order blockers and WF-0080 must treat them as co-primary.
> Recommendation: C — a production wedge fails if either the journey is confusing or the detail view is not useful enough to act on. A alone would underplay operational launch friction; B alone would treat usefulness as optional.
> **Selected: C**

**Q3: What exact researcher job-to-be-done should this wedge optimize for?**
- A) “I want fast, grounded feedback on one proposal snippet for one call so I can make my next revision decision.”
- B) “I want a comprehensive submission-readiness assessment across my whole proposal.”
- C) “I want a reusable AI coach for multiple calls and drafts.”
> Recommendation: A — it is the narrowest real researcher outcome that fits a launch wedge. B and C broaden the product into full-proposal evaluation or generalized coaching before one honest wedge is proven.
> **Selected: A**

**Q4: What should count as the main product failure in Phase 0 if we do nothing?**
- A) The app technically works, but researchers still would not trust it enough to use it without support.
- B) The app cannot handle small-cohort launch traffic or abuse safely.
- C) The internal architecture remains too messy to scale later.
> Recommendation: A — this WF is about product launch truth, not architecture cleanup. B matters, but only as a launch guardrail. C is specifically the drift this workflow is supposed to resist.
> **Selected: A**

**Q5: Which scope statement best protects us from platform-building drift?**
- A) Lock one call, one submit-to-detail happy path, one review-detail reading model, and only the minimum launch guardrails needed for a 5-10 researcher cohort.
- B) Lock one call now, but design guardrails and persistence so all supported calls can adopt them immediately after.
- C) Use the wedge to clean up the underlying review platform so later launches are easier.
> Recommendation: A — it keeps the workflow honest and falsifiable. B and C are platform-building in nicer words and would likely reopen broad seams before usefulness is proven.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What measurable change should define success for this MVP wedge?**
- A) At least 5 of 10 researcher sessions complete submit-to-detail and report the feedback was useful enough to inform a next revision step.
- B) Median review generation time stays under a fixed threshold for all sessions.
- C) Operators report fewer support questions than before.
> Recommendation: A — usefulness plus end-to-end completion is the actual launch claim. B and C are useful secondary metrics, but neither proves the wedge helped a researcher decide what to revise.
> **Selected: A**

**Q2: What should the researcher be able to do immediately after reading review detail?**
- A) Identify the top 1-3 issues to act on next, with enough evidence to trust why they surfaced.
- B) Read every evaluation criterion and element in full before deciding anything.
- C) Export a full review packet for offline analysis.
> Recommendation: A — it targets the actual revision decision. B makes the MVP too dense, and C turns the wedge into an export product rather than a usable reading experience.
> **Selected: A**

**Q3: What should “good enough for MVP” mean for the review-detail reading model?**
- A) Above the fold shows prioritized feedback first, clear pass/no-blocker states when applicable, and expandable evidence only when needed.
- B) Above the fold shows all cards with full evidence expanded by default.
- C) Above the fold shows only an overall summary; detailed cards can wait for later.
> Recommendation: A — it balances actionability with traceability. B overloads the researcher immediately; C hides too much grounding for a trust-sensitive product.
> **Selected: A**

**Q4: What should the launch usefulness artifact be?**
- A) A small structured session log tying each of 5-10 researcher sessions to call, outcome, usefulness rating, and next-step evidence.
- B) A general retrospective note after launch.
- C) Analytics events only.
> Recommendation: A — it is attributable, reviewable, and still small enough for an MVP. B is too vague and retrospective; C lacks the qualitative “what did they revise next?” proof.
> **Selected: A**

**Q5: What should count as failure even if the system technically returns a review?**
- A) Researchers still cannot tell what to do next or why the top feedback matters.
- B) The review takes a bit longer than ideal.
- C) Operators need to inspect logs occasionally.
> Recommendation: A — the wedge exists to create next-step clarity. B and C may matter operationally, but they do not define product usefulness by themselves.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary target actor for this launch wedge?**
- A) Any authenticated user who reaches the app.
- B) An invited small cohort of researchers actively working on `ERC-2026-PoC`.
- C) Internal admins and maintainers validating the product.
> Recommendation: B — it matches the launch-wedge goal and supports attributable usefulness evidence. A is too broad for a first production wedge; C would turn the launch into an internal proof instead of a real researcher workflow.
> **Selected: B**

**Q2: What launch-cohort gate should we prefer by default?**
- A) An authenticated allowlist or equivalent narrow cohort gate on the existing auth/BFF/API seam.
- B) An invite-request flow with custom onboarding screens.
- C) Open access with monitoring only.
> Recommendation: A — it is the narrowest honest launch control. B adds onboarding product work; C removes the cohort boundary needed for safe MVP launch.
> **Selected: A**

**Q3: What should happen for out-of-cohort users?**
- A) They should be blocked clearly before review execution starts.
- B) They may enter the flow but be blocked only after backend validation.
- C) They may use the wedge until quota problems show up.
> Recommendation: A — the product should fail closed before cost-bearing or side-effecting work. B and C allow ambiguous or wasteful partial execution.
> **Selected: A**

**Q4: What secondary actor should Phase 0 care about?**
- A) A narrow support/maintainer actor who must explain one failed or disputed session.
- B) A full operator team needing dashboards and cohort management tools.
- C) No secondary actor; support can be manual and opaque.
> Recommendation: A — some operator visibility is necessary for launch, but B is admin-platform drift and C is unrealistic for a production wedge.
> **Selected: A**

**Q5: What researcher workflow shape are we optimizing for?**
- A) One snippet-review moment that helps the researcher choose the next revision step.
- B) Full-proposal lifecycle management across multiple drafts.
- C) A reusable AI coaching workspace across calls.
> Recommendation: A — it is the smallest meaningful user job. B and C would expand the product surface far beyond this wedge.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What implementation direction best fits the wedge without drifting into architecture cleanup?**
- A) Keep the current submit and detail surfaces, and add one bounded review-detail projection plus the minimum launch guardrails.
- B) Introduce a new review persistence hierarchy tailored to launch UX.
- C) Pause launch work and first unify the underlying platform architecture.
> Recommendation: A — it matches the additive-seam rule and keeps the wedge grounded in current repo reality. B and C would replace seams before proving they are blockers.
> **Selected: A**

**Q2: How should the review-detail experience handle density?**
- A) Show prioritized issues first with optional evidence expansion.
- B) Show every card and every evidence field at once.
- C) Hide details and rely mostly on a summary.
> Recommendation: A — it helps the researcher act quickly without discarding grounding. B overwhelms; C risks sounding generic and ungrounded.
> **Selected: A**

**Q3: How should positive states appear?**
- A) Use explicit pass/no-critical-blocker states with bounded wording and optional supporting evidence.
- B) Let absence of critical cards imply success silently.
- C) Show celebratory success language with minimal caveats.
> Recommendation: A — it avoids both ambiguity and overclaiming. B is too easy to misread; C risks overstating confidence.
> **Selected: A**

**Q4: How should waiting/timeout/retry be treated in MVP?**
- A) As part of the core submit-to-detail product contract for this single wedge.
- B) As backend reliability work that can be deferred from the user experience.
- C) As a future admin concern.
> Recommendation: A — the user cannot complete the wedge without understanding these states. B and C understate a direct launch blocker.
> **Selected: A**

**Q5: What support surface should we prefer?**
- A) Narrow trace correlation and failure categorization tied to one session.
- B) A new operator console for inspecting all launch activity.
- C) Manual guesswork from scattered logs if issues arise.
> Recommendation: A — it is the minimum honest support seam. B is platform work; C is not credible for a real launch.
> **Selected: A**

## Section 5 — Constraints

**Q1: What is the strongest scope constraint?**
- A) Stay locked to `ERC-2026-PoC` unless a concrete blocker forces a split.
- B) Design now for all currently supported calls.
- C) Leave the call open until implementation clarifies the easiest path.
> Recommendation: A — the wedge only works if the call boundary is fixed. B and C reopen scope too early.
> **Selected: A**

**Q2: What persistence constraint should govern planning?**
- A) Prefer additive seams and block any new persistence hierarchy unless a launch blocker proves it necessary.
- B) Allow a new hierarchy if it seems cleaner for future scale.
- C) Defer persistence decisions and let Phase 2 decide implicitly.
> Recommendation: A — it matches the explicit non-negotiable. B and C make it too easy to widen scope under the banner of cleanliness.
> **Selected: A**

**Q3: What task-planning discipline should this brainstorm enforce?**
- A) Atomic Phase 2 tasks with clear file boundaries, stop-if conditions, and targeted verification.
- B) One umbrella task for launch guardrails and one umbrella task for UX.
- C) Flexible task sizing so the implementer can decide later.
> Recommendation: A — this keeps Phase 2 honest and verifiable. B and C hide coupling and make stop-if boundaries too soft.
> **Selected: A**

**Q4: How should existing repo seams influence planning?**
- A) Reuse existing auth, BFF, backend, and review-detail seams wherever possible.
- B) Use the launch wedge as a reason to rework the core flow end to end.
- C) Ignore current seams so the plan can stay cleaner conceptually.
> Recommendation: A — the repo already has usable seams. B and C favor speculative redesign over shipping a real wedge.
> **Selected: A**

**Q5: What closure constraint is non-negotiable?**
- A) Attributable usefulness evidence from 5-10 real researcher sessions plus pass/fail launch proofs.
- B) A confident narrative that the wedge should help users.
- C) Internal team sign-off that the launch feels ready.
> Recommendation: A — it is the only option that makes the launch claim auditable. B and C are too subjective.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: Which assumption is most fragile?**
- A) `ERC-2026-PoC` can ship as one honest wedge without forcing broader platform work.
- B) Researchers will naturally understand any review-detail improvement we show them.
- C) The launch cohort will tolerate missing support visibility.
> Recommendation: A — if this assumption fails, the whole wedge boundary may have to split. B and C are important, but they are downstream of the fundamental scope bet.
> **Selected: A**

**Q2: What must be validated early about the reading model?**
- A) That prioritization can be built from existing review truth plus bounded additive seams, without whole-review reinterpretation.
- B) That we can eventually add richer exports.
- C) That every possible evidence field can be rendered immediately.
> Recommendation: A — it is the narrowest make-or-break question for the review-detail contract. B and C are follow-on concerns.
> **Selected: A**

**Q3: Which guardrail question is riskiest if left vague?**
- A) Exactly which guardrails are must-ship now versus deferred.
- B) Whether we might someday build a better admin console.
- C) Whether cohort members prefer one copy variant over another.
> Recommendation: A — guardrail vagueness is how launch-readiness plans silently sprawl or overclaim safety.
> **Selected: A**

**Q4: What could make the usefulness gate fake?**
- A) Non-attributable sessions or vague definitions of “useful.”
- B) Taking a few more days to collect data.
- C) Asking operators for their impressions instead of researchers.
> Recommendation: A — without attributable evidence and a clear usefulness question, the gate becomes theater. B is schedule pressure, not evidence corruption. C is weak evidence, but still a symptom of A.
> **Selected: A**

**Q5: What process risk should the workflow explicitly guard against?**
- A) Platform-building drift hidden inside “launch readiness.”
- B) Slightly repetitive wording across artifacts.
- C) Having to say “defer” to desirable ideas.
> Recommendation: A — this is the dominant failure mode. B and C are minor compared with silent scope expansion.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: If limited to 2-3 days, what absolutely must exist?**
- A) One invited `ERC-2026-PoC` researcher can access the wedge, submit, wait safely, open detail, and understand the top next actions.
- B) Every likely launch follow-on is scaffolded for later.
- C) A generalized framework for future calls.
> Recommendation: A — it defines a real wedge. B and C are future leverage, not launch reality.
> **Selected: A**

**Q2: Which guardrails belong in `must ship in WF-0080` by default?**
- A) Cohort gate, one cost-control seam, honest waiting/timeout/retry UX, narrow support traceability, usefulness capture, and any already-required privacy/retention enforcement for the cohort.
- B) Only the UX states; guardrails can follow once the product feels useful.
- C) A broad admin and onboarding layer so launch operations are future-proof.
> Recommendation: A — it is the minimum set that makes the wedge launchable without support heroics. B under-protects the launch; C is platform-building.
> **Selected: A**

**Q3: What should be deferred by default?**
- A) Multi-call generalization, review-history/list redesign, broad export redesign, new persistence hierarchies, and generalized admin platforms.
- B) Nothing; launch readiness should cover all adjacent surfaces.
- C) Only backend cleanup, while UI and admin additions stay in scope.
> Recommendation: A — it keeps the wedge sharply bounded. B and C both reopen adjacent surfaces too easily.
> **Selected: A**

**Q4: How should page-local copy/export on the detail page be treated?**
- A) As an existing same-page truth boundary that must be handled honestly in the wedge.
- B) As out of scope because exports are generally deferred.
- C) As the main focus of the wedge.
> Recommendation: A — it already exists on the target surface, so deferring it vaguely would leave a truth gap. B is too coarse; C over-centers a secondary seam.
> **Selected: A**

**Q5: What is the right response if a guardrail turns into a platform project?**
- A) Stop and split into a follow-on WF rather than broadening WF-0080 silently.
- B) Keep going because launch readiness justifies broader scope.
- C) Remove the guardrail from must-ship without explanation.
> Recommendation: A — the workflow should fail closed on scope drift. B normalizes drift; C weakens launch honesty.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: What tempting feature must be postponed?**
- A) A generalized cross-call launch platform.
- B) Clear pass/no-blocker states on the target detail page.
- C) Honest timeout/retry messaging on the target path.
> Recommendation: A — B and C are core wedge needs, while A is classic platform drift.
> **Selected: A**

**Q2: What persistence move is explicitly out of scope by default?**
- A) Introducing a new review persistence hierarchy for launch UX.
- B) Adding bounded additive seams to current review truth.
- C) Verifying current persistence is sufficient.
> Recommendation: A — it matches the non-negotiable. B and C are the preferred route.
> **Selected: A**

**Q3: What support scope is explicitly out of scope?**
- A) A separate operator/admin application.
- B) Narrow trace correlation for one disputed session.
- C) Clear failure categories on the target flow.
> Recommendation: A — B and C are part of the launch wedge; A is a separate product.
> **Selected: A**

**Q4: What evidence shortcut is explicitly out of scope?**
- A) Declaring launch readiness without attributable researcher-session proof.
- B) Using a small structured session log.
- C) Recording pass/fail verification rows in the walkthrough.
> Recommendation: A — B and C are the desired evidence surfaces. A would make the launch claim unauditable.
> **Selected: A**

**Q5: What planning mindset should be rejected?**
- A) “Launch readiness” as a reason to smuggle in broad cleanup or future-proofing.
- B) Additive seams over replacement seams.
- C) One explicit call wedge first.
> Recommendation: A — B and C are the guardrails protecting the wedge. A is the mindset that causes silent scope drift.
> **Selected: A**
