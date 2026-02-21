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

### 18:55 - Local `/app` auth flow hardened (no crash, no manual path guessing)
> User reported repeated local `/app` crashes and requested a hard fix.
> Outcome: Updated `frontend/src/proxy.ts` to (1) redirect unauthenticated `/app/*` requests to local `/sign-in` with `redirect_url`, (2) return a clear JSON error for `/api/bff/*` when Clerk env is missing/placeholder, and (3) avoid depending on hosted Clerk redirect paths for local navigation. Updated `frontend/src/app/sign-in/[[...sign-in]]/page.tsx` to show a clear config-error UI (`auth_config_error=1`) and enforce safe local post-sign-in redirects.

### 20:17 - Phase 0 Brainstorming Started (8.0C Deployment Wiring)
> User asked to start Task 8.0C at Phase 0 (deployment wiring: Vercel/Clerk/BFF + FastAPI + managed Postgres + secrets/domains/CORS/health checks).
> Outcome: Created `knowledge_base/logs/brainstorming-8.0C-deployment-wiring.md` with critical gaps/risks, clarification questions, tentative MVP decisions, env mapping, explicit local-vs-deploy verification split, non-scope backlog, and Phase 1 PRD readiness criteria.

### 20:25 - 8.0C Brainstorming Revised (MVP decisions locked)
> User requested a senior critical review and then asked to revise the brainstorming doc by deciding the MVP-fast defaults.
> Outcome: Revised `knowledge_base/logs/brainstorming-8.0C-deployment-wiring.md` to (1) elevate Vercel timeout alignment as a first-class risk, (2) lock MVP defaults (Vercel+Render, prod-only, backend stays on provider URL, no Alembic yet, manual seed runbook, public `/docs`, CORS disabled), and (3) add a recommended execution sequencing to keep “deployment wiring” shippable.

### 20:35 - Phase 1 PRD Started (8.0C Deployment Wiring)
> User approved moving from Phase 0 to Phase 1.
> Outcome: Created `tasks/prd-8.0C-deployment-wiring.md` and linked Task 8.0C in `tasks/index.md`.

### 10:44 - Phase 2 Plan Created (8.0C Deployment Wiring)
> User requested revisions based on senior critique and asked to update the brainstorming/PRD/task artifacts.
> Outcome: Revised `knowledge_base/logs/brainstorming-8.0C-deployment-wiring.md` and `tasks/prd-8.0C-deployment-wiring.md` with concrete timeout defaults and staged rollout, and created `tasks/task-8.0C-deployment-wiring.md` (Phase 2 plan). Updated `tasks/index.md` to link the task plan.

### 10:59 - 8.0C Phase 2 Plan Tightened (Render + Bootstrap Prereqs)
> User requested a senior review of the 8.0C plan and asked to revise the task file for MVP-fast shipping.
> Outcome: Updated `tasks/task-8.0C-deployment-wiring.md` to add explicit Render build/start mechanics, tightened Postgres URL/SSL expectations, and corrected bootstrap to include the required active `PromptTemplate` (not just YAML ingest). Updated `tasks/prd-8.0C-deployment-wiring.md` accordingly.

### 11:20 - 8.0C Phase 3 Implementation Started (Backend + Bootstrap + BFF runtime)
> User approved starting Phase 3 with AGENTS/lessons enforcement.
> Outcome: Implemented `DATABASE_URL` normalization + `/health/db` readiness in backend, added idempotent bootstrap script `backend/scripts/ensure_prompt_template.py`, updated backend runbook for production bootstrap, and set `runtime/maxDuration` on `frontend/src/app/api/bff/reviews/route.ts`. Added walkthrough `knowledge_base/walkthroughs/walkthrough_task_8.0C_deployment_wiring.md` with verification results and explicit deploy-only pending items.

### 12:04 - 8.0C Task Plan Revised Before Next Phase 3 Round
> User asked to revise the task plan first using critical feedback, keep implemented subtasks intact, and add concrete next-step tracking for MVP-fast shipping.
> Outcome: Updated `tasks/task-8.0C-deployment-wiring.md` to add next-round execution decisions and new subtasks: `8.0C.6` (readiness-failure hardening to explicit `503`), `8.0C.7` (deploy Stage 1 stub execution), and `8.0C.8` (deploy Stage 2 one-shot openai verification). Logged new architecture decisions and deferred non-scope hardening items.

