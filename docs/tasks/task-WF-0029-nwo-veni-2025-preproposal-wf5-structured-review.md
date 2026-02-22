# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-22

## Task Breakdown (Sequential Order)

### [x] Task 1 — Domain model changes + Alembic migration

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
- Schema compiles; targeted model import smoke test passes.

**Verification Steps:**
- Run `alembic upgrade head` successfully.
- Run `alembic downgrade -1` then `alembic upgrade head` again.
- `python -c "from app.models.domain import Review, ReviewCard, AssessmentStatus"` succeeds.

**Risks:** Nullable conversion on `proposal_snippet_id` will require follow-on repository adaptation (Tasks 4–5).

---

### [x] Task 2 — Extract LLM helpers module

**Goal:** Extract `_parse_llm_response()` and `_generate_with_timeout()` from `ReviewerService` into standalone functions in `llm_helpers.py`. Refactor `ReviewerService` to import from there.

**Files to modify:**
1. `backend/app/services/llm_helpers.py` — **[NEW]** Standalone `parse_llm_response(raw_response: str) -> LLMReviewResponse` and `generate_with_timeout(llm_client, prompt: str, timeout: float) -> str`.
2. `backend/app/services/reviewer_service.py` — Remove private methods, import from `llm_helpers`. No behavior change.

**Acceptance Criteria:**
- `llm_helpers.py` exports both functions with identical signatures/error messages.
- `ReviewerService` imports and uses them identically to before.
- All existing `ReviewerService` tests pass without modification (parity proof).

**Verification Steps:**
- Run `pytest tests/` — all existing tests pass (parity assertion).

**Risks:** Error message strings must be preserved exactly to avoid test assertion failures.

---

### [x] Task 3 — Extend prompt builder with cross-node context

**Goal:** Add optional `cross_node_context` parameter to `build_review_prompt()`.

**Files to modify:**
1. `backend/app/services/prompt_builder.py` — Add `cross_node_context: dict[str, str] | None = None` parameter. When present, append "Cross-Node Context" section to prompt.
2. `backend/tests/test_prompt_builder.py` — **[NEW or extend]** Test with `None` (legacy behavior unchanged) and with context dict.

**Acceptance Criteria:**
- `build_review_prompt(node, text, expectations)` still works (backward-compatible).
- `build_review_prompt(node, text, expectations, cross_node_context={"academic_profile": "..."})` appends context section.

**Verification Steps:**
- Run prompt builder tests — all pass including new test.

**Risks:** None — additive change with default `None`.

---

### [x] Task 4 — Repository write-path adaptation for structured reviews

**Goal:** Adapt `create_review()` and `create_review_card()` to accept the new structured review fields. Must be done BEFORE `StructuredReviewerService` (Task 6).

**Files to modify:**
1. `backend/app/repositories/review_repository.py` — `create_review()`: add optional `review_type`, `structured_payload` params; make `snippet_id` optional (nullable). `create_review_card()`: add optional `assessment_status`, `not_assessable_reason` params.
2. `backend/tests/test_api.py` — **[Extend]** Add smoke test: create a structured review record (`snippet_id=None`, `review_type="structured"`) and a review card with `assessment_status=NOT_ASSESSABLE`. Verify round-trip.

**Acceptance Criteria:**
- `create_review(snippet_id=None, review_type="structured", structured_payload={...})` succeeds.
- `create_review_card(..., assessment_status=AssessmentStatus.NOT_ASSESSABLE, not_assessable_reason="missing context")` succeeds.
- Existing single-node `create_review(snippet_id=uuid)` behavior unchanged (backward-compatible).

**Verification Steps:**
- Run `pytest tests/` — all pass (existing + new smoke tests).

**Risks:** Must preserve existing call signatures as backward-compatible (use keyword defaults).

---

### [x] Task 5 — Repository read-path adaptation (F9, F10, F11)

