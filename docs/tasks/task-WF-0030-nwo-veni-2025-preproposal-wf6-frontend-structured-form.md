# WF-0030 — NWO Veni 2025 Preproposal (WF-6 Phase) Tasks

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Base Local Storage & UI Shell (VeniSubmitForm)

Goal: Create the hardcoded UI form for the NWO Veni 2025 preproposal with local draft persistence and real-time word counting.
Files to modify:
- `frontend/src/hooks/useLocalStorageDraft.ts` (NEW)
- `frontend/src/components/submit/VeniSubmitForm.tsx` (NEW)
- `frontend/src/app/app/submit/page.tsx` (NEW)
Acceptance Criteria:
- Form renders with 3 textareas: `academic_profile`, `key_outputs`, `research_idea` and a toggle for ENW/Science.
- UI disclaimer on rich text limitations is visible.
- Text typed into the areas correctly counts words locally in real-time.
- Inputs are persisted to `localStorage` under `draft_${call_id}_v1`.
Verification Steps:
- Open `/app/submit` in the browser.
- Type in the 3 areas, check word counts update immediately.
- Refresh the page and verify text is restored from local storage.
Risks: Local storage quota limits (unlikely for plain text).

### [ ] Task 2 — Implement BFF API Routes

Goal: Create Next.js API routes (BFF) to securely proxy requests to the FastAPI backend for compliance checks and structured review submission.
Files to modify:
- `frontend/src/app/api/bff/check-compliance/route.ts` (NEW)
- `frontend/src/app/api/bff/structured-review/route.ts` (NEW)
- `frontend/src/lib/types/submit.ts` (NEW or update existing)
Acceptance Criteria:
- `/api/bff/check-compliance` forwards requests with the signed Clerk token to the core API's `/check-compliance` endpoint.
- `/api/bff/structured-review` forwards requests with the signed Clerk token and `Idempotency-Key` header to the core API's `/structured-review` endpoint.
- Type definitions correctly represent the expected payload shapes.
Verification Steps:
- Add a dummy test or use `curl`/Postman to hit the new BFF endpoints locally and verify they forward correctly (or return 401 if unauthorized).
Risks: Header proxying mistakes (like dropping the auth or idempotency key).

### [ ] Task 3 — Form Orchestration & Compliance Bypass UI

Goal: Connect the `VeniSubmitForm` to the BFF endpoints, implementing the two-step orchestration, explicit idempotency generation, and the compliance bypass modal.
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/submit/ComplianceBypassModal.tsx` (NEW)
Acceptance Criteria:
- Clicking "Submit" triggers `/api/bff/check-compliance`.
- If 200 OK (no errors), automatically proceed to `/api/bff/structured-review` with a generated UUID v4 `Idempotency-Key`.
- If 200 OK (with `errors[]`), display `ComplianceBypassModal` ("Your draft exceeds official limits. Proceed?"). Clicking "Submit Anyway" bypasses the check and proceeds to `/api/bff/structured-review`.
- If 422 Unprocessable Entity, hard-block submission and show the error natively.
Verification Steps:
- Mock the compliance endpoint to return a violation, verify the modal appears.
- Mock a 422 response, verify the hard-block behavior.
Risks: State race conditions between the compliance check and the final submission.

### [ ] Task 4 — Submission Lifecycle & UX Handling

Goal: Complete the submission lifecycle by adding the 90-second blocking overlay, timeout toasts, session 401 handling, and post-success routing.
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/ui/BlockingOverlay.tsx` (NEW)
Acceptance Criteria:
- When `/api/bff/structured-review` is called, a high z-index `BlockingOverlay` spinner covers the screen for up to 90 seconds.
- On successful submission (returns `review_id`), route the user to `/app/reviews/{review_id}` and clear the local draft.
- Handle 401 Unauthorized implicitly: ensure local storage sync and redirect to the Clerk sign-in page.
- Add minimal telemetry (`console.info`) on bypass modal display and confirmation.
Verification Steps:
- Mock a slow backend response, verify the overlay blocks the screen.
- Mock a 401 response, verify redirection to sign-in.
- Verify successful route traversal to `/app/reviews/{review_id}`.
Risks: Timeout issues causing infinite spinners.
