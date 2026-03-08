<!-- docs/prds/prd-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-08

Type: docs

## 0. User Stories (MVP)

- US1: As the repo owner, I want active product docs to state that PeerLens is focused on NWO/ERC/MSCA only, so that live planning does not imply broader commitments that no longer exist.
- US2: As a future planning agent, I want the active backlog and decision log to stop treating ZonMw or broader promised-program coverage as planned or launch-blocking, so that later WF planning starts from truthful constraints.
- US3: As a maintainer protecting documentation provenance, I want the workflow to correct only the active live-doc set and leave historical artifacts intact, so that current truth is fixed without rewriting history.
- US4: As a maintainer using the mission as positioning anchor, I want `docs/mission.md` checked for contradiction but left unchanged unless a concrete conflict is found, so that scope-lock work does not become an unnecessary mission rewrite.

## Deferred Stories (Not in MVP)

- DS1: Broader positioning cleanup across historical/completed artifacts or non-SSOT reference docs.
- DS2: Landing-page copy changes, product UI changes, or call-authoring work for any additional agency or program.
- DS3: Mission rewrite work that goes beyond a contradiction check on the current `docs/mission.md`.

## 1. In Scope

- Produce a docs-only workflow centered on the active live-doc set named in the brainstorm: `docs/parking_lot.md`, `docs/logs/decisions.md`, and `docs/memory/domain/project_docs.md`, with `docs/mission.md` used only for mission check. (US1, US2, US3, US4)
- Inspect the entire named live-doc set, but edit only the files that still carry active contradictory language; compliant target docs should be recorded as verified no-ops rather than rewritten. (US1, US2, US3, US4)
- Remove or rewrite active language that implies ZonMw is planned, that a remaining promised-program call gap is a launch blocker, or that coverage breadth beyond NWO/ERC/MSCA remains a current commitment. (US1, US2)
- Reframe launch-readiness language around truthfulness and usefulness within the NWO/ERC/MSCA wedge rather than breadth expansion. (US1, US2)
- Preserve historical provenance by treating completed artifacts and older historical records as out of scope unless they still function as active SSOT. (US3)
- Record the scope-lock rule in memory so future sessions inherit the narrowed commitment without reintroducing fake breadth promises. (US2, US3)

## 2. Out of Scope

- Adding ZonMw or any other new agency/program coverage. (DS2)
- Treating broader coverage beyond NWO/ERC/MSCA as deferred, optional MVP follow-up, or launch-readiness requirement. (DS2)
- Rewriting completed WFs, historical brainstorms/PRDs/tasks, or old logs purely for wording consistency. (DS1)
- Shipping product/code changes, review-quality changes, UX changes, or ingestion work. (DS2)
- Rewriting `docs/mission.md` unless the mission check finds a concrete contradiction with the locked wedge. (DS3)

## 3. User / System Flow

### Happy path

1. The maintainer reads the approved brainstorm and the current live-doc set to confirm this WF is a docs-only scope-lock correction focused on active SSOT/backlog surfaces. (US1, US2, US3, US4)
2. The maintainer checks `docs/mission.md` for contradiction and confirms the current mission remains funder-agnostic and compatible with an NWO/ERC/MSCA-only wedge. (US4)
3. The maintainer updates `docs/parking_lot.md` only if it still treats a missing ZonMw-like call or broader promised-program gap as planned or launch-blocking; otherwise the file is recorded as a verified no-op. (US1, US2, US3)
4. The maintainer updates `docs/logs/decisions.md` only if the active scope-lock decision is missing or contradictory; otherwise the file is recorded as a verified no-op. (US1, US2, US3)
5. The maintainer updates `docs/memory/domain/project_docs.md` with a concise future-session rule that active product/docs planning must not reintroduce breadth commitments beyond NWO/ERC/MSCA. (US2, US3)
6. Verification records an explicit pass/fail result for each named target doc plus the mission check, and confirms the active live-doc set now points to truthful launch readiness within the chosen wedge while historical artifacts remain unchanged. (US1, US2, US3, US4)

### Failure path A — backlog still encodes breadth as launch blocker

1. `docs/parking_lot.md` still says a remaining promised-program gap, ZonMw, or equivalent breadth is the current launch blocker after this WF. (US1, US2)
2. Future planning would continue to prioritize fake breadth work and misstate launch readiness. (US1, US2)
3. The workflow remains incomplete until active backlog wording is rewritten around truthful usefulness within NWO/ERC/MSCA. (US1, US2)

