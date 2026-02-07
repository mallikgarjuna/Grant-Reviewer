# Architectural Decisions

## Date: 2026-02-06

### AD 0.1: Recursive Proposal Node Structure
- **Decision**: All hierarchical levels of a grant proposal (Part B, Section 1, Subsection 1.1) will be stored in a single `ProposalNode` table with a reflexive `parent_node_id` foreign key.
- **Rationale**: User confirmed preference for generic hierarchy. Simplifies querying for all children of a section or identifying the full path of a snippet.
- **Status**: Approved.

### AD 0.2: Anonymous User with TTL
- **Decision**: MVP uses `User` records with `is_anonymous = true` and `email = null`. Each record represents one logical session. Records are cascade-deleted after TTL (24-72h).
- **Rationale**: Allows tracking snippets/reviews per session without authentication. Explicit lifecycle for data cleanup.
- **Status**: Approved.

### AD 0.3: Call-Locked Evaluation Criteria
- **Decision**: `EvaluationCriterion` and `EvaluationElement` records are unique to a specific `FundingCall`.
- **Rationale**: Avoids complexity of sharing rubrics across calls where guidance might subtly differ.
- **Status**: Approved.

---

## Date: 2026-02-06 (Stage 1 Clarifications)

### AD 1.1: ReviewCard Links to NodeExpectation
- **Decision**: `ReviewCard.node_expectation_id` references `NodeExpectation`, not `EvaluationElement` directly.
- **Rationale**: Provides full traceability to the specific node+element+strength+intent context. The `NodeExpectation` row contains the `evaluation_intent` and `expectation_strength` that informed the review.
- **Status**: Approved.

### AD 1.2: Dual Guidance Fields
- **Decision**: Two distinct guidance fields exist:
  - `ProposalNode.guidance_text`: *"What the applicant is expected to write here."* (Proposal Context in prompt)
  - `NodeExpectation.guidance_note`: *"What the reviewer should actively look for."* (Evaluation Expectations in prompt)
- **Rationale**: Separates applicant-facing guidance from reviewer-internal criteria. Both feed the AI prompt in different sections.
- **Status**: Approved.

### AD 1.3: PromptTemplate Immutability
- **Decision**: Prompt templates are immutable. Updates create a new row with incremented `version` and `is_active = true`. Old templates are set to `is_active = false`.
- **Rationale**: Ensures every `Review` can be traced back to the exact prompt version used. Critical for auditability.
- **Status**: Approved.

### AD 1.4: Mandatory TTL on ProposalSnippet
- **Decision**: `ProposalSnippet.expires_at` is mandatory. Default TTL is 24 hours (configurable). A background job handles cleanup with cascade delete.
- **Rationale**: Ensures ephemeral data for anonymous MVP. Reduces storage and avoids stale data.
- **Status**: Approved.

---

## Date: 2026-02-06 (Stage 2 Validation)

### AD 2.1: Reject Nodes with Zero Expectations
- **Decision**: If a `ProposalNode` has zero `NodeExpectation` records, the system must reject the review request with error: *"No evaluation criteria defined for this section."*
- **Rationale**: A review without expectations is meaningless. Forces administrators to define criteria before enabling sections for review.
- **Status**: Approved.

### AD 3.1: Tech Stack
- **Decision**: Backend uses **SQLModel** (ORM), **UV** (package manager), **FastAPI** (API framework, for Stage 4+).
- **Rationale**: User preference. SQLModel integrates Pydantic + SQLAlchemy. FastAPI is performant and type-safe.
- **Status**: Approved.

---

## Date: 2026-02-07 (Stage 4 Interface Readiness)

### AD 4.1: Structured Rating on ReviewCards
- **Decision**: Added `ReviewCard.rating` using a `ReviewRating` enum (`CRITICAL`, `WARNING`, `SUCCESS`, `NOTE`).
- **Rationale**: Supports "Traffic Light" indicators in the UI without requiring clients to parse human-readable text. Provides a structured way to sort/filter findings by severity.
- **Status**: Implemented.

### AD 4.2: Async Status and Summaries for Reviews
- **Decision**: Added `Review.status` (`PENDING`, `COMPLETED`, `FAILED`), `Review.overall_summary`, and `Review.overall_rating`.
- **Rationale**: Prepare for asynchronous AI generation logic. The UI can poll for status and display an "Executive Summary" at the top of the review page before the detailed cards.
- **Status**: Implemented.

### AD 4.3: Aggregate Rating Calculation
- **Decision**: The `Review.overall_rating` is calculated as the "maximum severity" of its child `ReviewCard` ratings.
- **Ranking**: `CRITICAL (4) > WARNING (3) > SUCCESS (2) > NOTE (1)`.
- **Rationale**: Ensures the overall review status reflects the most urgent finding found by the AI.
- **Status**: Implemented.

---

## Date: 2026-02-07 (Phase 1: Admin Ingestion)

### AD 5.1: Call Definition as Code (YAML)
- **Decision**: Funding Calls, Rubrics, and Proposal Hierarchies will be defined in a version-controlled YAML file and ingested via a CLI script.
- **Rationale**: Matches the complex recursive structure of the domain. Easier to version and copy-paste than a UI.
- **Status**: Approved.

### AD 5.2: No Admin UI for MVP
- **Decision**: We will NOT build a web-based Admin Dashboard for creating calls/rubrics in the MVP.
- **Rationale**: High development cost for low frequency of use. YAML + CLI is sufficient for technical admins.
- **Status**: Approved.

---

## Date: 2026-02-07 (LLM Integration MVP Scope)

### AD 6.1: Single LLM Call per Review
- **Decision**: One LLM call generates feedback for ALL expectations in a review (not one call per expectation).
- **Rationale**: Simpler, cheaper. Full context in one prompt helps coherence.
- **Status**: Approved.

### AD 6.2: Structured JSON Output
- **Decision**: LLM returns structured JSON with `expectation_id` + `feedback` pairs. Validated via Pydantic schema.
- **Rationale**: Parseable, validatable, traceable to specific NodeExpectations.
- **Status**: Approved.

### AD 6.3: Feedback Only (No Rating from LLM)
- **Decision**: MVP LLM returns text feedback only. Ratings will be a Phase-2 concern.
- **Rationale**: Simplifies prompt design and output parsing for MVP. Rating logic can be added later.
- **Status**: Approved.

### AD 6.4: Static Prompt Template
- **Decision**: Use simple f-string template with variable substitution. No Jinja2, no versioning for MVP.
- **Rationale**: KISS principle. Fast iteration on prompts.
- **Status**: Approved.

### AD 6.5: Store Prompt and Raw Response
- **Decision**: Add `prompt_sent` and `raw_llm_response` fields to `Review` table for debugging.
- **Rationale**: Critical for prompt iteration and debugging malformed outputs.
- **Status**: Approved.

### AD 6.6: Failure Policy (MVP)
- **Decision**: If LLM call fails or returns invalid JSON → `Review.status = FAILED`. No partial ReviewCards. User retries manually.
- **Rationale**: Simple, safe. Production-grade resilience is Phase-2.
- **Status**: Approved.

### AD 6.7: Out of Scope for MVP
- Retries, backoff, rate-limit handling
- Partial results handling  
- Cost optimization
- Async workers / horizontal scaling
