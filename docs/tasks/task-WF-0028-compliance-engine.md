# WF-0028 — NWO Veni 2025 preproposal Compliance Engine Tasks

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Define Pydantic request/response schemas

**Goal:** Create the `ComplianceCheckRequest` and `ComplianceCheckResponse` Pydantic models that lock down the API contract for the compliance endpoint.

**Files to modify:**
- `backend/app/schemas/compliance.py` [NEW]
- `backend/app/schemas/__init__.py` (re-export)

**Acceptance Criteria:**
- `ComplianceCheckRequest` has fields: `call_id: UUID`, `domain: str | None = None`, `draft_nodes: list[DraftNode]`.
- `DraftNode` has fields: `node_logical_id: str`, `text: str`.
- `ComplianceCheckResponse` has fields: `is_compliant: bool`, `errors: list[ComplianceViolation]`, `warnings: list[ComplianceViolation]`.
- `ComplianceViolation` has fields: `node_logical_id: str`, `rule_id: str`, `severity: str`, `actual: str`, `expected: str`, `message: str`, `is_blocking: bool`.
- All models pass `mypy`/`ruff` checks.

**Verification Steps:**
- `cd backend && python -c "from app.schemas.compliance import ComplianceCheckRequest, ComplianceCheckResponse; print('OK')"`
- `cd backend && ruff check app/schemas/compliance.py`

**Risks:** None. Pure data definition, no side effects.

---

### [ ] Task 2 — Implement pure `evaluate_compliance()` engine

**Goal:** Build the core compliance evaluation logic as a pure Python function, decoupled from FastAPI transport (PRD F5).

**Files to modify:**
- `backend/app/services/compliance_engine.py` [NEW]

**Acceptance Criteria:**
- Function signature: `def evaluate_compliance(request: ComplianceCheckRequest, hydrated_nodes: list[HydratedNode]) -> ComplianceCheckResponse`.
- Implements word counting via whitespace splitting (PRD F2).
- Implements domain-aware limit resolution: if `domain` is provided AND `word_limit_by_domain` exists on a node config, use domain-specific max; otherwise fallback to `total_word_limit.max_words` (PRD F3).
- Implements mandatory detection: node is mandatory if `total_word_limit.min_words > 0` or node has a `MANDATORY` expectation strength (PRD F4).
- Flags missing mandatory nodes (not sent in `draft_nodes`) as blocking errors (PRD Edge Case).
- Returns 422-equivalent error info for unknown `node_logical_id`s submitted by the caller.
- Empty/whitespace-only text treated as missing for mandatory checks.

**Verification Steps:**
- Unit tests (Task 3) cover all above scenarios.

**Risks:**
- Domain key naming must match canonical YAML exactly (`science_enw`). Verify against `nwo_veni_2025_preproposal.yaml`.

---

### [ ] Task 3 — Add unit tests for compliance engine

**Goal:** Exhaustive unit test suite for the pure `evaluate_compliance()` function covering happy path, failure paths, and edge cases.

**Files to modify:**
- `backend/tests/test_compliance_engine.py` [NEW]

**Acceptance Criteria:**
- Test: happy path (all nodes compliant) → `is_compliant=True`, empty errors/warnings.
- Test: word limit exceeded → blocking error with correct `actual`/`expected`.
- Test: word limit under minimum → blocking error.
- Test: domain-specific override applied when `domain` is provided.
- Test: fallback to `total_word_limit` when no domain provided.
- Test: mandatory node omitted from payload → blocking error.
- Test: empty/whitespace text on mandatory node → blocking error.
- Test: unknown `node_logical_id` → validation error returned.
- Test: node with no `content_constraints` passes silently.
- All tests pass: `cd backend && python -m pytest tests/test_compliance_engine.py -v`.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_engine.py -v`

**Risks:** Test fixtures must accurately reflect the canonical JSON shape from `CallDefinitionService.get_hydrated_nodes()`.

---

### [ ] Task 4 — Wire FastAPI endpoint in `main.py`

**Goal:** Expose `POST /api/check-compliance` in the existing `main.py` router, delegating to the compliance engine service.

**Files to modify:**
- `backend/main.py`

**Acceptance Criteria:**
- New route `POST /api/check-compliance` accepting `ComplianceCheckRequest` body.
- Route calls `CallDefinitionService.get_hydrated_nodes(call_id)` to hydrate constraints.
- Route validates that `domain` is present if any hydrated node has `word_limit_by_domain`; returns 422 if missing.
- Route validates all submitted `node_logical_id`s exist in hydrated config; returns 422 for unknowns.
- Route delegates to `evaluate_compliance()` and returns `ComplianceCheckResponse`.
- Route inherits existing BFF auth dependency (`require_bff_user_id`).
- Consistent error responses using existing `APIException` / `build_error_response` patterns.

**Verification Steps:**
- `cd backend && ruff check main.py`
- Integration test via `curl` or pytest (Task 5).

**Risks:**
- `main.py` is already 618 lines. Keep the new handler minimal (delegate to service).

---

### [ ] Task 5 — Add integration test for `/api/check-compliance`

**Goal:** End-to-end integration test hitting the FastAPI endpoint via TestClient, verifying the full request→hydrate→evaluate→respond pipeline.

**Files to modify:**
- `backend/tests/test_compliance_endpoint.py` [NEW]

**Acceptance Criteria:**
- Test: valid payload returns 200 with correct `ComplianceCheckResponse` shape.
- Test: unknown `node_logical_id` returns 422.
- Test: missing `domain` when required returns 422.
- Test: empty `draft_nodes` with mandatory nodes returns blocking errors.
- Tests use a seeded test database with a known `CallDefinition` fixture.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_endpoint.py -v`

**Risks:**
- Requires test DB with seeded `CallDefinition` + `FundingCall`. Check existing test fixtures or create minimal ones.

---

### [ ] Task 6 — Verify end-to-end and update docs

**Goal:** Final verification pass and documentation updates.

**Files to modify:**
- `docs/index.md` (status update)
- `docs/tasks/task-WF-0028-compliance-engine.md` (mark tasks complete)

**Acceptance Criteria:**
- All unit and integration tests pass.
- `ruff check` passes on all new/modified files.
- `docs/index.md` status updated to `Phase 3 (Done)`.
- Walkthrough artifact created at `docs/walkthroughs/walkthrough-WF-0028-compliance-engine.md`.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_engine.py tests/test_compliance_endpoint.py -v`
- `cd backend && ruff check app/schemas/compliance.py app/services/compliance_engine.py main.py`

**Risks:** None.

---

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD v0.3.
