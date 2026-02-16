# Q&A History

## 2026-02-06

### Q: Hierarchy structure for proposal nodes?
**A**: Use a generic `ProposalNode` table with `parent_id` recursive relationship for arbitrary depth.

### Q: MVP persistence model?
**A**: Anonymous sessions. User record created per session with `is_anonymous=true`, cascade-deleted after TTL (24h).

### Q: Are evaluation criteria shared across calls?
**A**: No. Strictly per-call in MVP. Each `EvaluationElement` belongs to one `FundingCall`.

### Q: Should we store full prompt/model state?
**A**: Not for MVP. Focus on linking ReviewCards to NodeExpectation IDs for traceability.

### Q: ReviewCard links to EvaluationElement or NodeExpectation?
**A**: NodeExpectation. Provides full context (strength, intent, guidance_note).

### Q: Two guidance fields - what's the difference?
**A**: 
- `ProposalNode.guidance_text`: What the applicant should write
- `NodeExpectation.guidance_note`: What the reviewer should look for

### Q: What if a node has zero NodeExpectations?
**A**: Reject with error: "No evaluation criteria defined for this section." (AD 2.1)

### Q: Tech stack for backend?
**A**: SQLModel (ORM), UV (package manager), FastAPI (API framework for Stage 4+).

## 2026-02-07

### Q: How to support UI "traffic light" indicators?
**A**: Added a typed `rating` field (`ReviewRating` Enum) to `ReviewCard`. This allows the UI to render findings based on severity (Critical, Warning, etc.) without string parsing. (AD 4.1)

### Q: How to handle async AI latency in the UI?
**A**: Added `Review.status` (Pending/Completed/Failed). The UI can poll this status before fetching results. (AD 4.2)

### Q: Does the system provide an overall verdict?
**A**: Yes. Added `Review.overall_summary` and `Review.overall_rating` (calculated as the highest severity among individual findings). (AD 4.2 & 4.3)

### Q: "In SQLModel, the table name is plural while the class name is singular. Is this correct?"
**A:** Yes, this is the industry standard convention for ORMs.
- **Class (`FundingAgency`)**: Represents a *single object* (row) in memory.
- **Table (`funding_agencies`)**: Represents a *collection* (set) of records in the database.
Using plural for classes (`FundingAgencies`) would be confusing as the object instance is singular.

## 2026-02-08

### Q: What does it mean by adding `!` prefix in `.gitignore` files?
**A:** `!` negates a previous ignore rule (“un-ignores” a path). Git evaluates rules top-to-bottom; a later `!pattern` can re-include files/dirs ignored earlier. If a parent dir is ignored, you must also unignore the parent (and sometimes `/**`) so Git will descend into it.

### Q: Clarify phase terminology used in artifacts and commits.
**A:** Standardized pipeline naming:
- **Phase 0** = Brainstorming
- **Phase 1** = PRD creation
- **Phase 2** = Task breakdown creation
- **Phase 3** = Task implementation and verification

### Q: Where should process rules be stored for Codex work in this repo?
**A:** Use `AGENTS.md` as the primary source for Codex workflow instructions in this project.

### Q: Should Phase 3 commits happen after each subtask (e.g., 7.1, 7.2)?
**A:** Yes. During Phase 3, commit after each completed subtask with a short message that includes the subtask ID.

### Q: How are we going to approach building the rest of the app?
**A:** API-first with a minimal FastAPI surface first, then UI. Next major slice is **Task 7.0 (FastAPI MVP)**: add discovery endpoints (calls + nodes) and a `POST /reviews` endpoint that wraps the existing `ReviewerService`, followed by tests and then a thin frontend.

### Q: What is a PR (Pull Request) and why push to a remote?
**A:** A PR is a “proposed merge” of a branch into `main` on a remote host (e.g., GitHub). Pushing uploads your local branch/commits to the remote so the PR can exist there. PRs add review, CI checks, traceability, collaboration, and off-machine backup; they are optional for local-only work.

### Q: Can I run the project locally without merging a feature branch into `main`?
**A:** Yes. You run whatever code is currently checked out. If you’re on a feature branch (e.g., `task-7.0-fastapi-mvp`), you can run/test that branch without merging it into `main`. Switching branches changes which code you run.

### Q: Before starting Task 8.0, what’s the app goal, what’s done, and what’s next?
**A:** Goal: help researchers improve grant proposals by generating rubric-grounded feedback (“review cards”) on pasted snippets, based on ingested funding-call rubrics and proposal structure. Done through Task 7.0: SQLModel domain + ingestion (YAML → DB), reviewer service with OpenAI + stub mode, and a minimal FastAPI API (`/calls`, `/calls/{call_id}/nodes`, `POST /reviews`, `GET /reviews/{review_id}`) with canonical errors and tests. Next: define and implement a thin frontend UI that consumes these endpoints (call + section selection, snippet submission, results view), then do end-to-end verification in stub mode and optional real-LLM mode.

### Q: What hosting/auth/DB choices fit the v1 architecture?
**A:** Picked v1 direction: Next.js (SEO + app) hosted on Vercel with Clerk auth; FastAPI hosted separately (BFF calls server-to-server); production DB on Render managed Postgres. Use BFF to avoid cross-origin auth complexity, and implement quotas first to control LLM spend.

## 2026-02-12

### Q: Should we revise the Task 8.0C Phase 3 plan before continuing implementation?
**A:** Yes. For MVP-fast shipping, first tighten the plan (without rewriting completed subtasks), then execute in strict order: provider/env wiring, readiness-failure hardening (`503` semantics), deploy Stage 1 in `stub`, then one Stage 2 real-LLM verification.

## 2026-02-14

