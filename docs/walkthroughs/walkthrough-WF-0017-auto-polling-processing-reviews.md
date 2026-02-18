# WF-0017 — Auto Polling for Processing Reviews

Artifact: walkthrough
Version: v0.1
Status: Draft
Last Updated: 2026-02-18

## Summary

Implemented bounded client-side auto-polling on the review detail page so users no longer need manual refresh while a review is pending.

## How To Run

```bash
cd frontend
npm run dev
```

Open a pending review page:

```text
/app/reviews/<review_id>
```

## How To Verify

### Automated

```bash
cd frontend
npm run lint
```

Result: passed during Task 1-5 implementation checkpoints.

### Scenario A: Pending -> Terminal Auto-Transition

1. Open a review detail URL where status is `PENDING`.
2. Observe status message: "Still processing. Checking status automatically..."
3. Wait for backend to transition review to `COMPLETED` or `FAILED`.
4. Confirm page updates without manual refresh and polling stops.

Evidence in code:
- Poll trigger/status semantics: `PENDING` only.
- Poll stop on terminal statuses.

### Scenario B: Pending -> Cap Fallback

1. Open a review detail URL where status remains `PENDING` for >90 seconds.
2. Confirm polling stops at cap.
3. Confirm fallback message appears: processing may still finish soon and user can refresh later.
4. Confirm page does not label this state as `FAILED`.

Evidence in code:
- 90-second cap constant.
- Cap-reached UI fallback copy.

### Scenario C: Transient Polling Error

1. While pending polling is active, simulate transient network/API errors.
2. Confirm polling notice appears ("retrying automatically") while keeping pending context.
3. Confirm cap timer remains bounded and does not restart because of transient errors.

## Known Limitations

- No websocket/SSE push updates (intentionally out of scope).
- Cap fallback still requires user re-check if backend is slow beyond 90 seconds.
- Cross-tab polling coordination is not implemented.

## Changelog

- v0.1 (2026-02-18): Initial implementation walkthrough with verification guidance and limits
