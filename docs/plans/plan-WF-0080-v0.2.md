<!-- docs/plans/plan-WF-0080-v0.2.md -->
# Plan — WF-0080 Production MVP Launch Wedge

Status: Draft helper plan
WF ID assumption: `WF-0080` is the next available WF after `WF-0079`
Purpose: reusable reference for future Phase 0/1/2 runners

## Important Usage Note

This file is a planning helper, not a workflow artifact substitute.
Use it to seed the next WF, then create the canonical brainstorm/PRD/task/walkthrough artifacts under `docs/` per the workflow system.

Suggested future-chat prompt:

```text
Use @docs/plans/plan-WF-0080-v0.2.md
Start WF-0080 using the standard phase runners.
Treat the plan as intent/reference only.
Generate the canonical WF artifacts from it.
```

## Intent

Change the trajectory from an architecture-first refactor to a **production MVP launch wedge**.
The primary outcome of this workflow is not a cleaner internal model. The primary outcome is that a real researcher can submit a proposal snippet for one locked call, wait safely, read the response, trust the feedback enough to revise, and complete that loop without support intervention.

This WF should assume the current engine contracts remain the source of truth unless a specific launch blocker proves otherwise.
Deep persistence redesign is deferred by default.

## Repo Reality Anchor

Current researcher-visible flow:

```text
/app
  -> /api/bff/structured-review
  -> backend /api/structured-review
  -> StructuredReviewerService
  -> current deterministic card path
  -> optional additive companion text
  -> /app/reviews/[reviewId]
```

Current output unit:

```text
review -> cards[]
```

Current architecture reality to preserve unless proven insufficient:

- `DiagnosticFinding v1` remains the engine SSOT.
- `ReviewCard` remains the compatibility surface for persistence and researcher-visible detail rendering.
- `WF-0079` already proved one narrow researcher-visible additive carry-through on the review-detail surface.
- Do not introduce a new `ReviewFinding` persistence hierarchy in this WF unless a concrete launch blocker cannot be solved additively.

## Outcome Definition

The sufficient outcome is a launchable researcher experience for one tightly bounded call wedge.

That means:

- the UI surfaces the most important feedback first
- the UI can gracefully show evidence when needed without forcing a dense compliance reading experience
- waiting, timeout, retry, and quota states are understandable
- operators can diagnose failed or suspicious sessions without inventing a separate admin platform
- launch usefulness can be measured from real researcher sessions

This WF is complete only if it improves actual ship readiness, not just architecture cleanliness.

## Scope Lock

### In scope

- one explicit call wedge, named in Phase 0 and preserved unchanged through closure
- one happy-path submit-to-detail review flow
- one review-detail reading experience
- minimum launch guardrails required to let a small cohort use the product safely
- one bounded usefulness-capture mechanism

### Out of scope by default

- new review persistence hierarchies
- multi-call generalization
- reviews-list/history redesign
- export redesign
- subordinate-prompt-level UI atomization
- generic internal platformization for support/admin use cases

### Stop-if conditions

Stop and split into a separate WF if Phase 1 or Phase 2 discovers any of the following:

- the launch wedge cannot be delivered without touching more than one funded-call wedge
- the chosen UI improvement requires a new top-level persistence model rather than additive carry-through
- auth/onboarding, quota, privacy, or support replay each need materially different architecture and cannot fit as narrow guarded slices
- the task plan cannot maintain the project rule of atomic tasks with roughly three files or fewer per task

## Required Product Decisions for Phase 0

Phase 0 must lock the following before any implementation-ready recommendation:

1. **Call wedge**
   - name the exact call code
   - explain why this is the launch wedge
   - list what other calls are explicitly deferred
2. **Primary researcher job-to-be-done**
   - what exact researcher outcome this wedge helps complete
3. **Detail-page reading model**
   - what appears above the fold
   - how priority is determined
   - when evidence expands
   - how explicit positive states are shown
4. **Launch cohort gate**
   - simple auth or whitelist mechanism
   - who can access the wedge at launch
5. **Usefulness capture**
   - exact mechanism for collecting 5–10 researcher session signals
   - exact evidence artifact expected at closure

If these are still vague, the WF is not ready for Phase 1.

## Sufficient Contract Strategy

### 1. Keep existing persistence surfaces unless blocked

Default strategy:

- preserve `DiagnosticFinding v1` as engine truth
- preserve `ReviewCard` as persisted/displayed compatibility surface
- prefer additive detail projection over schema expansion
- if additive text is needed, use the already-approved narrow carry-through pattern instead of inventing a new hierarchy

Do not use vague escape hatches like “or equivalent extension” in the canonical WF artifacts. Phase 1 must pick one exact seam.

### 2. Add one bounded review-detail projection

