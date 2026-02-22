# WF-0030 — NWO Veni 2025 Preproposal Structured AI Review (WF-6 Phase) PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-22

## 1. In Scope
- A universal, dynamically rendered submission form at `/app/submit`.
- Dynamic generation of flat `<textarea>` inputs based on backend `FundingCall` schemas.
- **Fail-fast behavior**: If the dynamically fetched schema contains nested nodes, explicitly prevent rendering and redirect/show a blocking error.
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
1. User enters text in "Research Idea" violating standard limit.
2. User clicks "Submit".
3. Frontend calls `/api/check-compliance`. Backend returns 200 OK with `errors[]` from the compliance report.
4. Frontend traps the presence of `errors`, maps them, and shows summary alert + Bypass Modal ("Your draft exceeds official limits. Proceed?").
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
- **Dynamic Field Mapping**: Map top-level node IDs to textareas. Parse a new backend DTO endpoint providing `node_logical_id`, labels, and constraints. Ignore non-text nodes and explicitly show "Unsupported Input Type". Fail-fast on nested node structures.
- **Real-Time Word Counter**: Apply standard `text.split(/\s+/)` algorithm locally for live counters (e.g., "450 / 400 words").
- **ENW/Science Toggle**: Add contextual toggle to change local client-side limits. Persist the selected exact domain string in the local draft and pass it explicitly to the BFF `/api/check-compliance` proxy.
- **Draft Persistence**: Save drafts to `localStorage` under `draft_${call_id}_${schema_hash}`. Restore implicitly on schema load. Show ephemeral toast upon restoration.

## 5. Data & API Contracts
**Client -> `/api/check-compliance` (POST)**
- Purpose: Execute standard compliance without locking tokens or triggering LLM.
- Payloads: `ComplianceCheckRequest` shape containing `call_id`, optional `domain` string, and `draft_nodes` array (`node_logical_id`, `text`).
- Requirement: Implement Next.js BFF route for `/api/check-compliance` proxying signed headers.

**Client -> `/api/structured-review` (POST)**
- Expected headers: `Idempotency-Key: <UUIDv4>`
- Payloads: `StructuredReviewRequest` shape containing `call_id`, and `nodes` array (`node_logical_id`, `text`).
- Requirement: Implement Next.js BFF route for `/api/structured-review` proxying signed headers.

**Backend Node Metadata DTO Route**
- Requirement: Implement a new API endpoint (e.g. `GET /calls/{call_id}/form-schema`) to serve `node_logical_id`, labels, and constraints explicitly for frontend rendering, without exposing raw JSON.

**Response Handling:**
- Trap `ComplianceViolation` objects mapped from the `errors[]` compliance engine response to render the bypass warnings.

## 6. Components / Modules
- `SubmitForm`: Top-level orchestrator.
- `DynamicStructureRenderer`: Consumes `proposal_structure` mapping.
- `LocalStorageDraftManager`: React hook for safe persistance.
- `ComplianceBypassModal`: Headless UI logic for secondary confirmation.
- `BlockingOverlay`: High z-index spinner overlay locking inputs.

## 7. Edge Cases
- Schema changes while user has a stored draft -> Composite keys ensure user doesn't load a draft onto a mismatched schema. No cross-version remap in MVP unless backend explicitly passes a stable schema generation hash.
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
- v0.3 (2026-02-22): Codex Audit resolutions applied: Universal Form + Fail Fast, API Metadata Route, Soft-enforce Compliance, and ENW toggle via domain string.
