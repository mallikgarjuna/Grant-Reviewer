# WF-0017 — Auto Polling for Processing Reviews

Artifact: spec
Version: v0.2
Status: Ready for PRD
Last Updated: 2026-02-18

## 1. Purpose

Improve trust in the review wait experience by removing manual refresh as the default way to detect review completion or failure.

## 2. User / System Context

The target flow is authenticated users in the app who submit a review and remain on a processing state view. Today they manually refresh to check status. The system already exposes review status (`PROCESSING`, `COMPLETED`, `FAILED`) and this workflow should reuse that existing contract.

## 3. Core Behavior

When a review is in `PROCESSING`, the client automatically polls review status on a fixed interval (3 seconds) with a maximum duration cap of 90 seconds. Polling starts after submit returns `PROCESSING` and when opening an existing processing review view. Polling stops when:
- status becomes `COMPLETED` or `FAILED`
- polling cap is reached
- the user leaves the page / component unmounts

If the initial or subsequent fetch returns a terminal status, the client should not continue polling and should render terminal state immediately.

If cap is reached while still processing, the UI shows a clear fallback message indicating processing may still be ongoing and suggests a later refresh/check (without labeling the review as failed).

## 4. In Scope

- Client-side bounded polling for processing review status.
- Automatic terminal-state handling without manual refresh.
- Poll lifecycle cleanup on unmount/navigation.
- Clear fallback UI state when polling cap is reached.
- Terminal-first behavior when status is already `COMPLETED`/`FAILED` (no polling loop).
- Targeted verification of transition handling and stop conditions.

## 5. Out of Scope

- Submit-flow redesign items (e.g., start-over button, deep-link/sign-out adjustments, slow-hint redesign).
- Websocket/SSE or any real-time transport upgrade.
- New backend status endpoints or contract changes.
- System-wide loading/empty-state redesign.
- New analytics/monitoring initiatives dedicated to polling.

## 6. Data & Dependencies

- Existing review status fetch path in frontend app.
- Existing backend review status API contract (no schema change expected).
- Authenticated app context where review status is visible after submit.
- Existing review lifecycle statuses (`PROCESSING`, `COMPLETED`, `FAILED`).
- Existing UI view where processing review status is shown.

## 7. Edge Considerations

- Prevent duplicate timers and memory leaks from repeated mounts/renders.
- Ensure only one active polling loop exists per review view instance.
- Ensure polling does not continue after terminal state is reached.
- Keep request volume bounded with fixed cadence and max duration.
- Avoid client-side misclassification of long processing as failure.
- Ensure long-processing fallback copy is explicit and actionable.

## Changelog

- v0.1 (2026-02-18): Initial spec from brainstorm
- v0.2 (2026-02-18): Applied review edits, locked polling cap semantics, and marked ready for PRD
