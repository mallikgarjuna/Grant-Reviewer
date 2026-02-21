# WF-0017 — Auto Polling for Processing Reviews

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-18

---

## 1. Problem Statement

### Decisions (Section 1)
- Primary affected users: returning users running repeated submissions.
- Core pain: the flow feels broken when status does not update automatically.
- Main friction point: immediately after submit while review is in `PROCESSING`.
- Priority rationale: this is a pre-real-user trust issue and should be fixed before broader usage.
- WF focus: remove manual refresh by auto-checking status transitions only.

### Summary
The key problem is trust and clarity during the waiting window. Users should not need to manually refresh to discover completion or failure.

---

## 2. Desired Outcome

### Decisions (Section 2)
- Success signal: `PROCESSING` reviews auto-transition to terminal status (`COMPLETED/FAILED`) without manual refresh for most runs.
- Expected behavior shift: users wait on-page and trust automatic updates.
- MVP threshold: fixed-interval polling with a clear max-duration stop condition.
- Completion UX: auto-show completed state as soon as status changes.
- Timeout UX: if cap is reached, show a clear “still processing / try refresh” fallback state (without client-side failure claims).

### Summary
The desired outcome is reliable, bounded auto-polling that removes manual refresh as the default behavior while still handling long-running server processing safely.

---

## 3. Target User / Actor

### Decisions (Section 3)
- Primary actor: signed-in users actively waiting on newly submitted reviews.
- Current behavior to replace: repeated manual refresh after submit.
- Main frustration: uncertainty about whether processing is still active.
- Primary usage context for MVP decisions: desktop single-tab wait flow.
- De-prioritized actor: first-time anonymous landing visitors.

### Summary
This WF is centered on the authenticated in-app wait experience immediately after submission, not on marketing-entry or multi-surface behavior.

---

## 4. Rough Idea (Unstructured Thinking)

### Decisions (Section 4)
- MVP direction: client-side interval polling using the existing status-fetch path.
- Poll start trigger: immediately for reviews in `PROCESSING` after submit (and when opening a processing review page).
- Interval: every 3 seconds with bounded total duration.
- Stop conditions: terminal status, component/page unmount, or max duration cap.
- Long-running fallback: stop at cap and show clear next-step guidance.

### Summary
The rough idea is a bounded client-driven polling loop that requires no new real-time transport and preserves existing backend contracts.

---

## 5. Constraints

### Decisions (Section 5)
- Delivery constraint: target a single focused implementation session.
- Technical constraint: reuse existing backend status endpoint; no new API surface for MVP.
- Scope boundary: keep WF-0017 limited to polling behavior (do not absorb submit-flow hardening).
- Efficiency constraint: enforce safe cadence and a hard polling cap.
- Verification constraint: include targeted frontend verification for transition and stop behavior.

### Summary
This WF is intentionally narrow, backend-compatible, and bounded to reduce risk while delivering immediate UX trust gains.

---

## 6. Risks / Unknowns

### Decisions (Section 6)
- Fragile assumption: current status endpoint behavior remains reliable under bounded polling.
- Primary implementation risk: polling lifecycle bugs (duplicate intervals, cleanup misses).
- Early validation focus: correct state transition detection and stop semantics.
- Rework risk if ignored: ambiguous timeout/fallback messaging.
- Operational risk: request volume inflation from misconfigured polling cadence.

### Summary
Main risk management focuses on lifecycle correctness and bounded request behavior, not infrastructure expansion.

---

## 7. MVP Definition

### Decisions (Section 7)
- Must-have slice: bounded auto-polling for `PROCESSING` reviews with automatic terminal-state handling and timeout fallback guidance.
- Explicitly deferred: submit-flow hardening items outside polling scope.
- Explicit exclusion: websocket/SSE and backend contract redesign.
- Minimum acceptance: terminal transitions, max-cap fallback behavior, and polling cleanup on unmount/navigation.
- “Done” signal for implementation phase: verified in-app processing-to-terminal flow plus long-processing capped fallback behavior.

### Summary
The MVP scope is a narrow, behavior-focused reliability improvement to the waiting experience, with strict avoidance of adjacent UX redesign work.

---

## 8. Explicit Non-Goals

### Decisions (Section 8)
- Postponed feature: real-time transport (websocket/SSE).
- Out-of-scope adjacent UX: submit-flow redesign items tracked separately from polling.
- Non-goal for this WF: new analytics/monitoring initiatives specific to polling.
- Deferred cross-cutting work: system-wide loading/empty-state redesign.
- Keep separate backlog path: submit-flow hardening remains a distinct follow-up WF candidate.

### Summary
WF-0017 is strictly focused on bounded auto-polling behavior for review processing status. It intentionally avoids adjacent UX and infrastructure expansions.
