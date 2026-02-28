# Architectural Decisions

## Date: 2026-02-28 (WF-0035: Universal form dynamic UI renderer)

### AD 35.1: Frontend render model composes flat nodes ordering + metadata enrichment
- **WF ID**: WF-0035
- **Context**: Existing backend contracts split ordering/identity (`GET /calls/{call_id}/nodes?view=flat`) from UI labels/constraints (`GET /api/public/calls/{call_logical_id}/nodes/metadata`).
- **Decision**: Define frontend render model as the composition of these two inputs; nodes ordering SSOT is flat nodes endpoint, while metadata enriches labels/constraints via `logical_id`.
- **Why**: Avoids adding new backend endpoints while preventing Veni-specific hardcoding in the renderer.
- **Tradeoff**: Frontend must own deterministic merge/fallback logic and handle partial metadata responses.
- **Status**: Approved.

### AD 35.2: Flat-only support hard-blocks nested and missing-logical-id calls in MVP
- **WF ID**: WF-0035
- **Context**: WF-0035 explicitly defers recursion; structured submit payloads require `node_logical_id`.
- **Decision**: Universal form supports a call only when all nodes are flat (`parent_node_id == null`) and have non-empty `logical_id`; otherwise the call is blocked with explicit unsupported/contract-error messaging.
- **Why**: Prevents silent partial rendering and malformed structured-review submissions.
- **Tradeoff**: Some structured calls remain unusable until recursive rendering and/or data-contract fixes ship.
- **Status**: Approved.

### AD 35.3: Keep existing call-gating API pattern with deterministic client guardrails
- **WF ID**: WF-0035
- **Context**: No new backend endpoint is in scope for filtering structured calls at source.
- **Decision**: Gate eligibility client-side using `GET /api/public/calls/{code}/config` per call, with fixed guardrails (max 4 concurrent requests, 4-second timeout, partial-results UX).
- **Why**: Preserves MVP scope while avoiding all-or-nothing failure as call count grows.
- **Tradeoff**: Introduces N+1 request cost and requires robust degraded-state UX.
- **Status**: Approved.

### AD 35.4: Domain handling remains compliance-scoped with interim per-call options mapping
- **WF ID**: WF-0035
- **Context**: Veni compliance depends on domain input, but domain options are not yet delivered via canonical call-definition UI contract.
- **Decision**: Add generic domain picker surface only where configured via interim per-call mapping; pass selected domain to compliance precheck, while keeping structured-review contract unchanged.
- **Why**: Preserves correctness for domain-gated compliance without expanding backend/API scope in WF-0035.
- **Tradeoff**: Domain options are temporarily maintained outside canonical metadata until a follow-on contract WF.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0034: Unify review execution core)

### AD 34.1: Preserve separate external create contracts; share internal execution core
- **WF ID**: WF-0034
- **Context**: `POST /reviews` and `POST /api/structured-review` have different request shapes and persistence semantics but duplicate core execution concerns.
- **Decision**: Keep both external create endpoints stable and extract shared internal execution pipeline seams (policy injection/post-checks, LLM call seam, parse/validate, telemetry seam).
- **Why**: Reduces drift and duplicate fixes without forcing risky contract changes.
- **Tradeoff**: Two adapter/orchestration surfaces remain and require explicit parity tests.
- **Status**: Approved.

### AD 34.2: No-behavior-change parity is per-endpoint baseline, not cross-endpoint equivalence
- **WF ID**: WF-0034
- **Context**: “Shared core” can be misread as making both endpoints behave identically, which would break endpoint-specific semantics.
- **Decision**: Define parity against each endpoint’s existing baseline (error semantics, idempotency behavior, persistence side effects, card rules), not against each other.
- **Why**: Preserves existing client/API expectations while enabling safe internal refactor.
- **Tradeoff**: Shared core design must remain persistence-agnostic and avoid over-normalizing behavior.
- **Status**: Approved.

### AD 34.3: Incremental migration with structured-first adapter flip
- **WF ID**: WF-0034
- **Context**: Big-bang migration across both endpoints increases blast radius and rollback difficulty.
- **Decision**: Migrate incrementally: establish parity tests, introduce shared core seam, flip structured endpoint first, then single-node endpoint.
- **Why**: Structured path has higher complexity and better stress-tests shared-core boundaries first.
- **Tradeoff**: Temporary mixed architecture during migration window.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0033: Data Contract foundation for hierarchical grants)

### AD 33.1: Universal node identity is `logical_id` + DB UUID
- **WF ID**: WF-0033
- **Context**: A universal renderer needs stable, environment-agnostic identifiers, while the backend persists nodes by UUID.
- **Decision**: Expose both `logical_id` (V2) and `id` (UUID) in UI-facing node DTOs. Frontend binds drafts/state by `logical_id`; backend uses UUID for persistence and joins.
- **Why**: Avoids program-specific code and prevents environment drift (UUIDs differ across DBs; `logical_id` is stable across ingest runs).
- **Tradeoff**: Slightly larger payloads and dual-identifier handling for clients.
- **Status**: Approved.

### AD 33.2: Nodes endpoint uses `view=flat|tree` with flat as default
- **WF ID**: WF-0033
- **Context**: Existing clients depend on a flat nodes list; the new universal renderer needs a tree.
- **Decision**: Keep `GET /calls/{call_id}/nodes` as the canonical endpoint and add `view=flat|tree` (default `flat`). Tree view returns roots with nested `children`.
- **Why**: Enables incremental migration while preserving backward compatibility.
- **Tradeoff**: Endpoint has two response shapes; API typing/docs must be explicit.
- **Status**: Approved.

### AD 33.5: Tree source-of-truth uses V2 `parent_logical_id` (canonical JSON) when available
- **WF ID**: WF-0033
- **Context**: The V2 call-definition schema expresses hierarchy via `proposal_nodes[].parent_logical_id` (not nested `children` lists).
- **Decision**: Build tree structure/order from V2 canonical JSON `proposal_nodes` using `id` + `parent_logical_id` and the list order for sibling ordering; use DB adjacency (`parent_node_id`) only as a fallback when no V2 definition is present/valid.
- **Why**: Keeps the hierarchy consistent with the authored call definition while allowing deterministic fallback for legacy calls.
- **Tradeoff**: Requires careful mismatch handling between canonical JSON logical IDs and active DB nodes.
- **Status**: Approved.

### AD 33.3: Metadata DTO is a bulk public route with optional filtering and partial-success semantics
- **WF ID**: WF-0033
- **Context**: UI needs node-specific constraints/rules without fetching heavy metadata up front, and must support lazy hydration.
- **Decision**: Add `GET /api/public/calls/{call_logical_id}/nodes/metadata` sourced from `CallDefinition.canonical_json`, support repeated `node_logical_ids` filters, and return partial success with `unknown_node_logical_ids` when filters include unknown IDs.
- **Why**: Minimizes API surface area while supporting both bulk and progressive loading patterns.
- **Tradeoff**: Consumers must handle a mixed "known + unknown" result set.
- **Status**: Approved.

