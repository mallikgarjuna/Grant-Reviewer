# WF-0029 — NWO Veni 2025 Preproposal Structured AI Review PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

## 1. In Scope

- New `POST /api/structured-review` endpoint accepting multi-node payload (`call_id` + `nodes[]` with `node_logical_id` + `text`), returning per-node AI feedback cards grouped by node.
- New `StructuredReviewerService` orchestrating: multi-node snippet creation → per-node LLM review with cross-node context → deterministic `NOT_ASSESSABLE` card generation → single `Review` record persistence.
- New `StructuredSubmission` aggregate table linking multiple `ProposalSnippet` rows (one per submitted node) to a single `Review`.
- Schema additions: `review_type` on `Review`, `node_logical_id` + `assessment_status` + `not_assessable_reason` on `ReviewCard`.
- New `AssessmentStatus` enum (`ASSESSED` / `NOT_ASSESSABLE`).
- `requires_context_from` field on `NodeExpectation` (ingested from YAML) to drive machine-readable cross-node dependency resolution.
- Cross-node context injection in prompt builder: when an expectation's `requires_context_from` lists other nodes, their submitted text is included as context in the LLM prompt.
- Alembic migration for all schema changes.
- Integration with existing review history listing (`GET /reviews`).

## 2. Out of Scope

