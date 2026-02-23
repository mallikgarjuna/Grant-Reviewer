# WF-0030 — NWO Veni 2025 Preproposal (WF-6 Phase) Tasks

Artifact: task
Version: v1.1
Status: Ready for Implementation
Last Updated: 2026-02-23

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD
- v1.0 (2026-02-22): Applied review edits and marked Ready for Implementation
- v1.1 (2026-02-23): Addressed Codex review: refined atomic boundaries, folded UI shell into existing page.tsx, grouped API bindings, and extracted testing orchestrations.

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Base Local Storage & UI Shell (VeniSubmitForm)

Goal: Modify the current submit flow entrypoint to use the hardcoded Veni form with local draft persistence and real-time word counting.
Files to modify:
- `frontend/src/hooks/useLocalStorageDraft.ts` (NEW)
- `frontend/src/components/submit/VeniSubmitForm.tsx` (NEW)
- `frontend/src/app/app/page.tsx`
Acceptance Criteria:
- `/app/page.tsx` is updated to route submissions to the `VeniSubmitForm`.
- Form renders with 3 textareas: `academic_profile`, `key_outputs`, `research_idea` and a toggle for ENW/Science.
- UI disclaimer on rich text limitations is visible.
- Text typed into the areas correctly counts words locally in real-time.
- Inputs are persisted to `localStorage` under `draft_${call_id}_v1`.
Verification Steps:
- Open `/app` in the browser.
- Type in the 3 areas, check word counts update immediately.
- Refresh the page and verify text is restored from local storage.
Risks: Local storage quota limits (unlikely for plain text).

### [ ] Task 2 — Implement BFF API Routes & Client Adapter

Goal: Create Next.js API routes (BFF), update client types, and wire the client adapter to proxy requests to the FastAPI backend.
Files to modify:
- `frontend/src/app/api/bff/check-compliance/route.ts` (NEW)
- `frontend/src/app/api/bff/structured-review/route.ts` (NEW)
- `frontend/src/lib/types/submit.ts`
- `frontend/src/lib/api/adapter.ts` (or client equivalent)
Acceptance Criteria:
- `/api/bff/check-compliance` forwards requests with the signed Clerk token to the core API's `/check-compliance` endpoint.
- `/api/bff/structured-review` forwards requests with the signed Clerk token and exactly preserves the frontend-generated `Idempotency-Key` header to the core API's `/structured-review` endpoint.
- Type definitions explicitly define frontend payload shapes and match backend domain expectations.
- API client adapter is wired to use the new BFF endpoints.
Verification Steps:
- Add a dummy test or use `curl`/Postman to hit the new BFF endpoints locally and verify they forward headers (Clerk auth, Idempotency-Key) correctly.
Risks: Header proxying mistakes (like dropping the auth or idempotency key) or type desync.

### [ ] Task 3 — Form Orchestration & Compliance Bypass Logic

Goal: Implement the core API flow orchestration within `VeniSubmitForm`, including the two-step bypass modal.
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/submit/ComplianceBypassModal.tsx` (NEW)
Acceptance Criteria:
- Clicking "Submit" maps inputs and triggers the check-compliance adapter.
- If 200 OK (no errors), automatically proceed to structured-review with a generated UUID v4 `Idempotency-Key`.
- If 200 OK (with `errors[]`), display `ComplianceBypassModal` ("Your draft exceeds official limits. Proceed?"). Clicking "Submit Anyway" bypasses the check and proceeds.
- If 422 Unprocessable Entity, backend errors (e.g., `UNKNOWN_NODE_ID`, `DOMAIN_INVALID`) are hard-blocked and listed natively in the UI. No modal is shown.
Verification Steps:
- Mock the compliance endpoint to return a violation, verify the modal appears.
- Mock a 422 response with specific error codes, verify the hard-block behavior.
Risks: State race conditions between the compliance check and the final submission.

### [ ] Task 4 — Submission Lifecycle & UX Handling

Goal: Complete the submission lifecycle by wiring 90-second blocking overlay, timeouts, 401 redirect handling, and cleanup.
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/ui/BlockingOverlay.tsx` (NEW)
- `frontend/src/routes.ts` (or equivalent redirect helper)
Acceptance Criteria:
- Use shared route constants (`routes.ts`) for consistent redirection to `/app/reviews/{review_id}` or sign-in on 401.
- `BlockingOverlay` spinner covers the screen for up to 90 seconds while `/api/bff/structured-review` is inflight.
- Handle 401 Unauthorized securely: redirect to the Clerk sign-in page without losing local draft state.
- Clear the local draft key (`draft_${call_id}_v1`) strictly on successful submission only. Must NOT clear draft on 401 or 422 errors.
- Add minimal telemetry (`console.info`) on bypass modal display and confirmation.
Verification Steps:
- Mock a slow backend response, verify the overlay blocks.
- Mock a 401 response, verify safe redirection to sign-in.
- Mock successful success, verify routing to new review and verify `localStorage` draft is removed.
Risks: Timeout issues causing infinite spinners.

### [ ] Task 5 — Automated Frontend Testing

Goal: Construct independent integration/unit tests for the submission and API orchestration.
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.test.tsx` (NEW)
Acceptance Criteria:
- Test 200 no-errors path triggers both requests with the generated Idempotency-Key.
- Test 200 with-errors path correctly awaits user confirmation before triggering the second request.
- Test 422 prevents second request.
- Test 401 handles safe redirection logic without clearing storage.
Verification Steps:
- Execute `npm run test` (or equivalent test runner). All orchestrations test cases must pass.
Risks: Difficulty mocking API headers correctly in test environment.
