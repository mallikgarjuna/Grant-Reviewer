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

### 19:05 - Docs Sync After 8.0B
> User requested: "Update KB and readme files."
> Outcome: Updated `README.md` project status/API notes and added implementation decisions (AD 8.7, AD 8.8) in `knowledge_base/logs/decisions.md`.

### 19:20 - Task 8.1 Phase 0 Started (Lint Baseline Cleanup)
> User requested creation of a new task ID and to start the gated phase workflow.
> Outcome: Created `knowledge_base/logs/brainstorming-8.1-lint-baseline-cleanup.md`, added Task 8.1 to `tasks/index.md`, and started Phase 0 on branch `task-8.1-lint-baseline-cleanup`.

### 19:30 - Task 8.1 Phase 0 Revision (critical review)
> User provided critical feedback on baseline/gating gaps and asked for MVP-fast decisions plus non-scope backlog.
> Outcome: Revised `knowledge_base/logs/brainstorming-8.1-lint-baseline-cleanup.md` (v0.2) with explicit decisions for diff-based lint gating, CI parity, ownership, formatter policy (Ruff-only), rule/behavior guardrails, done definition, and deferred split into Tasks 8.2/8.3.

### 19:40 - Workflow Instruction Recorded (MVP vs lint debt)
> User clarified that perfect linting should not block MVP progress and asked to record this safely for future runs.
> Outcome: Added an always-on rule in `AGENTS.md` and detailed lesson `L9` in `tasks/lessons.md` to enforce "changed-files lint now, full debt cleanup as separate task."

### 20:05 - Local Wrap-Up Workflow Recorded + Branch Consolidation
> User asked to wrap up all local work before the next task and to record lessons for future runs.
> Outcome: Added always-on guidance in `AGENTS.md` and detailed lessons (`L10`, `L11`) in `tasks/lessons.md` for no-remote branch consolidation (integration branch + tag + `git bundle`) and local workspace-file handling (`skip-worktree`).

### 20:20 - Task 8.0A Phase 0 Started (Frontend UI Slice)
> User: "OK. Let's proceed to Phase 0 for 8.0A (also consider the deferred 8.0A tasks from 8.0B from earlier)"
> Outcome: Created `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md` to define MVP UI slice scope and explicitly include the deferred “8.0A.0 scaffolding” (Next.js scaffold + BFF adapter + staged lint boundary).

### 20:30 - Task 8.0A Phase 0 Revised (critical review closure)
> User provided critical feedback focused on sync UX risk, idempotency key lifecycle, BFF enforcement timing, FAILED retry semantics, and SEO privacy guardrails.
> Outcome: Revised `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md` to lock MVP decisions for idempotency key storage (`sessionStorage`), FAILED retry behavior (new key, prefilled inputs), client timeout messaging (no auto-retry), deep-link expectations, and immediate server-only env enforcement for `FASTAPI_BASE_URL`.

### 20:45 - Task 8.0A Phase 0 Revised (footgun hardening)
> User asked to incorporate additional critical feedback (idempotency edge cases, signing brittleness, adapter drift risk, SEO misconfiguration risk).
> Outcome: Revised `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md` to persist draft + attempt metadata in `sessionStorage`, define payload normalization for hashing, require “sign exact bytes sent,” lock an in-flight submit disable policy, and add a lightweight verification guardrail for `/app/*` noindex.

### 21:00 - Task 8.0A Phase 1 PRD Started (Frontend UI Slice)
> User: "go ahead to Phase 1"
> Outcome: Drafted `tasks/prd-8.0A-frontend-ui.md` and linked it in `tasks/index.md`.

### 21:10 - Task 8.0A Phase 1 PRD Revised (critical review closure)
> User requested incorporating critical feedback (Clerk identity mapping, signing brittleness, idempotency storage semantics, adapter surface definition, timeout/SEO guardrails) with MVP-fast decisions.
> Outcome: Revised `tasks/prd-8.0A-frontend-ui.md` to lock the missing decisions, define the adapter API surface, clarify tab-scoped attempt persistence, align timeout expectations, and make the SEO verification step concrete.

### 21:20 - Task 8.0A Phase 2 Plan Started (Frontend UI Slice)
> User: "go ahead to Phase 2"
> Outcome: Created `tasks/task-8.0A-frontend-ui.md` and linked it in `tasks/index.md`.

### 21:30 - Task 8.0A Phase 2 Plan Revised (commit-sized subtasks)
> User requested incorporating critical feedback on plan size/risks and commit granularity.
> Outcome: Revised `tasks/task-8.0A-frontend-ui.md` to lock `frontend/` location and BFF route-handler approach, split 8.0A.0 and 8.0A.1 into commit-sized subtasks, and make adapter/SEO verification steps concrete.

