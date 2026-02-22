# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-22

## 1. In Scope (MVP-Now)

- New `POST /api/structured-review` endpoint accepting multi-node payload (`call_id` + `nodes[]` with `node_logical_id` + `text`), returning per-node AI feedback cards.
- New `StructuredReviewerService` orchestrating: multi-node validation → per-node LLM review with cross-node context → deterministic `NOT_ASSESSABLE` card generation → single `Review` record persistence.
- **Extracted LLM helpers module** (`app/services/llm_helpers.py`): `parse_llm_response()` and `generate_with_timeout()` extracted from `ReviewerService` private methods into standalone functions. Both `ReviewerService` and `StructuredReviewerService` import from here.
- Schema additions on `Review`: `review_type` (str, default `"single"`), `structured_payload` (JSONB, nullable — stores `{node_logical_id: text}` for audit/replay), make `proposal_snippet_id` nullable.
- Schema additions on `ReviewCard`: `assessment_status` (enum, default `ASSESSED`), `not_assessable_reason` (str, nullable).
- New `AssessmentStatus` enum (`ASSESSED` / `NOT_ASSESSABLE`).
- **Hardcoded NWO Veni cross-node context rules** in `StructuredReviewerService`: for `elem_cv_idea_alignment` and `elem_alignment_plan_credibility`, include `academic_profile` text as cross-node context when building the prompt. No generalized dependency metadata for MVP.
- Adapt existing repository queries (`list_reviews`, `get_review_owner`, `delete_review_hard`) to handle `proposal_snippet_id=NULL` for structured reviews.
- Alembic migration for all schema changes.
- Integration with existing review history listing and detail endpoints (reuse existing response shapes).

## 2. Out of Scope

