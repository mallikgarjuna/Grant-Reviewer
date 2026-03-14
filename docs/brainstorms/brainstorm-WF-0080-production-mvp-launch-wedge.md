<!-- docs/brainstorms/brainstorm-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-14

Type: feature

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1–3 “Contract Notes / Non-obvious constraints” bullets and link to the relevant Q&A section header.
- `DiagnosticFinding v1` remains engine truth and `ReviewCard` remains the compatibility surface unless a concrete launch blocker proves otherwise.
- This workflow is launch-wedge planning, not architecture cleanup; any proposed persistence hierarchy replacement is out unless Phase 1 proves the current seams cannot ship the wedge additively.

---

## Long-Form Problem Intake

The product still behaves more like a proving ground than a production wedge researchers can trust for real proposal work. The current structured-review flow already spans `/app`, the BFF layer, the backend structured-review API, `StructuredReviewerService`, deterministic review cards, and the review-detail page. But that path is not yet locked as a small-cohort launchable experience for one explicit funding call.

The request for WF-0080 is to stop planning as though broad architecture cleanup is the MVP. Instead, the workflow must define the narrowest production wedge a real researcher can use end to end: submit one proposal snippet for one locked call, wait safely, open review detail, and decide whether the feedback is useful enough to revise. The detail experience must surface the most important feedback first, remain grounded in evaluation criteria and elements, and avoid collapsing into a dense compliance spreadsheet.

The non-negotiables sharpen the boundary. Scope must stay to one explicit call wedge, one happy-path submit-to-detail flow, and one review-detail experience. Additive seams are preferred over replacement seams. A new persistence hierarchy is disallowed unless a concrete launch blocker proves it necessary. Every Phase 1 claim must be testable in Phase 2, and the launch guardrails have to be split into `must ship in WF-0080` versus deferred follow-on work. Closure also requires a usefulness gate with explicit evidence from 5–10 researcher sessions.

Contract Notes / Non-obvious constraints:
- The wedge is only honest if both researcher-facing usefulness and minimum operational safety are present; a pretty detail view without launch guardrails is not enough.
- This WF is not allowed to quietly expand into multi-call platform building, admin-platform design, or persistence redesign.
- The helper plan is input only; canonical scope must live in the WF artifacts themselves.

---

## Repo Reality Snapshot (Read-Only)

- The live researcher path already exists as a bounded chain: `frontend/src/app/api/bff/structured-review/route.ts` proxies to `POST /api/structured-review`, which runs through `StructuredReviewerService.generate_structured_review_pipeline_v1`.
- The backend already enforces at least two launch-adjacent API gates in `backend/main.py`: `REVIEWS_DISABLED` and per-user `QUOTA_EXCEEDED`. That means guardrail planning should start from existing seams, not from a greenfield access-control design.
- The review-detail stack is already call-aware and additive in some places: `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` preserves backend trust fields and normalizes optional `synthesized_companion_text`, while the page renders grouped call-linked cards and already contains retry logic for failed reviews.
- The review-detail page still exports a deterministic text bundle labeled `PeerLens deterministic review export` and explicitly omits additive companion guidance. That is a real same-page truth boundary, so Phase 1 cannot defer “exports” vaguely if the launch wedge changes what researchers rely on on this page.
- `StructuredReviewerService` already contains call-scoped behavior toggles from earlier WFs, especially around `ERC-2026-PoC`. That suggests there is an existing single-call additive seam available, but it also raises a drift risk if WF-0080 tries to universalize before one wedge is proven useful.

Contract Notes / Non-obvious constraints:
- Existing seams already carry some launch behavior, so the default planning posture should be additive hardening of those seams rather than replacement.
- Review-detail truth includes page-local copy/export behavior because it already sits on the target surface.
- Existing quota/disable gates do not automatically make the product launch-ready; they only prove there are narrow seams to extend.

---

## 1. Problem Statement

- WF-0080 is locked to `ERC-2026-PoC` as the single production launch wedge. Other calls are explicitly deferred unless this wedge proves they are required for honest closure.
- The primary researcher job is narrow: submit one proposal snippet for one explicit call, receive grounded feedback, and decide what to revise next without support intervention.
- The launch blocker is two-part and co-primary: the submit-to-detail journey must be operationally understandable, and the resulting review-detail experience must be trustworthy and useful enough to act on.
- The core failure today is not that the repo lacks generic architecture. The core failure is that the product still does not clearly earn researcher trust for a real small-cohort launch on one call wedge.
- Scope is locked to one call, one happy-path submit-to-detail flow, one review-detail reading model, and only the smallest launch guardrails needed for a 5-10 researcher cohort.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 1)

