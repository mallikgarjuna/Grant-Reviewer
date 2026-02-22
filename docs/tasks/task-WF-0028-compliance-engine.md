# WF-0028 — NWO Veni 2025 preproposal Compliance Engine Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-22

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Define Pydantic request/response schemas

**Goal:** Create the `ComplianceCheckRequest` and `ComplianceCheckResponse` Pydantic models that lock down the API contract for the compliance endpoint.

**Files to modify:**
- `backend/app/schemas/compliance.py` [NEW]

**Acceptance Criteria:**
- `ComplianceCheckRequest` has fields: `call_id: UUID`, `domain: str | None = None`, `draft_nodes: list[DraftNode]`.
- `DraftNode` has fields: `node_logical_id: str`, `text: str`.
- `ComplianceCheckResponse` has fields: `is_compliant: bool`, `errors: list[ComplianceViolation]`, `warnings: list[ComplianceViolation]`.
- `ComplianceViolation` has fields: `node_logical_id: str`, `rule_id: str`, `severity: str`, `actual: str`, `expected: str`, `message: str`, `is_blocking: bool`.
- All models pass `ruff` checks.

**Verification Steps:**
- `cd backend && python -c "from app.schemas.compliance import ComplianceCheckRequest, ComplianceCheckResponse; print('OK')"`
- `cd backend && ruff check app/schemas/compliance.py`

**Risks:** None. Pure data definition, no side effects.

---

### [ ] Task 2 — Implement pure `evaluate_compliance()` engine

**Goal:** Build the core compliance evaluation logic as a pure Python function, decoupled from FastAPI transport (PRD F5). This function ONLY returns domain-level violation/result objects; all HTTP semantics (422, error codes) belong to Task 4.

**Files to modify:**
- `backend/app/services/compliance_engine.py` [NEW]

**Acceptance Criteria:**
- Function signature: `def evaluate_compliance(request: ComplianceCheckRequest, hydrated_nodes: list[HydratedNode]) -> ComplianceCheckResponse`.
- Implements word counting via whitespace splitting (PRD F2).
- Implements domain-aware limit resolution: if `domain` is provided AND `word_limit_by_domain` exists on a node config, use domain-specific max. If `domain` is NOT provided but `word_limit_by_domain.default_max_words` exists, use that fallback. Only if neither path resolves does the engine use `total_word_limit.max_words` (PRD F3).
- Accepts only canonical lowercase domain IDs (e.g., `science_enw`); returns a violation result (not HTTP error) for unrecognized aliases.
- Implements mandatory detection: node is mandatory if `total_word_limit.min_words` > 0. (`MANDATORY` expectation strength is used by the AI review workflow, NOT by the deterministic compliance engine.)
- Flags missing mandatory nodes (not sent in `draft_nodes`) as blocking errors (PRD Edge Case).
- Empty/whitespace-only text treated as missing for mandatory checks.
- Does NOT validate unknown node IDs or return HTTP-level errors — that responsibility belongs to the route layer (Task 4).

**Verification Steps:**
- Unit tests (Task 3) cover all above scenarios.

**Risks:**
- Domain key naming must match canonical YAML exactly (`science_enw`). Verify against `nwo_veni_2025_preproposal.yaml`.

---

### [ ] Task 3 — Add unit tests for compliance engine

**Goal:** Targeted unit test suite for the pure `evaluate_compliance()` function covering deterministic critical paths.

**Files to modify:**
- `backend/tests/test_compliance_engine.py` [NEW]

