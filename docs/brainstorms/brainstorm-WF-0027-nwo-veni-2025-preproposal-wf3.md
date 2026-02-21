# WF-0027 — NWO Veni 2025 preproposal — WF-3 Brainstorm

Artifact: brainstorm
Version: v0.1
Status: Draft
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
A new API endpoint (e.g., `GET /api/public/calls/{id}/config`) returns the expected structure for a call, which the frontend uses to set its data entry mode. The backend dictates the expected data shape configuration.

**What becomes possible?**
The frontend receives the configuration, knows the call is "structured", and renders the correct layout. It does not need to submit the actual structured data to the backend yet (safe incremental delivery).

---

## 3. Target User / Actor

**Who is this for?**
The researcher evaluating the grant proposal.

**What is their current behavior?**
Trying to submit an NWO Veni evaluation but being faced with a generic single-textarea form that doesn't match the complex NWO rubric.

**What frustration or inefficiency exists?**
Preventing a poor UX where the tool's form doesn't match the required assessment format.

---

## 4. Rough Idea (Unstructured Thinking)

**Simplest implementation direction:**
Add a new public API endpoint `GET /api/public/calls/{call_id}/config` that reads the `CallDefinition` and returns a JSON schema or simple UI hints (e.g., `ui_mode: "structured_nodes", expected_nodes: ["academic_profile", ... ]`). A dedicated endpoint ensures we don't bloat the list endpoint, and keeps the frontend dynamic rather than hardcoded.

**Frontend handling:**
When a user selects a call, fetch the config. If `ui_mode === 'structured_nodes'`, display a "Coming Soon: Structured form required" empty state for now. If legacy, show the single text box. This safely gates the UI without overstepping into the next workflow chunk.

---

## 5. Constraints

**Technical constraints:**
We must ensure the new endpoint is public (unauthenticated) because call selection happens before the user might be fully committed/logged in to a review draft. The `CallDefinition` metadata must be accessible during the pre-submission UX phase.

**Dependencies:**
WF-0021 must be merged (which provides the `logical_id` and V2 YAML ingestion so the Call Definition actually exists in the DB). We cannot serve a config for a V2 call until V2 calls exist in the DB.

**Time constraints:**
We must strictly stop after the endpoint exists and the frontend can switch its state (e.g., showing a placeholder). Do not implement the actual structured data ingestion in this chunk.

---

## 6. Risks / Unknowns

**Assumptions:**
That the frontend can just render an empty state without completely breaking the user flow for structured calls. The empty state must be graceful; if deciding to submit is blocked, the UX must clearly explain why.

**What could cause rework?**
If the structure of the JSON returned by the new config endpoint doesn't match what the future frontend components actually need to render the 3 inputs. The API contract needs to be just robust enough to indicate "mode" now, but extensible for actual "fields" later.

---

## 7. MVP Definition

**Smallest functional slice:**
The backend endpoint returns the mode, and the frontend uses it to either show the legacy textarea OR a static disabled state saying "Structured submissions coming soon". This safely completes the "frontend gating" requirement.

---

## 8. Explicit Non-Goals

**What are we NOT solving?**
Any changes to the `POST /api/reviews/submit` endpoint or the database `Review` schema. The actual React components for the 3 distinct NWO nodes (We are NOT touching submission logic, and we are NOT building the full structured UI yet. We are just building the *gate*).

**What future ideas should be postponed?**
Handling file uploads (PDF/Docx), the compliance engine (word counts, item limits), and automatically determining NOT_ASSESSABLE status based on missing inputs.