Contract Notes / Non-obvious constraints:
- `ERC-2026-PoC` is the approved wedge because it appears to have the narrowest existing additive seam; Phase 1 must still prove this assumption against live boundaries.
- “Researcher can use it” means both journey clarity and detail usefulness; either failure blocks launch honesty.
- Multi-call readiness, generic AI coaching, and platform cleanup are explicitly out of scope for this workflow.

---

## 2. Desired Outcome

- Success is not “the API returns a review.” Success is that at least 5 of 10 invited researcher sessions complete the submit-to-detail flow and produce evidence that the feedback was useful enough to inform a next revision step.
- The review-detail page should help a researcher identify the top 1-3 issues to act on next, with enough supporting evidence to understand why those issues surfaced.
- The reading model should be action-first: above the fold shows at most the top 3 actionable cards, ordered from highest concern to lowest using existing card truth in this order: assessment status first, lowest rating next, and existing call/node order as the final tie-breaker.
- Evidence stays collapsed by default and expands per card only on demand, except for explicit failure states where the first visible card must already include enough summary context to explain why it is ranked first.
- An explicit `no critical blockers found` state appears only when no card is in a blocking or clearly weak state; the UI may still show lower-priority improvement cards underneath that positive state.
- The usefulness artifact at closure must be a `Usefulness Evidence Log` appendix in the walkthrough with 5-10 attributable session rows: session alias, date, researcher cohort/user, call code, snippet goal, completion outcome, top issue shown, usefulness rating (`useful` / `mixed` / `not useful`), stated next revision action, and evidence/note reference.
- A returned review still counts as failure if the researcher cannot tell what to do next or cannot tell why the system surfaced the top feedback.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 2)

Contract Notes / Non-obvious constraints:
- “Useful enough” must be evidenced per session, not inferred from launch optimism or operator anecdotes.
- The outcome is next-step clarity, not comprehensive proposal readiness coverage.
- Evidence expansion is part of trust, but default density must stay low enough for real researcher reading behavior.

---

## 3. Target User / Actor

- The primary user is an invited small-cohort researcher working on an `ERC-2026-PoC` proposal who needs grounded feedback on one proposal snippet before deciding the next revision step.
- The launch cohort is explicitly access-gated: an authenticated allowlist of approved cohort identities is checked at the existing BFF boundary before proxying review requests, with a mirrored fail-closed backend rejection for any direct signed API request that bypasses the BFF.
- The maintainer/operator is a secondary actor only to the extent needed to diagnose one failed or disputed session using narrow logs and trace correlation; WF-0080 must not grow into a separate admin platform.
- Out-of-cohort users should be blocked before downstream review execution starts. The launch wedge is not honest if access control happens only after cost-bearing work or partial side effects.
- The wedge serves a focused snippet-review moment, not whole-proposal management, review-history redesign, or generic coaching across calls.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 3)

Contract Notes / Non-obvious constraints:
- “Researcher” here means a real launch cohort member, not an internal tester pretending to be the end user.
- The cohort gate should reuse existing auth/request seams where possible rather than creating a separate onboarding subsystem.
- Support visibility is required, but only as a narrow launch operation seam.

---

## 4. Rough Idea (Unstructured Thinking)

- Keep the existing structured-review happy path as the backbone and improve launch readiness additively rather than by replacing review persistence or inventing a new review object hierarchy.
- Improve review-detail usefulness through one bounded projection layer on top of existing review truth, with deterministic cards and approved additive companion fields remaining the baseline sources rather than reinterpreting the whole review from scratch.
- The detail page should present prioritized issues first using existing card status/rating/order truth, then allow evidence expansion on demand, and show explicit positive states when no critical blockers are found so silence does not masquerade as success.
- Waiting, timeout, and retry behavior should be honest and legible on the current submit-to-detail journey. The goal is not generic job orchestration; it is a single trustworthy path for this wedge.
- Support diagnosis should stay narrow: traceable session identifiers, clear failure categories, and enough replay/inspection signal to explain one problematic session without manual heroics or a new back-office product.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 4)

Contract Notes / Non-obvious constraints:
- The preferred seam is additive projection over existing truth, not a new persistence hierarchy.
- A positive state must be explicit and bounded so the UI does not overstate confidence.
- If prioritization requires whole-review reinterpretation, the workflow should stop and split rather than hiding a major product rewrite inside “reading model.”

---

## 5. Constraints

