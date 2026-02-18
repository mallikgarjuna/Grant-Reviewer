# WF-0018 — Harden Submit Flow UX

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-02-18

---

## 1. Problem Statement

### Decisions (Section 1)
- Primary user-visible failure: users do not know what action to take while processing is slow.
- Most impacted users: first-time signed-in users on their first submission.
- First optimization moment: immediately after submit while waiting for result.
- Highest-priority trust issue: the system appears stuck during slow processing.
- Scope frame: submit-flow UX hardening only (start-new, actionable slow-hint, auth round-trip validation).

### Summary
The core problem is post-submit uncertainty that reduces trust in the app. This WF should focus narrowly on submit-flow clarity and recovery actions, without expanding into broader UI cleanup.

---

## 2. Desired Outcome

### Decisions (Section 2)
- Success signal: reduce "stuck/confusing" moments by providing actionable waiting and recovery paths.
- Expected behavior change: users follow clear in-flow actions instead of random refresh/retry behavior.
- MVP threshold: start-new action works, slow-hint is actionable, and auth round-trip/sign-out redirect are verified.
- Completion evidence: manual end-to-end checks pass with no dead-end states.
- Scope discipline: only submit-flow hardening outcomes are included in this WF.

### Summary
Desired outcome is a predictable, confidence-building submit flow where users always have a clear next action.

---

## 3. Target User / Actor

### Decisions (Section 3)
- Primary actor: first-time signed-in users submitting their first review.
- Secondary actor: returning users running repeated attempts.
- Current behavior to replace: uncertainty-driven refreshes and ambiguous restart decisions.
- Primary frustration: unclear system state during slow processing.
- Context emphasis: in-app submission and immediate post-submit wait state.

### Summary
This WF is centered on signed-in users immediately after submission, where trust and continuity matter most.

---

## 4. Rough Idea (Unstructured Thinking)

### Decisions (Section 4)
- Provide a clear "Start new review" action that explicitly resets draft/attempt context.
- Convert slow-processing hint into actionable guidance with explicit next steps.
- Validate auth deep-link round-trip so users return to the intended flow state.
- Validate sign-out redirect behavior to avoid dead-end navigation states.
- Keep interaction model simple and consistent with existing app patterns.

### Summary
The rough direction is targeted UX hardening of key submit-flow transitions without redesigning surrounding screens.

---

## 5. Constraints

### Decisions (Section 5)
- Time constraint: keep implementation small and shippable in one focused WF.
- Technical constraint: reuse existing API contracts and frontend patterns.
- Scope constraint: do not absorb broader loading/empty-state or legal/accessibility initiatives.
- Verification constraint: require direct scenario-based checks for submit/wait/auth transitions.
- Process constraint: keep docs and WF status synchronized per phase gates.

### Summary
Constraints enforce a narrow, testable UX hardening slice with minimal architectural movement.

---

## 6. Risks / Unknowns

### Decisions (Section 6)
- Fragile assumption: current auth redirect mechanics consistently preserve intended destination.
- Main product risk: users may still misinterpret slow-processing state without clear action priority.
- Main implementation risk: reset/start-new behavior could accidentally preserve stale attempt data.
- Validation focus: confirm no dead-end states across submit, wait, sign-in return, and sign-out paths.
- Rework trigger: if auth/state continuity is inconsistent across environments.

### Summary
Top risks are continuity and clarity at flow boundaries; early manual verification is necessary to prevent regressions.

---

## 7. MVP Definition

### Decisions (Section 7)
- Must-have slice: working "Start new review" reset action, actionable slow-hint, and verified auth round-trip/sign-out redirects.
- Explicitly deferred: loading/empty state overhaul, legal pages, and broad accessibility pass.
- Delivery quality bar: no dead-end flow states in core submit scenarios.
- Verification bar: targeted end-to-end manual checks for all three hardening outcomes.
- Done condition: users can always continue intentionally (wait, restart, or re-enter flow) without ambiguity.

### Summary
MVP is a focused reliability layer on submit flow transitions that removes confusion and preserves user momentum.

---

## 8. Explicit Non-Goals

### Decisions (Section 8)
- Not adding new backend endpoints or transport mechanisms.
- Not redesigning full app-shell/navigation beyond submit-flow touchpoints.
- Not including legal/privacy expansion work.
- Not including full a11y audit work in this WF.
- Not incorporating unrelated P1/P2 backlog items.

### Summary
This WF intentionally excludes adjacent product polish and platform work to preserve fast, low-risk delivery.
