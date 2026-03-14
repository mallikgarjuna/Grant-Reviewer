<!-- docs/plans/plan-WF-0080-v0.2.md -->
# Plan — WF-0080 Production MVP Launch Wedge

Status: Draft helper plan
WF ID assumption: `WF-0080` is the next available WF after `WF-0080` (or replacing it as the next active WF).
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

Change the trajectory from an "architectural atomization refactor" to a **"Production MVP Launch Wedge."**
The primary outcome of this workflow is that real researchers can submit a proposal snippet, wait, read the response, trust the feedback, and act on it—for a tightly scoped call set.

We will defer any deep database refactoring (like new `ReviewFinding` tables) unless explicitly proven necessary by real-world friction. We will solve the UX problems with additive UI detail projections off the existing Engine contracts.

## Repo Reality Anchor

Current researcher-visible flow:

```text
/app
  -> /api/bff/structured-review
  -> backend /api/structured-review
  -> StructuredReviewerService
  -> pipeline_v1 deterministic cards
  -> optional additive companion text
  -> /app/reviews/[reviewId]
```

Current output unit:
```text
review -> cards[] (DiagnosticFinding v1 projected as ReviewCard)
```

We will keep `DiagnosticFinding v1` as the SSOT and `ReviewCard` as the compatibility surface. We will not build a new `ReviewFinding` table for this launch.

## Outcome Definition

The new sufficient output unit is a highly usable, priority-ranked UI detail projection, protected by production-grade operational gates.

Instead of a dense list of micro-findings everywhere, the UI will present priority-ranked feedback. Unactionable passes ("requirements met") are handled gracefully, and the entire flow is locked to a single happy-path review flow.

## Sufficient Contract Changes

### 1. Hard Scope Lock (Launch Wedge)

- **One Funded-Call Wedge:** e.g., `ERC-2026-PoC` only. Do not attempt multi-call generalizations for this MVP unless strictly necessary to close the wedge.
- **One Happy-Path Review Flow:** Focus on the core submission to read-detail path.
- **One Detail-Page Experience:** Upgrade the read surface without changing the DB.

### 2. Additive Detail Projection (No Persistence Burn)

Do not break the current persistence models. Use the existing `StructuredReviewSynthesisService` to provide additive detail projection on the fly or at synthesis time, storing the result in the existing schema (e.g., as `synthesized_companion_text` on the card or an equivalent JSON extension) rather than standing up an entirely new database hierarchy.

- The LLM acts as a bounded writer over deterministic evidence, not the source of the new product model.
- The UI projects this into "priority-ranked feedback with optional expand-for-evidence." Researchers want direction, not a compliance spreadsheet.

### 3. Explicit UI States

- Remove "empty finding arrays" as the primary pass signal.
- Show explicit, human-readable pass states where it matters (e.g., "Ready for Submission" or "No critical blockers").
- Focus the researcher's attention only on the highest-severity deviations.

### 4. Production Operational Gates

We cannot ship without these minimum operational realities handled:

- **Auth/Onboarding:** A whitelist or simple auth gate to control the launch cohort.
- **Quota/Cost Guardrails:** Prevent a single user from running up massive OpenAI bills.
- **Latency Budget & Failure/Retry UX:** The engine takes time. Provide a clear waiting state, handle timeouts gracefully, and allow safe retries.
- **Support/Admin Replay Path:** A way for admins to see exactly what prompt was sent and what was returned if a researcher complains about hallucinations.
- **Privacy/Data Retention:** Ensure we are handling the submitted IP safely according to policy.
- **Observability:** Logging to trace failures.

## Minimal WF Slice Plan

### Phase 0 target

Lock the problem framing:

- The goal is Launch Readiness, not architecture refactoring.
- Scope is locked to one call wedge and one detail-page experience.
- Must include production operational gates (Auth, Quota, Latency UX).

### Phase 1 target

Lock the product contract:

- Define the specific UI detail projection (Priority ranking + optional evidence expansion) off existing `ReviewCard` structures.
- Define the specific production gates to build mapping (e.g., 5 requests per day limit rule).
- Define the Usefulness Gate metric (e.g., in-app thumbs up/down, or logging 5-10 specific researcher sessions).

### Phase 2 target

Split into minimal tasks.

Recommended implementation order:

1. UI Detail Projection redesign (Priority-ranked feedback using existing Card data + synthesis text).
2. Latency Budget & Failure/Retry UX in the frontend client.
3. Auth/Onboarding and Quota guardrails backend implementation.
4. Support logging/observability review.
5. Walkthrough closeout verifying the End-to-End wedge on the chosen call.

## Must-Have Verification

- **End-to-End Simulation:** A pseudo-researcher can log in, hit the quota limit, see correct UI errors, and successfully run a review within limits.
- **UI Degradation Test:** The UI degrades gracefully if the synthesis LLM times out but the deterministic engine succeeds.
- **Usefulness Gate Validation:** A mechanism exists (even if it's just logging) to capture the required 5-10 researcher session usefulness signals.

## Explicit Non-Goals for the Next WF

- Deep persistence refactoring (No new `ReviewFinding` table).
- Multi-call generalization.
- Slicing findings to a 1:1 subordinate prompt mapping.

## Ship Bar

The next WF is only complete when:
- A real researcher can securely submit a snippet for the locked call wedge.
- The UI handles the wait time elegantly and recovers from timeouts.
- The resulting feedback is prioritized, readable, and actionable (no dense compliance spreadsheets).
- We have a clear way to measure if the researcher found that session useful.