### AD 33.4: Missing call definition is an explicit error for metadata requests
- **WF ID**: WF-0033
- **Context**: Legacy calls may not have V2 canonical JSON; metadata DTO depends on it.
- **Decision**: If a call lacks a V2 definition, metadata endpoint returns `CALL_DEFINITION_MISSING` (409). Clients should gate behavior via `/api/public/calls/{call_logical_id}/config`.
- **Why**: Prevents silent empty responses that mask configuration problems and simplifies debugging.
- **Tradeoff**: Client must respect the gating endpoint to avoid 409s.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0032: ERC StG 2026 reviewer-policy hardening)

### AD 32.1: Reviewer policy is first-class call-definition data (`reviewer_policy`)
- **WF ID**: WF-0032
- **Context**: Reviewer guidance was captured as notes/compliance hints, but not modeled as enforceable runtime policy.
- **Decision**: Extend V2 call YAML/schema with `reviewer_policy` rules containing stage scope, node scope, enforcement mode, and source hints.
- **Why**: Each funding call has distinct reviewer-policy constraints that must be versioned with evaluation criteria/elements and consumed by runtime.
- **Tradeoff**: Slight schema complexity increase; authoring now requires structured policy fields.
- **Status**: Implemented.

### AD 32.2: Review stage must be explicit API input
- **WF ID**: WF-0032
- **Context**: Inferring Step 1 vs Step 2 from node ID can drift in mixed or future workflows.
- **Decision**: Require `review_stage` (`STEP_1`/`STEP_2`) in `/reviews` and `/api/structured-review`, and reject node/stage mismatches.
- **Why**: Prevents silent scope errors and makes policy enforcement deterministic at request time.
- **Tradeoff**: API clients must send one additional required field.
- **Status**: Implemented.

### AD 32.3: Critical ERC reviewer-policy rules are blocking
- **WF ID**: WF-0032
- **Context**: Warning-only checks allow policy-violating reviewer output to be persisted.
- **Decision**: Promote critical ERC rules (Excellence-only criterion scope, no Step-1 resource judgments) to `BLOCKING`.
- **Why**: These are hard guardrails from official reviewer guidance and should fail-fast instead of degrade silently.
- **Tradeoff**: Some reviews will fail and need regeneration/retry when outputs violate policy.
- **Status**: Implemented.

## Date: 2026-02-28 (WF-0037: NWO Vidi 2025 full proposal call definition)

### AD 37.1: Defer AES-only impact clause until domain gating exists
- **WF ID**: WF-0037
- **Context**: The Call PDF contains an AES-specific impact clause, but the app does not currently select a Vidi domain, so any AES-only element would be evaluated for all submissions.
- **Decision**: Exclude AES-only clause from canonical evaluation criteria/elements until domain selection/branching is introduced.
- **Why**: Prevents incorrect universal evaluation semantics and preserves source-grounded correctness.
- **Tradeoff**: AES-specific nuance is not evaluated until domain gating ships.
- **Status**: Approved.

## Date: 2026-02-28 (WF-0036 branch closure hygiene)

### AD 36.4: WF-0036 merged via direct main merge (no PR), then stale branch deleted
- **WF ID**: WF-0036
- **Context**: WF-0036 artifacts were already marked Done and commits were contained in `main`, but the old WF branch pointer remained on origin, causing closure ambiguity.
- **Decision**: Keep workflow state as Done (no content changes), record that merge path differed from current PR-first policy, and delete stale local/remote WF-0036 branch refs after ancestry verification.
- **Why**: Preserves audit clarity without rewriting history and prevents repeated confusion about whether WF-0036 is still open.
- **Status**: Approved.

### AD 37.2: Keep WF-0037 YAML-only; schema gaps require a follow-on WF
- **WF ID**: WF-0037
- **Context**: During planning we may discover schema needs (domain gating, separate non-evaluable guidance fields).
- **Decision**: No schema/contract changes in WF-0037; if a gap is discovered, stop and promote a dedicated follow-on WF.
- **Why**: Schema changes have high blast radius across ingestion/runtime/tests and must remain explicitly scoped and gated.
- **Tradeoff**: Some desired modeling fidelity is deferred.
- **Status**: Approved.

### AD 37.3: Deadlines store timezone verbatim from sources
- **WF ID**: WF-0037
- **Context**: Deadlines in the call sources use human labels like CET/CEST; conversion/normalization can introduce ambiguity.
- **Decision**: Store `funding_call.deadlines.*.timezone` verbatim as written in the authoritative source document; treat IANA normalization as a follow-on.
- **Why**: Avoids silent conversion errors and preserves legal defensibility.
- **Tradeoff**: Consumers may later need normalization logic.
- **Status**: Approved.

## Date: 2026-02-23 (WF-0030: Local QA/Test DB Isolation Hardening)

### AD 30.1: Dedicated test database is required for DB-backed backend tests
- **WF ID**: WF-0030
- **Context**: Running `backend/tests/test_api.py` against the same `DATABASE_URL` used by local app QA overwrote call-definition projection data, causing false UI regressions (e.g., `academic_profile` dropping to one expectation).
- **Decision**: Enforce a hard safety policy:
  - DB-backed tests must run only when `DATABASE_URL` points to a test database whose name includes `test`.
  - Add pytest guardrails in `backend/tests/conftest.py` to fail fast for unsafe DB URLs.
  - Keep DB-less tests explicitly marked (`@pytest.mark.no_db`) to bypass DB checks safely.
- **Why**: Prevents accidental mutation of the local QA dataset and removes a recurring source of workflow confusion.
- **Tradeoff**: Developers must set `DATABASE_URL` explicitly for backend test runs, which adds one setup step but avoids costly debugging.
- **Status**: Implemented.

### AD 30.2: Separate Docker stacks for dev DB and test DB
- **WF ID**: WF-0030
- **Context**: A single Postgres stack encouraged accidental sharing between manual app testing and test fixtures.
- **Decision**:
  - Keep `backend/docker-compose.dev.yml` for local app development (`grant_reviewer_dev`, port `5432`).
  - Add `backend/docker-compose.test.yml` for backend tests (`grant_reviewer_test`, port `5433`).
- **Why**: Environment-level separation is simpler and more reliable than relying on developer memory.
- **Tradeoff**: Slightly more local setup overhead (one extra compose file), but much safer operationally.
- **Status**: Implemented.

### AD 30.3: Standardized reset scripts for deterministic local state
- **WF ID**: WF-0030
- **Context**: Repeated manual reset sequences were error-prone and inconsistently applied.
- **Decision**:
  - Add `backend/scripts/reset_dev_db.sh` to reset dev DB + ensure active prompt template + ingest canonical Veni definition.
  - Add `backend/scripts/reset_test_db.sh` to reset isolated test DB with safety checks.
- **Why**: One-command recovery reduces mistakes and makes state transitions explicit before QA/test runs.
- **Tradeoff**: Local data is intentionally wiped during reset workflows; this is acceptable for deterministic development.
- **Status**: Implemented.

