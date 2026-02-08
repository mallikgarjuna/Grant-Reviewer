# Task 6.0: LLM Integration MVP

**Status**: [ ] Not Started
**PRD**: [prd-6.0-llm-integration.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/tasks/prd-6.0-llm-integration.md)

---

## MVP Scope Guardrails

- **Single snippet per request** (batch review out of scope)
- **OpenAI only** (Azure deferred to future task)
- **No prompt truncation** (if too long → FAIL)
- **Review status**: PENDING → COMPLETED or FAILED (no partial states)

---

## 6.1 Schema & Model Updates
- [ ] 6.1.1 Add `prompt_sent: str | None` to `Review` model
- [ ] 6.1.2 Add `raw_llm_response: str | None` to `Review` model
- [ ] 6.1.3 Add `llm_model: str | None` to `Review` model
- [ ] 6.1.4 Create `app/schemas/llm_response.py` with `ExpectationFeedback` and `LLMReviewResponse`

## 6.2 Configuration
- [ ] 6.2.1 Create `backend/.env.example` with `OPENAI_API_KEY`, `LLM_MODEL`
- [ ] 6.2.2 Load config via `os.getenv()` directly in client (no config.py for MVP)

## 6.3 LLM Client (OpenAI Only)
- [ ] 6.3.1 Create `app/services/llm_client.py` with `OpenAIClient` class
- [ ] 6.3.2 Implement `generate(prompt: str) -> str` returning raw text response
- [ ] 6.3.3 Handle timeout (30s) and API errors → raise exception

## 6.4 Prompt Builder
- [ ] 6.4.1 Create `app/services/prompt_builder.py`
- [ ] 6.4.2 Implement `build_review_prompt()` with:
  - Node title, guidance_text
  - Snippet text
  - Each expectation: id, element_name, description, strength, intent, guidance_note

## 6.5 Reviewer Service Update
- [ ] 6.5.1 Replace `_generate_mock_feedback()` with real LLM call
- [ ] 6.5.2 Parse raw response via `LLMReviewResponse` Pydantic model
- [ ] 6.5.3 Validate cardinality: len(feedbacks) == len(expectations)
- [ ] 6.5.4 Validate each `node_expectation_id` exists and belongs to the node
- [ ] 6.5.5 Atomic persistence: all ReviewCards + Review.status=COMPLETED in one commit
- [ ] 6.5.6 On any error: Review.status=FAILED, no ReviewCards, store raw_llm_response
- [ ] 6.5.7 Store `prompt_sent`, `raw_llm_response`, `llm_model` on Review

## 6.6 Verification
- [ ] 6.6.1 Test: Valid response → ReviewCards created, status=COMPLETED
- [ ] 6.6.2 Test: Invalid JSON → status=FAILED, no cards
- [ ] 6.6.3 Test: Wrong cardinality → status=FAILED
- [ ] 6.6.4 Test: Unknown expectation_id → status=FAILED
- [ ] 6.6.5 End-to-end: `run_review.py` with real LLM call

---

## Working Notes

**Dependencies:**
- `openai` Python package (add via `uv add openai`)
- Valid `OPENAI_API_KEY` in `.env`

**Deferred:**
- Azure OpenAI support
- Prompt versioning
- Batch snippet review
- Token limit / truncation logic
