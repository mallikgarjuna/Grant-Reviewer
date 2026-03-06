# WF-0058 — Docs Sanitization Expansion

Artifact: brainstorm-qna
Version: v1.0
Status: Complete
Last Updated: 2026-03-06

## Q1
Should workflow docs be tool-agnostic?
- Decision: Yes. Keep process docs stable and vendor-neutral.

## Q2
Where can tool/model names remain?
- Decision: Adapter/reference/history docs only.

## Q3
How to enforce with minimal overhead?
- Decision: Add one CI guard script and incremental workflow-doc cleanup.

## Q4
How to reduce regression risk?
- Decision: Add tests for script CWD handling and CI step contract.

## Changelog
- v1.0 (2026-03-06): Captured final Q&A decisions used in WF-0058.
