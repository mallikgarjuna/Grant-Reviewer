# Walkthrough: WF-0027 (NWO Veni 2025 Preproposal - WF3)

Artifact: walkthrough
Version: v0.1
Status: Done
Last Updated: 2026-02-21

## Objective
The goal of WF-0027 was to implement API-driven frontend mode gating, allowing the UI to gracefully disable the single-snippet submission flow for new structured calls (like NWO Veni 2025 Preproposal) while keeping legacy calls functional.

## Changes Made

### 1. Backend API (`/api/public/calls/{call_logical_id}/config`)
- **Implemented Config Endpoint:** Added a new public route in FastAPI to serve the required `CallConfigResponse` schema, keeping internal DB metadata safely hidden.
- **Data Integrity Fail-safe:** Added explicit logic to check whether `canonical_json.proposal_nodes` is truly a list of valid nodes. If malformed or missing, it logs a warning telemetry event and gracefully falls back to `ui_mode: "legacy_single_snippet"`.
- **404 Behavior:** Returns a clean HTTP 404 `CALL_NOT_FOUND` if the logical string ID doesn't correspond to any active funding call.
- **Route Isolation:** The new route (`/api/public/calls/...`) uses a distinct path prefix, completely avoiding any collision risk with the authenticated integer-based `/calls/{id}/nodes` route.

### 2. Frontend BFF Adapter & UI State
- **BFF Client:** Created `getCallConfig` in `lib/bff/adapter.ts` to proxy the request.
- **Robust State Resolution:** Built `resolveCallConfigUiState` with strict type validation. It handles network errors, 500s, 404s, unsupported `config_version` values, and unexpected `ui_mode` strings by resolving them into a safe canonical fallback state.
- **Decoupled View Logic:** Consolidated the complex boolean logic determining whether inputs should be disabled into a pure, testable function `deriveReviewFormUiState(input)`.

### 3. Frontend Gating (`app/page.tsx`)
- Integrated the config fetch hook triggered by the Call selector.
- **Four Distinct Render States:**
  1. **Legacy Mode:** Textarea enabled, Submit button active.
  2. **Structured Disabled:** Textarea disabled, Submit disabled, explicit "coming soon" banner visible.
  3. **Fallback Warning:** Textarea enabled (legacy fallback), but with a non-blocking amber warning indicating the config fetch failed or the payload was malformed.
  4. **Call Not Found (404):** Textarea disabled, Submit disabled, explicit red error banner visible.
- Replaced the word "rubric" with "evaluation criteria/evaluation elements" in the description text.
- **Proxy Middleware Fix:** Updated `lib/proxy-routes.ts` to ensure the Clerk NextJS proxy protects `/api/bff` and `/app` routes specifically, preventing global middleware interception from breaking unauthenticated public assets.

## Validation & Testing

### Backend Coverage
- **Tests Added:** `test_get_call_config_returns_structured_mode`, `test_get_call_config_legacy_omits_expected_nodes`, `test_get_call_config_unknown_call_returns_404` added to `backend/tests/test_api.py`.
- **Verified:** HTTP statuses, exact payload keys, conditionally required `expected_nodes`, and telemetry pathing.
- **Status:** All 36 backend tests passing (`uv run pytest -q`).

### Frontend Coverage
- **Logic Tests (`call-config.test.ts` & `review-form-ui-state.test.ts`):** 10 tests verifying the data parser correctly defaults to safe boundary states when given malformed payloads or HTTP errors.
- **Middleware Tests (`proxy-routes.test.ts`):** 3 tests verifying correct route URL matching.
- **Component Tests (`page.test.tsx`):** Added a React Testing Library suite with mocked HTTP intercepts to verify the actual DOM outputs the 4 distinct UI boundary states (legacy enabled, structured disabled placeholder, fetch-fail fallback warning, and 404 call-not-found disabled).
- **Status:** All 16 frontend tests passing (`npm run test:ui`).
- **Build/Lint:** `npm run build` and `npm run lint` passing with 0 warnings.

## Remaining Risks / Next Steps
- **Structured Form Implementation:** This workflow successfully fenced off structured calls. A future workflow must actually implement the dynamic multi-node React form and submit payload construction to unlock structured reviews.
