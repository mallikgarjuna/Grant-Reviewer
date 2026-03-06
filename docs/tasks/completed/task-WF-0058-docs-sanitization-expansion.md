# WF-0058 — Docs Sanitization Expansion Tasks

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-03-06

## Task Breakdown

### [x] Task 1 — Define sanitization policy
Goal: establish explicit scope/rules for tool/model names.
Files:
- docs/reference/doc-sanitization-policy.md
Verification:
- manual review of policy sections and rollout states.

### [x] Task 2 — Add docs sanitization guard
Goal: add deterministic guard script and CI integration.
Files:
- scripts/check_docs_sanitization.sh
- .github/workflows/ci.yml
Verification:
- bash scripts/check_docs_sanitization.sh

### [x] Task 3 — Sanitize workflow docs
Goal: replace tool-specific wording in phase docs.
Files:
- docs/workflow/phase-0-0-start-workflow.md
- docs/workflow/phase-0-1-brainstorm.md
- docs/workflow/phase-0-2-brainstorm-risk-audit.md
- docs/workflow/phase-0-3-brainstorm-revise.md
- docs/workflow/phase-1-1-prd-generate.md
- docs/workflow/phase-1-2-prd-risk-audit.md
- docs/workflow/phase-1-3-prd-revise.md
- docs/workflow/phase-2-1-task-generate.md
- docs/workflow/phase-2-2-task-review.md
- docs/workflow/phase-2-3-task-revise.md
Verification:
- rg -n "Codex chat|How to Invoke in Codex Chat|Reference it in Codex chat" docs/workflow/*.md

### [x] Task 4 — Add guard regression tests
Goal: protect CWD-invariant behavior and CI step contract.
Files:
- backend/tests/scripts/test_docs_sanitization_guard.py
- backend/tests/scripts/test_ci_policy_event_scope.py
Verification:
- cd backend && uv run pytest tests/scripts/test_docs_sanitization_guard.py -q
- cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0058_docs_sanitization_guard_step_contract or wf0054_ci_policy_ or wf0055_platform_policy_ or wf0056_live_rehearsal_safety_gates or wf0056_live_rehearsal_apply_contract or wf0056_live_rehearsal_verify_tracer_contract"

## Changelog
- v1.0 (2026-03-06): Finalized task artifact with implemented checklist.