### 21:45 - Task 8.0A Skill Guardrails Identified
> User ran `npx skills find ...` and shared results for Next.js/React and UI/accessibility.
> Outcome: Locked recommended optional skill guardrails in 8.0A docs (Vercel React/Next best practices + web accessibility) without expanding MVP scope.

### 22:00 - Task 8.0A Docs Revised (execution risk closure)
> User requested incorporating critical execution feedback (tooling availability, adapter-first gating, sync UX/SEO guardrails as concrete verify steps).
> Outcome: Revised 8.0A brainstorming/PRD/task docs to explicitly include Node tooling preflight + local scaffold fallback and to require adapter invariant checks before building UI pages.

### 22:20 - Task 8.0A Visual Style Decisions Locked (MVP)
> User provided explicit design choices for MVP UI direction (primary `#2563EB`, slate neutrals, Inter, medium-rounded corners, comfortable spacing, light-only theme) plus interaction principles.
> Outcome: Updated PRD + task plan to lock these values as implementation inputs for Phase 3 (`8.0A.0a2`).

### 22:35 - Task 8.0A Phase 3 Started (Tooling preflight result)
> User approved Phase 3.
> Outcome: Ran tooling preflight successfully (`nvm use v22.17.0`, node/npm/npx available) but Next scaffold was blocked in Codex due npm registry network resolution failure (`ENOTFOUND registry.npmjs.org`). Updated task plan with a local-scaffold fallback note and requested user to scaffold `frontend/` locally and commit.

### 22:55 - Task 8.0A.0a2 Completed (MVP style guide in code)
> User provided the local scaffold commit for `8.0A.0a`.
> Outcome: Implemented `8.0A.0a2` style baseline in `frontend` (Inter font, light-only palette/tokens, primary `#2563EB`, medium-rounded radius defaults, focus-visible outline, reduced-motion support), updated task checklist progress, and ran `cd frontend && npm run lint` successfully.

### 23:05 - Verification Policy Tightened (per-subtask commits)
> User requested: enforce tests/verification for each subtask and remember for future runs.
> Outcome: Added an always-on AGENTS rule requiring at least one targeted verification per Phase 3 subtask before commit, and updated Task 8.0A plan with explicit “verify before commit” checkpoints per remaining subtask.

### 23:15 - Task 8.0A Phase 2 Plan Renumbered (strict sequence)
> User requested strict numeric subtask IDs (instead of grouped labels like `0a`, `1b`).
> Outcome: Renumbered Task 8.0A Phase 3 subtasks to a continuous sequence `8.0A.1` through `8.0A.12` for clearer tracking.

### 23:25 - Node Tooling Reminder Locked for 8.0A
> User reiterated: use `nvm use v22.17.0` before Node/npm commands and store for future runs.
> Outcome: Continued Phase 3 using Node `v22.17.0` in every frontend verification command.

### 23:40 - Task 8.0A.4 Completed (Clerk route protection)
> User asked to continue and complete remaining 8.0A subtasks.
> Outcome: Implemented Clerk middleware protection for `/app/*` and `/api/bff/*`, added Clerk provider + sign-in route, verified with `cd frontend && npm run lint`, and checked off subtask `8.0A.4` in the task plan.  
> Note: npm registry remains unreachable in Codex environment (`ENOTFOUND registry.npmjs.org`), so package installation must be run locally.

### 23:55 - Task 8.0A.5 Completed (BFF adapter core + invariants)
> User asked to continue Phase 3 execution end-to-end.
> Outcome: Implemented `frontend/src/lib/bff/*` with server-only env access, typed Result/API error parsing, canonical payload normalization + payload hashing helpers, request signing over exact bytes, and adapter functions (`listCalls`, `listNodes`, `createReview`, `getReview`). Added `frontend/scripts/bff-invariant-check.mjs` and verified via `cd frontend && npm run check:bff && npm run lint`.

### 00:10 - Task 8.0A.6 Completed (BFF route handlers)
> User asked to complete remaining 8.0A implementation subtasks.
> Outcome: Added authenticated Next route handlers under `frontend/src/app/api/bff/*` for calls, nodes, review create, and review detail. Handlers now require Clerk user context, forward requests only through the adapter, and preserve canonical error response shape. Verified with `cd frontend && npm run lint`.

### 00:20 - Task 8.0A.7 Completed (SEO privacy guardrails)
> User asked to continue implementation with subtask-level verification.
> Outcome: Added `/app` noindex guardrails using `src/app/robots.ts` and `next.config.ts` headers, plus `frontend/scripts/check-seo-guardrails.mjs` and `npm run check:seo` for repeatable verification. Verified with `cd frontend && npm run check:seo && npm run lint`.

