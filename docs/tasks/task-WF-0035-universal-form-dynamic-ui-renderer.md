# WF-0035 — Universal Form: Dynamic UI renderer Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-28

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: mount universal submit shell with dynamic nodes + submit

Goal:
- Replace the hardcoded Veni submit shell with a universal component that renders node textareas from API data and submits with idempotency for one flat structured call.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR4, FR8, FR9, FR10, FR17
Depends on: none
Enables: Task 2, Task 3
Parallelizable: no
Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/page.test.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.tsx` (new)
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx` (new)
Acceptance Criteria:
- Submit route mounts `UniversalSubmitForm` instead of `VeniSubmitForm`.
- Submit page test no longer asserts the legacy hardcoded Veni shell and instead asserts universal-form mount behavior.
- Universal form loads one selected call, renders dynamic textarea fields from nodes API order, and supports submit with non-empty node filtering.
- Structured submit request includes `Idempotency-Key` header.
TDD Plan:
- RED: add failing `UniversalSubmitForm.test.tsx` for dynamic node render + at-least-one validation + idempotent submit header.
- GREEN: implement minimal universal component, route wiring, and updated page-level test expectations to pass.
- REFACTOR: remove duplicated payload shaping helpers in component (`skip` if none).
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx`
- `cd frontend && nvm use && npx vitest run src/app/app/page.test.tsx`
Risks (if any):
- Early component may duplicate logic currently in `VeniSubmitForm` and need cleanup in later tasks.

### [x] Task 2 — Structured-call gating with deterministic timeout/concurrency defaults

Goal:
- Enforce structured-only call dropdown via config gating with fixed defaults and partial-results UX.
Slice: call-gating
User Stories: US1, US4
PRD Requirements: FR2, FR3, FR16
Depends on: Task 1
Enables: Task 6, Task 8
Parallelizable: no
Files to modify:
- `frontend/src/lib/submit/loadStructuredCalls.ts` (new)
- `frontend/src/lib/submit/loadStructuredCalls.test.ts` (new)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
Acceptance Criteria:
- Form includes only calls whose config reports `ui_mode="structured_nodes"`.
- Config fetch uses max 4 concurrent requests and 4-second timeout per request.
- Partial gating failures show non-blocking warning banner while keeping eligible calls usable.
TDD Plan:
- RED: add failing `loadStructuredCalls.test.ts` cases for structured filtering, timeout behavior, and partial failure aggregation.
- GREEN: implement concurrency-limited gated loader and connect it in component.
- REFACTOR: extract error-to-banner mapping helper.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/lib/submit/loadStructuredCalls.test.ts`
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "gating"`
Risks (if any):
- Promise throttling bugs can accidentally hide eligible calls.

### [x] Task 3 — Render-model deep module with identity precedence and hard-block guards

Goal:
- Centralize render-model assembly and unsupported-state classification (nested nodes, missing logical IDs, metadata fallback).
Slice: render-model-core
User Stories: US1, US3, US4
PRD Requirements: FR6, FR7, FR12, FR15, FR18
Depends on: Task 1
Enables: Task 6
Parallelizable: yes (planning-only)
Files to modify:
- `frontend/src/lib/submit/renderModel.ts` (new)
- `frontend/src/lib/submit/renderModel.test.ts` (new)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
Acceptance Criteria:
- Render model preserves nodes endpoint ordering and uses nodes `logical_id` as authoritative submission identity.
- Component enters explicit hard-block state for nested calls or any missing `logical_id`.
- Metadata gaps degrade safely (fallback labels/hidden constraints) without identity drift.
TDD Plan:
- RED: add failing render-model tests for nested detection, missing `logical_id`, and metadata mismatch precedence.
- GREEN: implement pure render-model builder and integrate in component.
- REFACTOR: simplify discriminated result state (`ready|unsupported|contract_error`).
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/lib/submit/renderModel.test.ts`
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "unsupported"`
Risks (if any):
- Incorrect state classification can over-block otherwise valid calls.

### [x] Task 4 — BFF metadata contract support in adapter/types

Goal:
- Add typed metadata contract and adapter call for call-node metadata retrieval.
Slice: bff-metadata-contract
User Stories: US1, US4
PRD Requirements: FR5
Depends on: Task 1
Enables: Task 5
Parallelizable: yes (planning-only)
Files to modify:
- `frontend/src/lib/bff/types.ts`
- `frontend/src/lib/bff/adapter.ts`
- `frontend/src/lib/bff/adapter.metadata.test.ts` (new)
Acceptance Criteria:
- `types.ts` defines metadata DTO shapes required by universal renderer.
- Adapter exposes metadata fetch method for `GET /api/public/calls/{call_logical_id}/nodes/metadata`.
- Adapter tests validate path, method, and successful payload parsing behavior.
TDD Plan:
- RED: add failing adapter metadata tests asserting request path and typed response handling.
- GREEN: implement metadata adapter function and types.
- REFACTOR: reuse existing request helper typing where duplicated.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/lib/bff/adapter.metadata.test.ts`
Risks (if any):
- Mis-typed metadata DTO can silently break render enrichment.

