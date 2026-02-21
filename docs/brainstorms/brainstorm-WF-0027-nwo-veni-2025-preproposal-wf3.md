# WF-0027 — NWO Veni 2025 preproposal — WF-3 Brainstorm

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-02-21

---

## 1. Problem Statement

**What problem are we solving?**
The frontend has no way of knowing if a selected funding call requires a structured submission form (multiple fields) versus a standard single-snippet form, leading to incorrect UI presentation.

**Who experiences it?**
The researcher/applicant who would be presented with the wrong input form, leading to submission errors or misrouting.

**Why does it matter now?**
The NWO Veni 2025 preproposal is our first structured call; without this, the system will break when users try to submit against it. (Failing to solve this means a complete failure of the review submission flow for structured calls).

**Fundamental Nature of Change Required:**
An incremental, non-breaking extension that adds configuration context (via a new endpoint) to the frontend so it can conditionally render the correct UI mode.

---

## 2. Desired Outcome

**What changes after this exists?**
The frontend dynamically renders the NWO Veni structured layout correctly when that call is selected (the immediate unblocking requirement is simply rendering the correct UI mode).

**What becomes easier or faster?**
A new API endpoint (`GET /api/public/calls/{call_logical_id}/config`) returns a stable call configuration payload, which the frontend uses to set its data entry mode. The backend dictates the expected data shape configuration.

**What becomes possible?**
The frontend receives the configuration, knows the call is "structured", and renders the correct layout. It does not need to submit the actual structured data to the backend yet (safe incremental delivery).

---

## 3. Target User / Actor

**Who is this for?**
The researcher evaluating the grant proposal.

**What is their current behavior?**
Trying to submit an NWO Veni evaluation but being faced with a generic single-textarea form that does not match the call's evaluation elements.

**What frustration or inefficiency exists?**
Preventing a poor UX where the tool's form doesn't match the required assessment format.

---

## 4. Rough Idea (Unstructured Thinking)

**Simplest implementation direction:**
Add a new public API endpoint `GET /api/public/calls/{call_logical_id}/config` that returns a fixed, minimal payload for UI mode gating. A dedicated endpoint avoids bloating the list endpoint and keeps frontend behavior data-driven instead of hardcoded.

MVP response contract (locked for WF-0027):

```json
{
  "call_logical_id": "nwo_veni_2025_preproposal",
  "config_version": "1",
  "ui_mode": "structured_nodes",
  "expected_nodes": ["academic_profile", "knowledge_utilisation", "scientific_proposal"]
}
```

Contract notes:
- `ui_mode` enum for WF-0027: `legacy_single_snippet | structured_nodes`
- `expected_nodes` required when `ui_mode=structured_nodes`, omitted for legacy mode
- `config_version` is required for forward-compatible frontend parsing
- Endpoint response is an explicit allowlist and must not expose internal-only metadata

**Frontend handling:**
When a user selects a call, fetch the config. If `ui_mode === 'structured_nodes'`, display a disabled-state message with explicit next step text (no silent dead end). If legacy, show the single text box. This safely gates the UI without overstepping into the next workflow chunk.

If config fetch fails (network/server/parsing), frontend must:
- fall back to `legacy_single_snippet` mode
- show a non-blocking warning that structured mode could not be loaded
- keep the page usable instead of blank/broken

---

## 5. Constraints

**Technical constraints:**
The endpoint is public (unauthenticated) because call selection happens pre-submission. Public payload is restricted to UI-mode fields only: `call_logical_id`, `config_version`, `ui_mode`, `expected_nodes`.

**Dependencies:**
WF-0021 must be merged (which provides the `logical_id` and V2 YAML ingestion so the Call Definition actually exists in the DB). We cannot serve a config for a V2 call until V2 calls exist in the DB.

**Time constraints:**
We must strictly stop after the endpoint exists and the frontend can switch its state (e.g., showing a placeholder). Do not implement the actual structured data ingestion in this chunk.

---

## 6. Risks / Unknowns

**Assumptions:**
That the frontend can just render an empty state without completely breaking the user flow for structured calls. The empty state must be graceful; if deciding to submit is blocked, the UX must clearly explain why.

**What could cause rework?**
If the contract drifts between backend and frontend. Rework is reduced by locking the WF-0027 response schema and versioning it from day one (`config_version`).

---

## 7. MVP Definition

**Smallest functional slice:**
The backend endpoint returns the locked config contract, and the frontend uses it to either show the legacy textarea OR a disabled structured-mode state with clear user guidance. This safely completes the frontend gating requirement.

Acceptance criteria (WF-0027 MVP):
1. `GET /api/public/calls/{call_logical_id}/config` exists and returns HTTP 200 with required fields for known calls.
2. Endpoint lookup key is `call_logical_id` (not numeric DB ID), aligned with WF-0021.
3. For `ui_mode=legacy_single_snippet`, frontend renders the current single textarea flow.
4. For `ui_mode=structured_nodes`, frontend renders a disabled placeholder state with explicit message and no active submit path.
5. On config fetch failure, frontend falls back to legacy mode and shows a non-blocking warning.
6. Endpoint response excludes internal/private fields beyond the explicit allowlist.

---

## 8. Explicit Non-Goals

**What are we NOT solving?**
Any changes to the `POST /api/reviews/submit` endpoint or the database `Review` schema. The actual React components for the 3 distinct NWO nodes (We are NOT touching submission logic, and we are NOT building the full structured UI yet. We are just building the *gate*).

**What future ideas should be postponed?**
Handling file uploads (PDF/Docx), the compliance engine (word counts, item limits), and automatically determining NOT_ASSESSABLE status based on missing inputs.

---

## 9. Changelog

- v0.2 (2026-02-21): Locked endpoint identity to `call_logical_id`, defined MVP response contract and versioning, added public-field allowlist constraint, added frontend failure-mode behavior, added explicit MVP acceptance criteria, aligned terminology to evaluation criteria/elements.
