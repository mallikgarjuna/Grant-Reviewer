<!-- docs/prds/prd-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-04-03

## 0. User Stories (MVP)

- US1: As the repo owner, I want Codex's default repo-local context load reduced, so that more reasoning budget is available for real task work.
- US2: As the repo owner, I want repo instruction surfaces classified as always-on, on-demand, or archival, so that future docs do not silently become default prompt payload.
- US3: As the repo owner, I want workflow safety, traceability, and researcher-facing terminology preserved while optimizing context load, so that improvements do not create hidden regressions.
- US4: As the repo owner, I want a concrete before/after estimate for the likely default-load path, so that the optimization is measurable rather than purely aesthetic.

## Deferred Stories (Not in MVP)

- As the repo owner, I want exact tokenizer-based measurements for multiple session archetypes.
- As the repo owner, I want the same operating model generalized into a reusable pattern for other repos.
- As the repo owner, I want a full historical memory/archive redesign beyond the highest-impact entrypoints.

## 1. In Scope

- Define the default-context policy for this repo in practical, repo-specific terms. (US1, US2, US3)
- Inventory the current instruction surfaces and classify them by intended load posture. (US2)
- Reduce the highest-cost likely default-load surfaces, starting with `docs/index.md`. (US1, US4)
- Narrow broad entrypoint triggers that cause oversized docs to be opened too early. (US1, US2)
- Preserve workflow safety, traceability rules, and researcher-facing terminology while making these changes. (US3)
- Produce a concrete before/after estimate for the likely repo-local default-load path using one consistent estimation method. (US4)

## 2. Out of Scope

- Rewriting the full WF system or every workflow artifact. (US3)
- Deep review of all historical WFs or task files. (US1)
- Exact token accounting for every possible prompt path. (US4)
- Broad product, backend, or frontend architecture changes outside Codex instruction surfaces. (US1, US3)
- Deleting historical material purely for neatness where archive/reference splits preserve value. (US3)

## 3. User / System Flow

### Happy Path

1. Review the approved brainstorm and the current repo instruction surfaces to establish the likely default-load path and the initial inventory. (US1, US2, US4)
2. Classify each relevant surface as always-on, on-demand, or archival based on whether the repo explicitly encourages it to be opened early or for most tasks. (US2)
3. Identify the smallest high-impact changes that materially reduce likely default load without weakening workflow safety or terminology/traceability expectations. (US1, US3)
4. Apply the prioritized doc/instruction changes, starting with the heaviest likely entrypoints such as `docs/index.md` and any overly broad `AGENTS.md` triggers. (US1, US2, US4)
5. Recalculate the same likely default-load estimate and verify that routing, traceability, and terminology expectations still hold. (US3, US4)
6. Document the resulting context-budget policy so future additions follow the same classification model. (US2, US3)

### Failure Path 1

1. A proposed reduction lowers context load but weakens workflow safety, provenance expectations, or researcher-facing terminology. (US3)
2. The change must fail closed: preserve the safety/traceability rule, narrow the optimization, or move the rule behind a better trigger rather than deleting it. (US3)

### Failure Path 2

1. A cleanup idea improves wording but does not materially change the likely default-load path. (US1, US4)
2. The change should not count as core MVP progress unless paired with a real routing or entrypoint improvement. (US1, US4)

### Failure Path 3

1. A history-heavy doc is still genuinely useful, but expensive as a default surface. (US2, US3)
2. Split it into a compact active summary plus archive/reference content instead of deleting it or leaving it as the main entrypoint. (US2, US3)

## 4. Functional Requirements

