# Prompt History

## 2026-02-06

### 19:33 - Initial Request
> Project Brief: Grant Reviewer App (MVP – Locked Scope)
> Help me build the app incrementally from the ground up, using real world software building principles.
> Let's start with: Stage 0 only. Core use case: brainstorm and fine tune and scope the database architecture.

### 19:39 - Stage 0 Clarifications
> 1. Yes (generic ProposalNode with parent_id)
> 2. Anonymous
> 3. Single call (criteria locked per call)
> 4. No (no full audit for MVP)

### 20:06 - Finalized Database Schema
> User provided 11-table schema with detailed fields and relationships.

### 20:25 - Schema Clarifications
> 1. User lifecycle: anonymous, TTL-based
> 2. ReviewCard → NodeExpectation (not EvaluationElement)
> 3. Dual guidance fields confirmed
> 4. expires_at mandatory, 24h TTL
> 5. PromptTemplate immutable with versioning

### 20:44 - Stage 2 Approval
> User agreed to reject nodes with zero expectations.

### 20:59 - Stage 3 Tech Stack
> - Use SQLModel instead of SQLAlchemy
> - Use UV package manager
> - Follow clean architecture from reference repo
> - Backend code in /backend, frontend in /frontend
> - Use FastAPI for API implementation

### 22:49 - Stage 3 Execution
> OK. Go. Always ask questions if needed.
> Follow GEMINI.md and commit after each minor task.

## 2026-02-07

### 11:15 - Adding Field Descriptions
> User requested to add descriptive comments to all `Field` arguments in `models/domain.py`.
> Outcome: Updated all 11 models with concise field descriptions.

### 12:18 - Phase 0: Admin Workflow Brainstorming
> User asked: "What should an admin do to prepare the backend?"
> Outcome: Brainstormed Admin Workflow. User rejected PDF parsing, preferred "Manual Knowledge Encoding" (YAML).

### 12:23 - Phase 1: Definition (PRD)
> - Created `tasks/prd-5.0-admin-ingest.md`.
> - User feedback: Align YAML keys 1:1 with DB tables. Explicitly map IDs.
> - Outcome: Revised PRD v1.1 approved.

### 13:34 - Technical Q&A
> User asked about SQLModel naming convention (Singular Class vs Plural Table). Confirmed as standard practice.

### 13:42 - Phase 2: Planning
> - Created `tasks/task-5.0-admin-ingest.md`.
> - User feedback: Rename schemas to `call_definitions.py`, add `--dry-run`, add edge-case tests.
> - Outcome: Revised Task 5.0 plan approved. Ready for Phase 3.

### 14:21 - Phase 3: Execution (Task 5.0)
> User: "Start Phase 3: Execution for Task 5.0 (Admin Ingestion). Please verify you can read these files, then start with Task 5.1."
> Outcome: Completed all 4 sub-tasks:
> - 5.1: Created `call_definitions.py` with 7 Pydantic schemas and 2 validators
> - 5.2: Created `ingest_call.py` with atomic upsert and `--dry-run` flag
> - 5.3: Created 3 YAML test files (valid, invalid, edge cases)
> - 5.4: All 6 verification tests passed (schema validation, dry run, ingestion, edge cases, idempotency, integration)

## 2026-02-08

### 13:17 - Task 7.0 Alignment (FastAPI MVP)
> User requested an overview of what’s coming next.
> Alignment:
> 1) API-first
> 2) Minimal endpoint set
> Approved to start Phase 0 brainstorming for Task 7.0.

### 14:26 - Task 7.0 Phase 0 Approved → Phase 1 PRD
> User: "Phase 0 approved for Task 7.0; proceed to Phase 1 PRD"
> Outcome: Drafted `tasks/prd-7.0-fastapi-mvp.md`.

### 15:21 - Task 7.0 PRD Revision (critical review)
> User requested updates to PRD 7.0 based on critical review feedback (ratings semantics, lifecycle flexibility, error taxonomy, idempotency clarity, client timeout guidance).
> Outcome: Revised `tasks/prd-7.0-fastapi-mvp.md` (v0.2).

