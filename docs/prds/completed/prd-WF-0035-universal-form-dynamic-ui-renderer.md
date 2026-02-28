# WF-0035 — Universal Form: Dynamic UI renderer PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-28

## 0. User Stories (MVP)

- US1: As a researcher, I want to select any structured call and see its flat proposal nodes rendered dynamically, so that I can submit non-Veni calls without frontend code changes.
- US2: As a researcher, I want to submit partially completed node content (at least one non-empty node) through the existing compliance + structured review flow, so that I can iterate on drafts without being blocked.
- US3: As a researcher, I want explicit unsupported-call messaging when nested nodes are present, so that I do not submit incomplete or misleading content.
- US4: As a frontend maintainer, I want a deterministic render model built from existing backend contracts, so that the renderer remains stable as new calls are ingested.

## Deferred Stories (Not in MVP)

- DS1: Recursive/nested rendering for calls with `parent_node_id != null`.
- DS2: Legacy single-snippet mode unification into the universal form.
- DS3: Markdown/rich text node input support.
- DS4: Server-side draft persistence.
- DS5: New backend form-schema endpoint.

## 1. In Scope

- Replace the Veni-specific submit form shell with a universal submit form on the existing submit route. (US1)
- Build structured-call eligibility from existing endpoints and include only calls with `ui_mode="structured_nodes"`. (US1, US4)
- Build a flat render model from:
  - `GET /calls/{call_id}/nodes?view=flat` for ordering and node identity.
  - `GET /api/public/calls/{call_logical_id}/nodes/metadata` for labels and UI constraints. (US1, US4)
- Enforce flat-only guardrail: hard-block selected calls if any node has `parent_node_id != null`. (US3)
- Preserve current compliance flow semantics:
  - local counters/helpful client UX,
  - `POST /api/bff/check-compliance` before review submit,
  - warning bypass modal remains supported. (US2)
- Preserve review submit contract via `POST /api/bff/structured-review`, submitting only non-empty nodes. (US2)
- Keep local draft persistence scoped per selected call. (US2)
- Preserve domain-aware compliance behavior using a generic domain selector when a call has configured domain options; pass selected domain to compliance checks. (US2)

## 2. Out of Scope

- Backend endpoint additions or schema changes.
- Recursive rendering/navigation patterns for nested trees.
- Full submit-page redesign.
- New content widgets beyond plain-text textarea inputs.
- Server-side drafts, autosync, or collaboration.

## 3. User / System Flow

### Happy Path

1. User opens submit page; frontend fetches calls via `GET /api/bff/calls`. (US1)
2. Frontend gates each call by fetching `GET /api/public/calls/{code}/config` and keeps `ui_mode="structured_nodes"` only. (US1, US4)
3. User selects a structured call; frontend fetches nodes list from `GET /calls/{call_id}/nodes?view=flat` and metadata from `GET /api/public/calls/{code}/nodes/metadata`. (US1, US4)
4. Frontend assembles render model in nodes API order, using metadata labels/constraints and safe fallbacks for missing metadata. (US1, US4)
5. User enters text in one or more node textareas; per-call draft persists in localStorage. (US2)
6. User submits; frontend requires at least one non-empty node, runs compliance precheck, shows warnings if present, then calls structured review submit. (US2)
7. Backend accepts payload with `nodes[] { node_logical_id, text }`, creates review, and returns review id/status. (US2)

### Failure Path A — Nested Nodes Detected (Unsupported)

1. User selects a structured call. (US3)
2. Frontend detects at least one node with `parent_node_id != null` from nodes response. (US3)
3. Frontend blocks editing/submission and displays explicit unsupported nested-call message with recursion deferment note. (US3)

### Failure Path B — Call Config Gating Errors

1. Frontend attempts to fetch config for each call. (US1, US4)
2. One or more config requests timeout/fail; failed calls are excluded from structured list. (US1, US4)
3. Frontend surfaces non-blocking banner indicating some calls could not be loaded, while allowing eligible calls to proceed. (US1)

### Failure Path C — Metadata Missing/Partial