- FR1 (US1, US4): The workflow must establish one consistent, practical method for estimating the likely repo-local default-load path before and after changes.
- FR1A (US1, US4): The before and after estimates must use the same command, formula, or script so the comparison is replayable and not based on mixed measurement methods.
- FR2 (US2): The workflow must classify the relevant instruction surfaces into always-on, on-demand, or archival categories using a repo-specific definition of default context.
- FR3 (US1, US4): The workflow must prioritize the highest-cost likely default entrypoint for cleanup first, with `docs/index.md` as the initial target.
- FR4 (US1, US2): The workflow must narrow or reroute broad triggers that encourage large docs to be opened for most tasks when those docs are better treated as on-demand or archival.
- FR5 (US3): The workflow must preserve or explicitly justify any change to workflow safety rules, provenance/traceability expectations, and researcher-facing terminology.
- FR6 (US2, US3): If a history-heavy document remains useful, the workflow must prefer compact active-summary plus archive/reference splits over destructive deletion.
- FR7 (US1, US4): The workflow must favor the smallest edits that materially change likely load behavior before broader doc cleanup.
- FR8 (US2, US3): The workflow must leave behind an explicit operating rule that future instruction surfaces can follow to avoid re-bloating default context.
- FR9 (US3): Verification must include routing checks showing that workflow guidance remains discoverable after entrypoint or archive changes.
- FR10 (US1, US2, US4): The workflow must distinguish between aesthetic trimming and actual likely-load reduction when evaluating success.

## 5. Data & API Contracts

### Primary Inputs

- Approved brainstorm: defines scope, success threshold, non-goals, and initial surface inventory. (US1, US2, FR1, FR2)
- Current repo instruction surfaces: `AGENTS.md`, `docs/index.md`, `docs/memory/index.md`, selected memory leaves, and relevant workflow/guides when triggered. (US1, US2, FR2, FR3)

### Working Data Shape

- Instruction Surface Record (`FR2`, `FR10`)
  - `surface_path`: project-relative file path
  - `role`: short description of why the file exists
  - `load_posture`: `always_on | on_demand | archival`
  - `current_trigger`: what currently causes the file to be opened or referenced
  - `estimated_cost`: practical size signal using the chosen estimation method
  - `action`: `keep | revise | compact | archive`
  - `rationale`: short reason tied to likely-load behavior and safety constraints

### Required Inventory Output Artifact

- Phase 2 must produce a compact surface inventory table or equivalent structured artifact that records, at minimum, `surface_path`, `load_posture`, `estimated_cost`, `action`, and `rationale`. (`FR2`, `FR8`, `FR10`)

- Default Load Estimate (`FR1`, `FR10`)
  - `path_name`: e.g. likely repo-local default-load path
  - `method`: consistent practical estimation method
  - `included_surfaces`: list of included files
  - `estimated_before`
  - `estimated_after`
  - `notes`

### Validation Rules

- A surface cannot be marked `archival` if doing so would hide required workflow or safety guidance with no active routing path. (FR5, FR9)
- A surface cannot be marked `keep` if its current behavior is “default entrypoint” but the PRD identifies it as oversized and reroutable without safety loss. (FR3, FR4)
- A change does not satisfy the contract if it only reduces wording while leaving the same likely-load entrypoint behavior intact. (FR7, FR10)

### State Transitions

- `Draft inventory` -> `classified inventory` when each relevant surface has a posture and action. (FR2)
- `proposed edits` -> `accepted edits` only if safety/traceability/terminology checks remain satisfied. (FR5, FR9)
- `accepted edits` -> `verified optimization` only after the same estimation method shows the before/after default-load comparison. (FR1, FR10)

## 6. Components / Modules

### Boundaries

- Brainstorm / PRD / task artifacts
  - Hold scope, contracts, task ordering, and verification expectations.
- Repo instruction surfaces
  - `AGENTS.md`
  - `docs/index.md`
  - `docs/memory/index.md`
  - selected `docs/memory/*`
  - selected `docs/guides/*` and `docs/workflow/*`
- Verification surface
  - practical before/after context estimate
  - routing/traceability checks after edits

### Responsibilities

- `AGENTS.md`
  - tiny always-on repo policy
  - narrow triggers only
- `docs/index.md`
  - active dashboard/router, not historical registry dump
- `docs/memory/index.md`
  - compact memory router
- memory leaf docs
  - active operating rules or archival/reference history, depending on classification
- workflow/guides
  - on-demand procedural references

### Design Tree (Dependencies + Ordering)

1. Confirm brainstorm scope and measurement standard.
2. Inventory current instruction surfaces and likely-load triggers.
3. Classify surfaces and choose minimal high-impact edits.
4. Apply entrypoint cleanup first, centered on `docs/index.md` and any overly broad triggers.
5. Only expand into deeper memory/archive work if the entrypoint cleanup is insufficient or already complete.
6. Verify before/after estimate and routing/safety preservation.
7. Document the durable operating rule for future additions.