### AD 30.4: Carry-forward rule for future funding call workflows
- **WF ID**: WF-0030
- **Context**: Additional funding calls will amplify the risk of accidental fixture contamination.
- **Decision**: Treat DB isolation + reset scripts as mandatory preflight for every new funding-call WF before Phase 3 QA.
- **Why**: This preserves reproducibility as multi-call complexity increases.
- **Status**: Approved (always-on policy).

## Date: 2026-02-21 (WF-0021: NWO Veni 2025 preproposal WF-2)

### AD 21.1: 1:1 FundingCall to CallDefinition Relationship
- **WF ID**: WF-0021
- **Context**: The canonical JSONB document needs to link to existing funding calls in the system.
- **Decision**: Introduce a `CallDefinition` table with a 1:1 foreign key to `FundingCall` containing the canonical JSONB.
- **Why**: Keeps the new document storage cleanly separated from the high-level call metadata while enforcing exactly one canonical definition per call.
- **Tradeoff**: Requires an extra join if querying both simultaneously, but read service hydrates this efficiently.
- **Status**: Approved.

### AD 21.2: Mandatory `archived_at IS NULL` Query Filters
- **WF ID**: WF-0021
- **Context**: Re-ingesting calls with missing logical IDs soft-deletes the missing entities. Existing read queries would return these deleted entities and prompt them to the AI or UI.
- **Decision**: Enforce that all application read queries for nodes, criteria, and elements explicitly filter `archived_at IS NULL`.
- **Why**: Safest way to handle dropped YAML sections without destroying historical review data that might reference them (orphan handling).
- **Tradeoff**: High risk of bugs if a query forgets the filter; requires auditing all existing read paths.
- **Status**: Approved.

### AD 21.3: Derive criterion description text for V2 projection
- **WF ID**: WF-0021
- **Context**: V2 `evaluation_criteria` schema does not include a free-text `description`, while the relational projection table requires one.
- **Decision**: Persist a deterministic derived description in projection format: `stage=<stage>; weight_percent=<weight_percent>`.
- **Why**: Preserves V2 metadata in the existing table contract without schema-expansion of `EvaluationCriterion`.
- **Tradeoff**: This is synthesized text, not original narrative guidance; richer criterion-level prose can be added in a future schema revision.
- **Status**: Implemented.
## Date: 2026-02-21 (WF-0022: Workflow System Upgrade)

### AD 22.1: Consolidate Phase 1/2/3 Runners into Universal Parametric Runner
- **WF ID**: WF-0022
- **Context**: The Phase 1, Phase 2, and Phase 3 runners share 90% boilerplate (Part A/B/C logic, trace statements, gates). This causes maintenance debt and file sprawl.
- **Decision**: Replace `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` with a single `universal-phase-runner.md` that uses conditional variables for inputs/outputs based on the phase number.
- **Why**: Reduces file sprawl and centralizes the "Runners are Routers" logic so any future structural changes to a phase gate only need to be written once.
- **Tradeoff**: Relies on the AI agent's ability to correctly parse markdown tables/variables to substitute the correct input/output paths for the given phase.
- **Status**: Approved.

## Date: 2026-02-20 (Terminology)

### AD T.1: Standardize on “Evaluation criteria/elements” in product copy
- **Context**: Different funders use different labels (e.g., “Assessment criteria” vs “Evaluation criteria”), and “rubric” is less familiar to many researchers.
- **Decision**: Use **“Evaluation criteria”** and **“Evaluation elements”** consistently across all calls in user-facing copy to reduce confusion. Keep a private/internal note of funder-specific variations for reference only.
- **Notes (variations observed)**: NWO commonly uses “Assessment criteria”; Horizon Europe commonly uses “Evaluation criteria”; some people use “Review criteria”.
- **Status**: Approved.

## Date: 2026-02-21 (WF-0020: NWO Veni 2025 preproposal WF-1)

### AD 20.1: V1 vs V2 call-definition detection by `funding_agency` discriminant
- **WF ID**: WF-0020
- **Context**: Existing V1 call YAML uses `funding_agency.short_name`, while the NWO Veni V2 YAML uses `funding_agency.id`. V2 YAML does not currently declare an explicit schema version.
- **Decision**: Detect schema version via:
  - V1 if `funding_agency.short_name` exists
  - V2 if `funding_agency.id` exists
  - If both/neither exist: fail with a clear error (avoid silent precedence).
- **Why**: Deterministic routing is required to keep existing V1 ingest stable while enabling V2 validation for NWO.
- **Tradeoff**: This is a heuristic, not a formal version field; a future WF may add an explicit `schema_version` key if needed.
- **Status**: Approved.

### AD 20.2: `--dry-run` must run without `DATABASE_URL`
- **WF ID**: WF-0020
- **Context**: `backend/app/db.py` raises at import time if `DATABASE_URL` is unset. Today, `backend/scripts/ingest_call.py` imports DB code at module import time, which blocks dry-run validation on machines without DB configuration.
- **Decision**: Require that the dry-run path validates + prints a summary without importing/initializing DB connectivity code (defer DB imports until the non-dry-run path).
- **Why**: “Validate-only” should be safe, fast, and usable while authoring call YAML without provisioning Postgres.
- **Tradeoff**: Script structure must be slightly refactored (lazy imports) to avoid import-time DB resolution.
- **Status**: Approved.

### AD 20.3: Strict V2 schema (fail on unknown keys) + deterministic JSON summary output
- **WF ID**: WF-0020
- **Context**: Call-definition YAML authoring benefits from catching typos/unknown keys early. Dry-run output must be stable for repeated iteration and troubleshooting.
- **Decision**: Default to forbidding unknown keys in V2 validation, and print a self-describing, deterministic JSON summary in dry-run (include `schema_version` and `source_path`, stable ordering).
- **Why**: Reduces silent drift/typos in YAML and makes it easy to compare runs while editing.
- **Tradeoff**: Adding new YAML fields will require code/schema updates rather than being silently accepted.
- **Status**: Approved.

## Date: 2026-02-18 (WF-0019: Add Loading & Empty States)

### AD 19.1: Frontend-only state UX improvements
- **WF ID**: WF-0019
- **Context**: P1 launch-readiness issue is user confusion in loading/no-data moments, not backend correctness.
- **Decision**: Implement loading and empty-state improvements only in frontend route components and shared UI helpers; no backend/API changes.
- **Why**: Smallest change that addresses user-facing trust issues quickly.
- **Tradeoff**: Reuse of current fetch lifecycle means deeper async-state redesign is deferred.
- **Status**: Approved.

### AD 19.2: Deterministic empty-state CTA behavior
- **WF ID**: WF-0019
- **Context**: Empty states without explicit direction can stall first-time users.
- **Decision**: Every in-scope empty state includes a deterministic next-action CTA (for reviews-empty, CTA targets `/app` start flow).
- **Why**: Prevents dead-end UX and improves first-use onboarding clarity.
- **Tradeoff**: CTA destinations stay minimal; richer context-aware routing is deferred.
- **Status**: Approved.