### 12:13 - 8.0C.6 Implemented (Readiness failure semantics)
> User requested implementation of subtask `8.0C.6`.
> Outcome: Updated FastAPI readiness behavior so `GET /health/db` returns canonical `503` (`DB_UNAVAILABLE`) when DB checks fail, while keeping `GET /health` as liveness. Added failure-path API tests and updated backend docs + task/walkthrough artifacts with verification results.

### 16:20 - 8.0C Provider Change Locked (Neon DB)
> User chose Neon for managed Postgres (Render stays for FastAPI; Vercel for Next.js; Clerk for auth) and asked to lock this change in artifacts before pushing/deploying.
> Outcome: Updated `knowledge_base/logs/decisions.md`, `tasks/prd-8.0C-deployment-wiring.md`, and `tasks/task-8.0C-deployment-wiring.md` to replace Render Postgres with Neon Postgres without modifying completed implementation subtasks.

### 16:40 - 8.0C Deploy Wiring Verified (Stub)
> User completed provider wiring and deploy verification in `LLM_MODE=stub`.
> Outcome: Render FastAPI (`/health`, `/health/db`) connects to Neon Postgres (direct URL; avoid pooler + channel binding for MVP stability). Vercel + Clerk gating works and end-to-end submit via `/api/bff/reviews` succeeds with stub findings. Bootstrap was executed from a developer machine against the deployed Neon database because Render free instances do not support shell access.

### 18:07 - 8.0C Stage 1 Security Check Confirmed
> User verified that direct, unsigned access to protected backend endpoints fails.
> Outcome: `GET /reviews/{review_id}` without signature headers returns `401 UNAUTHORIZED`, confirming the BFF boundary is enforced in production.

### 18:22 - 8.0C Stage 2 OpenAI Verification Completed
> User approved one paid OpenAI verification run and provided the results.
> Outcome: Switched Render backend to `LLM_MODE=openai`, set `OPENAI_API_KEY`, and completed one real end-to-end review via Vercel BFF. Observed Vercel wait time was ~11.41s and the review completed successfully (`review_id=b3a9df0c-7c78-4a90-8ec8-51cf3fd5ce5e`, `status=COMPLETED`).

### 18:40 - 8.0C Operational Mode Set (Stub Until Launch)
> User chose to revert production default to `LLM_MODE=stub` until launch day after successful Stage 2 verification.
> Outcome: Locked the operational decision in `knowledge_base/logs/decisions.md` (AD 8.16) and updated the 8.0C walkthrough to reflect stub-default intent and the manual Render env flip requirement.

### 18:46 - 8.0C Stub Rollback Verified (UI)
> User confirmed post-redeploy UI submissions return “Stub feedback…”.
> Outcome: Updated task/walkthrough artifacts to mark the stub-default rollback as verified after Stage 2.

### 09:32 - Codex Instruction: “Check Skills First”
> User requested enforcing a habit to check for existing agent skills before starting a new type of task (e.g., “Do I have a skill for writing a migration?”).
> Outcome: Updated `.github/copilot-instructions.md` to instruct agents to check `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the relevant `SKILL.md` before proceeding.

### 09:33 - SSOT Update: “Check Skills First” in `AGENTS.md`
> User asked whether the “Check Skills First” habit should live in `AGENTS.md` since it is the SSOT.
> Outcome: Added “Check skills first” to `AGENTS.md` (Skills section) and kept `.github/copilot-instructions.md` as the enforcement hook for Codex/Copilot.

### 09:37 - Documented “Adapter File” Rationale
> User requested metadata explaining why `.github/copilot-instructions.md` exists, plus a durable record of this decision for use with other agent tools.
> Outcome: Added a “Why this file exists” header to `.github/copilot-instructions.md` and documented the pattern in `docs/reference/README_agent_instructions.md` (with a corresponding decision logged in `docs/logs/decisions.md`).

### 12:47 - Task 8.1 Completed (safe lint baseline)
> User requested Task 8.1 execution on a separate branch with a safety-first approach.
> Outcome: Created branch `task/8.1-lint-baseline-cleanup`, added backend Ruff baseline config in `backend/pyproject.toml` (`E4,E7,E9,F,I,B,UP`) with targeted `scripts/run_review.py:E402` ignore, applied Ruff autofix + one manual `B007` fix, and verified `cd backend && uv run ruff check .` plus `cd backend && uv run pytest -q` (`24 passed`).

### 12:55 - Task 8.1 Critical Review + Remediation Pass
> User requested another critical review of the active branch and asked to fix any findings.
> Outcome: Performed a severity-ordered review, then remediated findings by (1) resolving decision-log ID collision (`AD 10.4` -> `AD 10.5`), (2) aligning Task 8.1 scope language with delivered work (CI diff-gating deferred to follow-up), and (3) completing explicit `ruff format` verification. Re-verified with `cd backend && uv run ruff format . && uv run ruff check . && uv run pytest -q` (`24 passed`).

### 13:00 - Task 8.1 Merged to Main via GitHub PR
> User requested push + PR + merge for the completed branch.
> Outcome: Pushed `task/8.1-lint-baseline-cleanup`, opened PR `#11`, merged to `main` on GitHub, and confirmed local `main` fast-forwarded to merge commit `aad96f6`; remote task branch deleted.