### [x] Task 5 — Add BFF metadata proxy route and integrate enrichment in universal form

Goal:
- Expose metadata through authenticated BFF route and use it to enrich universal form labels/constraints.
Slice: metadata-enrichment
User Stories: US1, US4
PRD Requirements: FR5, FR12, FR18
Depends on: Task 3, Task 4
Enables: Task 8
Parallelizable: no
Files to modify:
- `frontend/src/app/api/bff/calls/[callId]/metadata/route.ts` (new)
- `frontend/src/app/api/bff/calls/[callId]/metadata/route.test.ts` (new)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
Acceptance Criteria:
- New BFF route proxies metadata request with existing auth/signature guards.
- Universal form reads metadata via the new BFF route (`/api/bff/calls/{code}/metadata`), not direct backend-public endpoint calls.
- Route test verifies auth guard passthrough + success and error response mapping.
TDD Plan:
- RED: add failing route test for metadata proxy success/error mapping and parameter forwarding.
- GREEN: implement BFF metadata route and component call-site wiring.
- REFACTOR: share route error handling structure with existing `calls/[callId]/config` and `calls/[callId]/nodes` routes.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/app/api/bff/calls/[callId]/metadata/route.test.ts`
- `cd frontend && nvm use && npx vitest run src/lib/bff/adapter.metadata.test.ts`
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "metadata route"`
Risks (if any):
- Route path mismatch (`code` vs `id`) can break metadata loading.

### [x] Task 6 — Domain options bridge + compliance hard-block UX

Goal:
- Add interim per-call domain options mapping and ensure domain-related compliance blocking prevents submit.
Slice: domain-bridge
User Stories: US2, US4
PRD Requirements: FR14
Depends on: Task 2, Task 3
Enables: Task 8
Parallelizable: no
Files to modify:
- `frontend/src/lib/submit/domainOptions.ts` (new)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
Acceptance Criteria:
- Domain selector appears only for calls with configured options in interim mapping.
- Compliance request includes selected `domain` when available; otherwise sends `domain: null`.
- Domain-related compliance hard-block responses prevent structured-review submit and show inline blocking state.
TDD Plan:
- RED: add failing tests for domain selector visibility and compliance 422 block behavior.
- GREEN: implement domain options helper and component integration.
- REFACTOR: extract domain payload builder.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "domain"`
Risks (if any):
- Interim mapping may drift if call codes change.

### [x] Task 7 — Per-call draft isolation helper and call-switch safety

Goal:
- Ensure local drafts are isolated by selected `call_id` and preserved across call switches.
Slice: draft-isolation
User Stories: US2
PRD Requirements: FR11
Depends on: Task 1
Enables: Task 8
Parallelizable: yes (planning-only)
Files to modify:
- `frontend/src/lib/submit/draftStore.ts` (new)
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
Acceptance Criteria:
- Draft storage keying is per selected `call_id`.
- Switching calls loads the matching draft and does not overwrite other call drafts.
- Clearing submit success removes only the active call draft.
TDD Plan:
- RED: add failing tests for per-call draft persistence and cross-call isolation.
- GREEN: implement draft store helper and integrate in component.
- REFACTOR: remove ad-hoc localStorage key concatenation from component.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "draft"`
Risks (if any):
- Existing users may carry legacy draft keys from Veni-only implementation.

### [x] Task 8 — End-to-end submit orchestration parity and telemetry events

