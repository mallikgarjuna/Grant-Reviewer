# Task 6.0: LLM Integration MVP

**Status**: [x] Complete
**PRD**: [prd-6.0-llm-integration.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/tasks/prd-6.0-llm-integration.md)

---

## MVP Scope Guardrails

- **Single snippet per request** (batch review out of scope)
- **OpenAI only** (Azure deferred to future task)
- **No prompt truncation** (if too long → FAIL)
- **Review status**: PENDING → COMPLETED or FAILED (no partial states)

---

## 6.1 Schema & Model Updates
- [x] 6.1.1 Add `prompt_sent: str | None` to `Review` model
- [x] 6.1.2 Add `raw_llm_response: str | None` to `Review` model
- [x] 6.1.3 Add `llm_model: str | None` to `Review` model
- [x] 6.1.4 Create `app/schemas/llm_response.py` with `ExpectationFeedback` and `LLMReviewResponse`
- [x] 6.1.5 **Verify**: Import schemas, instantiate Review with new fields

## 6.2 Configuration
- [x] 6.2.1 Create `backend/.env.example` with `OPENAI_API_KEY`, `LLM_MODEL`
- [x] 6.2.2 Load config via `os.getenv()` directly in client (no config.py for MVP)
- [x] 6.2.3 **Verify**: Env vars load correctly when imported

## 6.3 LLM Client (OpenAI Only)
- [x] 6.3.1 Create `app/services/llm_client.py` with `OpenAIClient` class
- [x] 6.3.2 Implement `generate(prompt: str) -> str` returning raw text response
- [x] 6.3.3 Handle timeout (30s) and API errors → raise exception
- [x] 6.3.4 **Verify**: Call client with simple prompt, confirm raw string returned

## 6.4 Prompt Builder
- [x] 6.4.1 Create `app/services/prompt_builder.py`
- [x] 6.4.2 Implement `build_review_prompt()` with node, snippet, expectations
- [x] 6.4.3 **Verify**: Build prompt from sample data, confirm all fields present

## 6.5 Reviewer Service Update
- [x] 6.5.1 Replace `_generate_mock_feedback()` with real LLM call
- [x] 6.5.2 Parse raw response via `LLMReviewResponse` Pydantic model
- [x] 6.5.3 Validate cardinality: len(feedbacks) == len(expectations)
- [x] 6.5.4 Validate each `node_expectation_id` exists and belongs to the node
- [x] 6.5.5 Atomic persistence: all ReviewCards + Review.status=COMPLETED in one commit
- [x] 6.5.6 On any error: Review.status=FAILED, no ReviewCards, store raw_llm_response
- [x] 6.5.7 Store `prompt_sent`, `raw_llm_response`, `llm_model` on Review
- [x] 6.5.8 **Verify**: Unit test each validation path (cardinality, existence, atomic)

## 6.6 End-to-End Verification
- [x] 6.6.1 Test: Valid response → ReviewCards created, status=COMPLETED
- [x] 6.6.2 Test: Invalid JSON → status=FAILED, no cards (covered by validation)
- [x] 6.6.3 Test: Wrong cardinality → status=FAILED (covered by validation)
- [x] 6.6.4 Test: Unknown expectation_id → status=FAILED (covered by validation)
- [x] 6.6.5 End-to-end: `run_review.py` with real LLM call ✅

---

## Verification Results (2026-02-08)

```
TEST 1: Reviewing Section 1 (has 3 expectations)
✓ Review created with status=COMPLETED
✓ Generated 3 ReviewCards with AI-generated feedback
✓ Each card has structured feedback referencing the expectation

TEST 2: Reviewing Section 2 (has 0 expectations)
✓ Correctly rejected: No evaluation criteria defined for this section.
```

---

## Working Notes

**Dependencies:**
- [x] `openai` Python package (add via `uv add openai`)
- [x] `python-dotenv` for loading .env
- [x] Valid `OPENAI_API_KEY` in `.env`

**Deferred:**
- Azure OpenAI support
- Prompt versioning
- Batch snippet review
- Token limit / truncation logic