## Date: 2026-02-18 (WF-0018: Harden Submit Flow UX)

### AD 18.1: Submit-flow hardening without backend/API expansion
- **WF ID**: WF-0018
- **Context**: Current submit-flow trust issues are UX/state-transition problems; adding new backend endpoints would increase scope/risk.
- **Decision**: Keep WF-0018 frontend-focused and reuse existing review/auth contracts with no API changes.
- **Why**: Fastest path to eliminate user confusion before real-user rollout.
- **Tradeoff**: Some observability and deeper state guarantees are deferred to future workflows.
- **Status**: Approved.

### AD 18.2: Canonical restart and redirect targets for submit continuity
- **WF ID**: WF-0018
- **Context**: Ambiguous restart/redirect targets cause dead-end navigation and inconsistent user recovery paths.
- **Decision**: Define deterministic targets for restart (`/app/review/new` or equivalent create-review route) and sign-out public return (`/` unless auth contract requires equivalent canonical public route).
- **Why**: Deterministic routing is required to validate no dead-end submit-flow states.
- **Tradeoff**: If current route contracts differ, task implementation must align names while preserving deterministic target behavior.
- **Status**: Approved.

## Date: 2026-02-18 (Workflow System)

### AD W.1: Add Phase 0 End-to-End Runner
- **Decision**: Introduce `docs/workflow/phase-0-run-start-and-brainstorm.md` to execute Phase `0.0` then `0.1` sequentially in one run.
- **Rationale**: Reduces phase-sequencing errors and makes `run phase 0` consistent with existing end-to-end runners for phases 1-3.
- **Status**: Approved.

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

---

## Date: 2026-02-08 (Task 7.0 FastAPI MVP)

### AD 7.1: Minimal Endpoint Surface
- **Decision**: FastAPI MVP exposes only `GET /health`, `GET /calls`, `GET /calls/{call_id}/nodes`, `POST /reviews`, and `GET /reviews/{review_id}`.
- **Rationale**: Delivers a complete client flow with minimal API area and lower maintenance risk.
- **Status**: Implemented.

### AD 7.2: Canonical API Error Contract
- **Decision**: All non-2xx responses use `{ "error": { "code", "message", "details" } }` with centralized code→status mapping.
- **Rationale**: Keeps frontend handling consistent and avoids semantic drift across handlers.
- **Status**: Implemented.

### AD 7.3: Stub LLM Mode for Verification
- **Decision**: Added `LLM_MODE=stub` for deterministic, schema-valid local reviews without OpenAI calls.
- **Rationale**: Enables frequent, low-cost API verification while preserving production code paths.
- **Status**: Implemented.

---

## Date: 2026-02-08 (Task 8.0 Frontend + Launch Architecture)

### AD 8.1: Next.js Frontend with BFF Pattern (Split Hosting)
- **Decision**: Build the UI and SEO site as a single Next.js app (TS/React) with MDX for articles, using a Backend-for-Frontend pattern: browser talks to Next.js routes; Next.js calls FastAPI server-to-server.
- **Rationale**: Strong SEO + app UX on one site, while keeping LLM-backed FastAPI isolated from browser traffic and simplifying auth (no cross-origin cookie/CORS complexity).
- **Status**: Approved (implementation pending).

### AD 8.2: Login Required + Magic Link Auth + Quotas-First
- **Decision**: Require login to submit reviews. Use magic-link email auth (initially) and enforce free-tier usage quotas before adding payments.
- **Rationale**: Minimizes abuse/cost exposure early while keeping onboarding low-friction and preserving a straightforward upgrade path to Stripe later.
- **Status**: Approved (implementation pending).

### AD 8.3: Managed Postgres for v1
- **Decision**: Use managed Postgres for production v1 (replacing SQLite for deployed environments), and host it close to the backend.
- **Rationale**: Supports auth/session storage, quotas, and future scaling/reliability needs better than SQLite, especially under concurrent LLM traffic and split hosting.
- **Status**: Approved (implementation pending).

### AD 8.4: Clerk for Authentication (MVP)
- **Decision**: Use Clerk for login (magic link) in MVP/v1.
- **Rationale**: Avoids building email delivery + token/session plumbing during MVP while keeping login-required abuse control and a smooth upgrade path to payments later.
- **Status**: Approved (implementation pending).

### AD 8.5: Render Managed Postgres (v1)
- **Decision**: Use Render’s managed Postgres for v1 production database.
- **Rationale**: Consolidates DB ops (backups/availability) and pairs naturally with hosting the FastAPI service on Render.
- **Status**: Superseded by AD 8.15 (Neon).

### AD 8.6: Split Hosting: Vercel (Next.js) + Render (FastAPI + Postgres)
- **Decision**: Host Next.js on Vercel (with Clerk) and host FastAPI + Postgres on Render.
- **Rationale**: Best-in-class DX/SEO for Next.js on Vercel, while isolating long-running LLM requests to a backend host suited for persistent services and managed databases.
- **Status**: Approved (implementation pending).

### AD 8.7: Backend BFF Contract Enforcement (8.0B)
- **Decision**: Protected review routes require a BFF signature (`X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`) and `POST /reviews` requires `Idempotency-Key`.
- **Rationale**: Prevent direct browser abuse of review-generation endpoints, enforce ownership boundaries, and avoid duplicate LLM spend on retries.
- **Status**: Implemented.

### AD 8.8: Review Failure as Lifecycle State (not API error)
- **Decision**: LLM call/validation/timeout failures persist `Review(status=FAILED)` and return `200` with `{review_id, status:"FAILED"}` instead of 5xx LLM errors.
- **Rationale**: Keeps client behavior state-driven and retry-safe with idempotency while preserving observability in persisted review records.
- **Status**: Implemented.

---

## Date: 2026-02-10 (Task 8.0A Frontend UI)

### AD 8.9: Auto-load `backend/.env` on API startup (Dev Convenience)
- **Decision**: `backend/main.py` loads `backend/.env` on startup when present, without overriding already-set environment variables.
- **Rationale**: Removes a common footgun when running `uvicorn main:app --reload` locally (especially for `BFF_SHARED_SECRET` and `OPENAI_API_KEY`), while keeping production behavior safe (deployments inject env vars; `.env` is not shipped).
- **Status**: Implemented.

---

## Date: 2026-02-12 (Task 8.0C Deployment Wiring - Phase 3)

### AD 8.10: Normalize `DATABASE_URL` for Render Postgres
- **Decision**: Backend DB config normalizes `DATABASE_URL` for SQLAlchemy/psycopg compatibility:
  - `postgres://...` and `postgresql://...` are rewritten to `postgresql+psycopg://...`
  - default query params enforce `sslmode=require` and `connect_timeout=3` when missing
- **Rationale**: Removes provider-specific URL footguns and forces secure, bounded connection behavior for MVP.
- **Status**: Implemented.

### AD 8.11: Readiness check endpoint at `GET /health/db`
- **Decision**: Keep `GET /health` as liveness and add `GET /health/db` that executes a minimal DB ping.
- **Rationale**: Deployment wiring needs a DB-aware health signal; liveness-only checks are insufficient for launch gating.
- **Status**: Implemented.