**Acceptance Criteria:**
- Test: happy path (all nodes compliant) → `is_compliant=True`, empty errors/warnings.
- Test: word limit exceeded → blocking error with correct `actual`/`expected`.
- Test: word limit under minimum → blocking error.
- Test: domain-specific override applied when `domain` is provided.
- Test: fallback to `word_limit_by_domain.default_max_words` when no domain provided.
- Test: fallback to `total_word_limit.max_words` when no `word_limit_by_domain` exists.
- Test: mandatory node omitted from payload → blocking error.
- Test: empty/whitespace text on mandatory node → blocking error.
- Test: node with no `content_constraints` passes silently.
- All tests pass: `cd backend && python -m pytest tests/test_compliance_engine.py -v`.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_engine.py -v`

**Risks:** Test fixtures must accurately reflect the canonical JSON shape from `CallDefinitionService.get_hydrated_nodes()`.

---

### [ ] Task 4 — Wire FastAPI endpoint in `main.py`

**Goal:** Expose `POST /api/check-compliance` in the existing `main.py` router, delegating to the compliance engine service. This layer owns ALL request validation and HTTP error semantics.

**Files to modify:**
- `backend/main.py`

**Acceptance Criteria:**
- New route `POST /api/check-compliance` accepting `ComplianceCheckRequest` body.
- Route calls `CallDefinitionService.get_hydrated_nodes(call_id)` to hydrate constraints.
- Route normalizes `domain` (lowercase/strip) before passing to engine.
- Route validates all submitted `node_logical_id`s exist in hydrated config; returns 422 (`UNKNOWN_NODE_ID`) for unknowns.
- Route validates no duplicate `node_logical_id`s in `draft_nodes`; returns 422 (`DUPLICATE_NODE_ID`) for duplicates.
- Route validates `domain` is present if any hydrated node has `word_limit_by_domain` AND no `default_max_words` fallback exists; returns 422 (`DOMAIN_REQUIRED`) if missing. Returns 422 (`DOMAIN_INVALID`) if `domain` value is unrecognized.
- Route delegates to `evaluate_compliance()` and returns `ComplianceCheckResponse`.
- Route inherits existing BFF auth dependency (`require_bff_user_id`).
- Route logs a warning if `evaluate_compliance()` takes longer than 500ms (PRD §8 Telemetry — single log line only).
- Consistent error responses using existing `APIException` / `build_error_response` patterns with explicit error codes above.

**Verification Steps:**
- `cd backend && ruff check main.py`
- Integration test via pytest (Task 5).

**Risks:**
- `main.py` is already 618 lines. Keep the new handler minimal (delegate to service).

---

### [ ] Task 5 — Add integration tests for `/api/check-compliance`

**Goal:** End-to-end integration tests hitting the FastAPI endpoint via TestClient, verifying the full request→hydrate→evaluate→respond pipeline. Add tests to existing `test_api.py` if it exists, otherwise create a new file.

**Files to modify:**
- `backend/tests/test_api.py` (append compliance section) OR `backend/tests/test_compliance_endpoint.py` [NEW] (if isolation is cleaner)

**Acceptance Criteria:**
- Test: valid payload returns 200 with correct `ComplianceCheckResponse` shape.
- Test: unknown `node_logical_id` returns 422 with `UNKNOWN_NODE_ID` error code.
- Test: duplicate `node_logical_id` returns 422 with `DUPLICATE_NODE_ID` error code.
- Test: missing `domain` when required returns 422 with `DOMAIN_REQUIRED` error code.
- Test: empty `draft_nodes` with mandatory nodes returns 200 with blocking errors.
- Test: unauthenticated request (missing BFF headers) returns 401/403.
- Tests use a seeded test database with a known `CallDefinition` fixture.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_endpoint.py -v` (or `test_api.py`)

**Risks:**
- Requires test DB with seeded `CallDefinition` + `FundingCall`. Check existing test fixtures or create minimal ones.

---

### [ ] Task 6 — Verify end-to-end and update docs

**Goal:** Final verification pass and documentation updates.

**Files to modify:**
- `docs/index.md` (status update)
- `docs/tasks/task-WF-0028-compliance-engine.md` (mark tasks complete)
- `docs/walkthroughs/walkthrough-WF-0028-compliance-engine.md` [NEW]

**Acceptance Criteria:**
- All unit and integration tests pass.
- `ruff check` passes on all new/modified files.
- Walkthrough artifact created at `docs/walkthroughs/walkthrough-WF-0028-compliance-engine.md` documenting changes, test results, and validation.
- `docs/index.md` status updated to `Done`.

**Verification Steps:**
- `cd backend && python -m pytest tests/test_compliance_engine.py tests/test_compliance_endpoint.py -v`
- `cd backend && ruff check app/schemas/compliance.py app/services/compliance_engine.py main.py`

**Risks:** None.

---

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD v0.3.
- v0.2 (2026-02-22): Applied Part B review feedback (domain normalization AC, telemetry AC). Status to Ready for Implementation.
- v0.3 (2026-02-22): Codex adversarial review: removed 422 semantics from engine (Task 2), fixed domain fallback chain, constrained mandatory to `min_words` only, moved unknown-node validation to route layer (Task 4), added explicit error codes, added auth test AC (Task 5), fixed status vocabulary (Task 6).
