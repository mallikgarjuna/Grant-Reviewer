# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review Tasks

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Domain model changes + Alembic migration

**Goal:** Add `AssessmentStatus` enum, extend `Review` and `ReviewCard` models, generate migration.

**Files to modify:**
1. `backend/app/models/domain.py` — Add `AssessmentStatus` enum. On `Review`: add `review_type` (str, default `"single"`), `structured_payload` (JSONB, nullable), make `proposal_snippet_id` nullable. On `ReviewCard`: add `assessment_status` (default `ASSESSED`), `not_assessable_reason` (nullable str).
2. `backend/migrations/versions/xxx_add_structured_review.py` — Alembic migration for all 5 column changes.

**Acceptance Criteria:**
- `AssessmentStatus` enum with `ASSESSED`, `NOT_ASSESSABLE` values.
- `Review.proposal_snippet_id` is nullable (existing rows keep their FK value).
- `Review.review_type` defaults to `"single"`.
- `Review.structured_payload` is JSONB, nullable.
- `ReviewCard.assessment_status` defaults to `ASSESSED`.
- Migration upgrades and downgrades cleanly.
- Existing tests pass unchanged (backward-compatible defaults).

**Verification Steps:**
- Run `alembic upgrade head` successfully.
- Run `alembic downgrade -1` then `alembic upgrade head` again.
- Run existing test suite — all pass.

**Risks:** Nullable conversion on `proposal_snippet_id` must not break existing queries that assume non-null.

---

### [ ] Task 2 — Extract LLM helpers module

**Goal:** Extract `_parse_llm_response()` and `_generate_with_timeout()` from `ReviewerService` into standalone functions in `llm_helpers.py`. Refactor `ReviewerService` to import from there.

**Files to modify:**
1. `backend/app/services/llm_helpers.py` — **[NEW]** Standalone `parse_llm_response(raw_response: str) -> LLMReviewResponse` and `generate_with_timeout(llm_client, prompt: str, timeout: float) -> str`.
2. `backend/app/services/reviewer_service.py` — Remove private methods, import from `llm_helpers`. No behavior change.
3. `backend/tests/test_reviewer_service.py` — Verify existing tests still pass (no behavior change).

**Acceptance Criteria:**
- `llm_helpers.py` exports both functions.
- `ReviewerService` imports and uses them identically to before.
- All existing `ReviewerService` tests pass without modification.
- Error messages preserved exactly (avoid test regressions).

**Verification Steps:**
- Run `pytest tests/test_reviewer_service.py` — all pass.
- Run full test suite — all pass.

**Risks:** Error message strings must be preserved exactly to avoid test assertion failures.

---

### [ ] Task 3 — Extend prompt builder with cross-node context

**Goal:** Add optional `cross_node_context` parameter to `build_review_prompt()`.

**Files to modify:**
1. `backend/app/services/prompt_builder.py` — Add `cross_node_context: dict[str, str] | None = None` parameter. When present, append "Cross-Node Context" section to prompt.
2. `backend/tests/test_prompt_builder.py` — **[NEW or extend]** Test with `None` (legacy behavior unchanged) and with context dict.

**Acceptance Criteria:**
- `build_review_prompt(node, text, expectations)` still works (backward-compatible).
- `build_review_prompt(node, text, expectations, cross_node_context={"academic_profile": "..."})` appends context section.
- Existing prompt builder tests pass.

**Verification Steps:**
- Run prompt builder tests — all pass including new test.
- Run full test suite — all pass.

**Risks:** None — additive change with default `None`.

---

### [ ] Task 4 — Request schema + structured review endpoint (F1, F8, F16)

**Goal:** Add `StructuredReviewRequest` Pydantic model and wire up `POST /api/structured-review` route with validation (payload size, duplicates, node existence), idempotency, and quota checks. Route returns `CreateReviewResponse`. Service call is stubbed.

**Files to modify:**
1. `backend/app/schemas/structured_review.py` — **[NEW]** `StructuredReviewNodeInput` and `StructuredReviewRequest` with validators (non-empty nodes, max chars, duplicate check).
2. `backend/main.py` — Add `POST /api/structured-review` route. Wire auth (`X-GR-User-Id`), idempotency (`Idempotency-Key` header), quota check, payload validation. Call service (stubbed to raise `NotImplementedError` for now).
3. `backend/tests/test_structured_review_endpoint.py` — **[NEW]** Test: empty nodes → 422, unknown node_id → 422, duplicate node → 422, payload too large → 422, valid payload → reaches service call.

**Acceptance Criteria:**
- Pydantic model validates per-node max 10,000 chars and total max 30,000 chars.
- Duplicate `node_logical_id` returns 422.
- Empty `nodes` list returns 422.
- Idempotency-Key header required (409 on mismatch, return existing on match).
- Quota check counts structured reviews against daily limit.

**Verification Steps:**
- Run endpoint tests — all pass.
- Manual: `curl` with invalid payload → 422.

**Risks:** Must match existing idempotency pattern from `POST /reviews` exactly.

---

### [ ] Task 5 — StructuredReviewerService core logic (F2–F7, F13)

**Goal:** Implement `StructuredReviewerService` with full orchestration: per-node LLM review, cross-node context injection, NOT_ASSESSABLE card generation, single Review persistence.

**Files to modify:**
1. `backend/app/services/structured_reviewer_service.py` — **[NEW]** Core service. Imports from `llm_helpers`, `prompt_builder`. Hardcodes NWO Veni alignment rules (F3). Partitions expectations into assessable/not-assessable. Builds prompt per node with cross-node context. Creates `ReviewCard`s with `assessment_status`. Persists single `Review` with `review_type="structured"`, `structured_payload` JSONB.
2. `backend/tests/test_structured_reviewer_service.py` — **[NEW]** Unit tests: happy path (3 nodes, all assessable), partial submission (missing academic_profile → NOT_ASSESSABLE alignment cards), LLM timeout on one node → FAILED status with partial cards, empty node text handling.