### Q: What is the minimal PeerLens MVP page set?
**A:** Chosen MVP route set is “6 pages”:
- `/` (PeerLens landing) with a static demo switcher (no backend calls)
- `/sign-in` (Clerk)
- `/app` (single-page submit wizard)
- `/app/reviews/[review_id]` (results)
- `/app/reviews` (recent review links stored locally on this device only)
- `/blog` (optional SEO surface; keep minimal)

### Q: Should the landing page allow running a real review while signed out?
**A:** No. The signed-out landing demo is pre-generated/static and does not call `POST /reviews`. Real reviews require login and go through the `/app` flow.

### Q: What is the MVP data retention promise for proposal snippets?
**A:** “Retained until the user deletes them”, with self-serve deletion in the UI that hard-deletes the review, cards, and associated snippet text.

### Q: Should deleting a review refund quota or allow rerun from results?
**A:** No quota refund, and deletion ends the results flow (user returns to `/app` to start a new submission).

### Q: Do we need a Privacy page in MVP, and how should “no training” + retention be stated?
**A:** Yes. MVP includes a minimal `/privacy` page stating:
- PeerLens does not use proposal snippets to train its models.
- Snippets are retained until the user deletes them (self-serve deletion).
- Minimal operational logs/backups may be retained for up to 30 days.

### Q: What should the landing page say about demos, funders, and privacy?
**A:** For MVP:
- Remove “Watch Demo” (single primary CTA).
- Use text-only “Supported calls” (no funder logos).
- Footer includes `Privacy` only (no `Terms` route implied).
- Keep privacy language minimal on landing and link to `/privacy` for specifics.

### Q: How should the landing demo express “both” (fix + rewrite), and what’s the locked copy?
**A:** Use micro-rewrite examples *inside* the suggested fix on some cards (not a separate before/after block). Keep the landing promise “Export your review”, and label the ERC tab “ERC Starting”.

### Q: Do Phase 0.1 decisions get written into `docs/workflow/phase-0-1-brainstorm.md`?
**A:** No. `docs/workflow/*` files are workflow instructions and should not be edited during execution; decisions belong in the WF artifacts (e.g., `docs/brainstorms/brainstorm-WF-0009-peerlens-landing-page.md`) and the registry in `docs/index.md`.

### Q: Can we change the Phase 0.1 facilitation to ask 5 questions at a time?
**A:** Yes (when explicitly requested). Updated `docs/workflow/phase-0-1-brainstorm.md` to ask 5 questions in a single batch per section and collect answers in one reply.

## 2026-02-15

### Q: If we choose Task 8.1 now, should it be done on the active WF-0010 branch or a separate branch?
**A:** Use a separate branch from `main` (e.g., `task/8.1-lint-baseline-cleanup`) to keep WF phase boundaries clean and avoid mixing broad backend lint churn into WF-0010 landing-refresh work.

### Q: What rule should we enforce before pushing a branch to remote?
**A:** Always update `docs/` with all relevant branch work before pushing (including status/index, decisions, Q&A, prompt history, and workflow artifacts where applicable).

### Q: During workflow runner output, can we require explicit proof that Part B reviewed Part A output and Part C applied Part B feedback?
**A:** Yes. Added required traceability-statement rules to `docs/workflow/phase-1-run-spec.md`, `docs/workflow/phase-2-run-prd.md`, and `docs/workflow/phase-3-run-task.md`, including path/version/commit references and explicit Part B findings → Part C edit mapping.

### Q: What exact landing copy should we use for supported funding calls and FAQ usage guidance?
**A:** Lock copy to:
- `Supported funding calls: NL (NWO, ZonMw), EU/Horizon-Europe (ERC, MSCA)`
- FAQ question: `How should I use PeerLens?`
- FAQ answer: `Select the funding call, then a proposal application's section heading, then paste one draft section at a time (for example, methodology, impact, or work plan) so the feedback stays specific and actionable.`

### Q: Which serif/sans pairing should we use for an elegant, gentle academic tone without heaviness?
**A:** Use `Lora` (`600`) for primary large/editorial headings and `Inter` (`400`, UI `500–600`) for body and interface text. Keep serif out of forms/inputs/dense UI text and use a lighter heading scale to avoid cramped or thick-looking typography.

### Q: How should “Next 2 actions” be formatted going forward in workflow guidance?
**A:** Before Phase 4 completion, provide only end-to-end runner options (e.g., `phase-1-run-spec`, `phase-2-run-prd`, `phase-3-run-task`) instead of part-level phase files. After Phase 4 completion, replace that section with “Next 2 WF ideas/features” (candidate follow-up workflows) and suggest starting each via Phase 0.0.

## 2026-02-16

### Q: Can we park two follow-up WF ideas for now and where should they go?
**A:** Yes. Park them in `docs/parking_lot.md` under **Parked Items** with date, why, and promote-when trigger. Added:
- Alembic migration baseline (`WF-0012` candidate)
- One-command local DB verification automation (`WF-0013` candidate)

## 2026-02-16

### Q: Can we discard SQLite completely and use only PostgreSQL for local/prod workflow?
**A:** Yes. Locked as Postgres-only runtime: backend now requires `DATABASE_URL` and no longer falls back to SQLite. Updated code (`backend/app/db.py`) and operational docs (`backend/.env.example`, `backend/README.md`, `AGENTS.md`) accordingly.

## 2026-02-16

### Q: Why does README readiness check fail even when `DATABASE_URL` is set in `backend/.env`?
**A:** The one-liner imports `app.db` directly; previously `app.db` did not load `.env` automatically (only `main.py` did). Updated `backend/app/db.py` to load `backend/.env` with `override=False`, so direct CLI imports now pick up `DATABASE_URL` consistently.
