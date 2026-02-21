# WF-0027 — nwo-veni-2025-preproposal-wf3 Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-21

## Task Breakdown (Sequential Order)

### [x] Task 1 — Backend API Endpoint (`/config`)
Goal: Implement the `GET /api/public/calls/{call_logical_id}/config` endpoint. Ensure it only returns the whitelisted contract fields (`call_logical_id`, `config_version`, `ui_mode`, and conditionally `expected_nodes`).
Files to modify: FastAPI public calls router/service modules for call retrieval and response shaping (plus schema/DTO file if required).
Acceptance Criteria: Returns HTTP 200 with proper schema for valid calls. Returns HTTP 404 for unknown calls. Does not leak internal DB metadata.
Verification Steps: Call the endpoint manually or via tests for a known `logical_id` and verify exact JSON payload matches PRD v0.3.
Risks (if any): Route collision with `GET /api/public/calls/{id}`. Ensure the new route is placed correctly or typing correctly differentiates them.

### [x] Task 2 — Backend Verification (Tests)
Goal: Add automated tests to lock in the endpoint contract and routing behavior.
Files to modify: Test files for public call endpoints.
Acceptance Criteria:
- Test-first bug workflow: write/adjust failing tests first, confirm they fail against pre-fix behavior, then implement/finalize until green.
- Tests cover HTTP 200 success shape for structured calls (`call_logical_id`, `config_version`, `ui_mode`, `expected_nodes`).
- Tests cover HTTP 200 success shape for legacy calls with `expected_nodes` omitted.
- Tests cover HTTP 404 for unknown `call_logical_id`.
- Tests assert route behavior explicitly:
  - `/api/public/calls/<logical_id>/config` resolves to config endpoint.
  - Existing `/api/public/calls/{id}` endpoint behavior remains unchanged for numeric ID requests.
Verification Steps: Run targeted backend endpoint tests and report which tests were added/updated, including initial failing reproducer evidence.
Risks (if any): False confidence if tests assert only status codes but not exact payload keys/types.

### [x] Task 3 — Frontend API Client & Validation (Fail-safe)
Goal: Fetch the config on call selection and validate the payload.
Files to modify: Frontend API client or React hook responsible for call selection.
Acceptance Criteria: Payload must be validated (`config_version` required and currently supported, `ui_mode` in enum, `expected_nodes` present only for `structured_nodes`). If malformed (even on HTTP 200) or fetch fails, fallback to legacy mode + non-blocking warning. If HTTP 404, trigger call-not-found state.
Verification Steps: Mock API responses (200 malformed, 500 error, 404, unsupported `config_version`) and verify the client/hook returns the correct state objects/errors.
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
Verification Steps:
- Add/update automated UI/component tests for: `legacy_single_snippet`, `structured_nodes` disabled placeholder, malformed/fetch-fail fallback warning, and 404 call-not-found state.
- Run targeted frontend tests for these states.
- Perform one manual sanity check in the running app for copy and disabled submit behavior.
Risks (if any): Leaking a submit path when in 404 or structured states.

## Changelog

- v0.1 (2026-02-21): Initial tasks from PRD v0.3
- v0.2 (2026-02-21): Internal risk audit passed; stabilized tasks for implementation
- v0.3 (2026-02-21): Tightened execution quality gates with explicit test-first bug workflow, concrete route-collision assertions, contract-version validation, and stronger automated frontend boundary-state verification.