**Acceptance Criteria:**
- One `Review` created per call with `review_type="structured"`.
- `proposal_snippet_id=NULL`, `structured_payload` stores raw node texts.
- Assessable expectations → LLM call → ASSESSED cards.
- NOT_ASSESSABLE cards created deterministically with reason text.
- LLM cardinality validated only for assessable expectations (F5).
- Partial LLM failure → `status=FAILED`, successful cards retained (F13).
- Counts as 1 review for quota (F7).

**Verification Steps:**
- Run service tests — all pass.
- Run full test suite — all pass.

**Risks:** Hardcoded element IDs must match NWO Veni YAML exactly (`elem_cv_idea_alignment`, `elem_alignment_plan_credibility`).

---

### [ ] Task 6 — Wire endpoint to service + integration test

**Goal:** Remove service stub from Task 4, wire `POST /api/structured-review` to `StructuredReviewerService`. Add integration test.

**Files to modify:**
1. `backend/main.py` — Replace `NotImplementedError` stub with actual `StructuredReviewerService` call. Wire repository + LLM client.
2. `backend/tests/test_structured_review_integration.py` — **[NEW]** Integration test: POST valid 3-node payload with mocked LLM → verify Review created with `review_type="structured"`, verify cards created with correct `assessment_status`, verify `structured_payload` stored.

**Acceptance Criteria:**
- `POST /api/structured-review` with valid payload → 200 with `review_id` + `status=COMPLETED`.
- Review record has `review_type="structured"`, `proposal_snippet_id=NULL`, `structured_payload` populated.
- Cards have correct `assessment_status` values.

**Verification Steps:**
- Run integration test — passes.
- Run full test suite — all pass.

**Risks:** None — wiring task only.

---

### [ ] Task 7 — Repository adaptation (F9, F10, F11)

**Goal:** Adapt `list_reviews_for_external_user()`, `get_review_owner_external_user_id()`, and `delete_review_hard()` to handle `proposal_snippet_id=NULL`.

**Files to modify:**
1. `backend/app/repositories/review_repository.py` — Adapt 3 methods: LEFT JOIN for listing, direct `external_user_id` fallback for ownership, NULL-safe snippet handling for delete.
2. `backend/tests/test_review_repository.py` — **[NEW or extend]** Tests for each adapted method with both single-node and structured review fixtures.

**Acceptance Criteria:**
- `list_reviews_for_external_user()` returns both single and structured reviews. Structured reviews show `node_title="Structured review"`.
- `get_review_owner_external_user_id()` resolves ownership for structured reviews via `Review.external_user_id`.
- `delete_review_hard()` safely handles `proposal_snippet_id=NULL` (skip snippet delete).
- Legacy single-node behavior unchanged for all three methods.

**Verification Steps:**
- Run repository tests — all pass.
- Run full test suite — all pass (existing tests confirm no regression).

**Risks:** LEFT JOIN change in list query may alter result ordering or duplicate rows — verify with test.

---

### [ ] Task 8 — API model extension + detail endpoint fix (F14, F15)

**Goal:** Extend `ReviewCardSummary` with `assessment_status` and `not_assessable_reason`. Fix `GET /reviews/{id}` to return cards for FAILED structured reviews.

**Files to modify:**
1. `backend/app/schemas/api.py` — Add `assessment_status: str | None = None` and `not_assessable_reason: str | None = None` to `ReviewCardSummary`.
2. `backend/main.py` — Change card loading condition: load cards when `status == COMPLETED` OR (`status == FAILED` and `review.review_type == "structured"`). Populate new fields from `ReviewCard` model.
3. `backend/tests/test_review_detail.py` — **[NEW or extend]** Test: FAILED structured review with partial cards → detail returns cards with `assessment_status` populated.

**Acceptance Criteria:**
- `ReviewCardSummary` includes `assessment_status` and `not_assessable_reason` (optional, backward-compatible).
- `GET /reviews/{id}` for COMPLETED reviews → cards shown (unchanged).
- `GET /reviews/{id}` for FAILED structured review with partial cards → cards shown.
- `GET /reviews/{id}` for FAILED single-node review → no cards (unchanged behavior).
- Old single-node cards return `None` for both new fields.

**Verification Steps:**
- Run detail endpoint tests — all pass.
- Run full test suite — all pass.

**Risks:** Must preserve backward compat for single-node reviews (no behavior change for existing FAILED single-node reviews).

---

### [ ] Task 9 — End-to-end verification

**Goal:** Verify the complete structured review flow end-to-end against a test database with NWO Veni V2 data.

**Files to modify:**
1. `backend/tests/test_structured_review_e2e.py` — **[NEW]** E2E test: ingest NWO Veni YAML → POST structured review with 3 nodes → verify Review + cards → GET detail → verify response shape including assessment_status. Also test: partial submission (2 nodes) → verify NOT_ASSESSABLE cards for alignment elements.

**Acceptance Criteria:**
- Full happy path works with ingested NWO Veni data.
- Partial submission produces correct NOT_ASSESSABLE cards for `elem_cv_idea_alignment` and `elem_alignment_plan_credibility`.
- Review appears in `GET /reviews` list with `node_title="Structured review"`.
- Review detail shows cards with `assessment_status` field populated.
- Deletion works for structured reviews.

**Verification Steps:**
- Run E2E test — passes.
- Run full test suite — all pass.

**Risks:** Requires NWO Veni V2 data ingested in test fixture. Must match exact element IDs from YAML.

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD v0.4.