### Failure path B — provenance is damaged by over-editing

1. The maintainer starts rewriting completed WFs or other historical artifacts just to normalize older broader-coverage language. (US3)
2. Current truth would improve at the cost of historical honesty and traceability. (US3)
3. The workflow must stop at the active live-doc set unless a supposedly historical artifact is still acting as present-tense SSOT. (US3)

### Failure path C — mission rewrite happens without contradiction

1. `docs/mission.md` is edited even though the mission check found no concrete contradiction with the NWO/ERC/MSCA wedge. (US4)
2. The workflow would widen from a goals-level scope lock into unnecessary mission churn. (US4)
3. The edit must be rejected unless a specific contradictory sentence is identified and logged. (US4)

### Failure path D — compliant docs get rewritten anyway

1. A target live doc already matches the scope lock, but Phase 2 still rewrites it just because it is on the inspection list. (US2, US3, US4)
2. The workflow would create unnecessary churn and weaken the “minimal edits, preserve provenance” constraint. (US3, US4)
3. The correct outcome is verification-only for already compliant docs, with no-op evidence recorded instead of gratuitous rewrites. (US2, US3, US4)

## 4. Functional Requirements

- FR1 (US1, US2, US3, US4): Phase 2 must stay limited to the active live-doc set identified in the brainstorm: `docs/parking_lot.md`, `docs/logs/decisions.md`, and `docs/memory/domain/project_docs.md`, with `docs/mission.md` used for mission check only unless a concrete contradiction is found.
- FR1a (US1, US2, US3, US4): Phase 2 must inspect every named target doc, but must edit only the files that still contain active contradiction; compliant docs are verification-only no-ops.
- FR1b (US1, US2, US3, US4): Workflow bookkeeping surfaces such as `docs/index.md` may be updated only for workflow-status traceability and do not become live-doc correction targets or justification to widen the named target set.
- FR2 (US1, US2): Active docs must not state or imply that ZonMw is planned, that a remaining promised-program call gap is the launch blocker, or that coverage beyond NWO/ERC/MSCA remains part of the current commitment.
- FR3 (US1, US2): Active launch-readiness language must be rewritten to focus on product truthfulness and usefulness within the permanent NWO/ERC/MSCA wedge.
- FR4 (US3): Historical/completed artifacts must remain unchanged in this WF unless they still function as active SSOT or current planning input.
- FR5 (US1, US2): `docs/parking_lot.md` must stop presenting broader promised-program expansion as the active P1 blocker or top launch-readiness dependency.
- FR6 (US1, US2, US3): `docs/logs/decisions.md` must contain or preserve an approved WF-0066 scope decision stating that broader promised-program expansion is not deferred for current planning.
- FR7 (US2, US3): `docs/memory/domain/project_docs.md` must record a short future-session rule that active product/docs planning should not reintroduce scope commitments beyond NWO/ERC/MSCA.
- FR8 (US4): `docs/mission.md` must be checked explicitly and left unchanged unless the workflow can point to a concrete contradiction between existing mission text and the locked wedge.
- FR9 (US1, US2, US3): Phase 2 tasks must preserve provenance by preferring additive or superseding edits in active docs over retroactive rewriting of historical context.
- FR10 (US1, US2, US3, US4): Readiness for implementation must require an explicit pass/fail evidence bundle covering each named target doc, the mission-check result, and proof that no broader-scope work was introduced.
- FR10a (US1, US2, US3, US4): No recommendation to proceed may be made unless the evidence bundle names the exact files inspected, the action taken for each (`edited` or `verified no-op`), the deterministic verification command(s) run, and whether each check passed or failed.

## 5. Data & API Contracts

### 5.1 Artifact contract

- The governing input is `docs/brainstorms/brainstorm-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`, which locks the workflow to a docs-only scope correction focused on active live docs. (US1, US2, FR1, FR4)
- The governing output of this phase is this PRD, which must constrain Phase 2 to documentation edits only unless a concrete mission contradiction is found. (US1, US4, FR1, FR8)

### 5.2 Live-doc correction contract

- `docs/parking_lot.md` represents active backlog truth and must not carry current-tense breadth commitments or breadth-based launch blockers. (US1, US2, FR2, FR3, FR5)
- `docs/logs/decisions.md` represents active scope decisions and must explicitly support the permanent NWO/ERC/MSCA wedge for current planning. (US1, US2, US3, FR2, FR6)
- `docs/memory/domain/project_docs.md` represents agent-facing future-session guidance and must encode the scope-lock rule succinctly. (US2, US3, FR7)
- `docs/mission.md` is an interpretation anchor, not an automatic edit target in this WF. (US4, FR8)
- A named target doc that already satisfies the scope lock remains in-scope for verification but not for mandatory editing. (US2, US3, US4, FR1a)