### 13:03 - New Pre-Push Documentation Rule Added
> User requested a new memory rule: always update docs before pushing a branch to remote.
> Outcome: Updated `AGENTS.md` Always rules to require `docs/` updates before any remote push, and logged the clarification in `docs/logs/qa_history.md`.

### 13:34 - WF-0010 Phase 1 Runner Completed (Spec)
> User asked to run Phase 1 end-to-end for WF-0010 using the workflow runner and print Part A/B/C.
> Outcome: Finalized and committed the WF-0010 brainstorm (Phase 0.1 gate), generated spec v0.1, ran strict review (non-blocking issues only), revised spec to v0.2 and marked it `Ready for PRD`, then updated `docs/index.md` WF-0010 row to include the spec link and `Phase 1` status.

### 13:42 - Phase 1 Runner Traceability Rule Added
> User requested clearer confirmation that Part B reviews Part A output and Part C uses Part B feedback.
> Outcome: Updated `docs/workflow/phase-1-run-spec.md` to require a final traceability statement with artifact references (path/version/commit) and explicit Part B findings → Part C edits mapping.

### 13:44 - Phase 2/3 Runner Traceability Rules Added
> User requested the same traceability requirement for Phase 2 and Phase 3 runners.
> Outcome: Updated `docs/workflow/phase-2-run-prd.md` and `docs/workflow/phase-3-run-task.md` to require reviewed-artifact output in Part B, explicit “Applied feedback from Part B” output in Part C, and a final required traceability statement with concrete references.

### 13:51 - WF-0010 Phase 2 Runner Completed (PRD)
> User asked to run Phase 2 end-to-end for WF-0010 using the workflow runner and print Part A/B/C.
> Outcome: Generated PRD v0.1 from the committed spec and updated WF-0010 to Phase 2, ran a no-edit risk audit (non-blocking findings), revised PRD to v0.2 and marked `Ready for Tasks`, logged WF-0010 PRD guardrail decisions in `docs/logs/decisions.md` (AD 10.5), and updated `docs/index.md` status to `Phase 2 (Ready)`.

### 14:01 - WF-0010 Phase 3 Runner Completed (Tasks)
> User asked to run Phase 3 end-to-end for WF-0010 using the workflow runner and print Part A/B/C.
> Outcome: Generated tasks v0.1 from the committed PRD and updated WF-0010 to Phase 3, ran a no-edit task review (non-blocking findings), revised tasks to v0.2 and marked `Ready for Implementation`, and updated `docs/index.md` status to `Phase 3 (Ready)`.

### 14:01 - WF-0010 Phase 4 Implementation Completed (Tasks 1-7)
> User requested sequential task execution with per-task commits, walkthrough update, and final `Done` status in `docs/index.md`.
> Outcome: Implemented all WF-0010 tasks in order with per-task commits (brand guideline alignment, token/type updates, layout rhythm improvements, copy refresh, demo/FAQ shell harmonization, a11y/mobile hardening), ran required frontend verification bundle (`lint`, `check:seo`, `next build --webpack`), updated walkthrough `docs/walkthroughs/walkthrough-WF-0010-peerlens-landing-design-refresh.md`, and set WF-0010 status to `Done` in `docs/index.md`.

### 15:28 - WF-0010 Manual Mobile/Keyboard Polish Pass
> User requested a quick local manual pass on `/` (keyboard-only + mobile widths) with one follow-up tiny polish commit if needed.
> Outcome: Re-validated via local lint and mobile screenshots, then applied small-screen polish in `frontend/src/app/page.tsx` and `frontend/src/app/_components/landing/demo-tabs.tsx` (header/nav small-screen fit, hero spacing, long-text wrapping safety) and updated the WF-0010 walkthrough with the follow-up verification notes.