1. Nodes list loads, metadata request returns partial or missing fields. (US1, US4)
2. Frontend renders with safe fallbacks (`label := logical_id`, hide absent constraints) and warning banner. (US1, US4)
3. Submission remains allowed if at least one non-empty node is present. (US2)

### Failure Path D — Compliance Hard-Block Response

1. User submits and compliance precheck returns blocking response (e.g., invalid/missing domain or node-level blocking rule). (US2)
2. Frontend surfaces blocking errors inline and prevents structured-review submit call. (US2)
3. User corrects inputs/domain selection and re-runs submit flow. (US2)

## 4. Functional Requirements

- FR1 (US1): Submit page MUST render via one universal form component instead of hardcoded call-specific field list.
- FR2 (US1, US4): Frontend MUST source call candidates from `GET /api/bff/calls` and include only calls whose config reports `ui_mode="structured_nodes"`.
- FR3 (US1, US4): Config gating MUST tolerate partial failures and still show successfully gated calls.
- FR4 (US1, US4): Frontend MUST fetch flat nodes from `GET /calls/{call_id}/nodes?view=flat` and preserve returned ordering as render order.
- FR5 (US1, US4): Frontend MUST fetch metadata from `GET /api/public/calls/{call_logical_id}/nodes/metadata` and enrich fields with labels/constraints when present.
- FR6 (US3): Frontend MUST treat any non-null `parent_node_id` as nested unsupported state and block submit for that selected call.
- FR7 (US3): Unsupported nested-call state MUST provide explicit user-facing explanation and prevent silent partial rendering.
- FR8 (US2): Client validation MUST require at least one non-empty node before submission.
- FR9 (US2): Compliance precheck flow MUST remain in-path before structured review submit.
- FR10 (US2): Structured review submit payload MUST include only non-empty nodes and preserve `node_logical_id` identity.
- FR11 (US2): Frontend MUST keep draft state isolated per selected call key to avoid cross-call overwrite.
- FR12 (US1, US4): Metadata gaps MUST degrade safely without blocking valid submission when node identity is present.
- FR13 (US1): MVP acceptance MUST be demonstrated on Veni plus at least one additional flat structured call.
- FR14 (US2): Universal form MUST support optional per-call domain selection for compliance requests and pass selected `domain` to `POST /api/bff/check-compliance`.
- FR15 (US2, US4): If any rendered node lacks required `logical_id`, UI MUST hard-block submission for that call and show an explicit data-contract error.
- FR16 (US1, US4): Config gating requests MUST use deterministic defaults (max concurrency = 4, per-request timeout = 4 seconds).
- FR17 (US2): Structured-review submit MUST preserve idempotency semantics by sending a valid `Idempotency-Key` header on every submit attempt.
- FR18 (US1, US2, US4): Render-model assembly MUST use deterministic identity precedence: nodes endpoint `logical_id` is authoritative for submission identity; metadata is enrichment-only and cannot override submission identity.
- FR19 (US1): MVP completion evidence MUST include an explicit acceptance matrix proving Veni + one additional flat structured call for render, compliance precheck, and submit.

## 5. Data & API Contracts

### Contract C1 — Calls Listing and Gating (US1, US4; FR2, FR3, FR16)

- Calls source: `GET /api/bff/calls`
  - Minimal required fields: `{ id, code, name }`.
- Per-call config gate: `GET /api/public/calls/{code}/config`
  - Include call only when `ui_mode == "structured_nodes"`.
- Client-side gating behavior:
  - Concurrency-limited config fetches (max 4 in-flight).
  - Timeout-safe per request (4 seconds, then mark call as failed-to-gate).
  - Partial results allowed; failures produce non-blocking warning banner.

### Contract C2 — Render Model Inputs (US1, US4; FR4, FR5, FR6, FR12, FR15)

- Node ordering/identity source: `GET /calls/{call_id}/nodes?view=flat`
  - Required per node: `{ id, logical_id, parent_node_id, title, order_index }`.
- Label/constraint source: `GET /api/public/calls/{code}/nodes/metadata`
  - Required to enrich when present: `{ logical_id, label, content_constraints, compliance_rules }`.
