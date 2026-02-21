# WF-0027 — nwo-veni-2025-preproposal-wf3 PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. In Scope
- Add a new public API endpoint `GET /api/public/calls/{call_logical_id}/config` that returns a fixed, minimal payload for UI mode gating.
- Endpoint response contract must include: `call_logical_id`, `config_version`, and `ui_mode`.
- `expected_nodes` is conditionally required when `ui_mode=structured_nodes`; for `legacy_single_snippet`, `expected_nodes` should be omitted.
- `ui_mode` enum restricted to `legacy_single_snippet` and `structured_nodes`.
- Frontend conditionally renders a disabled placeholder state for `structured_nodes` (indicating "Structured submissions coming soon") without an active submit path.
- Frontend fallback logic to `legacy_single_snippet` with a non-blocking warning if the config fetch fails.
- Replacing occurrences of the term "rubric" with "evaluation criteria/evaluation elements" in researcher-facing text.

## 2. Out of Scope
- Any database schema changes (`POST /api/reviews/submit` and `Review` schema remain untouched).
- Implementation of the actual React components for the 3 distinct NWO nodes.
- Handling file uploads (PDF/Docx).
- The compliance engine (word counts, item limits).
- Automatically determining NOT_ASSESSABLE status based on missing inputs.

## 3. User / System Flow

- **Happy path**:
  1. Researcher (applicant) selects the NWO Veni 2025 preproposal call on the frontend.
  2. Frontend makes a `GET` request to `/api/public/calls/nwo_veni_2025_preproposal/config`.
  3. Backend returns the configuration with `ui_mode: "structured_nodes"`.
  4. Frontend disables the legacy layout and renders a blocked state indicating that structured submissions are coming soon, with clear next step text.

- **Failure path 1 (Network/Server Error)**:
  1. Researcher selects a call.
  2. Frontend fails to fetch the config from `/api/public/calls/{call_logical_id}/config`.
  3. Frontend gracefully falls back to `legacy_single_snippet` mode.
  4. Frontend displays a non-blocking warning stating that structured mode could not be loaded, keeping the page usable.

- **Failure path 2 (Legacy Call Selected)**:
  1. Researcher selects an older call.
  2. Frontend successfully fetches config which returns `ui_mode: "legacy_single_snippet"` (or omits `expected_nodes`).
  3. Frontend renders the standard single-snippet format as usual.

- **Failure path 3 (Contract Validation Failure on HTTP 200)**:
  1. Frontend receives HTTP 200 from `/api/public/calls/{call_logical_id}/config` but payload is malformed (e.g., missing `config_version`, unknown `ui_mode`, wrong type for `expected_nodes`).
  2. Frontend treats response as invalid config.
  3. Frontend falls back to `legacy_single_snippet` mode and shows a non-blocking warning.
  4. Frontend logs the validation failure for telemetry/debugging.

## 4. Functional Requirements
1. **API Endpoint**: `GET /api/public/calls/{call_logical_id}/config` must exist and return HTTP 200 for known calls.
2. **Lookup Key**: The endpoint lookup key is `call_logical_id`.
3. **Payload Contract**: Response explicitly matches the locked contract in version `1`, with `expected_nodes` conditionally required only for `ui_mode=structured_nodes`.
4. **Data Isolation**: Response excludes internal/private fields beyond the explicit allowlist.
5. **Frontend Defaulting**: The frontend defaults to `legacy_single_snippet` processing.
6. **Frontend Gating UX**: When `ui_mode=structured_nodes` is detected, the frontend rendering path swaps to a disabled placeholder state with no active submission paths.
7. **Contract Fail-safe**: Frontend validates config payload and falls back to legacy mode with a warning if payload is malformed, even when HTTP status is 200.

## 5. Data & API Contracts

### Request Shape
`GET /api/public/calls/{call_logical_id}/config`

### Success Response Shape (HTTP 200)
```json
{
  "call_logical_id": "nwo_veni_2025_preproposal",
  "config_version": "1",
  "ui_mode": "structured_nodes",
  "expected_nodes": ["academic_profile", "knowledge_utilisation", "scientific_proposal"]
}
```

### Validation Rules & Constraints
- `ui_mode` is limited to `legacy_single_snippet | structured_nodes`.
- `config_version` is required for forward-compatible frontend parsing.
- `expected_nodes` is required when `ui_mode=structured_nodes` and omitted for `legacy_single_snippet`.
- Only the allow-listed public fields are included in the payload.

## 6. Components / Modules

- **Backend API Layer**: New public route `GET /api/public/calls/{call_logical_id}/config`. Responsible for retrieving the CallDefinition and shaping the public response.
- **Frontend Evaluation Viewer**: React component responsible for fetching the config upon call selection and toggling the UI mode. Must include explicit boundary states for fetch failure.

## 7. Edge Cases
- **Call ID doesn't exist**: Backend returns HTTP 404. Frontend shows a call-not-found error state and disables submission; do not silently treat unknown call IDs as valid legacy mode.
- **Missing `logical_id` on legacy calls**: Fall back to legacy rendering.
- **Route Collision**: Ensure `GET /api/public/calls/{call_logical_id}/config` does not conflict with any existing `GET /api/public/calls/{id}` routes in FastAPI (e.g., by placing the generic `{id}` route *after* static string routes, though `{call_logical_id}` is dynamic, so type hinting/path ordering must be verified).

## 8. Telemetry (Minimal)
- Track hits on the `/config` endpoint (standard server logs).
- Track instances of config fetch failures triggering the fallback state on the client.

## Deferred / Not in MVP
- Handling of actual structured data submission.
- Dynamic React layout generators.

## Open Questions
- None (resolved in v0.3: route path, conditional `expected_nodes`, unknown-call behavior, malformed-payload fail-safe).

## Changelog

- v0.1 (2026-02-21): Initial PRD from brainstorm v0.2
- v0.2 (2026-02-21): Applied risk audit edits (added route collision edge case) and marked Ready for Tasks
- v0.3 (2026-02-21): Resolved critical review findings: fixed backend route path, clarified conditional `expected_nodes` rule, added malformed-200 payload fail-safe behavior, and separated 404 unknown-call handling from legacy fallback.