**Goal:** Adapt `list_reviews_for_external_user()`, `get_review_owner_external_user_id()`, and `delete_review_hard()` to handle `proposal_snippet_id=NULL`.

**Files to modify:**
1. `backend/app/repositories/review_repository.py` — Adapt 3 methods: LEFT JOIN for listing (with `COALESCE` for structured title), direct `external_user_id` fallback for ownership, NULL-safe snippet handling for delete.
2. `backend/tests/test_api.py` — **[Extend]** Tests for each adapted method with both single-node (legacy backward-compat) and structured review fixtures.

**Acceptance Criteria:**
- `list_reviews_for_external_user()` returns both single and structured reviews. Structured reviews show `node_title="Structured review"`.
- `get_review_owner_external_user_id()` resolves ownership for structured reviews via `Review.external_user_id`.
- `delete_review_hard()` safely handles `proposal_snippet_id=NULL` (skip snippet delete).
- Legacy single-node behavior unchanged for all three methods (explicit backward-compat tests).

**Verification Steps:**
- Run `pytest tests/` — all pass.

**Risks:** LEFT JOIN change in list query may alter row ordering — verify with test.

---

### [ ] Task 6 — StructuredReviewerService core logic (F2–F7, F13)

**Goal:** Implement `StructuredReviewerService` with full orchestration. Depends on T2 (helpers), T3 (prompt builder), T4 (write-path).

**Files to modify:**
1. `backend/app/services/structured_reviewer_service.py` — **[NEW]** Core service. Imports from `llm_helpers`, `prompt_builder`. Hardcodes NWO Veni alignment rules: for `elem_cv_idea_alignment` and `elem_alignment_plan_credibility` on `research_idea` node, require BOTH `academic_profile` AND `key_outputs` context. Partitions expectations into assessable/not-assessable. Creates `ReviewCard`s with `assessment_status`. Persists single `Review` with `review_type="structured"`, `structured_payload` JSONB.
2. `backend/tests/test_structured_reviewer_service.py` — **[NEW]** Unit tests: happy path (3 nodes, all assessable), partial submission (missing `academic_profile` → NOT_ASSESSABLE for alignment cards), missing `key_outputs` → also NOT_ASSESSABLE, LLM timeout on one node → FAILED + partial cards, cardinality validation on assessable-only expectations.

**Acceptance Criteria:**
- One `Review` created per call with `review_type="structured"`, `proposal_snippet_id=NULL`.
- `structured_payload` stores raw node texts.
- Assessable expectations → LLM call → ASSESSED cards.
- NOT_ASSESSABLE cards created deterministically with reason text naming the specific missing node.
- Alignment dependency rule: `elem_cv_idea_alignment` and `elem_alignment_plan_credibility` require BOTH `academic_profile` AND `key_outputs` (matches PRD F3 exactly).
- LLM cardinality validated only for assessable expectations (F5).
- Partial LLM failure → `status=FAILED`, successful cards retained (F13).
- Counts as 1 review for quota (F7).

**Verification Steps:**
- Run `pytest tests/test_structured_reviewer_service.py` — all pass.

**Risks:** Hardcoded element IDs must match YAML exactly (`elem_cv_idea_alignment`, `elem_alignment_plan_credibility`).

---

### [ ] Task 7 — Endpoint + service wiring + integration tests (F1, F8, F16)

**Goal:** Add `POST /api/structured-review` route with full validation, idempotency, quota, and wired to `StructuredReviewerService`. No stub.

**Files to modify:**
1. `backend/app/schemas/structured_review.py` — **[NEW]** `StructuredReviewNodeInput` and `StructuredReviewRequest` with validators (non-empty nodes, max 10K chars/node, max 30K total, duplicate check).
2. `backend/main.py` — Add `POST /api/structured-review` route. Wire auth (`X-GR-User-Id`), idempotency (`Idempotency-Key` header, 409 on mismatch, permanent key uniqueness), quota check, payload validation. Call `StructuredReviewerService`. Return `CreateReviewResponse`.
3. `backend/tests/test_api.py` — **[Extend]** Integration tests: empty nodes → 422, unknown node → 422, duplicate node → 422, payload too large → 422, valid 3-node payload with mocked LLM → 200 + review created with correct `review_type`/`structured_payload`/card `assessment_status`. Cross-endpoint idempotency collision test (same key on `/reviews` then `/structured-review`).