### AD 8.12: Production bootstrap requires active `PromptTemplate`
- **Decision**: Production bootstrap uses explicit commands:
  1) ensure active prompt template (`scripts/ensure_prompt_template.py`)
  2) ingest at least one real call YAML (`scripts/ingest_call.py ...`)
- **Rationale**: `POST /reviews` requires an active `PromptTemplate`; YAML ingestion alone does not create it.
- **Status**: Implemented.

### AD 8.13: Phase 3 execution order is strict (`8.0C.1` -> readiness hardening -> staged deploy checks)
- **Decision**: Next implementation round must run in this sequence:
  1) provider/env wiring (`8.0C.1`)
  2) readiness failure semantics hardening (explicit `503` on DB-unreachable readiness)
  3) deploy Stage 1 verification in `LLM_MODE=stub`
  4) deploy Stage 2 one-shot verification in `LLM_MODE=openai`
- **Rationale**: Reduces thrash and isolates wiring risk/cost before real LLM verification.
- **Status**: Approved (implementation pending).

### AD 8.14: DB readiness failure should be explicit (`503`) for deploy probes
- **Decision**: Keep `GET /health` as liveness, but ensure DB readiness failures produce a stable `503` response instead of generic uncaught errors.
- **Rationale**: Improves operator signal quality and deployment diagnostics with minimal implementation overhead.
- **Status**: Implemented.

### AD 8.15: DB provider is Neon (not Render Postgres)
- **Decision**: Use Neon for managed Postgres; keep Render for hosting FastAPI.
- **Rationale**: Separates DB provider choice from backend hosting while preserving the existing `DATABASE_URL` integration (Task 8.0C).
- **Status**: Approved.

### AD 8.16: Production default `LLM_MODE=stub` until launch day
- **Decision**: Keep production running with `LLM_MODE=stub` by default until launch day; enable `LLM_MODE=openai` only for explicit verification runs.
- **Rationale**: Minimizes cost/blast radius while infra stabilizes; we already proved one real OpenAI end-to-end run fits within the timeout budget.
- **Status**: Approved.

---

## Date: 2026-02-14 (PeerLens Frontend MVP Decisions)

### AD 9.1: Product name is PeerLens (UI copy + metadata)
- **Decision**: Rename the user-facing product/app to **PeerLens** (keep “Grant Reviewer” as the repo/internal name if convenient).
- **Rationale**: Avoids repeated copy/SEO rework; aligns the MVP with the intended product brand early.
- **Status**: Approved.

### AD 9.2: Signed-out landing demo is static and pre-generated (no backend calls)
- **Decision**: The landing page demo is a **static example switcher** (no user-provided text, no calls to `POST /reviews`).
  - Examples to showcase: `NWO-Veni`, `ERC-Starting`, `MSCA-PF`.
- **Rationale**: Preserves the “login + quotas + BFF boundary” cost-control posture and avoids exposing review generation on the highest-traffic route.
- **Status**: Approved.

### AD 9.3: Data retention promise is “until user deletes” with self-serve deletion
- **Decision**: MVP promise: user proposal snippets are retained **until the user deletes them**, and deletion is **self-serve in the UI**.
- **Rationale**: Matches researcher expectations and reduces reluctance to paste sensitive proposal content.
- **Status**: Approved.

### AD 9.4: Deletion semantics (hard delete review + cards + snippet; no quota refund; no rerun)
- **Decision**: “Delete review” performs a **hard delete** of:
  - the `Review`
  - its `ReviewCard`s
  - the associated proposal snippet text
  - Deletion does **not** refund quota, and deletion ends the results flow (no “rerun from results”).
- **Rationale**: Keeps abuse/cost controls intact and makes the retention promise truthful.
- **Status**: Approved.

### AD 9.5: Review Library is local-only in MVP (device-scoped)
- **Decision**: `/app/reviews` is “Recent reviews on this device” (local storage) and is not account-wide in MVP.
- **Rationale**: Avoids new backend API surface and keeps the MVP focused on the submit → results loop.
- **Status**: Approved.

### AD 9.6: Add minimal `/privacy` page (MVP)
- **Decision**: Ship a minimal `/privacy` page in MVP that states:
  - PeerLens does not use proposal snippets to train its models.
  - Proposal snippets are retained until the user deletes them (self-serve deletion).
  - Minimal operational logs/backups may be retained for up to **30 days**.
- **Rationale**: Researchers expect explicit privacy posture before pasting sensitive proposal text; this keeps copy truthful while allowing operational reality.
- **Status**: Approved.

### AD 9.7: Landing page: remove “Watch Demo”, use text-only trust, privacy-only footer
- **Decision**: The landing page MVP:
  - Removes the secondary “Watch Demo” CTA (single primary CTA only).
  - Uses text-only “Supported calls” (no funder logos).
  - Uses a privacy-only footer (no Terms link in MVP scope).
  - Avoids making detailed privacy/training claims on the landing page; links to `/privacy` for specifics.
- **Rationale**: Reduces implied scope (extra routes/assets) and avoids accidental over-claims while preserving the conversion goal (sign-in).
- **Status**: Approved.

### AD 9.8: Landing demo content is fixed (micro-rewrites + export promise + ERC label)
- **Decision**: Lock the landing page static demo content for MVP:
  - Each tab includes micro-rewrite examples inside suggested fixes (not a separate before/after block).
  - Landing may promise “Export your review” (app feature).
  - Use the label “ERC Starting” (not “StG”).
- **Rationale**: Prevents copy/UI thrash during PRD/tasks and keeps the demo aligned with the sign-in funnel.
- **Status**: Approved.

### AD 9.9: Landing demo tabs use a minimal client component (no vendor deps)
- **Decision**: Implement the landing demo tab switcher as a small `use client` component with local state (no URL state, no third-party tab library).
- **Rationale**: Keeps the landing interactive enough to communicate value while avoiding dependency bloat and reducing performance/accessibility risk.
- **Status**: Approved.

### AD 9.10: MVP “Export your review” means copy/download text (no PDF)
- **Decision**: For MVP, “Export your review” is satisfied by providing a user-visible export action that supports “Copy as text” and/or “Download .txt”. PDF export is explicitly not required for MVP.
- **Rationale**: Keeps the landing copy truthful with minimal implementation effort and low UX risk.
- **Status**: Approved.

### AD 9.11: Delete review endpoint returns `200 { ok: true }` (MVP)
- **Decision**: `DELETE /reviews/{review_id}` returns `200` with JSON `{ "ok": true }` on successful deletion.
- **Rationale**: Simplifies Next.js BFF + UI handling and avoids special-casing `204` parsing behavior in the adapter.
- **Status**: Approved.

---

## Date: 2026-02-15 (Documentation Alignment)

