# PeerLens / Grant Reviewer — Project Context Brief

This is the “upload-to-ChatGPT Project” context file: what this repo is, what it’s for, what’s done, and how it fits together.

## TL;DR

Grant Reviewer (PeerLens) helps researchers improve grant proposal *snippets* by generating evaluation-criteria-grounded feedback that is traceable to funding-call expectations. Funding calls are defined as YAML (evaluation criteria + proposal section hierarchy), ingested into Postgres, and used to generate structured “review cards” for a user-selected proposal section.

## Audience & Problem

- **Primary user**: Researchers drafting grant proposals who want early, actionable feedback aligned to a funder’s evaluation criteria.
- **Problem**: Generic writing feedback isn’t funder-specific; applicants need feedback that is grounded in the call’s criteria and the specific section they’re drafting.
- **Value prop**: Paste one section at a time → get feedback mapped to explicit evaluation expectations for that section → export/share.

## Product Goals (current)

- Evaluation-criteria-grounded feedback for a selected call + proposal section.
- Traceability: each feedback card ties back to a specific expectation (node + evaluation element + strength/intent).
- Self-serve UX: submit → view progress → see results → export → delete.
- Safe iteration: cheap local verification via `LLM_MODE=stub`.

## Non-Goals (MVP / current scope)

- No full-proposal end-to-end authoring/review.
- No automatic rewriting as the primary output (focus is feedback).
- No scoring/ranking as a core mechanic (some rating fields exist, but scoring strategy is not the main product).
- No Admin UI for call creation (calls are “definition-as-code” via YAML + CLI ingest).

## Key Concepts / Vocabulary

- **Funding call**: A specific grant program instance (e.g., “ERC-COG-2026”).
- **Proposal node**: A selectable proposal section/subsection in a call (hierarchical).
- **Evaluation criterion**: A high-level evaluation dimension for a call (e.g., Excellence).
- **Evaluation element**: An atomic evaluable concern under a criterion (e.g., Methodology soundness).
- **Node expectation**: The “intelligence layer” mapping a proposal node to an evaluation element with:
  - strength (`MANDATORY/IMPORTANT/OPTIONAL`)
  - intent (`COMPLIANCE/QUALITY/RISK/STRATEGIC_FIT`)
  - reviewer guidance note (“what to look for”)
- **Review**: One run of analysis for a pasted snippet.
- **Review card**: A single feedback unit linked to a specific node expectation.

Canonical domain reference: `docs/reference/domain_model.md`.

## System Overview (high level)

1. **Define a funding call** in YAML (evaluation criteria + proposal structure).
2. **Ingest YAML** into Postgres (creates calls, nodes, criteria/elements, expectations).
3. **User flow**:
   - Select call → select proposal node → paste snippet → submit.
4. **Backend** builds a single prompt covering all expectations for the chosen node and generates a structured response:
   - `LLM_MODE=stub` for deterministic local testing (no cost)
   - `LLM_MODE=openai` for real model calls (cost)
5. **Persist output**:
   - `Review` + multiple `ReviewCard` rows (each traceable to a `NodeExpectation`).
6. **Frontend** renders results, supports export/download/delete, and handles loading/polling states.

## Architecture / Topology (current MVP)

- **Backend**: Python 3.12, SQLModel, FastAPI endpoints (minimal MVP).
- **Database**: Postgres (local Docker compose; Neon in production).
- **Frontend**: Next.js app (UI + SEO/marketing site).
- **Auth**: Clerk.
- **Pattern**: BFF-style signing where the browser talks to Next.js routes, and Next.js calls FastAPI server-to-server.

Deployment notes live in `README.md` and walkthroughs (see “Pointers” below).

## What’s Done So Far (at a glance)

The repo README maintains the best “status” checklist: `README.md`.

Highlights include:
- Domain model + ingestion pipeline (YAML → DB).
- Real OpenAI integration + stub mode for safe verification.
- Minimal FastAPI endpoints (health, calls/nodes, reviews).
- BFF contracts and frontend app scaffold.
- Landing page + privacy + delete/export flows.
- Multiple WF UX improvements (e.g., polling, submit-flow hardening, node hierarchy selector).

## Golden Paths (what to verify first)

### Local (safe, no OpenAI cost)

1. Start backend in stub mode:
   - `cd backend && LLM_MODE=stub uv run uvicorn main:app --reload`
2. Start frontend:
   - `cd frontend && npm run dev`
3. In the browser:
   - Visit `/` (marketing)
   - Visit `/app` → sign in → submit a review → land on review detail → export/delete

### Call ingestion

- Dry-run validate a call YAML:
  - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run`
- Ingest (writes to DB):
  - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml`

## Ops & Safety Notes (important)

- Running `scripts/run_review.py` or `LLM_MODE=openai` will call the OpenAI API (cost + external side effects).
- Backend runtime is Postgres-only: `DATABASE_URL` is required (no SQLite fallback).
- Avoid `source backend/.env` if `DATABASE_URL` contains `&` (shell parsing); prefer `python-dotenv` behavior or explicit `export DATABASE_URL='...'`.

## Workflow / Collaboration Rules (how we work)

Repo rules are the source of truth: `AGENTS.md`.

Key behaviors:
- Use WF workflow (`docs/workflow/README.md`) for new non-trivial work; keep artifacts in sync with `docs/index.md`.
- Keep diffs small; avoid drive-by refactors.
- Ask before: touching >3 files, adding deps, DB schema changes, or anything with external side effects.
- Log clarifications and decisions:
  - Q&A: `docs/logs/qa_history.md`
  - Decisions: `docs/logs/decisions.md`
  - Prompt iterations: `docs/logs/prompt_history.md`

## Pointers (SSOT)

- Project dashboard (what’s done / WF registry): `docs/index.md`
- Repo operating rules: `AGENTS.md`
- Architecture decisions: `docs/logs/decisions.md`
- Q&A / clarifications: `docs/logs/qa_history.md`
- Prompt history: `docs/logs/prompt_history.md`
- Domain model reference: `docs/reference/domain_model.md`
- Workflow system: `docs/workflow/README.md`
- Call YAML docs hub: `docs/call-yaml/README.md`

## How to Use This File in ChatGPT Projects

- Upload this file as the primary “context doc”.
- Also upload: `AGENTS.md`, `README.md`, and `docs/index.md` so answers stay grounded in repo SSOT.
- When asking implementation questions, include:
  - the exact file path(s) you’re working in, and
  - the goal + acceptance criteria (even 2–3 bullets is enough).