**Acceptance Criteria:**
- `POST /api/structured-review` with valid payload → 200 with `review_id` + `status`.
- All validation rules enforced (422 for each invalid case).
- Idempotency matches existing `/reviews` behavior (permanent key uniqueness, 409 on mismatch).
- Cross-endpoint idempotency test verifies distinct key requirement.
- Review record has `review_type="structured"`, `proposal_snippet_id=NULL`, `structured_payload` populated.

**Verification Steps:**
- Run `pytest tests/test_api.py` — all pass.

**Risks:** Must match existing idempotency pattern from `POST /reviews` exactly.

---

### [ ] Task 8 — API model extension + detail endpoint fix (F14, F15)

**Goal:** Extend `ReviewCardSummary` with `assessment_status` and `not_assessable_reason`. Fix `GET /reviews/{id}` to return cards for FAILED structured reviews.

**Files to modify:**
1. `backend/app/schemas/api.py` — Add `assessment_status: str | None = None` and `not_assessable_reason: str | None = None` to `ReviewCardSummary`.
2. `backend/main.py` — Change card loading condition: load cards when `status == COMPLETED` OR (`status == FAILED` and `review.review_type == "structured"`). Populate new fields from `ReviewCard` model.
3. `backend/tests/test_api.py` — **[Extend]** Tests: FAILED structured review with partial cards → detail returns cards with `assessment_status` populated. Old single-node review cards return `None` for both new fields (backward-compat mapping test).

**Acceptance Criteria:**
- `ReviewCardSummary` includes `assessment_status` and `not_assessable_reason` (optional, backward-compatible).
- `GET /reviews/{id}` for COMPLETED reviews → cards shown (unchanged).
- `GET /reviews/{id}` for FAILED structured review with partial cards → cards shown.
- `GET /reviews/{id}` for FAILED single-node review → no cards (unchanged behavior).
- Old single-node review cards return `assessment_status=None`, `not_assessable_reason=None`.

**Verification Steps:**
- Run `pytest tests/test_api.py` — all pass.

**Risks:** Must preserve backward compat for single-node reviews.

---

### [ ] Task 9 — (Optional) E2E smoke test

**Goal:** Thin smoke test verifying the complete structured review flow against ingested NWO Veni data. **Not on critical path — run after Tasks 1–8 pass.**

**Files to modify:**
1. `backend/tests/test_api.py` — **[Extend]** One thin E2E test: ingest NWO Veni YAML → POST structured review with 3 nodes → verify Review + cards + `assessment_status` → GET detail → verify response. One partial submission test (2 nodes, missing `academic_profile`) → verify NOT_ASSESSABLE cards.

**Acceptance Criteria:**
- Full happy path works with ingested NWO Veni data.
- Partial submission produces correct NOT_ASSESSABLE cards for alignment elements.

**Verification Steps:**
- Run `pytest tests/test_api.py` — all pass.

**Risks:** Requires NWO Veni V2 data ingested in test fixture.

## Changelog

- v0.1 (2026-02-22): Initial task breakdown from PRD v0.4.
- v0.2 (2026-02-22): Applied self-audit. Reordered repo adaptation before wiring.
- v0.3 (2026-02-22): Per Codex audit. Added Task 4 (repo write-path glue). Merged old T4+T7 into T7 (endpoint + wiring, no stub). Demoted T9 to optional. Fixed T1 acceptance criteria (removed false "existing tests pass unchanged"). Added explicit alignment rule AC to T6. Added backward-compat and mapping tests to T5/T8. Consolidated tests in `test_api.py` (no fragmented test files). Renumbered all tasks.
