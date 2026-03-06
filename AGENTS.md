# Agent Instructions (AGENTS.md)

**Grant Reviewer**: evaluation-criteria-grounded feedback on proposal snippets; outputs review cards traceable to evaluation criteria expectations.

## ⚠️ Core Directives for Agents

**Keep this file tiny; link SSOT.** Add rules only after an AI failure (1-3 lines).
**Surprises:** unexpected behavior or new rule idea -> alert developer first.
**Style (this file):** extreme concision; sacrifice grammar.
**Minimal Edits:** never replace content unnecessarily; only change what is requested.

## Quick Reference & Links

- **SSOT tasks:** use `docs/index.md`; add tasks under `docs/tasks/`. (Trigger: any work request.)
- **Terms:** say **evaluation criteria/elements** (not "rubric") in researcher-facing text; canonical: `backend/app/schemas/call_definitions_v2.py`. (Trigger: UI/docs/copy.)
- **Runtime:** Python `3.12` (see `backend/.python-version`, `uv`), Node `22.17.0` (see `.nvmrc`, `npm`). (Trigger: env/tooling issues.)
- **File traceability:** every file must include its project-relative path at top (comment/docstring/header) for copy/paste provenance. (Trigger: create/edit any file.)
- **Code phrases:** `verify workflow` = run verification pass; `workflow preflight` = check WF closure readiness; `next move` = run `repo reality check` first, then `workflow preflight` if WF active, then `verify workflow` only when implementation/code changed; return top 2 next actions with one recommendation + rationale. (Trigger: user says phrase.)

**Read these only if needed:**
- WF phases/branches/artifacts -> `docs/guides/workflow-system.md`
- tests/DB/migrations/setup/PR rules -> `docs/guides/engineering-standards.md`
- repo map/KB/zero-latency logging -> `docs/guides/knowledge-base.md`

## Memory Management

When you discover something valuable for future sessions — architectural decisions, bug fixes, gotchas, environment quirks — immediately append it to `docs/memory/`.

Don't wait to be asked. Don't wait for session end.

Keep entries short: date, what, why. Read `docs/memory/index.md` at the start of every session. Load other files only when relevant. If a file doesn't exist yet, create it and update `docs/memory/index.md`.

## Task Rules

- **Wait for Signal**: Always wait for the user's explicit signal BEFORE moving to writing code, changing files, or implementing a feature. "LGTM" on an artifact means approved (finish phase), not proceed to next phase.
- **3-File Limit**: If a task requires changes to more than 3 files, stop and break it into smaller sub-tasks first.
- **TDD Behavior Changes**: For bug fixes/behavior changes, write a test that reproduces it (RED), implement the minimal code change (GREEN), refactor.
