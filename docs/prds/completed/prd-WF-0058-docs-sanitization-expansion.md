# WF-0058 — Docs Sanitization Expansion PRD

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-03-06

## User Stories (MVP)
- US1: As a maintainer, I want workflow docs to be tool-agnostic so process guidance stays stable.
- US2: As a reviewer, I want CI to block forbidden tool/model names in process docs so regressions are prevented.

## Functional Requirements
- FR1 (US1): `AGENTS.md` and all `docs/workflow/*.md` must avoid forbidden tool/model terms.
- FR2 (US2): CI must execute a deterministic docs-sanitization guard and fail on violation.
- FR3 (US2): Guard must work regardless of caller CWD.

## Acceptance
- Guard script exists and runs in CI backend job.
- Phase 0–2 workflow docs are sanitized to "any coding agent" wording.
- Regression tests cover repo-root and backend-CWD execution.

## Changelog
- v1.0 (2026-03-06): Locked PRD for implemented WF-0058 scope.