### 15:40 - WF-0010 Copy Lock Update (Funding Line + FAQ Usage)
> User requested copy changes and source-artifact synchronization.
> Outcome: Updated landing funding line to `Supported funding calls: NL (NWO, ZonMw), EU/Horizon-Europe (ERC, MSCA)` in `frontend/src/app/page.tsx`; updated FAQ prompt/answer in `frontend/src/app/_components/landing/faq-accordion.tsx`; synced WF-0010 source artifacts (`brainstorm`, `spec`, `prd`, `walkthrough`) and logs (`qa_history`, `prompt_history`) with the new locked wording.

### 15:49 - WF-0010 Typography Architecture Update (Playfair + Inter)
> User requested frontend updates using `brand_guidelines.md` and `brand_typography_system.md`, plus a logged decision.
> Outcome: Updated font loading in `frontend/src/app/layout.tsx` to load Inter + Playfair Display via `next/font/google`, applied heading/body typography architecture and scale in `frontend/src/app/globals.css`, and recorded AD 10.6 in `docs/logs/decisions.md` to lock the serif-heading + sans-body system.

### 16:02 - Typography Decision Revision (Merriweather + Inter)
> User requested replacing Playfair Display with Merriweather and updating docs first (including size choices that pair well with Inter).
> Outcome: Updated `docs/reference/brand_typography_system.md`, `docs/reference/brand_guidelines.md`, and AD 10.6 in `docs/logs/decisions.md` to lock `Merriweather` for major headings, `Inter` for body/UI, and a tuned heading scale for readability with dense research content.

### 16:08 - Frontend Typography Implementation (Merriweather)
> User approved proceeding with frontend updates after docs-first changes.
> Outcome: Replaced `Playfair_Display` with `Merriweather` in `frontend/src/app/layout.tsx`, updated heading token mapping and scale in `frontend/src/app/globals.css` to match the revised typography docs, and verified with `cd frontend && npm run -s lint`.

### 16:20 - Typography Rebaseline (Lora + Inter)
> User requested another serif adjustment for a lighter, elegant academic tone (less heavy than previous choices).
> Outcome: Updated `docs/reference/brand_typography_system.md`, `docs/reference/brand_guidelines.md`, and AD 10.6 in `docs/logs/decisions.md` to lock `Lora` (`600`) for primary/editorial headings with Inter for body/UI; implemented frontend swap in `frontend/src/app/layout.tsx` and `frontend/src/app/globals.css`, kept dense UI headings on Inter, and verified with `cd frontend && npm run -s lint`.

### 16:36 - Landing “How It Works” Static Redesign + Global Type Scale Increase
> User requested a static, card-based “How it works” section (similar to provided visual direction) and a larger default text scale across the site with improved spacing/readability.
> Outcome: Redesigned `How it works` in `frontend/src/app/page.tsx` into a static three-card rail with a center highlighted card and subtle bottom accent bar, increased vertical section spacing, raised global default font size and line-height in `frontend/src/app/globals.css`, and relaxed heading letter-spacing slightly for a cleaner, less cramped academic reading feel. Verified with `cd frontend && npm run -s lint`.

### 16:48 - How-It-Works Copy Refinement
> User requested clearer proposal-focused wording for all three step bodies.
> Outcome: Updated step text in `frontend/src/app/page.tsx` to emphasize proposal draft text input and criteria-aligned revision feedback; verified with `cd frontend && npm run -s lint`.

### 16:55 - Supported Calls Visibility Redesign (NL/EU Grouped Cards)
> User requested improving the supported-calls design so NL and EU groups (and their child programs) are easier to scan.
> Outcome: Replaced the single-line supported-calls block in `frontend/src/app/page.tsx` with a static two-card grouped layout (`NL` and `EU/Horizon-Europe`) and pill-style child programs (`NWO`, `ZonMw`, `ERC`, `MSCA`), while preserving the original one-line copy beneath for continuity. Verified with `cd frontend && npm run -s lint`.

### 23:03 - Memory Rule Added for “Next 2” Guidance Format
> User requested a durable response-format rule: use end-to-end phase runners (not part files) for “Next 2 actions,” and after Phase 4 completion switch to “Next 2 WF ideas/features.”
> Outcome: Updated `AGENTS.md` Always rules and logged the clarification in `docs/logs/qa_history.md` + `docs/logs/prompt_history.md` for zero-latency memory.

### 23:10 - Parked Follow-up WF Ideas in Backlog
> User asked to park two follow-up ideas for later and commit them.
> Outcome: Added two dated parked items to `docs/parking_lot.md` (WF-0012 Alembic baseline, WF-0013 local DB verification automation) and logged the clarification in Q&A.

