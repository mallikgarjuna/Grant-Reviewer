# PRD 6.0: LLM Integration MVP

**Status**: Draft
**Date**: 2026-02-07
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
- Submit snippet → receive structured feedback for each expectation
- Feedback references the specific evaluation element
- Response time < 30 seconds

### US-6.2: Debug Prompt Issues
**As a** developer,  
**I want** to see the exact prompt sent and raw LLM response,  
**So that** I can iterate on prompt design.

**Acceptance Criteria:**
- `Review.prompt_sent` stores the assembled prompt
- `Review.raw_llm_response` stores the raw JSON from LLM
- Both fields are queryable via database

---

## Technical Specification

### LLM Response Schema

```python
class ExpectationFeedback(BaseModel):
    expectation_id: str  # UUID as string
    feedback: str        # AI-generated text

class LLMReviewResponse(BaseModel):
    feedbacks: list[ExpectationFeedback]
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
- [{expectation_id}] {element_name}: {element_description}
  Reviewer guidance: {guidance_note}

## Instructions
For EACH criterion above, provide constructive feedback.
Return JSON: {"feedbacks": [{"expectation_id": "...", "feedback": "..."}]}
```

### Database Changes

| Table | Field | Type | Description |
|-------|-------|------|-------------|
| `Review` | `prompt_sent` | `Text` | Full prompt sent to LLM |
| `Review` | `raw_llm_response` | `Text` | Raw JSON string from LLM |

### LLM Client Configuration

| Setting | Value |
|---------|-------|
| Provider | OpenAI (default), Azure OpenAI (configurable) |
| Model | `gpt-4o-mini` (configurable via env) |
| Response format | `json_object` (structured output) |
| Timeout | 30 seconds |

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (for Azure)
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Model selection
LLM_PROVIDER=openai  # or "azure"
LLM_MODEL=gpt-4o-mini
```

---

## Failure Policy

| Scenario | Behavior |
|----------|----------|
| LLM timeout | `Review.status = FAILED`, no ReviewCards |
| Invalid JSON | `Review.status = FAILED`, store raw response for debugging |
| Missing expectation_id | `Review.status = FAILED` |
| User action | Retry manually |

---

## Out of Scope (MVP)

- Rating generation from LLM
- Retries, backoff, rate-limit handling
- Partial results handling
- Cost tracking
- Async workers

---

## Files to Modify/Create

| File | Change |
|------|--------|
| `app/models/domain.py` | Add `prompt_sent`, `raw_llm_response` to `Review` |
| `app/schemas/llm_response.py` | [NEW] Pydantic schemas for LLM output |
| `app/services/llm_client.py` | [NEW] OpenAI/Azure client abstraction |
| `app/services/prompt_builder.py` | [NEW] Static template + variable substitution |
| `app/services/reviewer_service.py` | Replace mock with real LLM call |
| `backend/.env.example` | Add LLM config variables |