- LLM-generated overall summary across nodes (P2 #6).
- Mega-prompt optimization — single LLM call for all nodes (P2 #5).
- Prompt quality tuning for V2 expectations structure (P2 #7).
- Parallel per-node LLM calls (P2 #8).
- Batch submission of multiple proposals (P2 #9).
- Async processing / polling — synchronous only.
- Frontend changes — no UI form, no BFF proxy update (WF-6).
- Full prompt redesign — only minimal cross-node context addition.

## 3. User / System Flow

### Happy Path

1. Frontend POSTs `{ call_id, nodes: [{ node_logical_id: "academic_profile", text: "..." }, { node_logical_id: "key_outputs", text: "..." }, { node_logical_id: "research_idea", text: "..." }] }` to `/api/structured-review`.
2. Backend resolves `call_id` → `FundingCall`, validates all `node_logical_id`s exist for that call.
3. Backend creates a `StructuredSubmission` aggregate + one `ProposalSnippet` per submitted node.
4. For each submitted node (sequentially):
   a. Fetch `NodeExpectation`s for that node.
   b. Partition expectations into **assessable** (node text present + any `requires_context_from` nodes also present) and **not-assessable** (missing cross-node context).
   c. For assessable expectations: build prompt with node text + cross-node context texts → call LLM → parse response → create `ReviewCard`s with `assessment_status=ASSESSED`.
   d. For not-assessable expectations: create deterministic `ReviewCard`s with `assessment_status=NOT_ASSESSABLE` + reason text.
5. Create single `Review` record (`review_type="structured"`, `status=COMPLETED`) linking to `StructuredSubmission`. Attach all `ReviewCard`s.
6. Return HTTP 200 with `{ review_id, status, nodes: [{ node_logical_id, cards: [...] }] }`.

### Failure Path 1 — Unknown Node ID

1. Frontend submits a `node_logical_id` not in the call's `ProposalNode` set.
2. Backend returns HTTP 422 with field-level error: `"Unknown node_logical_id: 'invalid_node'"`.

### Failure Path 2 — LLM Timeout (Partial)

1. LLM call for one node times out (30s per-call timeout).
2. `Review` is created with `status=FAILED`. Cards from successful prior nodes are persisted. Error message indicates which node failed.
3. Frontend receives HTTP 200 with `status=FAILED` and partial results.

### Failure Path 3 — Empty Payload

1. Frontend submits `nodes: []` (empty list).
2. Backend returns HTTP 422: `"At least one node is required"`.

## 4. Functional Requirements

- **F1 (Endpoint):** `POST /api/structured-review` accepts `StructuredReviewRequest`, returns `StructuredReviewResponse`. Requires `X-GR-User-Id` header (existing auth pattern).
- **F2 (Service):** New `StructuredReviewerService` orchestrates the full flow. Does NOT call `ReviewerService.generate_review()`. Reuses `build_review_prompt()`, `_parse_llm_response()`, `_generate_with_timeout()` as imported helpers.
- **F3 (Cross-node context):** When building a prompt for a node, if any of its expectations have `requires_context_from: ["academic_profile"]`, the text from the `academic_profile` node (if submitted) is appended to the prompt as additional context.
- **F4 (NOT_ASSESSABLE):** If an expectation has `requires_context_from` referencing a node that was NOT submitted (or has empty text), that expectation's `ReviewCard` is created deterministically with `assessment_status=NOT_ASSESSABLE` and `not_assessable_reason` explaining the missing context. The LLM is NOT asked to evaluate it.
- **F5 (Cardinality):** LLM response validation enforces 1:1 cardinality ONLY for assessable expectations sent to the LLM (not for all expectations on the node).
- **F6 (Persistence):** One `Review` per structured submission. `review_type="structured"`. All `ReviewCard`s have `node_logical_id` set for grouping.
- **F7 (Quota):** Structured review counts as 1 review against daily quota (not N per node).
- **F8 (Idempotency):** Client-provided `idempotency_key` works the same as single-node reviews. One key = one structured review.
- **F9 (History integration):** Structured reviews appear in `GET /reviews` list. `ReviewListItem` shows `review_type` and the first node title (or "Structured review (3 nodes)").

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

**Validation:**
- `call_id`: required UUID, must exist in DB.
- `nodes`: non-empty list. Each entry: `node_logical_id` (string, must match a `ProposalNode.logical_id` for that call), `text` (string, may be empty — empty text means the node is "submitted but not filled in", triggering NOT_ASSESSABLE for that node's alignment-dependent expectations).
- Duplicate `node_logical_id` in same request → 422.

### Response (`HTTP 200`)

```json
{
  "review_id": "uuid",
  "status": "COMPLETED",
  "review_type": "structured",
  "nodes": [
    {
      "node_logical_id": "academic_profile",
      "cards": [
        {
          "id": "uuid",
          "node_expectation_id": "uuid",
          "criterion": "Peer-exceeding researcher quality",
          "criterion_description": "...",
          "rating": "NOTE",
          "feedback_text": "...",
          "assessment_status": "ASSESSED",
          "not_assessable_reason": null
        }
      ]
    },
    {
      "node_logical_id": "research_idea",
      "cards": [
        {
          "id": "uuid",
          "node_expectation_id": "uuid",
          "criterion": "CV ↔ research idea alignment",
          "criterion_description": "...",
          "rating": "NOTE",
          "feedback_text": "Context from academic_profile was used to evaluate alignment.",
          "assessment_status": "ASSESSED",
          "not_assessable_reason": null
        }
      ]
    }
  ]
}
```

### State Transitions

- `Review.status`: `PENDING` → `COMPLETED` (all nodes succeed) or `PENDING` → `FAILED` (any LLM call fails).
- `ReviewCard.assessment_status`: Set at creation time. `ASSESSED` (LLM-generated) or `NOT_ASSESSABLE` (deterministic).

### New Enums

- `AssessmentStatus`: `ASSESSED`, `NOT_ASSESSABLE`
- `ReviewType` (or string field): `"single"`, `"structured"`

### Schema Changes (Alembic migration)

| Table | Change | Type |
|---|---|---|
| `reviews` | Add `review_type: str` (default `"single"`) | Column |
| `reviews` | Make `proposal_snippet_id` nullable | Column alter |
| `reviews` | Add `structured_submission_id: UUID` (nullable FK) | Column |
| `review_cards` | Add `node_logical_id: str` (nullable) | Column |
| `review_cards` | Add `assessment_status: AssessmentStatus` (default `ASSESSED`) | Column |
| `review_cards` | Add `not_assessable_reason: str` (nullable) | Column |
| `node_expectations` | Add `requires_context_from: JSON` (nullable, default `[]`) | Column |
| `structured_submissions` | **New table**: `id`, `user_id`, `call_id`, `created_at` | Table |
| `proposal_snippets` | Add `structured_submission_id: UUID` (nullable FK) | Column |

## 6. Components / Modules

| Component | Responsibility | Suggested Path |
|---|---|---|
| **Schemas** | Request/response Pydantic models for structured review | `app/schemas/structured_review.py` |
| **Service** | Orchestration: cross-node context, LLM calls, NOT_ASSESSABLE, persistence | `app/services/structured_reviewer_service.py` |
| **Repository** | DB operations for StructuredSubmission, multi-snippet creation | `app/repositories/structured_review_repository.py` |
| **Domain models** | `StructuredSubmission` table, updated `Review`/`ReviewCard`/`NodeExpectation` | `app/models/domain.py` |
| **Migration** | Alembic migration for all schema changes | `migrations/versions/xxx_add_structured_review.py` |
| **Router** | FastAPI route `POST /api/structured-review` | `main.py` (existing pattern) |
| **Prompt builder** | Extended to accept cross-node context texts | `app/services/prompt_builder.py` |
| **YAML + Ingestion** | `requires_context_from` field on `node_expectations` entries | `data/calls/nwo/*.yaml` + `scripts/ingest_call.py` |

## 7. Edge Cases

- **Partial submission (2 of 3 nodes):** Valid. Missing node → NOT_ASSESSABLE for alignment-dependent expectations on present nodes. Present nodes still get full LLM review.
- **Single-node structured submission:** Valid. Returns one node group. `review_type` is `"structured"`.
- **Empty text for a submitted node:** Node is "present but empty." Node's own expectations that don't require cross-node context → LLM still tries (may produce low-quality feedback). Expectations requiring context FROM this empty node (on other nodes) → NOT_ASSESSABLE.
- **All LLM calls fail:** `Review` persisted with `status=FAILED`. Zero cards. Review appears in history as failed.
- **Node with zero expectations:** Logged warning. No cards generated for that node. Node still appears in response with empty `cards[]`.
- **Idempotency key collision:** Same behavior as existing single-node: return the existing review without re-processing.
- **Review history listing:** Structured reviews show `review_type="structured"` and `node_title="Structured review (N nodes)"` in `ReviewListItem`.

## 8. Telemetry (Minimal)

- Log total wall-clock time for structured review (all nodes combined).
- Log per-node LLM call time.
- Log count of NOT_ASSESSABLE cards per review.
- Log warning if total time exceeds 60s.

## Deferred / Not in MVP

- LLM-generated overall summary (P2 #6).
- Mega-prompt optimization (P2 #5).
- Prompt quality tuning (P2 #7).
- Parallel LLM calls (P2 #8).
- Batch submission (P2 #9).
- Async processing / polling.
- Frontend structured form (WF-6).

## Open Questions

- None. All structural decisions locked in brainstorm v1.2 (§9.1–§9.4).

## Changelog

- v0.1 (2026-02-22): Initial PRD generated from brainstorm v1.2.