### 23:20 - Postgres-only Runtime Policy Applied
> User requested removing SQLite completely to avoid dual-DB confusion.
> Outcome: Removed SQLite fallback from backend DB resolution (`DATABASE_URL` required), aligned backend/env/agent docs to Postgres-only operation, and recorded decision AD 11.4.

### 23:28 - Fixed README Readiness Check Env Loading
> User reported `DATABASE_URL is required` while running the README readiness command despite setting `backend/.env`.
> Outcome: Updated `backend/app/db.py` to load `backend/.env` (same behavior as `main.py`) so direct `uv run python -c ...` imports resolve `DATABASE_URL` consistently.

## 2026-02-16

### 09:10 - WF-0012 Restart and Phase 0→1 Execution Request
> User requested restarting WF-0012 from Phase 0.0 using workflow runners and keeping MVP-fast scope for a Postgres-only Alembic migration baseline.
> Outcome: Created WF-0012 branch/artifacts, completed Phase 0.1 brainstorm, and ran Phase 1 end-to-end with spec generation/review/revision for baseline init, first migration, docs/runbook updates, and verification commands.

### 09:20 - Workflow Process Correction (Runner Commit Boundaries + Interactive Brainstorm)
> User asked why brainstorming was not interactive and requested explicit commit discipline after each runner part and each phase.
> Outcome: Added an always-on AGENTS rule for runner part-level commits (Part A/Part C, plus Part B when edits exist), clarified no-commit behavior for no-edit Part B phases, and logged the interactive brainstorm expectation in Q&A history.

### 09:35 - WF-0012 Phase 2 Runner (PRD) Execution
> User selected next action `1` to run Phase 2 runner for WF-0012.
> Outcome: Generated PRD v0.1 from spec, ran no-edit risk audit, revised to PRD v0.2 (`Ready for Tasks`), updated WF-0012 status to `Phase 2 (Ready)`, and logged Alembic baseline decisions (AD 12.1, AD 12.2).

### 09:50 - WF-0012 Phase 3 Runner (Tasks) Execution
> User selected next action `1` to run Phase 3 runner for WF-0012.
> Outcome: Generated task breakdown v0.1 from PRD, ran no-edit task review, revised to tasks v0.2 (`Ready for Implementation`), and updated WF-0012 status to `Phase 3 (Ready)`.

### 10:05 - WF-0012 Phase 4.1 Implementation Completed
> User selected next action `1` to run Phase 4.1 implementation for WF-0012.
> Outcome: Implemented all six tasks with per-task commits: Alembic dependency/scaffold, Postgres metadata wiring, baseline migration generation, reversible lifecycle validation, backend migration runbook updates, and walkthrough/index/decision sync. WF-0012 status set to `Done`.

### 10:08 - Reporting Provenance Rule Added
> User requested that completion summaries always include what files/skills/instructions were considered for each completed phase/part/action.
> Outcome: Added an always-on AGENTS rule and logged corresponding Q&A clarification.

### 10:15 - Commit Message Slug Rule Added
> User requested a new rule that WF commit messages include the relevant slug.
> Outcome: Updated AGENTS + Q&A logs to enforce commit messages that include both WF ID and slug for clearer traceability.

### 10:20 - Commit History Handling Decision for Slug Rule
> User selected option `2` for commit-history handling.
> Outcome: Confirmed no retroactive history rewrite; enforce slug-inclusive WF commit messages from this point forward.

### 10:30 - Post-Push Docs Confirmation Rule Added
> User requested a reminder behavior for push operations.
> Outcome: Added an always-on rule to explicitly confirm docs/WF artifact update status after each successful remote push.