### 5.3 Validation rules

- Any active-doc sentence that frames ZonMw or equivalent broader expansion as planned, deferred, or required for launch is invalid for this WF. (US1, US2, FR2)
- Any edit that widens beyond the named live-doc set without a documented contradiction or active-SSOT justification is invalid scope drift. (US3, US4, FR1, FR4, FR8)
- Any rewrite of a named target doc that is already compliant, without a concrete contradiction or missing explicit rule to fix, is invalid unnecessary churn. (US2, US3, US4, FR1a)
- Any change that makes historical artifacts look current or erases historical breadth references from completed artifacts is invalid provenance loss. (US3, FR4, FR9)

### 5.4 State transitions

- `Draft` means the PRD describes the scoped docs-only correction but has not yet incorporated audit hardening. (US1, US2, US3, US4)
- `Ready for Tasks` means the PRD has explicit traceability, active-doc boundaries, provenance rules, mission-check rules, and verification gates for the docs-only implementation. (US1, US2, US3, US4, FR10)

## 6. Components / Modules

- [`docs/parking_lot.md`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/parking_lot.md)
  - Active backlog surface and current primary contradiction candidate; edit only if the stale launch-blocker/breadth language is still present at execution time. (FR1a, FR2, FR3, FR5)
- [`docs/logs/decisions.md`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/logs/decisions.md)
  - Active decision surface that must keep the scope-lock decision explicit for future planning without rewriting unrelated historical records; if already compliant, record a verified no-op instead of rewriting. (FR1a, FR2, FR6, FR9)
- [`docs/memory/domain/project_docs.md`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/memory/domain/project_docs.md)
  - Future-session guidance surface that prevents later agents from reintroducing broader-coverage commitments. (FR7)
- [`docs/mission.md`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/mission.md)
  - Mission-check input only unless contradiction is found. (FR8)

Workflow bookkeeping note:

- [`docs/index.md`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/index.md)
  - WF registry/status surface only. It may reflect Phase 1 state transitions, but it is not part of the live-doc correction target set and cannot justify widening Phase 2 doc scope. (FR1b, FR10)

Design tree / dependencies / ordering:

1. Confirm the brainstorm locks the workflow to docs-only scope and identifies the active live-doc set. (FR1, FR4)
2. Confirm the mission check result before planning any mission edit. (FR8)
3. For each named target doc, decide explicitly whether the result is `edit required` or `verified no-op`. (FR1a, FR8)
4. Rewrite the active backlog wording in `docs/parking_lot.md` so breadth-based launch blocking is removed. (FR2, FR3, FR5)
5. Preserve or minimally extend the active WF-0066 decision record in `docs/logs/decisions.md` only if needed for present-tense scope truth. (FR6, FR9)
6. Record the future-session rule in `docs/memory/domain/project_docs.md`. (FR7)
7. Record a per-target pass/fail evidence row for `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`, including whether each was edited or verified no-op. (FR1a, FR8, FR10, FR10a)
8. Verify only the contradiction-bearing live docs changed, that compliant docs stayed no-op where appropriate, and that historical artifacts remain untouched. (FR1a, FR4, FR10)

Deep module guidance:

- Keep the correction narrow and documentary; this WF should not manufacture replacement product work just because breadth language is removed.
- Treat `docs/parking_lot.md` as the primary contradiction surface and rewrite its rationale carefully enough that future prioritization remains useful after the old blocker is removed.
- Prefer additive or superseding wording in `docs/logs/decisions.md` over destructive cleanup of historical decision text.
- Keep the mission stable by default; the burden of proof is on any proposed mission edit.
- Treat “named target” and “must edit” as different concepts; inspection coverage is required, but no-op verification is the preferred outcome for already compliant docs.
- Keep workflow bookkeeping distinct from scope-correction surfaces; `docs/index.md` status updates are allowed bookkeeping, not live-doc targeting.
- Preserve the distinction between current planning truth and historical record throughout Phase 2 tasking.

Suggested file-path clusters (coarse only):

- active planning truth: `docs/parking_lot.md`, `docs/logs/decisions.md`
- future-session guidance: `docs/memory/domain/project_docs.md`
- mission anchor: `docs/mission.md`
- workflow bookkeeping only: `docs/index.md`

