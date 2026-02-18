# WF-0017 — Auto Polling for Processing Reviews

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-18

## 1. In Scope

- Client-side status polling for reviews in `PROCESSING`.
- Fixed polling interval of 3 seconds with hard cap at 90 seconds.
- Automatic transition handling when backend returns `COMPLETED` or `FAILED`.
- Poll lifecycle cleanup on unmount/navigation.
- Long-processing fallback UI message when cap is reached.
- Verification of happy path and capped long-processing behavior.

## 2. Out of Scope

- Any backend API contract change.
- Websocket/SSE or push transport.
- Submit-flow redesign items tracked separately in backlog.
- System-wide loading/empty-state redesign.
- New telemetry pipeline beyond minimal local logging hooks.

## 3. User / System Flow

### Happy Path
1. User submits review and sees review status as `PROCESSING`.
2. Client starts polling every 3 seconds.
3. Backend returns `COMPLETED` (or `FAILED`) before cap.
4. Client stops polling and renders terminal state immediately.

### Failure Path A: Long Processing Exceeds Cap
1. Review remains `PROCESSING` through 90 seconds.
2. Client stops polling.
3. UI shows fallback: processing may still be ongoing and user can refresh/check later.

### Failure Path B: Transient Request Error During Polling
1. Poll request errors (network or temporary server failure).
2. Client keeps bounded behavior and does not spawn duplicate loops.
3. UI maintains processing context and continues next scheduled attempt until cap or terminal state.

### Failure Path C: View Unmount/Navigate Away
1. User leaves processing view while polling is active.
2. Client clears polling loop immediately.
3. No further requests are sent from that view instance.

## 4. Functional Requirements

- FR1: Polling must run only when review status is `PROCESSING`.
- FR2: Polling cadence must be fixed at 3 seconds.
- FR3: Polling must stop on `COMPLETED`, `FAILED`, cap reached, or unmount/navigation.
- FR4: If status is already terminal on first fetch, polling must not start.
- FR5: Only one polling loop may exist per review view instance.
- FR6: At cap while still processing, UI must show non-failure fallback guidance.
- FR7: The feature must reuse existing review-status fetch paths and auth context.

## 5. Data & API Contracts

### Contracts Used
- Existing review read endpoint and response shape.
- Existing status enum values: `PROCESSING`, `COMPLETED`, `FAILED`.

### Request/Response Expectations
- Request: unchanged from current frontend read path.
- Response: must include status field used for polling state transitions.

### Validation Rules
- Polling starts only for recognized `PROCESSING` status.
- Unknown or missing status should fail safe by stopping polling and surfacing existing error handling.

### State Transitions (Client View)
- `PROCESSING` -> `PROCESSING`: continue polling until cap.
- `PROCESSING` -> `COMPLETED`: stop polling, render completed state.
- `PROCESSING` -> `FAILED`: stop polling, render failed state.
- `PROCESSING` -> cap reached: stop polling, render “still processing” fallback.

## 6. Components / Modules

### Responsibilities
- Processing review UI: owns polling lifecycle start/stop decisions.
- Review fetch utility/hook: executes status reads and returns normalized state.
- Status rendering component: renders processing, terminal, and cap-reached fallback states.

### Suggested File Paths
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/components/review/` (status display components as needed)

## 7. Edge Cases

- Duplicate interval creation from rerenders.
- Polling continuing after terminal state due to stale closures.
- Polling not cleaned on route change/unmount.
- Slow backend where status stays `PROCESSING` for >90 seconds.
- Transient request failures during active polling window.

## 8. Telemetry (Minimal)

- Reuse existing client logging paths for:
  - polling started
  - polling stopped reason (`terminal`, `cap`, `unmount`)
  - polling request error count (if available)

No new external monitoring integration in this WF.

## Deferred / Not in MVP

- Real-time push channel (websocket/SSE).
- Cross-tab polling coordination.
- Adaptive/backoff interval tuning.
- Submit-flow UX redesign backlog items.

## Open Questions (if any)

- None currently blocking. Cap messaging copy can be tuned in implementation.

## Changelog

- v0.1 (2026-02-18): Initial PRD from spec
