# PRD 6.0: LLM Integration MVP

**Status**: Draft (v1.1 - Revised)
**Date**: 2026-02-08
**Decisions**: AD 6.1–6.7

---

## Goal

Replace mock feedback generation with a real LLM call to provide meaningful, rubric-grounded feedback on grant proposal snippets.

## Problem Statement

The `ReviewerService._generate_mock_feedback()` returns hardcoded placeholder text. Researchers need actual AI-generated feedback that evaluates their writing against funding call criteria.

---

## User Stories

### US-6.1: Receive AI Feedback
**As a** researcher,
**I want** to submit my proposal text and receive AI-generated feedback,
**So that** I can improve my proposal before submission.

**Acceptance Criteria:**
- Submit exactly one snippet per request.
- Receive structured feedback for exactly N expectations, where N is the number of expectations linked to the ProposalNode.
- Feedback must reflect the `expectation_strength` and `evaluation_intent`.
- Response time < 30 seconds.

### US-6.2: Debug Prompt Issues
**As a** developer,
**I want** to see the exact prompt sent, raw LLM response, and model used,
**So that** I can iterate on prompt design and track performance.

**Acceptance Criteria:**
- `Review.prompt_sent` stores the full assembled prompt.
- `Review.raw_llm_response` stores the raw JSON/text from LLM.
- `Review.llm_model` stores the string identifier of the model used.

---

## Technical Specification

### LLM Response Schema (Pydantic)

```python
class ExpectationFeedback(BaseModel):
    node_expectation_id: str  # Valid UUID string
    feedback: str             # Non-empty feedback text

class LLMReviewResponse(BaseModel):
    feedbacks: list[ExpectationFeedback]  # Length must precisely match request cardinality
```

### Prompt Structure (Static Template)

```
You are a grant proposal reviewer evaluating text against specific criteria.

## Proposal Section
{node_title}
{guidance_text}

## Submitted Text
{snippet_text}

## Evaluation Criteria
{for each expectation:}
- ID: {node_expectation_id}
- Element: {element_name} ({element_description})
- Intent: {evaluation_intent} (e.g., QUALITY, RISK)
- Strength: {expectation_strength} (e.g., MANDATORY, VALUE_ADD)
- Reviewer guidance: {guidance_note}

## Instructions
1. For EACH criterion listed above, provide constructive, specific feedback based on the Submitted Text.
2. Consider the 'Strength' and 'Intent' of each criterion in your assessment.
3. You MUST return exactly one feedback item for every ID provided. Do not skip any IDs. Do not add extra IDs.
4. Return ONLY a JSON object: {"feedbacks": [{"node_expectation_id": "...", "feedback": "..."}]}
```

### Database Changes (`Review` Table)

| Field | Type | Description |
|-------|-------|-------------|
| `prompt_sent` | `Text` | Full prompt sent to LLM |
| `raw_llm_response` | `Text` | Raw response from LLM (before parsing) |
| `llm_model` | `String` | Model identifier (e.g., "gpt-4o-mini") |

### Workflow & Persistence (Atomic)

1. Service builds prompt using `NodeExpectation` fields (strength, intent).
2. Service calls `LLMClient` (target OpenAI, Azure fallback).
3. If call fails or timeout → `Review.status = FAILED`, **no ReviewCards created**.
4. If call succeeds, service parses `raw_llm_response` via `LLMReviewResponse` schema.
5. Service validates:
    - JSON is valid.
    - Cardinality: Number of feedbacks received == number of expectations sent.
    - All `node_expectation_id`s in response exist in the original request.
6. If validation fails → `Review.status = FAILED`, **no ReviewCards created**.
7. If validation succeeds → Create `ReviewCard` records and commit as one transaction with `Review.status = COMPLETED`.

### LLM Client Configuration

| Setting | Value |
|---------|-------|
| Provider | OpenAI (default), Azure OpenAI (configurable) |
| Model | `gpt-4o-mini` (default, configurable via env) |
| Max Tokens | Configurable via env (e.g., 2000) |
| Response format | Raw text (parsed by service) |

---

## Out of Scope (MVP)

- **AI-generated ratings**: Ratings remain in schema placeholder but are NOT populated by AI.
- **Advanced prompt versioning**: Rely on `prompt_sent` saved in DB for historical trace.
- **Retries/Backoff**: Simple fail-on-error behavior.
- **Async Workers**: REST request blocks until LLM responds.

---

## Clarifications & Answers

**Q1: Are ratings deferred or removed?**
**A:** Deferred. Keep `ReviewCard.rating` in schema (nullable) but populated with mock or default (e.g., `NOTE`) during MVP.

**Q2: How is node_expectation_id validated?**
**A:** Must exist in DB and belong to the correct `ProposalNode` for the current snippet. Any mismatch triggers `FAILED` status.

**Q3: Is review limited to one ProposalSnippet per request?**
**A:** Yes. MVP is strictly 1 request = 1 snippet = 1 review.

**Q4: Is prompt versioning in scope?**
**A:** No. `prompt_sent` in the `Review` record is our source of truth for "what ran".

---

## Files to Modify/Create

| File | Change |
|------|--------|
| `app/models/domain.py` | Add `prompt_sent`, `raw_llm_response`, `llm_model` |
| `app/schemas/llm_response.py` | [NEW] Pydantic schemas (ExpectationFeedback, LLMReviewResponse) |
| `app/services/llm_client.py` | [NEW] Abstraction for OpenAI/Azure |
| `app/services/prompt_builder.py` | [NEW] Multi-variable prompt assembly |
| `app/services/reviewer_service.py` | Implement atomic LLM logic + validation |
| `backend/.env.example` | Add keys, model, max_tokens |