### AD 10.1: Documentation Convergence (Phase 0-4 Alignment)
- **Decision**:
    1.  **Single Source of Truth**: `AGENTS.md` and `docs/workflow/README.md` are the SSOT for Process/Workflow/Git. `GEMINI.md` is restricted to Behavioral Guidelines only.
    2.  **Pipeline Alignment**: All docs now agree on: Phase 0 (Brainstorm) -> Phase 1 (Spec) -> Phase 2 (PRD) -> Phase 3 (Tasks) -> Phase 4 (Impl).
    3.  **Naming Convention**: Enforced `task-` (Singular) filename prefix inside `docs/tasks/` folder.
    4.  **Skills**: Consolidated local project skills into global `~/.agents/skills` and removed `agent-operating-protocol.md`.
- **Rationale**: Eliminates drift between agent instructions and actual workflow rules. Supports parallel agent usage (Antigravity/Codex).
- **Status**: Implemented.

### AD 10.2: “Check Skills First” Habit
- **Decision**: Before starting a new category of work, the agent should check for an existing skill in `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`.
- **Rationale**: Reuses battle-tested workflows and reduces “reinventing” patterns (migrations, a11y, API usage).
- **Status**: Implemented (`AGENTS.md` + Codex/Copilot instructions updated).

### AD 10.3: Tool-Specific Instruction Adapters Live Alongside `AGENTS.md`
- **Decision**: Keep `AGENTS.md` as the SSOT, and allow tool-specific instruction files (like `.github/copilot-instructions.md`) to exist as *adapters* that point tools back to `AGENTS.md`.
- **Rationale**: Different agent tools auto-discover different filenames/locations. Adapters reduce drift by centralizing real rules in `AGENTS.md` while still satisfying each tool’s discovery mechanism.
- **Status**: Implemented (added rationale header to `.github/copilot-instructions.md` and documented the pattern in `docs/reference/README_agent_instructions.md`).

## Date: 2026-02-15 (WF-0010: PeerLens Landing Design Refresh)

### AD 10.4: PeerLens Landing Visual Direction + Palette
- **Decision**: PeerLens landing should feel like a clean journal/institutional site (“ink on paper”), not a startup SaaS.
- **Palette (Ink + Parchment)**:
  - `--background`: `#FCFBF7` (paper)
  - `--foreground`: `#0B1F3B` (ink navy)
  - `--muted-foreground`: `#4B5563`
  - `--surface`: `#F4F2EC`
  - `--surface-muted`: `#EEEAE2`
  - `--border`: `#D6D3C8`
  - `--primary`: `#1F4E79` (institutional blue)
  - `--primary-foreground`: `#FFFFFF`
  - Optional accent (very sparing): `--accent`: `#0F766E` (deep teal) **or** `#A35D2A` (copper)
- **Rules**:
  - Primary color only for clickable actions/links.
  - Accent never for body text; use for small badges/markers only.
  - Maintain WCAG AA contrast for text/controls.
- **Scope**: WF-0010 may tweak landing copy and will update `docs/reference/brand_guidelines.md` to match.
- **Status**: Approved.

### AD 10.5: Backend Ruff MVP Baseline Scope (Task 8.1)
- **Decision**: Adopt a safe backend Ruff baseline in `backend/pyproject.toml` with:
  - `select = ["E4", "E7", "E9", "F", "I", "B", "UP"]`
  - per-file ignore: `"scripts/run_review.py" = ["E402"]`
- **Rationale**: Enables a reliable lint signal with low behavior-change risk by focusing on correctness/import hygiene and avoiding broad strictness families during MVP.
- **Scope note**: CI diff-gating is intentionally deferred to the next guardrails slice (Task 8.2) to keep 8.1 low-risk and mergeable.
- **Status**: Implemented.