## 7. Edge Cases

- A sentence stops naming ZonMw but still implies some unnamed broader promised-program expansion remains expected; this still violates the scope lock. (US1, US2, FR2)
- The backlog removes the old breadth blocker but replaces it with no truthful launch-readiness framing at all; Phase 2 must avoid leaving a planning vacuum. (US1, US2, FR3, FR5)
- A future-session memory note is too vague and allows agents to reintroduce “maybe later” breadth language; the memory update must be explicit enough to prevent that drift. (US2, US3, FR7)
- A decision-log edit rewrites historical approved text instead of adding a clear present-tense scope-lock note; that weakens provenance. (US3, FR6, FR9)
- `docs/logs/decisions.md` already contains the required scope-lock decision, but Phase 2 rewrites it anyway without adding missing semantics; that is unnecessary churn. (US2, US3, FR1a, FR6, FR9)
- `docs/mission.md` stays unchanged but later planning still claims mission conflict without naming contradictory text; the workflow must treat that as unsupported scope widening. (US4, FR8)
- A supposedly inactive doc turns out to be present-tense SSOT for launch readiness; Phase 2 must log that contradiction explicitly before expanding file scope. (US3, US4, FR1, FR4)
- Phase 2 reports a generic "docs verified" claim without a per-target result table or deterministic command evidence; that fails the readiness gate even if the edits themselves look reasonable. (US1, US2, US3, US4, FR10, FR10a)

## 8. Testing Decisions (TDD)

- This is a docs-only behavior/contract correction, so verification should still follow a fail-closed pattern: identify the stale language first, then make the minimal doc edits, then re-check that the stale language is gone. (US1, US2, US3, US4)
- Public verification seams are the rendered text/content of the active live-doc set, not historical artifacts. (US1, US2, US3, US4)
- Phase 2 must capture one explicit evidence table with four named rows: `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`. Each row must state `pre-state`, `action` (`edited` or `verified no-op`), `post-state`, and `pass/fail`. (US1, US2, US3, US4, FR10, FR10a)
- Phase 2 must use deterministic repo-root commands that enumerate the named files explicitly; broad repo-wide wording scans are insufficient evidence for closure. (US1, US2, US3, US4, FR10a)
- Minimum required checks:
  - mission check proving `docs/mission.md` contains no concrete contradiction and therefore remains unchanged, unless a contradiction is found and logged. (US4, FR8)
  - targeted stale-language scan across the active live-doc set for ZonMw/planned breadth/launch-blocker wording before and after edits. (US1, US2, FR2, FR5)
  - decision-log check proving the active WF-0066 scope-lock decision remains explicit. (US1, US2, US3, FR6)
  - memory check proving future-session guidance encodes the lock against reintroducing broader coverage commitments. (US2, US3, FR7)
  - no-op evidence check proving any already compliant named target doc was inspected and intentionally left unchanged. (US2, US3, US4, FR1a, FR8)
  - provenance check proving completed/historical artifacts were not edited as part of this WF. (US3, FR4, FR9)
- Minimum evidence commands must include:
  - a named-file stale-language scan before and after edits
  - a named-file content check for the explicit scope-lock decision and memory rule
  - a `git diff --name-only` style proof that only allowed files changed
  - a mission-check proof showing `docs/mission.md` stayed unchanged unless a contradiction was explicitly logged
- No unit/integration test code is required; the verification burden is document-level evidence and precise scope control. (US1, US2, US3, US4)

## 9. Telemetry (Minimal)

- No product telemetry is required.
- If Phase 2 needs any evidence artifact, it should be limited to deterministic doc-scan output or review notes captured in workflow artifacts, not new runtime instrumentation.

## 10. Deferred / Not in MVP

- Historical-artifact cleanup beyond the active live-doc set.
- Landing-page or product-positioning copy refresh outside the current SSOT docs.
- New launch blockers or replacement roadmap work unrelated to documentation truthfulness.
- Mission rewrite absent a concrete contradiction.

## 11. Open Questions (if any)

- None at PRD level. The live-doc target set and mission-check default are already locked by the brainstorm.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
- v0.2 (2026-03-08): Applied audit hardening to require inspect-all/edit-only-when-contradictory behavior for the named live-doc set and marked Ready for Tasks.
- v0.3 (2026-03-08): Tightened scope-control semantics to keep workflow bookkeeping out of the live-doc target set and required per-target pass/fail verification evidence before any proceed recommendation.