- Join key: `logical_id`.
- Identity precedence:
  - Submission identity is sourced from nodes endpoint `logical_id` only.
  - Metadata `logical_id` is used only to enrich matching nodes and must not create new submit-eligible nodes.
  - If metadata contains unmatched logical IDs, ignore for submission and emit warning telemetry.
- `logical_id` invariant:
  - Nodes lacking `logical_id` cannot be represented in structured submit payload.
  - Selected call enters explicit data-contract blocked state if any node lacks `logical_id`.
- Flat-only invariant:
  - Supported only when every node has `parent_node_id == null`.
  - Otherwise enter explicit unsupported state (no submission).

### Contract C3 — Compliance + Submit (US2; FR8, FR9, FR10, FR14, FR17)

- Compliance precheck: `POST /api/bff/check-compliance`
  - Request includes selected `call_id` and full draft snapshot.
  - Request includes optional `domain` when call has domain options and user has selected one.
  - Response may contain warnings and/or blocking issues.
- Review submit: `POST /api/bff/structured-review`
  - Request includes `call_id`, `review_stage`, and `nodes[]` with `{ node_logical_id, text }`.
  - Domain is not part of this request contract in MVP.
  - Submit payload contains only non-empty nodes.
  - At least one node is required.
  - Request must include `Idempotency-Key` header for safe retries.
- Success response remains current `CreateReviewResponse` shape (`review_id`, `status`).

### Contract C4 — Draft State (US2; FR11)

- Draft storage remains browser localStorage.
- Keying scope is per selected `call_id` to avoid cross-call collisions.
- Call switch loads the corresponding isolated draft snapshot.

### Contract C5 — Domain Options Source (US2, US4; FR14)

- Domain options source in WF-0035 is an explicit interim frontend mapping keyed by `call code`.
- If no mapping exists for selected call, domain selector is hidden and compliance request sends `domain: null`.
- If compliance returns domain-related blocking validation, UI surfaces block inline and does not call structured-review submit.

## 6. Components / Modules

### Boundaries and Responsibilities

- `frontend/src/app/app/page.tsx`
  - Keep route entrypoint; mount universal submit shell instead of Veni-specific shell. (FR1)
- `frontend/src/components/submit/UniversalSubmitForm.tsx` (new)
  - Own call selection, gating lifecycle, render-model assembly, and unsupported states. (FR2-FR7, FR12)
- `frontend/src/lib/api/*` (existing + extension)
  - Encapsulate calls/config/nodes/metadata/compliance/submit APIs with typed DTOs. (FR2-FR5, FR9, FR10)
- `frontend/src/lib/submit/renderModel.ts` (new)
  - Deterministic builder from nodes + metadata with fallback rules. (FR4, FR5, FR12)
- `frontend/src/lib/submit/draftStore.ts` (new or existing extraction)
  - Per-call local draft read/write/reset helpers. (FR11)
- `frontend/src/lib/submit/domainOptions.ts` (new)
  - Interim per-call domain options mapping for compliance-only domain picker. (FR14)

### Design Tree (Dependencies + Ordering)

1. Define frontend types and render-model contract (nodes + metadata + unsupported state).
2. Implement call gating and selection flow.
3. Implement flat renderer with fallback labels/constraints.
4. Integrate per-call draft persistence.
5. Integrate compliance precheck + structured submit with current UX semantics.
6. Add/adjust tests proving Veni + second call behavior and nested hard-block state.

### Deep Modules

- `renderModel` should be a deep module:
  - Small API: build renderable fields + state flags from API responses.
  - Hidden complexity: merge/join rules, fallback behavior, nested guardrail classification.

### Suggested File Paths

- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/lib/submit/renderModel.ts`
- `frontend/src/lib/submit/draftStore.ts`
- `frontend/src/lib/api/calls.ts` (or equivalent existing client module)
- `frontend/src/lib/api/submit.ts` (or equivalent existing client module)
- `frontend/src/components/submit/__tests__/...`

## 7. Edge Cases

- EC1 (US3): Call config says structured but nodes contain nested relationships; UI must hard-block.
- EC2 (US2, US4): `logical_id` missing for one or more nodes; UI must hard-block submit and surface explicit contract mismatch error.
- EC3 (US1, US4): Metadata unknowns/partials; UI must avoid crashes and expose fallback labeling.
- EC4 (US2): User submits whitespace-only entries; client trims/filters and enforces at least one non-empty node.
- EC5 (US2): Compliance warning bypass path must preserve existing confirmation semantics.
- EC6 (US1): Some calls fail config fetch; list remains usable with partial results warning.
- EC7 (US2): Domain-required compliance calls without domain selection must be blocked by compliance precheck and surfaced inline.
- EC8 (US1, US4): Metadata includes logical IDs not present in nodes list; renderer ignores unmatched metadata for submission identity and logs warning telemetry.

## 8. Testing Decisions (TDD)

- Public seams under test:
  - Universal form rendering and call selection behavior. (FR1-FR7)
  - Render-model builder deterministic outputs from fixture DTOs. (FR4, FR5, FR6, FR12, FR18)
  - Compliance + submit pipeline payload shaping. (FR8-FR10, FR17)
  - Draft isolation by call key. (FR11)

- Boundary mocking rules:
  - Mock network/API boundaries only.
  - Do not mock render-model pure logic internals.

- Minimal test types per story/requirement:
  - US1: component tests for call selection + dynamic field count/order across Veni and second call.
  - US2: component/integration-ish tests for at-least-one validation, compliance precheck invocation, and submit payload filtering.
  - US3: component tests for nested hard-block banner + disabled submit state.
  - US4: unit tests for render-model merge/fallback logic and partial metadata handling.
  - Domain path: tests verify domain selector appears only when configured, passes selected domain to compliance precheck, and preserves submit behavior.
  - Idempotency path: tests assert structured-review submit includes `Idempotency-Key` and retry semantics remain safe.
  - Contract precedence path: tests assert metadata cannot override nodes endpoint submission identity.

MVP acceptance evidence (required before marking implementation done):
- Acceptance matrix with 2 calls (Veni + 1 additional flat structured call), each proving:
  - dynamic render field coverage/order,
  - compliance precheck behavior (including warning/bypass and blocking path where applicable),
  - successful structured-review submit and review creation.

## 9. Telemetry (Minimal)

- Emit structured client logs/events for:
  - call gating summary (`total_calls`, `eligible_calls`, `failed_config_calls`),
  - unsupported nested call selection,
  - metadata fallback usage count,
  - submit attempt outcome (`precheck_blocked`, `precheck_warning_bypassed`, `submitted`).

## 10. Deferred / Not in MVP

- Recursive/nested form rendering and multi-level navigation.
- Domain-aware dynamic options sourced from canonical definitions.
- Legacy single-snippet + structured mode unification.
- Rich text/Markdown node inputs.
- Server draft sync/version history.
- Backend structured-call filtering endpoint to replace client-side N+1 config gating.
- Large-form navigation UX for calls beyond the MVP target size.

Parking lot traceability:
- `docs/parking_lot.md` P1 #1 (recursive nested rendering).
- `docs/parking_lot.md` P2 #20 (Markdown/rich text inputs).
- `docs/parking_lot.md` P2 #21 (legacy single-snippet unification).
- `docs/parking_lot.md` P2 #26 (backend structured-call filter endpoint).
- `docs/parking_lot.md` P2 #27 (canonical domain-options contract).
- `docs/parking_lot.md` P2 #28 (large-form navigation UX).

## 11. Open Questions (if any)

- None.
- Defaults applied in v0.3:
  - Missing `logical_id` in any selected-call node is a hard-blocking contract error.
  - Config gating defaults are fixed to 4 in-flight requests and 4-second timeout per request.

## 12. Changelog

- v0.1 (2026-02-28): Initial PRD from brainstorm.
- v0.2 (2026-02-28): Applied risk-audit edits (domain handling, explicit contract hard-blocks, deterministic gating defaults) and marked Ready for Tasks.
- v0.3 (2026-02-28): Applied adversarial hardening (identity precedence, idempotency requirement, compliance block flow, domain source defaults, and explicit MVP acceptance evidence).
