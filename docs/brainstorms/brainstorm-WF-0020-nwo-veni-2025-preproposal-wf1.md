# WF-0020 — NWO Veni 2025 preproposal (WF-1): V2 call YAML dry-run loader

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-21

---

## 1. Problem Statement

### Decisions (Section 1)
- Primary actor: internal dev/admin running ingestion scripts (not researchers).
- Core failure mode: both YAML parse issues and a mismatch between current schema/loader and the NWO Veni call definition shape.
- Success definition (dry-run only): `scripts/ingest_call.py --dry-run` validates V2 and prints a clear structured summary of the call definition (proposal structure + evaluation criteria/elements).
- Scope of support: NWO-focused CallDefinition V2 loader (reusable across NWO calls), not a universal cross-funder loader.
- Error posture: strict + fail-fast, with precise, actionable error messages (include field path; include location context where available).

### Summary
We need to unblock ingesting the NWO Veni 2025 preproposal call definition by making the YAML parseable and by adding a V2 loader that supports a dry-run validation path with clear diagnostics.

## 2. Desired Outcome

### Decisions (Section 2)
- CLI outcome: `uv run python scripts/ingest_call.py <nwo_v2_yaml> --dry-run` exits 0 and prints a deterministic summary (no DB writes).
- Summary must include: call metadata, proposal node tree/sections, evaluation criteria, and evaluation elements per criterion.
- Failure UX: validation errors show “what failed + where” (YAML location if possible; schema path always).
- Compatibility: do not break existing CallDefinition V1 ingest flows (e.g., existing ERC YAML).
- Acceptance evidence: one “happy path” dry-run and at least one intentional “broken YAML” dry-run that fails with a helpful message.

### Summary
After this, we can confidently validate NWO V2 call YAML locally without touching the database, and we can iterate on the call file quickly.

## 3. Target User / Actor

### Decisions (Section 3)
- Primary user: developer maintaining call definitions (`backend/scripts/ingest_call.py` workflow).
- Secondary user: future admin ingestion path (still via scripts today).
- Not a target: researchers in the web UI (no frontend/API changes in this WF).
- Primary pain: inability to validate call YAML quickly and safely due to parse/schema failures.
- Desired behavior: run dry-run validation early and often while authoring/updating call definitions.

### Summary
This is a dev-experience workflow: faster iteration on evaluation criteria/elements definitions with a safe “validate only” CLI.

## 4. Rough Idea (Unstructured Thinking)

### Decisions (Section 4)
- Introduce a CallDefinition V2 Pydantic schema (parallel to current definition) with a dedicated loader.
- Teach `scripts/ingest_call.py` to detect V2 vs V1 via a version field (or a discriminant key) and route to the correct loader.
- Add/extend `--dry-run` to validate + print summary without DB writes.
- Improve YAML parsing error messaging (surface line/column for syntax errors; print context).
- Keep output stable and readable (structured text / JSON-like blocks; avoid giant dumps).

### Summary
Keep the change small: add a V2 schema + loader and make dry-run the fast feedback loop for fixing YAML parse and shape issues.

## 5. Constraints

### Decisions (Section 5)
- No DB schema changes (explicit non-goal).
- No new API endpoints; no frontend changes.
- Dry-run must not require a live DB connection.
- Keep diffs focused: only YAML parsing/loading and the ingest script behavior.
- Use “evaluation criteria / evaluation elements” terminology in user-facing output and copy.

### Summary
This WF is intentionally “offline validation only” and must not ripple into persistence or UI.

## 6. Risks / Unknowns

### Decisions (Section 6)
- Risk: the V2 YAML spec will evolve; schema should be strict but not brittle without reason.
- Risk: mixing V1/V2 detection could break existing ERC ingest; add a narrow compatibility check.
- Unknown: where current YAML parse fails (syntax vs implicit typing vs anchors/aliases vs invalid keys).
- Validation focus: ensure at least one V1 file still dry-runs, plus the target NWO V2 file dry-runs.
- Rework trigger: if V2 structure can’t be expressed cleanly without DB-level IDs (defer to WF-2).

### Summary
The biggest risk is accidental regressions to existing ingest; we mitigate via targeted dry-run checks on at least one known-good V1 YAML.

## 7. MVP Definition

### Decisions (Section 7)
- Must-have: CallDefinition V2 schema + loader.
- Must-have: `scripts/ingest_call.py --dry-run` supports V2 YAML and does not write to DB.
- Must-have: actionable parse + validation errors.
- Defer: persistence of V2 into DB (WF-2), logical ID columns, API endpoints, frontend structured forms, compliance engine.
- Done: NWO V2 dry-run passes; an intentionally broken YAML fails with helpful diagnostics; existing V1 dry-run still passes.

### Summary
MVP is strictly “validate and summarize call definition V2 offline”; all persistence and product delivery happens in later WFs.

## 8. Explicit Non-Goals

### Decisions (Section 8)
- No DB writes for V2 in this WF (dry-run only).
- No new tables/columns/migrations; no Alembic work.
- No FastAPI contract/API changes.
- No frontend/UI work.
- No compliance engine, NOT_ASSESSABLE alignment logic, or assisted extraction features.

### Summary
This WF is a loader + validation utility only; it exists to unblock authoring the NWO Veni call definition safely.
