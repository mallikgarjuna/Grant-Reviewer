# WF-0030 — NWO Veni 2025 Preproposal Structured AI Review (WF-6 Phase) PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-02-22

## 1. In Scope
- A universal, dynamically rendered submission form at `/app/submit`.
- Dynamic generation of flat `<textarea>` inputs based on backend `FundingCall` schemas.
- Plain-text ingestion with a mandatory UI disclaimer regarding rich text / table limitations.
- Zero-latency client-side word count enforcement replicating backend standard whitespace rules.
- Two-step submission orchestration: `/api/check-compliance` followed by `/api/structured-review`.
- Form warning bypass modal ("Submit Anyway") allowing intentionally non-compliant submissions to proceed to evaluation.
- Local draft saving in `localStorage` securely keyed by `call_id` and schema version.
- Idempotency preservation via explicit client-side `UUID v4` generation passed in the `Idempotency-Key` header.
- Robust submission lifecycle handling: 90-second blocking overlay, timeout toasts, session 401 handling, and immediate post-success routing.

## 2. Out of Scope
- File uploads, document parsing (e.g., `.docx` to markdown via MarkItDown).
- Rendering deeply nested schemas or recursive form hierarchies (P2).
- Native rich-text (WYSIWYG) editors.
- Advanced evaluation constraint matching (e.g., lists boundaries inside outputs).
- Cross-node dependency visualizations.

## 3. User / System Flow
**Happy Path:**
1. User navigates to `/app/submit` and selects "NWO Veni 2025" from a dropdown.
2. Frontend fetches schema. Parses flat nodes. Renders 3 textareas.
3. User pastes text. Real-time counters update without network calls.
4. User clicks "Submit".
5. Frontend calls `/api/check-compliance`. Backend returns 200 OK (no violations).
6. Frontend automatically posts to `/api/structured-review` with `Idempotency-Key`.
7. UI shows 90-second blocking overlay.
8. Backend returns successful `review_id`.
9. Frontend routes to `/app/reviews/{review_id}` and clears the local draft for this schema.

**Soft Enforcement (Bypass) Path:**
1. User enters >100 words in "Research Idea" violating standard limit.
2. User clicks "Submit".
3. Frontend calls `/api/check-compliance`. Backend returns 400 Bad Request with violations.
4. Frontend traps error, maps it, and shows summary alert + Bypass Modal ("Your draft exceeds official limits. Proceed?").
5. User clicks "Submit Anyway".
6. Frontend posts to `/api/structured-review` with `Idempotency-Key` (bypassing compliance).
... proceeds to success.

**Failure Path (Session Expiration 401):**
1. User drafts proposal (persisted locally on every change).
2. User's Clerk session expires implicitly.
3. User clicks "Submit".
4. Request hits 401 Unauthorized.
5. Frontend traps 401, guarantees local storage sync, and redirects to Clerk sign-in page.

## 4. Functional Requirements
- **Dynamic Field Mapping**: Map top-level `ProposalNode` instances to textareas. Ignore non-text nodes and explicitly show "Unsupported Input Type".
- **Real-Time Word Counter**: Apply standard `text.split(/\s+/)` algorithm locally for live counters (e.g., "450 / 400 words").
- **ENW/Science Toggle**: Add contextual toggle to change local client-side limits without backend state changes. Pass boolean/rule identifier to backend `check-compliance` payload.
- **Draft Persistence**: Save drafts to `localStorage` under `draft_${call_id}_${schema_hash}`. Restore implicitly on schema load. Show ephemeral toast upon restoration.

## 5. Data & API Contracts
**Client -> `/api/check-compliance` (POST)**
- Purpose: Execute standard compliance without locking tokens or triggering LLM.
- Payloads: `call_id` and complete node payload objects (`node_id`, `text`). Options for specific ENW sub-rules.

**Client -> `/api/structured-review` (POST)**
- Expected headers: `Idempotency-Key: <UUIDv4>`
- Payloads: `call_id`, populated node array.

**Response Handling:**
- Trap `FeedbackCard`-shaped objects from the compliance engine to render the bypass warnings.

## 6. Components / Modules
- `SubmitForm`: Top-level orchestrator.
- `DynamicStructureRenderer`: Consumes `proposal_structure` mapping.
- `LocalStorageDraftManager`: React hook for safe persistance.
- `ComplianceBypassModal`: Headless UI logic for secondary confirmation.
- `BlockingOverlay`: High z-index spinner overlay locking inputs.

## 7. Edge Cases
- Schema changes while user has a stored draft -> Composite keys ensure user doesn't load a draft onto a mismatched schema. Can attempt `best-effort` mapping.
- Fast double clicks on Submit -> UUID Idempotency-Key prevents backend duplication; `BlockingOverlay` prevents rapid frontend clicks.
- Table / Multi-line pastes -> Accepted without processing; rich markup is stripped, rely on LLM to map tab-spaced chunks correctly. Add explicit UI disclaimer.

## 8. Telemetry (Minimal)
- None

## Deferred / Not in MVP
- Assisted Extraction via Document Upload (P2 #14).
- Cross-Node Context Dependency Visualization (P1 #12).

## Changelog
- v0.1 (2026-02-22): Initial PRD generated from brainstorm v1.0.
- v0.2 (2026-02-22): Applied risk audit refinements (explicit 401 draft sync, UUID specification, strict route expectations).
