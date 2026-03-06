# WF-0058 — Docs Sanitization Expansion

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-03-06

## Problem
Core process/workflow docs contained tool-specific language. This caused process drift risk and inconsistent expectations across agents.

## Goal
Enforce tool/model-neutral language in SSOT process docs and workflow instructions, while preserving tool-specific guidance in adapter/reference/history docs.

## Scope
- Add a policy describing allowed/disallowed placement of tool/model names.
- Add CI guard for `AGENTS.md` and `docs/workflow/*.md`.
- Sanitize phase workflow docs to agent-agnostic wording.
- Add regression tests for guard behavior.

## Non-Goals
- Rewriting historical logs/decision archives.
- Removing tool names from adapter/reference docs.

## Decisions
- Enforce via shell guard in CI backend job.
- Resolve repo root from script location to avoid CWD coupling.
- Roll out in phases to avoid broad CI churn.

## Risks
- False positives for words containing forbidden tokens.
- Future CI/workflow edits may remove the guard step.

## Changelog
- v1.0 (2026-03-06): Finalized scope/decisions and locked brainstorm for WF-0058.