The researcher-facing detail view should be improved through one bounded read model only.

Phase 1 must specify:

- where ranking happens
- what exact inputs ranking uses
- whether evidence expansion is deterministic-only or can include bounded additive text
- what fallback renders when synthesis is absent or rejected
- which existing fields remain the baseline truth

If the proposed detail projection needs whole-review reinterpretation, stop and split.

### 3. Add explicit pass / no-blocker states

Do not use empty arrays or silence as the primary human pass signal.

Phase 1 must define:

- exact labels for “requirements met” or “no critical blockers” states
- when those labels appear
- what evidence, if any, is still visible in those states
- how we avoid overstating confidence to the researcher

### 4. Add minimum launch guardrails only

The WF should include only the smallest guardrails required for a real small-cohort MVP launch.

The canonical artifacts must separate these into:

- **must ship in WF-0080**
- **acceptable follow-on WF**

Candidate guardrails to classify:

- access control for the launch cohort
- request quota or rate limit
- waiting / timeout / retry UX
- failure logging and trace correlation
- privacy / retention policy enforcement already required for launch
- bounded operator replay or support inspection surface

If a guardrail becomes a platform project, it is too large for this WF.

## Phase Targets

### Phase 0 target

Lock the wedge and reject architecture drift.

Phase 0 must answer:

- Why this call wedge first?
- Why this UX change is necessary for launch?
- Which operational risks are truly must-ship now?
- What is explicitly deferred even if desirable?

### Phase 1 target

Produce a product contract that is precise enough to generate atomic Phase 2 tasks.

Phase 1 must include:

- named call wedge
- named review-detail projection seam
- exact launch guardrails classified into must-ship vs deferred
- explicit usefulness gate with threshold and evidence artifact
- pass/fail ship bar with closure proofs, not aspirational language

### Phase 2 target

Split the WF into minimal, executable tasks with strong boundaries.

Each task must include:

- goal
- exact file surface
- out of scope
- stop-if condition
- session boundary guidance
- targeted acceptance criteria
- targeted verification command(s)

Do not allow Phase 2 to create umbrella tasks like “auth/onboarding and quota guardrails” unless the file surface is still narrow and the verification can prove both honestly.

## Recommended Task Shapes

The likely task order should be:

1. Review-detail priority/ranking projection on the existing detail surface
2. Review-detail explicit pass / no-blocker state rendering
3. Wait / timeout / retry UX on the structured-review happy path
4. Narrow launch-cohort access gate
5. Narrow quota / abuse-control gate
6. Logging / traceability slice for support diagnosis
7. Walkthrough closeout with end-to-end wedge proof and usefulness evidence

These are candidate shapes, not mandatory tasks. Phase 2 must still prove each slice can stay atomic.

## Must-Have Verification

Closure evidence must prove the launch wedge works in reality, not just in contracts.

Minimum proof categories:

- **End-to-end happy path:** one in-scope researcher can access the wedge, submit, wait, and view the result successfully
- **Protected-surface proof:** an out-of-cohort or over-quota user is blocked clearly and without downstream review execution
- **Timeout / degradation proof:** deterministic feedback path degrades honestly if additive synthesis fails or the request takes too long
- **Support trace proof:** operators can identify what happened for one failed or disputed session using the chosen narrow support surface
- **Usefulness gate proof:** the agreed 5–10 researcher-session mechanism exists and yields attributable evidence
- **Scope proof:** deferred surfaces remain unchanged unless explicitly approved

## Ship Bar

WF-0080 is only complete when all of the following are true:

- A real small-cohort researcher can securely submit a snippet for the locked call wedge.
- The UI handles waiting, timeout, and retry states without leaving the user confused.
- The review-detail page surfaces the most important feedback first and does not collapse into a dense compliance spreadsheet.
- At least one launch guardrail blocks misuse or runaway cost without relying on manual heroics.
- A support operator can inspect one problematic session well enough to explain what happened.
- We have explicit usefulness evidence from the agreed researcher-session mechanism.
- Closure includes pass/fail proof for each required verification row and names all deferred follow-on work.

## Explicit Non-Goals for WF-0080

- deep persistence refactoring
- multi-call generalization
- full admin console design
- full analytics platform work
- review history/list redesign
- export overhaul
- subordinate-prompt-level finding explosion

## Critical Guidance for Phase Runners

When using this helper plan to seed WF-0080:

- challenge any requirement that smells like platform-building instead of launch wedge closure
- prefer additive seams over replacement seams
- refuse vague wording like “improve trust,” “better UX,” or “support observability” without explicit proof surfaces
- force every Phase 1 claim into a Phase 2-verifiable boundary
- if a proposed task touches too many files or too many concerns, split it before proceeding