### AD 10.6: WF-0010 PRD Execution Guardrails (Landing-Only + Explicit Verification Gate)
- **Decision**: WF-0010 PRD is constrained to landing-surface work only (`/`, landing components, `globals.css`, brand guideline updates) with no backend/auth or `/app/*` behavior changes.
- **Verification Gate**: PRD requires this bundle before implementation close:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run check:seo`
  - `cd frontend && npx next build --webpack`
  - manual keyboard + mobile readability pass on `/`
- **Why**: Keeps the refresh MVP-fast while preserving functional stability and quality.
- **Tradeoff**: Defers conversion instrumentation and proof-asset expansion to a follow-up WF.
- **Status**: Approved.

### AD 10.7: Introduce Serif Heading Layer Alongside Inter
- **Decision**: Introduce a serif heading layer (`Lora`) alongside `Inter` to convey academic authority while preserving UI clarity and readability for dense research content.
- **Typography Architecture**:
  - `Lora` (`600`) for primary large headings and editorial titles.
  - `Inter` for body, navigation, controls, forms, and dense UI.
  - No serif usage in forms, tables, buttons, or long body paragraphs.
- **Scale Update (Lora + Inter pairing)**:
  - `H1` (editorial): `clamp(2.2rem, 3.6vw, 2.95rem)`, `line-height: 1.22`, `600`
  - `H2` (editorial): `clamp(1.55rem, 2.1vw, 1.95rem)`, `line-height: 1.28`, `600`
  - `H3` (default): `clamp(1.2rem, 1.45vw, 1.32rem)`, `line-height: 1.36`, Lora `600`
  - `Body`: Inter `16px`, `line-height: 1.6`
- **Exception Rule**:
  - Dense UI headings may explicitly opt into Inter (`font-sans`) to preserve compact readability.
- **Implementation Notes**:
  - Load both fonts via `next/font/google` and expose CSS variables in `frontend/src/app/layout.tsx`.
  - Map variables in `frontend/src/app/globals.css` and apply heading/body scale from `docs/reference/brand_typography_system.md`.
- **Rationale**: Adds scholarly tone on marketing surfaces without harming legibility or interaction clarity.
- **Status**: Approved.

## Date: 2026-02-15 (WF-0011: Local Postgres Dev DB)

### AD 11.1: Local Postgres blessed path is Docker Compose (`backend/docker-compose.dev.yml`)
- **WF ID**: WF-0011
- **Context**: Local development needs a single reproducible startup contract to reduce SQLite/Postgres drift and onboarding variance.
- **Decision**: Define one blessed local DB startup path using `backend/docker-compose.dev.yml` with `postgres` service, local bind on `localhost:5432`, and local dev persistence volume.
- **Why**: One standard path minimizes setup ambiguity and support overhead while staying MVP-fast.
- **Tradeoff**: Developers without Docker get only brief fallback notes in this WF (no full native setup playbooks).
- **Status**: Approved.

### AD 11.2: Local env safety contract defaults to localhost Postgres (`sslmode=disable`)
- **WF ID**: WF-0011
- **Context**: Current backend normalizer adds Postgres SSL defaults appropriate for hosted providers; local dev needs explicit local connection semantics and protection against accidental Neon usage.
- **Decision**: Local docs/env contract must default `DATABASE_URL` to localhost Postgres with `sslmode=disable`; Neon URLs are explicit opt-in only for local debugging.
- **Why**: Prevents accidental writes to hosted environments and keeps local startup predictable.
- **Tradeoff**: Requires stricter env-profile discipline in local onboarding docs.
- **Status**: Approved.

### AD 11.3: PRD verification gate requires minimum seed thresholds + terminal stub review flow
- **WF ID**: WF-0011
- **Context**: DB connectivity alone is insufficient; local workflow must prove functional readiness for review generation.
- **Decision**: Define readiness as: required seed thresholds met (`prompt_templates >= 1 active`, `funding_calls >= 1`, `proposal_nodes >= 1`) plus one local stub review submission reaching terminal status.
- **Why**: Ensures local Postgres setup is actually usable for app flows, not just reachable.
- **Tradeoff**: Adds a small verification step to local setup before development can proceed.
- **Status**: Approved.

## Date: 2026-02-16 (WF-0011 Follow-up: Postgres-only Runtime)

### AD 11.4: Remove SQLite fallback and require PostgreSQL `DATABASE_URL`
- **WF ID**: WF-0011 (follow-up policy hardening)
- **Context**: Mixed local DB modes (SQLite fallback vs local Postgres) caused confusing count mismatches and reduced confidence in development verification.
- **Decision**: Backend runtime is now PostgreSQL-only. `DATABASE_URL` is required; SQLite fallback behavior has been removed from `backend/app/db.py`.
- **Why**: Single-engine development and production parity reduces ambiguity and speeds iteration/debugging.
- **Tradeoff**: Local startup now depends on Postgres availability; missing `DATABASE_URL` fails fast at app startup.
- **Status**: Implemented.

## Date: 2026-02-16 (WF-0012: Alembic Migration Baseline)

### AD 12.1: Postgres-only Alembic baseline contract with a single root revision
- **WF ID**: WF-0012
- **Context**: The backend needs versioned schema evolution, but currently lacks a migration chain anchor.
- **Decision**: Initialize Alembic for Postgres-only runtime and create exactly one baseline root revision (`down_revision = None`) representing current SQLModel schema state.
- **Why**: Establishes a deterministic migration starting point for all future schema changes.
- **Tradeoff**: Baseline quality depends on careful review of autogenerated migration output before application.
- **Status**: Approved.

### AD 12.2: Baseline immutability + local-only drift recovery guidance
- **WF ID**: WF-0012
- **Context**: Existing developer DBs may drift from baseline assumptions and create confusion during first migration runs.
- **Decision**: Treat committed baseline migration as immutable; for local drift, document recovery via local reset or `alembic stamp` guidance in runbooks (no production automation in this WF).
- **Why**: Keeps migration history trustworthy and avoids rewriting applied revisions.
- **Tradeoff**: Some local environments may require manual cleanup before converging to the baseline.
- **Status**: Approved.

### AD 12.3: Explicit enum type cleanup in baseline downgrade for re-upgrade safety
- **WF ID**: WF-0012
- **Context**: Baseline downgrade left PostgreSQL enum types behind, causing re-upgrade failure (`DuplicateObject` on enum creation).
- **Decision**: Add explicit `DROP TYPE IF EXISTS` statements for workflow enums in baseline migration downgrade.
- **Why**: Ensures baseline migration remains reversible on local Postgres verification cycles.
- **Tradeoff**: Downgrade now assumes enum types are owned by this schema/migration path, which is valid for this baseline.
- **Status**: Implemented.

---

## Date: 2026-02-16 (WF-0014: Review History)

### AD 14.1: Simple Pagination for Reviews List
- **Decision**: `GET /reviews` uses a simple `limit` parameter (default 50, max 100) and no cursor/offset for MVP.
- **Rationale**: User volume is low; complex pagination is premature optimization.
- **Status**: Implemented.

### AD 14.2: Reviews are Server-Side (Overturns AD 9.5)
- **Decision**: "My Reviews" (`/app/reviews`) is backed by a server-side `GET /reviews` endpoint, making history available across devices for authenticated users.
- **Rationale**: User feedback and implementation reality favor persistent, accessible history over device-scoped MVP limitations.
- **Status**: Implemented.

---

## Date: 2026-02-17 (WF-0015: Practices Upgrade)

### AD 15.1: Strict Linting on Legacy Code
- **Decision**: Enforce strict `ruff` + `mypy` on *new* code, but use `per-file-ignores` or configuration excludes for existing legacy violations.
- **Rationale**: Blocking the upgrade on fixing 100% of legacy debt is impractical.
- **Status**: Proposed.

### AD 15.2: CI/CD Tooling Selection
- **Decision**: Use GitHub Actions for CI, `uv` for python management, and `npm` for frontend.
- **Rationale**: Standard, modern stack with excellent caching support. `uv` is significantly faster than pip/poetry.
- **Status**: Proposed.

---

## Date: 2026-02-18 (WF-0017: Auto Polling for Processing Reviews)

### AD 17.1: Bounded client polling with no backend contract changes
- **WF ID**: WF-0017
- **Context**: Users currently need manual refresh while reviews are in `PROCESSING`, but introducing new transport/API surface would expand MVP scope.
- **Decision**: Implement client-side polling every 3 seconds with a 90-second cap using existing review status contracts (`PROCESSING`, `COMPLETED`, `FAILED`) and no backend API changes.
- **Why**: Fastest low-risk path to improve user trust in wait-state behavior before real-user rollout.
- **Tradeoff**: Long-running reviews may still require manual follow-up after the polling cap, and this does not provide real-time push semantics.
- **Status**: Approved.

## Date: 2026-02-22 (WF-0028: Compliance Engine)

### AD 28.1: Deterministic Mandatory Field Definition
- **WF ID**: WF-0028
- **Context**: The V2 DB schema lacks an explicit `mandatory: boolean` flag on proposal nodes. The compliance engine needs a deterministic way to flag missing required text.
- **Decision**: A node is considered mandatory if its `CallDefinition` canonical JSON `content_constraints` block contains a `word_limit` (min or max) OR an explicit `mandatory: true` flag.
- **Why**: Safest heuristic given the current schema. Future YAML ingestion can simply add `mandatory: true` to bypass word-limit heuristics if needed.
- **Tradeoff**: Heuristics are loose; if a real mandatory field has no word limit and no explicit flag in the YAML, it won't be blocked.
- **Status**: Approved.

### AD 28.2: Phase 1.2 Risk Audit Feedback on PRD v0.3
- **WF ID**: WF-0028
- **Context**: Codex adversarial review flagged high risks in the v0.2 PRD draft regarding schema alignment, domain constraints, input structure, and router placement.
- **Decision**:
  1. Removed `mandatory: true` and `word_limit` flat fields, aligning F4 to use V2 schema (`total_word_limit.min_words` or Expectation `MANDATORY` strength).
  2. Made `domain` optional in request payload, enforcing it via 422 only when a call config defines `word_limit_by_domain`.
  3. Added explicit 422 handling for unknown `node_logical_id`s and missing mandatory nodes.
  4. Dropped `max_items` entirely from MVP scope to avoid NLP/fragile parsing heuristics on plain text input.
  5. Affirmed single tokenization strategy for MVP, explicitly ignoring semantic exclusions (e.g. "excludes references").
  6. Clarified routing placement in `main.py` (or explicit refactor action) to prevent architectural drift.
- **Why**: Protects MVP delivery speed by strictly aligning the PRD with database/JSON reality and stripping under-defined parsing heuristics.
- **Tradeoff**: Word counts remain approximate (ignoring semantic rules like "exclude references"); users must manually verify exact lengths against Funder PDFs.
- **Status**: Implemented in PRD v0.3.

## Date: 2026-02-22 (WF-0030: Frontend Structured Form)

### AD 30.1: Universal Form Over Hardcoded Routes
- **WF ID**: WF-0030
- **Context**: The frontend needs to support Veni's 3-node structure, but hardcoding `/app/submit/veni` reduces extensibility for future schemas (like ERC).
- **Decision**: The submit route `/app/submit` dynamically fetches the call schema and renders flat `<textarea>` elements mapped to `ProposalNode`s. Non-text nodes degrade visibly to "Unsupported Input Type". Nested nodes are explicitly unsupported in MVP.
- **Why**: Proves the value of a data-driven UI without over-engineering recursive structure rendering.
- **Tradeoff**: Less custom UI polish per funder, but radically faster ingestion of new calls.
- **Status**: Implemented in PRD v0.2.

### AD 30.2: Purely Local Word Counting
- **WF ID**: WF-0030
- **Context**: Real-time compliance feedback is needed, but bouncing every keystroke to `/api/check-compliance` is wasteful.
- **Decision**: Frontend implements a local JS equivalent of backend's `\s+` regex tokenization for zero-latency UI word counts.
- **Why**: Fastest, cheapest UX.
- **Tradeoff**: Requires developers to keep the JS and Python tokenization logic in perfect sync.
- **Status**: Implemented in PRD v0.2.

### AD 30.3: Client-Side Idempotency via UUID v4
- **WF ID**: WF-0030
- **Context**: Double-clicks during 90-second evaluations waste expensive LLM tokens.
- **Decision**: Frontend generates a UUID v4 session identifier and passes it as `Idempotency-Key` header on submission.
- **Why**: Explicitly maps to the backend draft deduplication contract.
- **Tradeoff**: None. Safe and standard pattern.
- **Status**: Implemented in PRD v0.2.

### AD 30.4: Universal Form + Fail Fast on Nested Nodes
- **WF ID**: WF-0030
- **Context**: PRD v0.2 excluded recursive rendering but kept a dynamic universal form. Actual test fixtures (e.g. ERC) have nested structures.
- **Decision**: Keep the universal dynamic renderer, but strictly fail-fast on any call with nested nodes, presenting a blocking error that the call is unsupported in the current MVP rather than rendering a broken form.
- **Why**: Protects the MVP delivery timeline while still proving the dynamic concept on flat schemas (like Veni).
- **Tradeoff**: Calls with nested structures cannot be supported until P2.
- **Status**: Implemented in PRD v0.3.

### AD 30.5: Backend Node Metadata DTO (`GET /calls/{id}/form-schema`)
- **WF ID**: WF-0030
- **Context**: `/calls/{call_id}/nodes` does not serve `logical_id`, labels, or constraints required to accurately render a dynamic UI form, making frontend logic impossible without hardcoding.
- **Decision**: Add a minimal DTO route for `/calls/{call_id}/form-schema` to serve `logical_id`, labels, and constraints explicitly for form rendering.
- **Why**: Establishes a clean API contract for dynamic UIs rather than forcing the frontend to read raw canonical JSON documents.
- **Tradeoff**: Expands the backend scope slightly to build the new route.
- **Status**: Implemented in PRD v0.3.

### AD 30.6: Enforce Domain String on Client
- **WF ID**: WF-0030
- **Context**: The NWO Veni call has an ENW/Science "pilot" altering word counts.
- **Decision**: The "ENW Toggle" directly specifies the exact backend domain string required by `/api/check-compliance`. The domain is persisted in the local draft and passed explicitly in proxy requests.
- **Why**: Prevents split-brain validation where the client interface counts 500 words, but the backend rejects over 100.
- **Tradeoff**: Minimal constraint mapping required in the Next.js client.
- **Status**: Implemented in PRD v0.3.

### AD 30.7: Revert Universal Form Pivot (Veni-Only Scope)
- **WF ID**: WF-0030
- **Context**: Second Codex adversarial review flagged the "Universal Form" + "New Node Metadata DTO" as high-risk platform work that expands the MVP scope unsafely.
- **Decision**: Revert AD 30.1 and AD 30.5. The WF-0030 MVP will be a hardcoded 3-node Veni form. No dynamic schema fetch. No backend DTO route.
- **Why**: Protects the delivery timeline and guarantees we ship the end-to-end V2 experience quickly. Universal rendering will be tackled in a future, dedicated workflow.
- **Tradeoff**: Adding the next funding call (e.g., ERC) will require a new React component until the universal form is built.
- **Status**: Implemented in PRD v0.4.

### AD 30.8: Explicit 422 Hard Block for Form Submission
- **WF ID**: WF-0030
- **Context**: The "Submit Anyway" bypass modal is designed for 200 OK `errors[]` (compliance warnings). If the payload is completely malformed (e.g., missing mandatory nodes, unknown IDs), the backend returns a 422.
- **Decision**: The frontend must explicitly differentiate handling: Trap 422s to hard-block submission and show the exact error message WITHOUT the bypass modal. Trap 200 `errors[]` to show the bypass modal.
- **Why**: Avoids invalid bypass UX and confusing retry loops.
- **Tradeoff**: None. Strict compliance with backend API design.
- **Status**: Implemented in PRD v0.4.

- Date: 2026-02-25
- WF ID: WF-0031
- Context: PRD generation and risk audit for accessibility pass.
- Decision: Defer automated a11y testing (Playwright) and rely on manual VoiceOver/keyboard verification for MVP.
- Why: Keeps scope tight and focused strictly on the most critical user flows (submission and reviewing results) for launch blocker resolution.
- Tradeoff: Risk of future regressions without automated regression tests, but significantly speeds up time-to-market for the required fix.

## Date: 2026-02-25 (WF-0032: ERC 2026 STG YAML & Hierarchical Ingestion)

### AD 32.1: Hierarchical Modeling via `parent_logical_id` in YAML
- **WF ID**: WF-0032
- **Context**: The ERC 2026 StG call has deep nesting (Parts B1, B2, CV) which our current V2 schema does not map to the database `proposal_node` hierarchy.
- **Decision**: Update `CallDefinitionV2` to support `parent_logical_id` (str) on nodes, which the ingestion script resolves to the DB's `parent_node_id` (UUID). `max_pages` will be stored in `canonical_json` as UI guidance without a DB column schema change.
- **Why**: Keeps the ingestion payload simple and avoids Alembic migration thrash while correctly expanding the schema for hierarchical data.
- **Tradeoff**: Ingestion script must perform topological sorting/two-pass insertion to construct the tree and defend against cycle loops.
- **Status**: Approved in PRD v0.2.