- The wedge must stay locked to `ERC-2026-PoC`; multi-call generalization is deferred unless a concrete launch blocker proves otherwise.
- The workflow must prefer additive seams over replacement seams and must not introduce a new persistence hierarchy unless Phase 1 proves an existing launch blocker cannot be solved additively.
- Phase 2 tasks must be aggressively split into atomic units with clear file boundaries, stop-if conditions, and targeted verification. If the plan cannot stay roughly within the project’s atomic-task discipline, scope is too broad.
- The launch experience must fit existing auth, BFF, backend, and review-detail surfaces as much as possible. Broad onboarding systems, platformized admin surfaces, or generic orchestration layers violate the wedge constraint by default.
- Closure must include explicit usefulness evidence from 5-10 real researcher sessions and pass/fail proof rows for the launch bar; narrative confidence is not sufficient.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 5)

Contract Notes / Non-obvious constraints:
- The atomic-task rule is not bookkeeping trivia; it is a scope-drift detector.
- Existing launch-adjacent gates in the repo are starting points, not proof that the launch wedge is already safe.
- If privacy, quota, or access control turn into standalone systems, the workflow has drifted too far.

---

## 6. Risks / Unknowns

- The most fragile assumption is that `ERC-2026-PoC` is already the narrowest honest launch wedge. Phase 1 must prove the chosen call does not secretly require broader cross-call or persistence work.
- The detail-page prioritization model may drift into whole-review reinterpretation if it cannot be built from existing card truth plus bounded additive fields. That would be a stop-and-split condition, not an invitation to quietly broaden scope.
- The minimum launch guardrails may still be underspecified: access gate, quota/rate control, timeout handling, privacy/retention enforcement, and support traceability each need a clear must-ship vs defer decision.
- The default cost-control and privacy/retention choices must stay narrow or they will become hidden platform projects.
- The usefulness gate could become fake evidence if the sessions are not attributable, if the success question is vague, or if “useful” is defined after the fact.
- The biggest process risk is platform-building drift: using “launch readiness” to smuggle in multi-call support, generalized admin tooling, or cleanup of unrelated review architecture.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 6)

Contract Notes / Non-obvious constraints:
- The right response to a hidden platform dependency is to stop and split, not to normalize the drift.
- Session evidence must be attributable enough to survive adversarial review later.
- Honest timeout/degradation behavior is part of the product contract, not merely an ops concern.

---

## Open Questions / Deferred

- Other call wedges besides `ERC-2026-PoC` are deferred unless Phase 1 proves this launch wedge cannot ship honestly without broadening scope.
- Exact field names and response-shape details for the bounded review-detail projection remain open until Phase 1 names the seam precisely.
- Exact implementation seam for the mirrored backend cohort rejection remains open until Phase 1 validates the safest existing boundary.
- Exact verification commands and selectors for the walkthrough evidence rows remain open until Phase 2.

---

## 7. MVP Definition

- The MVP is one `ERC-2026-PoC` submit-to-detail path where an invited researcher can access the wedge, submit one snippet, wait safely, open one review-detail page, see the most important feedback first, and understand what to revise next.
- The review-detail experience must include a prioritized above-the-fold reading model, explicit pass/no-critical-blocker states, and expandable evidence. It must not require exhaustive reading of every criterion and element before the researcher can act.
- The default must-ship guardrails for WF-0080 are:
  - launch-cohort access gate at the existing auth/BFF/API boundary;
  - retain the existing per-user quota seam as the launch cost-control gate unless Phase 1 proves a narrower call-scoped request cap is needed;
  - honest waiting, timeout, and retry states on the happy path;
  - trace correlation plus enough support inspection to explain one failed or disputed session;
  - the usefulness-capture mechanism and closure artifact for 5-10 researcher sessions;
  - one explicit cohort privacy/retention rule: launch-session inputs/outputs may stay only in the existing review storage and support traces, and access to those records is limited to the designated maintainers for launch support and usefulness evaluation.
- The default deferred follow-on items are:
  - multi-call generalization;
  - review-history/list redesign;
  - broad export redesign beyond truthful treatment of existing page-local behavior on the target detail page;
  - new persistence hierarchies or broad contract rewrites;
  - generalized admin/operator platforms;
  - full onboarding systems beyond the narrow launch-cohort gate.
- If we only had 2-3 days, the product must still ship one honest wedge rather than a half-built platform. That means choosing the smallest set of changes that makes one researcher session real, safe enough, and measurably useful.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 7)

Contract Notes / Non-obvious constraints:
- The page-local copy/export behavior on review detail still has to be treated truthfully because it already exists on the target surface.
- “Must ship” means required to let a small cohort use the wedge without support heroics, not “nice to have before scale.”
- Any guardrail that expands into its own platform effort is evidence the workflow should split.

---

## 8. Explicit Non-Goals

