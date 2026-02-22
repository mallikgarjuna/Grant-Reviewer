# WF-0030 — NWO Veni 2025 Preproposal Structured AI Review (WF-6 Phase) PRD

Artifact: prd
Version: v0.4
Status: Ready for Tasks
Last Updated: 2026-02-22

## 1. In Scope
- A hardcoded, structured submission form at `/app/submit` specifically for the **NWO Veni 2025 Preproposal (3 nodes)**.
- Plain-text ingestion into 3 distinct `<textarea>` inputs mapped exactly to backend `node_logical_id`s (`academic_profile`, `key_outputs`, `research_idea`).
- A mandatory UI disclaimer regarding rich text / table limitations.
- Zero-latency client-side word count enforcement replicating backend standard whitespace rules.
- Two-step submission orchestration: `/api/check-compliance` followed by `/api/structured-review`.
- Form warning bypass modal ("Submit Anyway") allowing intentionally non-compliant submissions to proceed to evaluation *only* if the backend returns a 200 OK with `errors[]`.
- Local draft saving in `localStorage` securely keyed by the static string `draft_${call_id}_v1`.
- Idempotency preservation via explicit client-side `UUID v4` generation passed in the `Idempotency-Key` header.
- Robust submission lifecycle handling: 90-second blocking overlay, timeout toasts, session 401 handling, and immediate post-success routing.

## 2. Out of Scope
- Dynamic "Universal Form" rendering from backend schemas (deferred to future WF).
- File uploads, document parsing (e.g., `.docx` to markdown via MarkItDown).
- Native rich-text (WYSIWYG) editors.
- Advanced evaluation constraint matching (e.g., lists boundaries inside outputs).
- Cross-node dependency visualizations.

## 3. User / System Flow
**Happy Path:**
1. User navigates to `/app/submit` and selects "NWO Veni 2025" from a dropdown.
2. Frontend renders the 3 hardcoded textareas for Veni.
3. User pastes text. Real-time counters update without network calls.
4. User clicks "Submit".
5. Frontend calls `/api/check-compliance`. Backend returns 200 OK (no violations).
6. Frontend automatically posts to `/api/structured-review` with `Idempotency-Key`.
7. UI shows 90-second blocking overlay.
8. Backend returns successful `review_id`.
9. Frontend routes to `/app/reviews/{review_id}` and clears the local draft for this schema.

**Soft Enforcement (Bypass) Path:**
1. User enters text in "Research Idea" violating standard limit.
2. User clicks "Submit".
3. Frontend calls `/api/check-compliance`. Backend returns 200 OK with `errors[]` from the compliance report.
4. Frontend traps the presence of `errors`, maps them, and shows summary alert + Bypass Modal ("Your draft exceeds official limits. Proceed?").
5. User clicks "Submit Anyway".
6. Frontend posts to `/api/structured-review` with `Idempotency-Key` (bypassing compliance).
... proceeds to success.

**Hard Enforcement (Block) Path:**
1. Payload is malformed (e.g., missing mandatory node, invalid domain).
2. User clicks "Submit".
3. Frontend calls `/api/check-compliance`. Backend returns 422 Unprocessable Entity.
4. Frontend hard-blocks submission, displays the 422 error message, and does *not* show the bypass modal.

**Failure Path (Session Expiration 401):**
1. User drafts proposal (persisted locally on every change).
2. User's Clerk session expires implicitly.
3. User clicks "Submit".
4. Request hits 401 Unauthorized.
5. Frontend traps 401, guarantees local storage sync, and redirects to Clerk sign-in page.

## 4. Functional Requirements
- **Veni Hardcoded Mapping**: Map the UI exactly to the 3 `node_logical_id`s (`academic_profile`, `key_outputs`, `research_idea`). Provide hardcoded labels and guidance text in the frontend component for MVP.
- **Real-Time Word Counter**: Apply standard `text.split(/\s+/)` algorithm locally for live counters (e.g., "450 / 400 words").
- **ENW/Science Toggle**: Add contextual toggle for ENW/Science. Persist the selected exact domain string in the local draft and pass it explicitly to the BFF `/api/check-compliance` proxy.
- **Draft Persistence**: Save drafts to `localStorage` under the static key `draft_${call_id}_v1`. Restore implicitly on page load. Show ephemeral toast upon restoration.

## 5. Data & API Contracts
**Client -> `/api/check-compliance` (POST)**
- Purpose: Execute standard compliance without locking tokens or triggering LLM.
- Payloads: `ComplianceCheckRequest` shape containing `call_id`, optional `domain` string, and `draft_nodes` array (`node_logical_id`, `text`).
- Requirement: Implement Next.js BFF route for `/api/check-compliance` proxying signed headers.

**Client -> `/api/structured-review` (POST)**
- Expected headers: `Idempotency-Key: <UUIDv4>`
- Payloads: `StructuredReviewRequest` shape containing `call_id`, and `nodes` array (`node_logical_id`, `text`).
- Requirement: Implement Next.js BFF route for `/api/structured-review` proxying signed headers.

**Response Handling:**
- Trap `ComplianceViolation` objects mapped from the `errors[]` compliance engine response to render the bypass warnings.

## 6. Components / Modules
- `VeniSubmitForm`: Top-level orchestrator hardcoded for Veni.
- `LocalStorageDraftManager`: React hook for safe persistance.
- `ComplianceBypassModal`: Headless UI logic for secondary confirmation.
- `BlockingOverlay`: High z-index spinner overlay locking inputs.

## 7. Edge Cases
- Schema changes while user has a stored draft -> Not applicable in MVP since the Veni structure is hardcoded to `_v1`.
- Fast double clicks on Submit -> UUID Idempotency-Key prevents backend duplication; `BlockingOverlay` prevents rapid frontend clicks.
- Table / Multi-line pastes -> Accepted without processing; rich markup is stripped, rely on LLM to map tab-spaced chunks correctly. Add explicit UI disclaimer.

## 8. Telemetry (Minimal)
- Basic `console.info` logging when a compliance warning is triggered, and when the user clicks "Submit Anyway" to bypass. No external analytics SDKs required for MVP.

## Deferred / Not in MVP
- Assisted Extraction via Document Upload (P2 #14).
- Cross-Node Context Dependency Visualization (P1 #12).

## Changelog
- v0.1 (2026-02-22): Initial PRD generated from brainstorm v1.0.
- v0.2 (2026-02-22): Applied risk audit refinements (explicit 401 draft sync, UUID specification, strict route expectations).
- v0.3 (2026-02-22): Codex Audit resolutions applied: Universal Form + Fail Fast, API Metadata Route, Soft-enforce Compliance, and ENW toggle via domain string.
- v0.4 (2026-02-22): Second Codex Audit resolutions applied: Pivoted to Veni-only MVP slice (dropping Universal Form and new DTO route), clarified 422 hard block vs 200 soft bypass, fixed local draft static keying, and added basic console telemetry.