- LLM-generated overall summary across nodes (P2 #6).
- Mega-prompt optimization — single LLM call for all nodes (P2 #5).
- Prompt quality tuning for V2 expectations structure (P2 #7).
- Parallel per-node LLM calls (P2 #8).
- Batch submission of multiple proposals (P2 #9).
- Async processing / polling (P2 #10).
- Frontend changes — no UI form, no BFF proxy update (WF-6).
- `StructuredSubmission` aggregate table — deferred; JSONB on Review for MVP (P2 #11).
- `requires_context_from` on `NodeExpectation` DB field + YAML ingestion + V2 schema update — deferred; hardcoded NWO rules for MVP (P2 #12).
- New structured-specific detail endpoint (`/reviews/{id}/structured`) — deferred; reuse existing flat detail shape (P2 #13).
- Per-node grouping in API response — deferred to frontend (WF-6).

## 3. User / System Flow

### Happy Path

1. Frontend POSTs `{ call_id, nodes: [{ node_logical_id, text }, ...] }` to `/api/structured-review` with `Idempotency-Key` header.
2. Backend resolves `call_id` → `FundingCall`, validates all `node_logical_id`s exist for that call.
3. Backend stores raw submission as `Review.structured_payload` (JSONB) for audit. Sets `Review.proposal_snippet_id = NULL`, `Review.review_type = "structured"`.
4. For each submitted node (sequentially):
   a. Fetch `NodeExpectation`s for that node.
   b. Determine assessability: if a hardcoded cross-node dependency exists (e.g., `elem_cv_idea_alignment` needs `academic_profile`) and that node's text was not submitted or is empty → NOT_ASSESSABLE.
   c. For assessable expectations: build prompt (with cross-node context text if applicable) → call LLM → parse response → create `ReviewCard`s with `assessment_status=ASSESSED`.
   d. For not-assessable expectations: create deterministic `ReviewCard`s with `assessment_status=NOT_ASSESSABLE` + reason text. LLM is NOT invoked for these.
5. Create single `Review` with all `ReviewCard`s. Set `status=COMPLETED`.
6. Return HTTP 200 with `{ review_id, status }` (same shape as `CreateReviewResponse`).

### Failure Path 1 — Unknown Node ID

1. Frontend submits a `node_logical_id` not in the call's `ProposalNode` set.
2. Backend returns HTTP 422: `"Unknown node_logical_id: 'invalid_node'"`.

### Failure Path 2 — LLM Timeout (Partial)

1. LLM call for one node times out (30s per-call timeout).
2. `Review` is set to `status=FAILED`. Cards from successful prior nodes are persisted (non-atomic). Error message indicates which node failed via `overall_summary`.
3. Frontend receives HTTP 200 with `status=FAILED` and partial cards.

### Failure Path 3 — Empty Payload

1. Frontend submits `nodes: []` (empty list).
2. Backend returns HTTP 422: `"At least one node is required"`.

## 4. Functional Requirements

- **F1 (Endpoint):** `POST /api/structured-review` accepts `StructuredReviewRequest`, returns `CreateReviewResponse` (existing shape: `review_id` + `status`). Requires `X-GR-User-Id` header + `Idempotency-Key` header (matching existing auth/idempotency pattern from `POST /reviews`).
- **F2 (Service):** New `StructuredReviewerService`. Does NOT call `ReviewerService.generate_review()`. Imports `parse_llm_response()` and `generate_with_timeout()` from `app/services/llm_helpers.py` (extracted from `ReviewerService` private methods). Also imports `build_review_prompt()` from prompt_builder.
- **F3 (Cross-node context):** Hardcoded in `StructuredReviewerService` for NWO Veni: when building a prompt for `research_idea` node, if `elem_cv_idea_alignment` or `elem_alignment_plan_credibility` expectations exist, include `academic_profile` text as context. Uses element `logical_id` matching against known IDs.
- **F4 (NOT_ASSESSABLE):** If a hardcoded cross-node dependency references a node that was NOT submitted (or has empty text), that expectation's `ReviewCard` is created deterministically with `assessment_status=NOT_ASSESSABLE` and `not_assessable_reason` explaining the missing context. The LLM is NOT asked to evaluate it.
- **F5 (Cardinality):** LLM response validation enforces 1:1 cardinality ONLY for assessable expectations sent to the LLM (exclude NOT_ASSESSABLE expectations from the count).
- **F6 (Persistence):** One `Review` per structured submission. `review_type="structured"`. `proposal_snippet_id=NULL`. Raw input stored in `structured_payload` JSONB.
- **F7 (Quota):** Structured review counts as 1 review against daily quota (not N per node).
- **F8 (Idempotency):** `Idempotency-Key` header (same transport as existing `POST /reviews`). One key = one structured review. Payload mismatch behavior: if key exists with different payload hash, return HTTP 409 Conflict (same as existing semantics).
- **F9 (History integration):** Structured reviews appear in `GET /reviews` list. `list_reviews_for_external_user()` must be adapted: use LEFT JOIN or UNION to include reviews with `proposal_snippet_id=NULL`. Display title: `"Structured review"` for structured reviews.
- **F10 (Ownership check):** `get_review_owner_external_user_id()` must handle structured reviews: resolve ownership via `Review.external_user_id` directly (already stored on Review) instead of the snippet join chain.
- **F11 (Delete cascade):** `delete_review_hard()` for structured reviews: delete cards + review only (no snippet to cascade since `proposal_snippet_id=NULL`). Structured payload is lost on delete (acceptable for MVP).
- **F12 (Prompt builder contract):** `build_review_prompt()` accepts optional `cross_node_context: dict[str, str]` parameter. When present, context texts are appended under a "Cross-Node Context" section. Existing call path passes `None` (no legacy behavior change).
- **F13 (Transaction model):** Non-atomic. Repository commits per-row (existing pattern). On partial LLM failure: `Review.status=FAILED`, successfully generated cards are kept, `overall_summary` reports which node failed. No automatic retry. Client may retry with same idempotency key after expiry.

## 5. Data & API Contracts

### Request (`POST /api/structured-review`)

```json
{
  "call_id": "uuid",
  "nodes": [
    { "node_logical_id": "academic_profile", "text": "..." },
    { "node_logical_id": "key_outputs", "text": "..." },
    { "node_logical_id": "research_idea", "text": "..." }
  ]
}
```

**Headers:** `X-GR-User-Id` (required), `Idempotency-Key` (required), `X-GR-Payload-SHA256` (optional).

**Validation:**
- `call_id`: required UUID, must exist in DB.
- `nodes`: non-empty list. Each: `node_logical_id` (string, must match `ProposalNode.logical_id` for that call), `text` (string, may be empty — triggers NOT_ASSESSABLE for cross-node dependent expectations).
- Duplicate `node_logical_id` → 422.

### Response (`HTTP 200`)

Reuses existing `CreateReviewResponse` shape:
```json
{
  "review_id": "uuid",
  "status": "COMPLETED"
}
```

Client then calls existing `GET /reviews/{review_id}` for full detail (flat `cards[]`).

### State Transitions

- `Review.status`: `PENDING` → `COMPLETED` (all nodes succeed) or `PENDING` → `FAILED` (any LLM call fails).
- `ReviewCard.assessment_status`: Set at creation time. `ASSESSED` (LLM-generated) or `NOT_ASSESSABLE` (deterministic).

### New Enums

- `AssessmentStatus`: `ASSESSED`, `NOT_ASSESSABLE`

### Schema Changes (Alembic migration)

| Table | Change | Type |
|---|---|---|
| `reviews` | Add `review_type: str` (default `"single"`) | Column |
| `reviews` | Make `proposal_snippet_id` nullable | Column alter |
| `reviews` | Add `structured_payload: JSONB` (nullable) | Column |
| `review_cards` | Add `assessment_status: AssessmentStatus` (default `ASSESSED`) | Column |
| `review_cards` | Add `not_assessable_reason: str` (nullable) | Column |

**5 column changes, 0 new tables.**

### Card Grouping (Query-Time Derivation)

Card → node grouping is derived at query time via: `ReviewCard.node_expectation_id` → `NodeExpectation.proposal_node_id` → `ProposalNode.logical_id`. No denormalized `node_logical_id` column on `ReviewCard` (avoids data duplication). Grouping is a presentation concern handled by the frontend (WF-6).

## 6. Components / Modules

| Component | Responsibility | Suggested Path |
|---|---|---|
| **Schemas** | Request Pydantic model for structured review | `app/schemas/structured_review.py` |
| **Service** | Orchestration: cross-node context, LLM calls, NOT_ASSESSABLE, persistence | `app/services/structured_reviewer_service.py` |
| **LLM Helpers** | Extracted: `parse_llm_response()`, `generate_with_timeout()` | `app/services/llm_helpers.py` |
| **Domain models** | Updated `Review` + `ReviewCard`, new `AssessmentStatus` enum | `app/models/domain.py` |
| **Migration** | 5 column changes | `migrations/versions/xxx_add_structured_review.py` |
| **Router** | FastAPI route `POST /api/structured-review` | `main.py` (existing pattern) |
| **Prompt builder** | Optional `cross_node_context` parameter | `app/services/prompt_builder.py` |
| **Repository (adapted)** | `list_reviews`, `get_review_owner`, `delete_review_hard` handle NULL snippet | `app/repositories/review_repository.py` |
| **ReviewerService (refactor)** | Import from `llm_helpers` instead of private methods | `app/services/reviewer_service.py` |

## 7. Edge Cases

- **Partial submission (2 of 3 nodes):** Valid. Missing node → NOT_ASSESSABLE for alignment-dependent expectations on present nodes. Present nodes still get full LLM review.
- **Single-node structured submission:** Valid. Returns one node group. `review_type` = `"structured"`.
- **Empty text for a submitted node:** Node is "present but empty." Node's own expectations that don't require cross-node context → LLM still tries. Expectations requiring context FROM this empty node (on other nodes) → NOT_ASSESSABLE.
- **All LLM calls fail:** `Review.status=FAILED`. Zero assessed cards. Review appears in history as failed.
- **Node with zero expectations:** Logged warning. No cards generated for that node.
- **Idempotency key collision (same payload):** Return existing review without re-processing.
- **Idempotency key collision (different payload):** HTTP 409 Conflict.
- **Review history listing:** `list_reviews_for_external_user()` adapted with LEFT JOIN. Structured reviews show `node_title="Structured review"`.
- **Review deletion:** Structured reviews have no snippet to cascade. Delete cards + review only.
- **Review detail:** Existing `GET /reviews/{review_id}` returns flat `cards[]` for both single and structured reviews. Per-node grouping deferred to frontend (WF-6).
- **Partial LLM failure (transaction model):** Non-atomic. Node-1 cards committed successfully, node-2 LLM times out. `Review.status=FAILED`, `overall_summary` reports failed node. Cards from node-1 are retained. Client may retry after idempotency key expiry.
- **Cross-endpoint idempotency collision:** `Idempotency-Key` is scoped to `(external_user_id, idempotency_key)`. Keys are shared across `/reviews` and `/structured-review`. Clients must use distinct keys per endpoint to avoid collisions.

## 8. Telemetry (Minimal)

- Log total wall-clock time for structured review (all nodes combined).
- Log per-node LLM call time.
- Log count of NOT_ASSESSABLE cards per review.
- Log warning if total time exceeds 60s.

## Deferred / Not in MVP

| Item | Parking Lot # | Rationale |
|---|---|---|
| LLM-generated overall summary | P2 #6 | Cross-node synthesis — separate LLM call |
| Mega-prompt optimization | P2 #5 | Latency optimization — requires new prompt/parser |
| Prompt quality tuning | P2 #7 | Prompt engineering — separate concern |
| Parallel per-node LLM calls | P2 #8 | Perf optimization |
| Batch submission | P2 #9 | Not needed until multi-proposal UX |
| Async processing / polling | P2 #10 | Adds WS/polling complexity |
| `StructuredSubmission` aggregate table | P2 #11 | Proper normalized multi-node storage; JSONB on Review sufficient for MVP |
| `requires_context_from` on NodeExpectation | P2 #12 | Generalized dependency engine; hardcoded NWO rules sufficient for MVP |
| Structured detail endpoint | P2 #13 | Per-node grouped response; flat cards sufficient for MVP |

## Open Questions

1. **Cross-endpoint idempotency collision risk:** Should structured endpoint use a separate unique constraint namespace, or is shared `(external_user_id, idempotency_key)` acceptable? **Default: shared, document that clients use distinct keys.**
2. **Review list display title:** Should structured reviews show "Structured review" or "Structured review (N nodes)"? Node count requires parsing `structured_payload` JSONB. **Default: static "Structured review" for MVP, avoid JSONB parsing in list query.**

## Changelog

- v0.1 (2026-02-22): Initial PRD generated from brainstorm v1.2.
- v0.2 (2026-02-22): Applied self-audit (Part B). Added F10–F12, flagged INNER JOIN landmine.
- v0.3 (2026-02-22): Per Codex adversarial review — tightened MVP scope. Removed `StructuredSubmission` table (→ JSONB on Review). Deferred `requires_context_from` DB persistence (→ hardcoded NWO rules). Extracted LLM helpers to shared module (F2 fix). Removed `node_logical_id` from ReviewCard (derive at query time). Defined transaction model (non-atomic, partial persistence). Specified idempotency transport (`Idempotency-Key` header). Added backward-compatible response strategy (reuse existing shapes). Moved 4 items to parking lot (P2 #10–#13). Schema reduced from 9 changes + 1 new table to 5 column changes + 0 new tables.