### 19:04 - MVP Readiness Audit + Parking Lot Restructuring
> User requested a project status overview, then a deep audit of 10 must-do items for MVP readiness.
> After two rounds of review (including cross-referencing with another agent's findings), produced a merged 15-item priority list across P0/P1/P2 tiers.
> User asked to formalize this into `docs/parking_lot.md` with priority tables, a code phrase (`park this`), and promotion mechanics.
> Outcome: Rewrote `docs/parking_lot.md` (v0.2) with P0 (5 items), P1 (6 items), P2 (4 items) tables, "Promoted Items" section, and guidelines. Added two always-on rules in `AGENTS.md` for parking lot hygiene and promotion workflow.
> Code phrases: **`park this`** to add a new item; **`pick P[x] #[n]`** (e.g., `pick P0 #1`) to promote a parked item into a new WF.

### 19:52 - Code Phrases System Created
> User requested shortcut code phrases for frequent actions (parking, picking, remembering rules, status, shipping, etc.).
> Outcome: Created `docs/reference/code_phrases.md` with 14 phrases in 4 categories (Backlog, Workflow, Knowledge, Session). Updated `AGENTS.md` to reference the code phrases file. Cross-linked from `docs/parking_lot.md`.

### 2026-02-16T20:05 — Pick P0 #1
- **User**: "Pick P0 #1" (app shell + sign-out)
- **Agent**: Promoted to WF-0013, initially skipped WF phases, corrected after user feedback.
- **Lessons logged**: L21 (never skip phase gates), L22 (small-scope self-directed).
- **Result**: Full WF pipeline (Phase 0-4) executed self-directed. Implementation committed on `wf/WF-0013-app-shell-signout`.

## 2026-02-17

### 09:40 - WF-0016 Scorecard Critical Review + Hardening
> User requested a targeted implementation review of WF-0016 (Scorecard UX) across frontend components and backend/BFF criterion-description flow.
> Outcome: Review identified edge-case hardening items and they were implemented:
> - `ScoreBadge` now uses an explicit neutral fallback (`Unrated`) for unexpected rating values.
> - Summary container rendering is now conditional on non-empty `overall_summary` to avoid empty spacing.
> - API test now asserts concrete `criterion_description` content from join mapping.
> Verification run: `cd backend && uv run pytest tests/test_api.py -k create_review_success_with_stub_mode`, `cd frontend && npm run lint`, `uvx pre-commit run --all-files`.

### 09:50 - Wrap Up Requested
> User requested `wrap up` via code phrase.
> Outcome: Updated WF-0016 docs (`walkthrough` + `prompt_history`), committed wrap-up docs updates on `wf/WF-0016-review-results-ux`, and prepared/pushed branch without merge.

## 2026-02-18

### 10:40 - Code Phrase Clarification: Context vs Kickoff
> User asked whether adding a new context-loading phrase would be redundant and requested constructive guidance.
> Outcome: Introduced distinct semantics for two phrases:
> - `context refresh` for bounded project-state re-grounding before deciding next work.
> - `new chat kickoff` for generating a compact 3-line starter once direction is known.
> Also expanded `docs/reference/code_phrases.md` with a "when to use what" table covering all existing phrases.

### 12:02 - Pick P0 #1 Promoted to WF-0017
> User issued code phrase `pick P0 #1`.
> Outcome: Promoted "Add auto-polling for processing reviews" to `WF-0017`, created baseline workflow artifacts, created branch `wf/WF-0017-auto-polling-processing-reviews`, and updated registry links in `docs/index.md` plus backlog renumbering in `docs/parking_lot.md`.

### 12:03 - WF-0017 Phase 0.1 Brainstorm Completed
> User selected "go with recommendations" for all five-question batches across Sections 1-8 in Phase 0.1.
> Outcome: Completed interactive brainstorm for `WF-0017` with tightened MVP scope, explicit constraints/risks, and non-goals; set brainstorm artifact status to `Draft Complete`.

### 12:04 - WF-0017 Phase 1 Runner Completed (Spec A/B/C)
> User selected `run phase 1`.
> Outcome: Executed Phase 1 runner end-to-end for `WF-0017`: generated spec `v0.1` (Part A), performed no-edit review gate (Part B), applied non-blocking clarifications in revision `v0.2` and marked `Ready for PRD` (Part C), then updated `docs/index.md` status to `Phase 1`.

### 12:05 - WF-0017 Phase 2 Runner Completed (PRD A/B/C)
> User requested: "run phase 2 end-to-end".
> Outcome: Executed Phase 2 runner end-to-end for `WF-0017`: generated PRD `v0.1` (Part A), completed no-edit risk audit (Part B), revised to `v0.2` and marked `Ready for Tasks` with decision logging (Part C), then updated `docs/index.md` to `Phase 2 (Ready)`.

### 12:06 - WF-0017 Phase 3 Runner Completed (Task A/B/C)
> User selected `1` to run Phase 3.
> Outcome: Executed Phase 3 runner end-to-end for `WF-0017`: generated task plan `v0.1` (Part A), performed no-edit task review (Part B), revised to `v0.2` and marked `Ready for Implementation` (Part C), then updated `docs/index.md` to `Phase 3 (Ready)`.

### 12:07 - WF-0017 Phase 4.1 Implementation Completed
> User selected `1` to proceed with implementation.
> Outcome: Implemented Task 1-5 sequentially with per-task commits: status semantic alignment (`PENDING`), bounded polling loop (3s interval, 90s cap), cap fallback UX, transient-error-safe polling behavior, and walkthrough verification docs. Updated `docs/index.md` status for `WF-0017` to `Done`.

### 13:07 - New Code Phrase Added: workflow preflight
> User requested a new phrase to run a critical review of current workflow readiness before starting the next WF, with explicit recommended actions and guidance on whether to start a new chat.
> Outcome: Added `workflow preflight` to `docs/reference/code_phrases.md` and registered it in `AGENTS.md` key phrase list.

### 13:14 - New Code Phrase Added: docs cleanup
> User asked whether a dedicated docs cleanup phrase exists and requested creation with explicit action guidance.
> Outcome: Added `docs cleanup` to `docs/reference/code_phrases.md` with a concrete closure checklist (status alignment, stale-label cleanup, log updates, pre-commit, docs-only commit) and registered it in `AGENTS.md`.

### 13:25 - WF-0018 Promotion + Workflow Routing Fix
> User issued `pick P0 #1` and then flagged that next step after Phase 0.0 should be Phase 0.1 brainstorm.
> Outcome: Promoted parking lot item to `WF-0018` (`harden-submit-flow-ux`) with branch/artifact baseline; then added a new end-to-end Phase 0 runner (`docs/workflow/phase-0-run-start-and-brainstorm.md`) and wired it into workflow action docs/code-phrase references to prevent sequencing mistakes.

### 13:35 - WF-0018 Phase 0 Runner Execution Completed
> User ran `run phase 0` and requested recommendation-driven completion.
> Outcome: Completed Phase 0.1 brainstorm for `WF-0018` with recommended selections across Sections 1-8; finalized brainstorm as `Draft Complete` and committed.

### 13:45 - WF-0018 Phase 1 Runner Completed (Spec A/B/C)
> User ran `run phase 1`.
> Outcome: Generated spec `v0.1`, executed no-edit review gate, applied non-blocking revisions to `v0.2` (`Ready for PRD`), and updated `docs/index.md` to `Phase 1`.

### 13:55 - WF-0018 Phase 2 Runner Completed (PRD A/B/C)
> User ran `run phase 2 end-to-end`.
> Outcome: Generated PRD `v0.1`, executed no-edit risk audit, revised to `v0.2` (`Ready for Tasks`), logged WF-0018 decisions in `docs/logs/decisions.md`, and updated `docs/index.md` to `Phase 2 (Ready)`.

### 14:05 - WF-0018 Phase 3 Runner Completed (Tasks A/B/C)
> User ran `run phase 3 end-to-end`.
> Outcome: Generated tasks `v0.1`, executed no-edit task review, revised to `v0.2` (`Ready for Implementation`), and updated `docs/index.md` to `Phase 3 (Ready)`.

### 14:20 - WF-0018 Phase 4 Implementation Completed
> User ran `run phase 4`.
> Outcome: Implemented Tasks 1-6 sequentially with per-task commits, added route constants and submit-flow hardening changes, updated walkthrough/task status docs, and set `WF-0018` to `Done` in `docs/index.md`.

### 14:30 - WF-0018 Wrap Up + Ship Request
> User requested `wrap up and then ship it`.
> Outcome: Performed final docs sync/cleanup, then executed push + PR + merge flow for `wf/WF-0018-harden-submit-flow-ux`, followed by local `main` sync.

### 16:10 - WF-0019 Kickoff via run-lifecycle-auto
> User requested autonomous lifecycle execution for parking lot `P1 #1` ("Add loading & empty states") using `docs/workflow/run-lifecycle-auto.md` with strict phase routing and docs/log updates.
> Outcome: Started `WF-0019` bootstrap on branch `wf/WF-0019-add-loading-empty-states`; promoted P1 item in `docs/parking_lot.md`, created WF artifacts, and registered `WF-0019` in `docs/index.md`.

### 16:15 - WF-0019 Phase 0.1 Brainstorm Completed (autonomous)
> Context: Executed via `run-lifecycle-auto` for parking lot item P1 #1.
> Outcome: Completed brainstorm sections 1-8 for `WF-0019` with MVP-tight scope (frontend-only loading/empty states), set brainstorm to `Draft Complete`, and prepared Phase 1 input.

### 16:20 - WF-0019 Phase 1 Runner Completed (Spec A/B/C)
> Context: Autonomous execution via `run-lifecycle-auto`.
> Outcome: Generated spec `v0.1`, ran no-edit spec review gate, revised to `v0.2` (`Ready for PRD`), and updated `docs/index.md` WF status to `Phase 1`.

### 16:28 - WF-0019 Phase 2 Runner Completed (PRD A/B/C)
> Context: Autonomous execution via `run-lifecycle-auto`.
> Outcome: Generated PRD `v0.1`, ran no-edit risk audit, revised to `v0.2` (`Ready for Tasks`), logged WF-0019 architectural decisions, and updated `docs/index.md` to `Phase 2 (Ready)`.

### 16:35 - WF-0019 Phase 3 Runner Completed (Tasks A/B/C)
> Context: Autonomous execution via `run-lifecycle-auto`.
> Outcome: Generated tasks `v0.1`, ran no-edit tasks review, revised to `v0.2` (`Ready for Implementation`), and updated `docs/index.md` to `Phase 3 (Ready)`.

### 16:52 - WF-0019 Phase 4 Implementation Completed
> Context: Executed tasks sequentially under `docs/workflow/phase-4-1-implement-tasks.md`.
> Outcome: Completed Task 1-4 with per-task commits; implemented loading skeleton states in `/app`, `/app/reviews`, and `/app/reviews/[reviewId]`, added deterministic no-calls onboarding state, updated walkthrough/task artifacts, and set `WF-0019` status to `Done` in `docs/index.md`.

### 16:23 - WF-0019 Docs Sync + Cleanup + Wrap/Ship Request
> User requested: `update docs`, then `docs cleanup`, then `wrap up`, then `ship it`.
> Outcome: Ran docs status/consistency checks for WF-0019, confirmed registry/backlog alignment, ran ignored-file audit, attempted `pre-commit run --all-files` (command unavailable in environment), and proceeded with wrap-up + shipping flow.

### 16:37 - CI Failure Triage (Run 22145822811)
> User reported a failing GitHub Actions run.
> Outcome: Identified two causes and applied fixes: (1) frontend build crash when Clerk keys are absent by adding Clerkless-safe render fallbacks (`RootLayout`, app shell, sign-in page), and (2) backend pytest DB table-loss across connections by switching CI test DB URL from in-memory SQLite to file-backed SQLite in `.github/workflows/ci.yml`. Verified locally with `frontend npm run build` (no Clerk keys) and `backend pytest tests/test_api.py`.

### 16:49 - New Code Phrase Added: verify workflow
> User asked for a predefined phrase to verify current-workflow outcomes and requested a future-reference rule for composing phrases from existing ones.
> Outcome: Added `verify workflow` to `docs/reference/code_phrases.md` as a composed verification bundle (`status` + `diff` + targeted checks + pass/fail summary), added composition guideline in code-phrases doc, and updated `AGENTS.md` to recognize `verify workflow` + composed-phrase execution rule.

## 2026-02-21

### 07:48 - Pick P1 #5 → WF-0020 Kickoff (NWO Veni 2025 preproposal WF-1)
> User requested `pick P1 #5` to start "NWO Veni 2025 preproposal — WF-1" with a strict scope: fix YAML parse issues, add CallDefinition V2 schema/loader, and support `scripts/ingest_call.py --dry-run` for V2 YAML (no DB schema, no API endpoints, no frontend changes).
> Outcome: Minted `WF-0020`, created baseline WF artifacts, promoted the parking lot item, created branch `wf/WF-0020-nwo-veni-2025-preproposal-wf1`, and prepared to run Phase 0.1 interactive brainstorm.

### 07:55 - WF-0020 Phase 0.1 Brainstorm Completed (recommendations)
> User requested: “go with your recommendations” for the remaining Phase 0.x decisions.
> Outcome: Completed brainstorm sections 1–8 for `WF-0020` with a tight scope: V2 YAML parsing + CallDefinition V2 loader + `scripts/ingest_call.py --dry-run` support (offline validation only), and set brainstorm status to `Draft Complete`.

### 08:05 - WF-0020 Phase 0.1 Revision (grounded in NWO Veni YAML)
> User asked whether Phase 0.0/0.1 considered the actual NWO Veni YAML + design summary; it had not.
> Outcome: Reviewed `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml` + `backend/data/calls/nwo/nwo_veni_2025_preproposal_design_summary.md`, then revised the WF-0020 brainstorm to reflect concrete V2 fields (schema mismatch vs existing V1 loader) while keeping scope unchanged.
