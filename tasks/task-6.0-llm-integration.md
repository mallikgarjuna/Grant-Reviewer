# Task 6.0: LLM Integration MVP

**Status**: [ ] Not Started
**PRD**: [prd-6.0-llm-integration.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/tasks/prd-6.0-llm-integration.md)

---

## 6.1 Schema & Model Updates
- [ ] 6.1.1 Add `prompt_sent: str | None` to `Review` model
- [ ] 6.1.2 Add `raw_llm_response: str | None` to `Review` model
- [ ] 6.1.3 Add `llm_model: str | None` to `Review` model
- [ ] 6.1.4 Create `app/schemas/llm_response.py` with `ExpectationFeedback` and `LLMReviewResponse`

## 6.2 Configuration & Environment
- [ ] 6.2.1 Create `backend/.env.example` with LLM config variables
- [ ] 6.2.2 Create `app/config.py` for loading env vars (provider, model, max_tokens)

## 6.3 LLM Client Abstraction
- [ ] 6.3.1 Create `app/services/llm_client.py` with `LLMClient` base class
- [ ] 6.3.2 Implement `OpenAIClient` with structured output call
- [ ] 6.3.3 Implement `AzureOpenAIClient` as fallback
- [ ] 6.3.4 Add factory function to select client based on config

## 6.4 Prompt Builder
- [ ] 6.4.1 Create `app/services/prompt_builder.py`
- [ ] 6.4.2 Implement `build_review_prompt()` with full NodeExpectation context
- [ ] 6.4.3 Include `expectation_strength` and `evaluation_intent` in prompt

## 6.5 Reviewer Service Update
- [ ] 6.5.1 Replace `_generate_mock_feedback()` with real LLM call
- [ ] 6.5.2 Implement response parsing with `LLMReviewResponse` schema
- [ ] 6.5.3 Implement cardinality validation (exact match)
- [ ] 6.5.4 Implement `node_expectation_id` existence validation
- [ ] 6.5.5 Implement atomic persistence (all-or-nothing)
- [ ] 6.5.6 Store `prompt_sent`, `raw_llm_response`, `llm_model` on Review

## 6.6 Verification
- [ ] 6.6.1 Test: Valid LLM response → ReviewCards created
- [ ] 6.6.2 Test: Invalid JSON → Review.status = FAILED, no cards
- [ ] 6.6.3 Test: Wrong cardinality → Review.status = FAILED
- [ ] 6.6.4 Test: Unknown expectation_id → Review.status = FAILED
- [ ] 6.6.5 End-to-end: Submit snippet via script, verify feedback

---

## Working Notes

**Dependencies:**
- OpenAI Python SDK (`openai` package)
- Valid API key in `.env`

**Risk Areas:**
- LLM response format consistency
- Timeout handling (30s default)
