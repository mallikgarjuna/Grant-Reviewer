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