- Building a generalized cross-call launch platform.
- Replacing `DiagnosticFinding v1` or `ReviewCard` with a new persistence hierarchy unless a concrete launch blocker proves the current surfaces cannot ship additively.
- Redesigning review history, review lists, or export products beyond the narrow truthfulness needs of the target detail page.
- Building a separate operator/admin application, broad onboarding funnel, or generalized support replay system.
- Claiming usefulness or launch readiness without attributable evidence from 5-10 researcher sessions and explicit pass/fail closure proofs.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0080-production-mvp-launch-wedge.md` (Section 8)

Contract Notes / Non-obvious constraints:
- “Platform hardening” is not an acceptable euphemism for reopened scope.
- A future WF may tackle broader launch infrastructure, but WF-0080 only earns that follow-on if it first proves one wedge is useful.

---

## Verification / Proceed Gate

- No proceed recommendation is valid unless Phase 1 names one exact review-detail projection seam, one exact launch cohort gate, one exact usefulness-capture artifact, and a must-ship vs deferred guardrail split.
- No proceed recommendation is valid if the proposed detail experience depends on a new persistence hierarchy or whole-review reinterpretation rather than additive use of current review truth.
- No ship recommendation is valid without explicit pass/fail proof for the locked `ERC-2026-PoC` wedge across the happy path, protected surfaces, timeout/degradation honesty, support traceability, and usefulness evidence.
- No ship recommendation is valid if 5-10 researcher sessions are mentioned only aspirationally rather than captured in a concrete evidence artifact.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| End-to-end happy-path wedge proof | Phase 2/3 verification plan + walkthrough evidence | `fail` (default until executed) | required | invited in-scope researcher can access, submit, wait, and open review detail successfully |
| Protected-surface proof | cohort-gate and quota/rate-limit proof | `fail` (default until executed) | required | out-of-cohort or over-limit access is blocked clearly before downstream review execution |
| Review-detail priority proof | detail-page render and ordering evidence | `fail` (default until executed) | required | top issues appear first and pass/no-critical-blocker states render explicitly |
| Timeout / degradation honesty proof | targeted timeout/additive-failure verification | `fail` (default until executed) | required | user sees honest fallback/retry behavior without fake success |
| Support trace proof | trace-correlation or narrow replay evidence | `fail` (default until executed) | required | one failed or disputed session can be explained without manual guesswork |
| Usefulness gate proof | structured 5-10 session evidence artifact | `fail` (default until executed) | required | each session is attributable to the locked wedge and records usefulness outcome |
| Scope proof | baseline-SHA/commit-range diff + deferred-surface check | `fail` (default until executed) | required | deferred surfaces remain unchanged unless explicitly approved |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 0 Part B risk audit | Required Phase 0 decisions still remained open for the detail ranking rule, cohort gate, usefulness artifact, and privacy obligation | blocking | lock each one in the brainstorm so Phase 1 cannot relitigate them as vague placeholders | closed | v0.3 now names exact defaults for the reading model, cohort gate, usefulness evidence log, and privacy/retention rule |
| Phase 0 Part B risk audit | Must-ship guardrail classification was still too soft because quota and privacy were described as generic options rather than explicit MVP choices | blocking | convert quota and privacy from conditional examples into explicit default must-ship guardrails, with follow-on escape only if Phase 1 proves a narrower existing seam is required | closed | v0.3 keeps existing quota as the default cost-control seam and names the cohort privacy/access rule directly |
| Phase 0 Part B risk audit | The brainstorm did not yet record the Phase 0 lock decisions in durable project memory/decision surfaces | non-blocking | append a narrow decision log entry and memory note summarizing the launch wedge lock | closed | prevents future Phase 1/2 drift in later chats |

---

## Appendix — Page Spec (MVP) (Optional; Type: page)

Trigger: only for `Type: page` workflows when UX/state/positioning is non-trivial.

Use `docs/templates/create-page-spec-prompt.md` to generate this appendix.

---

## Changelog

- v0.1 (2026-03-14): Initialized the canonical Phase 0 brainstorm, captured the long-form launch-wedge problem intake, and added a read-only repo snapshot to anchor later scope decisions.
- v0.2 (2026-03-14): Completed the Phase 0.1 brainstorm with a locked `ERC-2026-PoC` launch wedge, bounded MVP definition, must-ship vs deferred guardrail split, usefulness gate direction, and fail-closed proceed/ship evidence requirements.
- v0.3 (2026-03-14): Applied the Part B risk audit by locking the exact detail ranking model, the BFF-plus-backend cohort gate default, the walkthrough-based usefulness evidence log, and the explicit quota/privacy must-ship guardrails.
