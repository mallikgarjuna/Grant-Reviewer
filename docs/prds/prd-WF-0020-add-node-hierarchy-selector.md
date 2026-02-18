# WF-0020 — Add node hierarchy selector

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-18

## 1. In Scope

- Replace flat node selection UX in in-scope submit/review entry points with hierarchy-aware selection.
- Implement parent-first cascade interaction for node selection.
- Add parent-context disambiguation for ambiguous child labels where required.
- Preserve predictable ordering inside parent groups.
- Validate behavior on representative calls with 10+ nodes.

## 2. Out of Scope

- Backend/API/schema changes for node hierarchy data.
- Full selector redesign across every route in one WF.
- Broad information architecture or app navigation redesign.
- Legal/privacy updates, broad accessibility remediation, and call-ingestion backlog work.
- New analytics/experimentation framework for selector behavior.

## 3. User / System Flow

Happy path:
1. User enters an in-scope flow that requires node selection.
2. User first selects parent section/context.
3. System displays available child nodes for that parent with clear labels.
4. User selects intended child node and continues existing flow unchanged.

Failure path A - incomplete hierarchy metadata:
1. User opens selector for a call where some hierarchy metadata is missing.
2. System cannot fully populate expected parent-child mapping for a subset.
3. UI falls back to usable deterministic rendering without blocking selection.

Failure path B - ambiguous child names:
1. Multiple child nodes have similar or identical labels under different parents.
2. User risks wrong selection in a flat presentation.
3. UI shows parent-context disambiguation to prevent duplicate-looking options.

Failure path C - large option set fatigue:
1. User opens selector with 10+ nodes.
2. Large list increases scanning effort and backtracking risk.
3. Parent-first cascade reduces visible option set before child selection.

## 4. Functional Requirements

- FR1: In-scope node selection enforces parent selection before child selection.
- FR2: Child options update deterministically based on selected parent.
- FR3: Child labels include parent context where ambiguity exists.
- FR4: Existing submit/review behavior remains unchanged after node selection.
- FR5: Fallback rendering remains usable when hierarchy metadata is incomplete.
- FR6: Node ordering is stable within each parent context.
- FR7: Selector interaction preserves existing keyboard behavior.

## 5. Data & API Contracts

Request/response shapes:
- Reuse existing node payload contracts from backend responses; no contract changes.

Validation rules:
- Parent choice is required before child choice in the new interaction.
- Selected child must belong to the currently selected parent context.
- If metadata is incomplete, fallback path must still return valid selectable nodes.

State transitions:
- initial selector state -> parent selected -> child options populated -> child selected
- metadata incomplete -> fallback option rendering -> child selected

## 6. Components / Modules

Boundaries and responsibilities:
- In-scope route-level form components:
  - host parent and child selector controls
  - preserve existing submit/review form behavior
- Selector utility/adapter logic:
  - derive parent/child groupings from existing node payload
  - provide fallback grouping when hierarchy metadata is incomplete

Suggested file paths:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` (if node selection appears in this flow)
- `frontend/src/components/**` for reusable selector UI pieces
- `frontend/src/lib/**` for grouping/fallback transformation helpers

## 7. Edge Cases

- Parent contains zero eligible children; child selector must communicate this clearly.
- User switches parent after selecting child; stale child selection must reset safely.
- Duplicate child labels across parents must remain distinguishable.
- Calls with partial hierarchy metadata must not break selection controls.
- Very large hierarchies should remain scannable without freezing UI.

## 8. Telemetry (Minimal)

- No new telemetry pipeline in MVP.
- Optional temporary local debug logging during verification is allowed but should not ship as persistent instrumentation.

## Deferred / Not in MVP

- Cross-app standardization of all selector experiences.
- Advanced tree navigation UI (expand/collapse explorer).
- Search-first selector mode and personalization.
- Dedicated analytics for selection accuracy/conversion.

## Open Questions (if any)

- Confirm exact set of routes/components that currently expose flat node selection and must be included in this WF.

## Changelog

- v0.1 (2026-02-18): Initial PRD from spec
