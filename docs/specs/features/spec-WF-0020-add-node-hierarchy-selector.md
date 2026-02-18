# WF-0020 — Add node hierarchy selector

Artifact: spec
Version: v0.1
Status: Draft
Last Updated: 2026-02-18

## 1. Purpose

Improve node findability and selection accuracy by introducing hierarchy context in node selection flows where users currently navigate a confusing flat list.

## 2. User / System Context

- Primary users are signed-in researchers creating or editing review feedback in app flows that require node selection.
- Current UX presents a flat node selector, which hides parent-child structure for calls with many nodes.
- Friction is highest at first selection, where users must infer hierarchy from labels alone and often backtrack.
- Scope is limited to in-app node selection surfaces; admin tooling and backend ingestion are out of scope.

## 3. Core Behavior

- Provide hierarchy-aware selection so users can choose nodes with clear parent context.
- Prioritize a simple grouped/cascaded flow that reduces wrong selections and re-navigation.
- Keep node ordering predictable and labels disambiguated where necessary.
- Preserve existing backend contracts and submission semantics.

Behavioral definitions:
- `Hierarchy-aware selection`: parent grouping (and/or parent-first cascade) is visible before final child node choice.
- `Selection accuracy`: users can choose intended nodes in representative long-node scenarios without repeated trial-and-error.

## 4. In Scope

- Frontend selector UX updates for primary node-selection entry points in submit/review flows.
- Parent-context grouping/cascade behavior for node choices.
- Label adjustments for ambiguous child nodes (for example, parent-prefixed labels where needed).
- Stable ordering within parent groups.
- Manual verification across representative calls with 10+ nodes.

## 5. Out of Scope

- Backend/API/schema/model changes for node data.
- Global navigation or full information architecture redesign.
- Selector standardization across all routes/components in one pass.
- Legal/privacy content updates, full accessibility sweep, and call-ingestion backlog items.
- Analytics instrumentation and experimentation framework for selector behavior.

## 6. Data & Dependencies

- Existing frontend app routes/components that render node selection controls.
- Existing node payload shape and hierarchy metadata from current backend responses.
- Current frontend UI primitives and styling conventions (no new dependencies).
- Existing lint/pre-commit quality gates and manual QA process for launch-readiness checks.

## 7. Edge Considerations

- Some nodes may have ambiguous names; UI must avoid duplicate-looking options without context.
- Calls may contain uneven hierarchy depth; selector behavior should remain deterministic.
- Added interaction steps must not create dead-end states or hidden values.
- If hierarchy metadata is incomplete for certain calls, fallback rendering must remain usable.
- Large option sets should remain scannable and keyboard-friendly.

## 8. Verification Expectations

- Primary node-selection flows show parent context during selection.
- Representative long-node calls (10+ nodes) support reliable target-node selection.
- No obvious regressions in existing submit/review route behavior.
- Lint and pre-commit checks pass for changed files.
- Manual QA confirms reduced backtracking in selection scenarios.

## Changelog

- v0.1 (2026-02-18): Initial spec from brainstorm
