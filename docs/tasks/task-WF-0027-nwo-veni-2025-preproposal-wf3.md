# WF-0027 — nwo-veni-2025-preproposal-wf3 Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-21

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Backend API Endpoint (`/config`)
Goal: Implement the `GET /api/public/calls/{call_logical_id}/config` endpoint. Ensure it only returns the whitelisted contract fields (`call_logical_id`, `config_version`, `ui_mode`, and conditionally `expected_nodes`).
Files to modify: FastAPI router file handling public calls.
Acceptance Criteria: Returns HTTP 200 with proper schema for valid calls. Returns HTTP 404 for unknown calls. Does not leak internal DB metadata.
Verification Steps: Call the endpoint manually or via tests for a known `logical_id` and verify exact JSON payload matches PRD v0.3.
Risks (if any): Route collision with `GET /api/public/calls/{id}`. Ensure the new route is placed correctly or typing correctly differentiates them.

### [ ] Task 2 — Backend Verification (Tests)
Goal: Add automated tests to lock in the endpoint contract and routing behavior.
Files to modify: Test files for public call endpoints.
Acceptance Criteria: Tests cover HTTP 200 success shape, HTTP 404 for unknown `call_logical_id`, omitted `expected_nodes` on legacy, and route ordering safely ignoring integer IDs.
Verification Steps: Run the specific test suite.
Risks (if any): None.

### [ ] Task 3 — Frontend API Client & Validation (Fail-safe)
Goal: Fetch the config on call selection and validate the payload.
Files to modify: Frontend API client or React hook responsible for call selection.
Acceptance Criteria: Payload must be validated (must have `config_version` and valid `ui_mode`). If malformed (even on HTTP 200) or fetch fails, fallback to legacy mode + non-blocking warning. If HTTP 404, trigger call-not-found state.
Verification Steps: Mock API responses (200 malformed, 500 error, 404) and verify the functions return the correct state objects/errors.
Risks (if any): Silently ignoring errors instead of showing the required warning or error states.

### [ ] Task 4 — Frontend UI Gating & Rendering
Goal: Render the correct UI mode based on the validated config state.
Files to modify: Frontend evaluation viewer component.
Acceptance Criteria:
- `legacy_single_snippet`: Render standard textarea.
- `structured_nodes`: Render disabled placeholder stating "Structured submissions coming soon" (no submit path).
- Fallback/Error: Render legacy + non-blocking warning.
- 404: Render call-not-found error state + disable submission completely.
- Text: Use "evaluation criteria/evaluation elements" instead of "rubric" across researcher-facing text.
Verification Steps: Boot the frontend, intercept requests or select known DB fixtures to manually verify the 4 distinct UI boundary states.
Risks (if any): Leaking a submit path when in 404 or structured states.

## Changelog

- v0.1 (2026-02-21): Initial tasks from PRD v0.3
- v0.2 (2026-02-21): Internal risk audit passed; stabilized tasks for implementation
