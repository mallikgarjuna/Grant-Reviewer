# WF-0018 — Harden Submit Flow UX

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-02-18

## 1. In Scope

- Add a clear `Start new review` action from submit-related result/wait states.
- Ensure `Start new review` resets active draft/attempt context and lands on clean review creation start.
- Replace passive slow-processing hint copy with actionable guidance.
- Validate and harden auth deep-link round-trip continuity in submit flow.
- Validate and harden sign-out redirect behavior from submit-related views.
- Add targeted manual verification for submit/wait/restart/auth transition scenarios.

## 2. Out of Scope

- New backend endpoints, workers, or transport mechanisms.
- Broad app-shell or navigation redesign.
- Full loading/empty-state redesign.
- Legal/privacy content expansion.
- Full accessibility remediation sweep.

## 3. User / System Flow

Happy path:
1. Signed-in user submits review.
2. While waiting, user sees clear processing state with explicit next actions.
3. User can continue waiting or intentionally choose `Start new review`.
4. If user chooses `Start new review`, active draft/attempt state is cleared.
5. User lands at clean submission start without stale content or dead-end navigation.

Failure path A - stale state risk:
1. User selects `Start new review`.
2. Previous draft/attempt state is not fully cleared.
3. New flow incorrectly shows old content.
4. System must prevent this by explicit reset boundary and scenario verification.

Failure path B - auth round-trip mismatch:
1. User enters submit flow and auth interruption occurs.
2. After sign-in, user lands on wrong route or generic page.
3. User loses flow continuity.
4. System must preserve intended destination and return context.

Failure path C - sign-out redirect dead end:
1. User signs out from submit-related area.
2. Redirect lands on unusable/incorrect route.
3. User cannot recover flow quickly.
4. System must redirect to expected public entry point.

## 4. Functional Requirements

- FR1: `Start new review` action is visible in relevant submit-related states.
- FR2: Triggering `Start new review` clears current draft/attempt identifiers used by submit flow.
- FR3: After reset, user is routed to the base review creation step.
- FR4: Slow-processing message includes explicit next-step actions.
- FR5: Auth deep-link round-trip restores intended submit-flow destination.
- FR6: Sign-out from submit-related views redirects to defined public entry route.
- FR7: Submit-flow states must avoid dead-end routes/actions.
- FR8: Manual verification evidence is captured for all core scenarios in walkthrough.

## 5. Data & API Contracts

Request/response shapes:
- Reuse existing review creation/status/auth contracts; no new API surface is introduced.

Route contract assumptions:
- Clean submit start route: `/app/review/new` (or current equivalent create-review entry route in codebase).
- Public entry route after sign-out: `/` (marketing/home entry), unless current auth middleware contract defines a different canonical public route.

Validation rules:
- `Start new review` must clear current submit-flow draft/attempt context before navigation.
- Slow-processing UI must present at least one direct action (not passive informational copy only).
- Auth/sign-out transitions must land on predefined valid routes.

State transitions:
- submit in progress -> waiting state with actionable guidance
- waiting state -> start new review -> clean submit start
- auth interrupt -> sign-in success -> restored intended submit-flow route
- signed-in submit-related view -> sign out -> public entry route

## 6. Components / Modules

Boundaries and responsibilities:
- Submit/result UI components:
  - render `Start new review` action
  - render actionable slow-processing guidance
- Flow state management:
  - clear draft/attempt context on restart
  - enforce clean start boundary
- Auth routing integration:
  - preserve and restore deep-link return target
  - enforce sign-out redirect destination

Suggested file paths (to refine in Tasks phase):
- `frontend/src/app/app/...` submit/result flow pages/components
- `frontend/src/lib/...` flow-state/reset helpers
- `frontend/src/middleware.ts` or auth routing integration points (if needed)

## 7. Edge Cases

- Rapid repeat clicks on `Start new review` must not create inconsistent state.
- Restart during pending/processing UI must still produce clean reset.
- Returning user with existing local session artifacts should not inherit stale attempt after restart.
- Auth return target missing/invalid should fail safely to deterministic in-app entry.
- Sign-out redirect should remain correct regardless of originating submit subroute.

## 8. Telemetry (Minimal)

- Optional lightweight client-side logs/counters only if existing instrumentation hooks are already available.
- Do not add new backend telemetry pipelines in this WF.

## Deferred / Not in MVP

- Full analytics dashboards and funnel instrumentation.
- Cross-app loading/empty-state UX modernization.
- Legal/privacy/a11y epics.
- New backend workflow semantics.

## Open Questions (if any)

- Confirm canonical in-app create-review route string used by current frontend routing.
- Confirm whether explicit fallback UI is needed if restart reset guard detects stale state.

## Changelog

- v0.1 (2026-02-18): Initial PRD from spec
- v0.2 (2026-02-18): Added route contract assumptions, tightened telemetry scope, and marked Ready for Tasks