### Deep Modules

- Surface classification policy
  - Small interface: a posture label plus action decision
  - Hidden complexity: deciding when a surface is truly default, on-demand, or archival without breaking safety
- Default-load estimation method
  - Small interface: consistent before/after estimate
  - Hidden complexity: keeping the estimate practical, stable, and comparable without requiring exhaustive tokenization
- Archive split strategy
  - Small interface: active summary + archive/reference path
  - Hidden complexity: preserving discoverability and traceability while reducing prompt payload

### Suggested File Paths

- `AGENTS.md`
- `docs/index.md`
- `docs/memory/index.md`
- `docs/memory/domain/*.md`
- `docs/memory/tools/*.md`
- `docs/reference/*` where durable operating rules belong
- `docs/logs/decisions.md` for major scope/contract decisions

## 7. Edge Cases

- A small file may still need reclassification if it routes to large follow-on reads too broadly. (US1, FR4)
- A large file may remain acceptable as on-demand reference if the repo stops treating it as a first-stop surface. (US2, FR6)
- A workflow-specific guide might need a dashboard link, but should still remain on-demand unless the repo truly requires it for most tasks. (US2, FR9)
- A memory note already codified elsewhere should not remain in active memory purely as duplication. (US2, FR8)
- If an archive split would touch too many files at once, Phase 2 should sequence the work into smaller atomic tasks. (US3, FR7)

## 8. Testing Decisions (TDD)

This WF is documentation/instruction-surface work rather than an application behavior change, so classic RED/GREEN tests are not the primary seam. Verification should instead be contract-like and deterministic where possible.

- Public seams to verify
  - before/after likely default-load estimate
  - `docs/index.md` routing behavior
  - preservation of workflow safety/traceability and researcher-facing terminology
- Mocking
  - none; rely on direct file/content inspection and deterministic repo commands
- Minimal verification by requirement
  - FR1/FR1A/FR10: rerun the same estimation method before and after edits
  - FR2/FR8: inspect the resulting classification/routing policy in the edited docs
  - FR3/FR4/FR7: verify the first cleanup target and broad triggers were actually reduced or rerouted
  - FR5/FR9: verify safety/traceability/terminology guardrails remain present and reachable

### Minimal Verification Matrix

| Proof item | Requirement(s) | Replay surface | Expected outcome |
| :--- | :--- | :--- | :--- |
| Baseline default-load estimate | FR1, FR1A, FR10 | one deterministic repo command/script/formula run before edits | baseline estimate captured with included surfaces listed |
| Post-change default-load estimate | FR1, FR1A, FR10 | same deterministic repo command/script/formula run after edits | comparable after-state estimate captured |
| Entry-point routing check | FR3, FR4, FR9 | direct inspection of `AGENTS.md` and `docs/index.md` | heavy default entrypoint is reduced or rerouted without losing discoverability |
| Surface inventory proof | FR2, FR8, FR10 | inspect produced inventory artifact | every in-scope surface has posture, action, and rationale |
| Safety/traceability preservation | FR5, FR9 | direct inspection of edited safety/provenance/terminology surfaces | no silent loss of required workflow safety, provenance, or terminology rules |

## 9. Telemetry (Minimal)

- Record the chosen estimation method and before/after values in workflow evidence or walkthrough materials.
- Capture which surfaces changed and why, so future sessions can distinguish successful optimizations from cosmetic edits.

## 10. Deferred / Not in MVP

- Exact tokenizer-based auditing for multiple prompt archetypes.
- Full memory-system redesign.
- Cross-repo Codex operating model extraction.
- Broad cleanup of all historical workflow artifacts.

## 11. Open Questions (if any)

- What concrete after-state target should count as “material” reduction for the likely default-load path?
- Should memory classification stay index-driven, or eventually use explicit `active` and `archive` tiers?
- Which durable policy belongs in `docs/reference/` versus `AGENTS.md` versus memory?

## 12. Changelog

- v0.1 (2026-04-03): Initial PRD from brainstorm
- v0.2 (2026-04-03): Applied risk-audit edits by locking measurement consistency, requiring a concrete inventory output artifact, tightening sequencing around entrypoint cleanup, and adding a minimal verification matrix.