### 00:35 - Task 8.0A.8 Completed (`/app` submit flow)
> User asked to complete the remaining 8.0A subtasks.
> Outcome: Implemented `/app` submission UI (`frontend/src/app/app/page.tsx`) with call/node selectors, snippet limits, idempotent attempt reuse via `sessionStorage`, submit in-flight lock, 40s slow-request hint, and redirect to `/app/reviews/[review_id]` on success. Added client attempt helper (`frontend/src/lib/review-attempt.ts`). Verified with `cd frontend && npm run lint`.

### 00:55 - Task 8.0A.9 Completed (results page + retry/error mapping)
> User asked to continue through all remaining subtasks.
> Outcome: Added `/app/reviews/[reviewId]` page with deep-link loading, completed/failed/pending state rendering, masked not-found handling, and error-code-first messaging (`UNAUTHORIZED`, `QUOTA_EXCEEDED`, `REVIEWS_DISABLED`, validation variants). Implemented FAILED retry path that reuses saved draft with a new idempotency key. Verified with `cd frontend && npm run lint`.

### 01:15 - Tasks 8.0A.10 + 8.0A.11 Completed (landing + blog/MDX)
> User asked to complete the remainder of Task 8.0A.
> Outcome: Replaced the default homepage with an MVP marketing landing page (`/`) and CTA to `/app`; added `/blog` index and one article route in MDX (`/blog/writing-better-grant-snippets`). Enabled MDX page extensions in Next config and added MDX component mapping. Verified with `cd frontend && npm run lint`.

### 01:30 - Task 8.0A.12 Verification + Walkthrough Sync
> User asked to complete the rest of Task 8.0A.
> Outcome: Ran local verification scripts (`npm run check:bff`, `npm run check:seo`, `npm run lint`), created walkthrough `knowledge_base/walkthroughs/walkthrough_task_8.0A_frontend_ui.md`, and updated task/index status. Remaining gap is manual end-to-end `/app` happy-path verification in a local environment with full npm package installation.

### 01:45 - Verify Prereqs Retried (Sandbox Blockers)
> User asked to continue the remaining pending tasks now that `node` is available in the login shell.
> Outcome: `node -v` and `npm -v` work in `zsh -lc`. Attempted `cd frontend && npm install` with project-local npm cache/logs, but registry resolution still fails (`ENOTFOUND registry.npmjs.org`). Attempted backend smoke via `uv run`, but backend deps are not installed in this sandbox (`ModuleNotFoundError: fastapi`). Manual UI happy-path verify remains a local-machine step.

### 01:55 - Gitignore Pre-Commit Rule Recorded
> User requested an always-on rule: before any commit, check `.gitignore` behavior and update it when necessary using best practices.
> Outcome: Added an `AGENTS.md` rule to run `git status --ignored --short` before committing and prefer narrow ignore/unignore rules over force-adding files.

### 02:05 - Clerk UX Decisions Locked (8.0A)
> User selected MVP options:
> 1) Dedicated `/sign-in` route only (no global header auth buttons).
> 2) Marketing + blog accessible while signed out; only `/app/*` and `/api/bff/*` are protected.
> Outcome: Treat these as locked UX constraints for remaining `8.0A.12` manual verification and any follow-on UI polish.

### 02:10 - Repo-Specific Clerk LLM Prompt Template Added
> User asked to use the corrected Clerk prompt for this repo and proceed.
> Outcome: Added `knowledge_base/logs/prompt_template_clerk_nextjs_app_router.md` as the canonical reusable prompt template for Clerk + Next.js (App Router), aligned to this repo's `frontend/` layout and MVP UX constraints.

### 02:20 - Local Dev Fixes Identified (Clerk middleware + MDX loader)
> User ran `npm run dev` and hit two runtime errors:
> 1) Clerk complained middleware was misplaced and required `./src/middleware.ts`.
> 2) Next MDX compilation failed due to missing `@mdx-js/loader`.
> Outcome: Updated code to place Clerk middleware at `frontend/src/middleware.ts` and added `@mdx-js/loader` to `frontend/package.json`. Dependency install must be run in a network-enabled environment.

### 02:30 - Next Proxy Convention Applied (8.0A)
> User saw Next dev warning: the `middleware` file convention is deprecated and to use `proxy` instead.
> Outcome: Migrated from `frontend/src/middleware.ts` to `frontend/src/proxy.ts` and updated the repo-specific Clerk prompt template accordingly.

### 02:40 - Local Dev Debug Notes (Auth Signature Failure)
> User clicked “Generate Review” and saw: “Authentication signature verification failed.”
> Likely cause: backend `BFF_SHARED_SECRET` not set or does not match `frontend/.env.local` `BFF_SHARED_SECRET` (backend does not auto-load `.env` for uvicorn entrypoint).
> Next step: restart backend with explicit env vars and retry the submit flow.