Goal:
- Finalize universal submit orchestration parity (warnings bypass, blocking paths, telemetry counters) with comprehensive component coverage.
Slice: orchestration-parity
User Stories: US1, US2, US3
PRD Requirements: FR5, FR8, FR9, FR10, FR12, FR17, FR18
Depends on: Task 2, Task 5, Task 6, Task 7
Enables: Task 9
Parallelizable: no
Files to modify:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/page.test.tsx`
Acceptance Criteria:
- Warning bypass modal behavior remains parity with current flow.
- Compliance hard-block, auth redirect, and submit success paths are all covered for universal form.
- Metadata enrichment assertions exist for label rendering + unmatched metadata non-creation of submit-eligible nodes.
- Telemetry events are emitted for gating summary, unsupported-call selection, metadata fallback usage, and submit outcomes.
TDD Plan:
- RED: add failing tests for metadata enrichment behavior, warning bypass gating, hard-block prevention of submit, and telemetry event calls.
- GREEN: implement final orchestration paths and event emission.
- REFACTOR: prune superseded `VeniSubmitForm`-specific assertions from page-level tests.
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx src/app/app/page.test.tsx`
Risks (if any):
- Event logging placement may accidentally duplicate or miss key transitions.

### [ ] Task 9 — Legacy cleanup: remove Veni-specific submit form/test surface

Goal:
- Remove legacy Veni-specific submit component/test artifacts so the codebase/testbase aligns with universal structured submit direction and avoids fallback drift to old assumptions.
Slice: legacy-cleanup
User Stories: US1, US4
PRD Requirements: FR1, FR2
Depends on: Task 8
Enables: Task 10
Parallelizable: no
Files to modify:
- `frontend/src/components/submit/VeniSubmitForm.tsx`
- `frontend/src/components/submit/VeniSubmitForm.test.tsx`
- `frontend/package.json`
Acceptance Criteria:
- No runtime route depends on `VeniSubmitForm`.
- Legacy `VeniSubmitForm` test entry is removed/replaced from test script targets.
- Any retained compatibility shim (if needed) is explicitly marked deprecated and non-default.
TDD Plan:
- RED: ensure task-local test command fails when legacy test target remains in script list or imports remain in active route path.
- GREEN: remove/replace legacy component and test wiring with universal-form equivalents.
- REFACTOR: clean stale naming/comments implying hardcoded Veni-only submit UX.
Verification Steps:
- `cd frontend && nvm use && npm run test:ui`
- `cd frontend && nvm use && rg -n "VeniSubmitForm" src/app src/components/submit src/lib || true`
Risks (if any):
- Deleting legacy files too early can break in-progress references if prior tasks are incomplete.

### [ ] Task 10 — Capture MVP acceptance matrix evidence for two flat calls

Goal:
- Produce explicit implementation evidence matrix for Veni + one additional flat structured call across render/compliance/submit.
Slice: acceptance-evidence
User Stories: US1
PRD Requirements: FR13, FR19
Depends on: Task 9
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0035-universal-form-dynamic-ui-renderer.md`
Acceptance Criteria:
- Walkthrough includes matrix rows for Veni and second flat call.
- Each row includes proof links/evidence for dynamic render, compliance precheck outcome, and successful review creation.
- Any gaps are explicitly listed with pass/fail status (no implicit assumptions).
TDD Plan: N/A (documentation evidence task)
Verification Steps:
- `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx`
- `cd backend && PYTHONPATH=. uv run pytest tests/test_api.py -k "structured_review"`
- `cd /home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer && rg -n "Veni|second flat structured call|render|compliance|submit|pass|fail" docs/walkthroughs/walkthrough-WF-0035-universal-form-dynamic-ui-renderer.md`
Risks (if any):
- Evidence can become stale if implementation changes after matrix capture.

## Changelog

- v0.1 (2026-02-28): Initial task breakdown from PRD
- v0.2 (2026-02-28): Applied task review tightenings (metadata route test coverage, explicit metadata enrichment assertions in orchestration task) and marked Ready for Implementation
- v0.3 (2026-02-28): Applied adversarial micro-revision (early page-test alignment, Task 5 integration verification, explicit evidence-check command) and added legacy submit-surface cleanup task to avoid regression to old assumptions.