### 15:31 - Task 7.0 PRD Approved → Phase 2 Plan
> User: "PRD 7.0 approved; proceed to Phase 2 task plan"
> Outcome: Created `tasks/task-7.0-fastapi-mvp.md` and linked it in `tasks/index.md`.

### 15:56 - Task 7.0 Phase 2 Plan Revision (critical review)
> User requested updates to the Phase 2 task breakdown to clarify phase semantics, enforce forward-compat status typing, centralize error mapping, add atomicity tests, and add a stub LLM verification mode.
> Outcome: Revised `tasks/task-7.0-fastapi-mvp.md` and tightened error mapping in `tasks/prd-7.0-fastapi-mvp.md`.

### 16:00 - Task 7.0 Phase 2 Approved → Phase 3 Execution
> User approved Phase 2 and requested Phase 3 implementation.
> Outcome: Implemented FastAPI MVP endpoints, API schemas, repository query extensions, stub LLM mode, and API tests.

### 16:17 - Commit Granularity Clarification
> User asked to enforce commits after each implementation subtask (`7.1`, `7.2`, ...).
> Outcome: Added a permanent rule in `AGENTS.md` and `tasks/lessons.md` and reorganized Phase 3 work into subtask-scoped commits.

### 17:05 - Task 8.0 Direction + Phase 0 Approved
> User requested guidance on frontend stack/hosting/auth/DB for a v1 launch with SEO content.
> Decisions: Next.js (TS/React) + Tailwind + shadcn/ui + MDX, BFF pattern (Next routes call FastAPI server-to-server), Clerk auth (magic links), quotas-first, split hosting (Vercel for Next.js + Render for FastAPI + Render Postgres).
> User: "Go ahead to Phase 0"
> Outcome: Created `knowledge_base/logs/brainstorming-8.0-frontend-ui.md` and recorded AD 8.x decisions.

### 17:40 - Task 8.0B Phase 1 PRD (BFF Contracts)
> User: "OK. Go ahead to Phase 1 and draft prd for 8.0B."
> Outcome: Drafted `tasks/prd-8.0B-bff-contracts.md` and linked it in `tasks/index.md`.

### 18:05 - Task 8.0B Phase 2 Plan (BFF Contracts)
> User: "go ahead to Phase 2"
> Outcome: Created `tasks/task-8.0B-bff-contracts.md` and linked it in `tasks/index.md`.

### 18:20 - Task 8.0B Phase 2 Plan Revision (MVP simplifications)
> User provided critical feedback on the Phase 2 plan (idempotency concurrency risk, sync latency, lint timing, timeout policy).
> Outcome: Revised `tasks/task-8.0B-bff-contracts.md` to simplify idempotency concurrency (unique constraint + fetch-on-conflict), lock a 30s timeout budget policy, stage lint enforcement, explicitly defer `GET /quota`, and document manual-only retries.

### 18:30 - Task 8.0B Phase 2 Plan Sequencing Fix (8.0B before 8.0A)
> User flagged that the Phase 2 plan referenced a Next.js scaffold dependency even though 8.0B is sequenced before 8.0A.
> Outcome: Revised `tasks/task-8.0B-bff-contracts.md` to make Next scaffolding + adapter/lint an explicit “8.0A.0” prerequisite step, while keeping 8.0B focused on backend contract enforcement first.

### 18:55 - Task 8.0B Phase 3 Implementation (backend contracts)
> User approved Phase 3 and requested strict AGENTS workflow (new branch + commits per subtask).
> Outcome: Implemented subtask commits for 8.0B.1-8.0B.5:
> - signature auth on protected routes
> - ownership enforcement with masked 404 + internal logging
> - idempotency persistence + payload mismatch handling
> - failed-state semantics for LLM/timeout paths (`200` with `status=FAILED`)
> - daily quota + kill switch controls
> Added walkthrough `knowledge_base/walkthroughs/walkthrough_task_8.0B_bff_contracts.md` and updated `tasks/index.md`.
