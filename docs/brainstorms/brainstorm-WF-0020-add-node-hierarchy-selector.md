# WF-0020 — Add node hierarchy selector

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-02-18

---

## 1. Problem Statement

### Decisions (Section 1)
- Primary affected users: first-time users selecting a node for proposal sections.
- Core failure: flat list hides parent-child structure, so users cannot orient quickly.
- Highest-friction moment: initial node selection before writing feedback.
- Priority rationale: this is launch-readiness UX for larger call structures.
- Scope frame: selector hierarchy UX only; no backend/API changes.

### Summary
The current flat selector creates orientation friction at first use, especially when calls have many nodes. This workflow should focus narrowly on adding hierarchy clarity to node selection.

## 2. Desired Outcome

### Decisions (Section 2)
- Success signal: users find intended nodes faster with fewer wrong selections in manual QA.
- Expected behavior change: users navigate by parent context first, then choose child nodes confidently.
- MVP quality bar: grouped selector with clear parent labels and stable ordering.
- Verification evidence: targeted manual checks on long-node calls plus lint pass.
- Guardrail: deliver hierarchy clarity only; defer unrelated UX refactors.

### Summary
Outcome is a selector that makes proposal structure legible at a glance, reducing mis-selection and hesitation without expanding scope into broader UX work.

## 3. Target User / Actor

### Decisions (Section 3)
- Primary actor: signed-in researchers drafting and reviewing proposal snippets.
- Secondary actor: returning researchers editing existing reviews across many nodes.
- Behavior to replace: guessing from long flat labels and backtracking to find correct nodes.
- Main frustration: losing context about where a node sits in proposal hierarchy.
- Context boundary: in-app node selection surfaces only (submit/review flows).

### Summary
This workflow serves end users inside the app where node choice drives review accuracy. It does not include admin tooling or marketing/navigation surfaces.

## 4. Rough Idea (Unstructured Thinking)

### Decisions (Section 4)
- Start with grouped selector options by parent hierarchy.
- Preferred interaction model: two-step cascade (choose parent, then child).
- Label strategy: parent-prefixed child labels where needed to reduce ambiguity.
- Complexity guard: reuse existing data shape and UI patterns with no schema additions.
- MVP coverage: primary node-selection entry points first.

### Summary
The simplest path is a focused selector enhancement that introduces hierarchy guidance without creating a new navigation system.

## 5. Constraints

### Decisions (Section 5)
- Time: keep implementation to a small, shippable slice within one WF.
- Technical: frontend-only UX changes; no backend/API/schema changes.
- Dependencies: use current UI stack; add no new third-party packages.
- Verification: targeted manual checks on long-node flows plus lint/pre-commit.
- Process: keep diffs focused and update WF docs/logs at phase boundaries.

### Summary
Constraints enforce a low-risk launch-readiness improvement with minimal moving parts and explicit verification discipline.

## 6. Risks / Unknowns

### Decisions (Section 6)
- Fragile assumption: existing node data consistently supports parent-child grouping in UI.
- Primary failure risk: incomplete hierarchy mapping could misplace or duplicate options.
- Early validation target: representative calls with 10+ nodes render correct grouping/cascade.
- Rework trigger: users still cannot locate intended nodes quickly in manual scenarios.
- Secondary risk: extra interaction step may increase clicks while improving accuracy.

### Summary
Risk centers on data-to-UI mapping quality. Early verification on realistic call data is required to avoid false confidence.

## 7. MVP Definition

### Decisions (Section 7)
- Must-have slice: hierarchical node selector with clear labels in core node-selection flows.
- Done criteria: verified correctness on representative long-node calls with no obvious regressions.
- Explicit defer: broader navigation redesign and app-wide selector standardization.
- Must-not-include: backend/API/schema changes and unrelated content/page work.
- Quality bar: users can reliably find intended nodes with parent context.

### Summary
MVP is a targeted hierarchy upgrade to node selection that improves findability now without broad system churn.

## 8. Explicit Non-Goals

### Decisions (Section 8)
- Postponed: full tree-navigation redesign across all pages.
- Future WF candidate: selector standardization across every node-touching surface.
- Out of scope: backend schema/API changes for node model.
- Out of scope: legal/privacy pages, accessibility sweep, and call-ingestion backlog items.
- Out of scope: telemetry instrumentation and experimentation framework for selector behavior.

### Summary
This workflow is intentionally limited to hierarchy clarity in current selector flows; adjacent product and platform improvements remain in separate backlog workflows.
