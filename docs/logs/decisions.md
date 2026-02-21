# Architectural Decisions

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
