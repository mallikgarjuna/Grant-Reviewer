# WF-0019 — Add Loading & Empty States

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-18

---

## 1. Problem Statement

### Decisions (Section 1)
- Main UX issue: users see plain `Loading...` text with no progress affordance.
- Highest-friction moment: initial call list load on `/app` and review list/status loads.
- Primary impact: first-time users lose confidence and may abandon before submit.
- Empty-state gap: no onboarding guidance when calls or reviews are absent.
- Scope frame: improve loading/empty UX only; no API behavior changes.

### Summary
Current state feedback is too bare and does not guide users. MVP needs visible loading polish and intentional no-data onboarding.

## 2. Desired Outcome

### Decisions (Section 2)
- Success signal: no plain `Loading...` remains in core app flows.
- Behavior change: users understand what is happening and what to do next when no data exists.
- MVP quality bar: skeleton/shimmer loaders in key waits and explicit empty-state guidance.
- Completion evidence: manual route checks plus lint pass.
- Constraint: keep work UI-only and consistent with existing styling.

### Summary
Outcome is a calmer, guided UX for waiting and no-data states that reduces confusion before launch.

## 3. Target User / Actor

### Decisions (Section 3)
- Primary actor: signed-in researcher using `/app` to submit or view reviews.
- Secondary actor: returning user with zero saved reviews on a fresh browser/device.
- Pain point: uncertainty during load and no direction when data is absent.
- Context: call selection load, review list load, and review detail fetch states.
- Exclusion: admin ingestion and backend operators are out of scope.

### Summary
This workflow serves end users in the frontend app during state transitions and first-use empty contexts.

## 4. Rough Idea (Unstructured Thinking)

### Decisions (Section 4)
- Replace plain loading text with lightweight skeleton blocks that mirror final layout.
- Add empty-state cards with short explanation and a clear CTA to the next action.
- Keep copy concise and practical (what happened + what to do now).
- Reuse existing UI primitives where possible; avoid a design-system expansion.
- Apply changes only where users currently hit plain loading or blank states.

### Summary
The simplest approach is targeted UI-state components in existing pages, not a broad refactor.

## 5. Constraints

### Decisions (Section 5)
- Time constraint: complete within one focused WF with small diffs.
- Technical constraint: no backend/API/schema changes.
- UX constraint: preserve current app information architecture and route behavior.
- Verification constraint: lint plus manual smoke checks on updated states.
- Process constraint: commit per phase and per implementation task.

### Summary
Constraints force a fast frontend-only improvement with minimal system risk.

## 6. Risks / Unknowns

### Decisions (Section 6)
- Risk: loaders may not match real layout and cause visual jump.
- Risk: empty-state CTAs could point users to the wrong next step.
- Unknown: all locations of plain loading copy may not be obvious initially.
- Validation focus: route-by-route scan for loading and empty UX coverage.
- Rework trigger: if empty-state wording creates user ambiguity in manual checks.

### Summary
Main risks are incomplete coverage and misleading guidance; both are manageable with targeted verification.

## 7. MVP Definition

### Decisions (Section 7)
- Must-have: remove plain loading text from key app routes with skeleton/shimmer equivalents.
- Must-have: add onboarding empty states for no calls/no reviews contexts.
- Must-have: include clear next-action CTA in each empty state.
- Defer: advanced animations, telemetry instrumentation, and full global state-component library.
- Done condition: updated flows verified manually and lint passes.

### Summary
MVP is polished state UX in current core pages, not a generalized UI framework effort.

## 8. Explicit Non-Goals

### Decisions (Section 8)
- No backend contract or async workflow changes.
- No legal content work (`/terms`, `/privacy`) in this WF.
- No broad accessibility remediation sweep beyond existing behavior.
- No node selector redesign.
- No call data ingestion work.

### Summary
This WF stays tightly scoped to loading and empty-state user experience polish.
