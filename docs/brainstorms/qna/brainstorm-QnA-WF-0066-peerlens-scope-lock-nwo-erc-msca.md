<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

## Section 1 — Problem Statement

**Q1: How should this change be classified in the brainstorm contract?**
- A) Goals-level product-scope lock with backlog/positioning consequences.
- B) Mission-level change requiring mission rewrite.
- C) Pure copy cleanup with no planning significance.
 > Recommendation: A — this matches repo reality and the stated request. B overstates the change because `docs/mission.md` stays valid; C understates the planning effect.
 > **Selected: A**

**Q2: What is the primary failure mode this WF must fix?**
- A) Active docs falsely imply broader funding-call coverage is still planned or required.
- B) The mission statement is too vague about supported calls.
- C) The repo lacks enough technical proof for NWO/ERC/MSCA support.
 > Recommendation: A — this is the live truthfulness defect. B is not currently proven; C is not the scope-cut problem this WF is meant to solve.
 > **Selected: A**

**Q3: What should happen to ZonMw in the product-scope contract?**
- A) Mark it permanently out of scope, not deferred.
- B) Keep it as future optional expansion with weaker wording.
- C) Leave it ambiguous to avoid closing future doors.
 > Recommendation: A — this matches the explicit strategic instruction. B and C would preserve the ambiguity this WF exists to remove.
 > **Selected: A**

**Q4: What should replace the old "remaining promised-program gap" framing as the live product concern?**
- A) Truthfulness and usefulness inside the NWO/ERC/MSCA wedge.
- B) A later revisit of broader funder breadth after launch.
- C) A neutral "coverage still evolving" statement.
 > Recommendation: A — it reflects the current repo reality and prevents fake optionality. B and C would keep the old breadth logic alive.
 > **Selected: A**

**Q5: What is the strict boundary for this WF?**
- A) Docs-only scope lock across active SSOT/backlog artifacts; no feature/call-expansion work.
- B) Docs plus landing-page/product copy changes in the same WF.
- C) Docs plus a new backlog for future broader coverage options.
 > Recommendation: A — smallest correct WF, lowest scope-drift risk. B and C widen the initiative beyond the approved decision.
 > **Selected: A**

## Section 2 — Desired Outcome

**Q1: What should count as the main success condition for this WF?**
- A) Active docs and backlog stop implying broader planned coverage beyond NWO/ERC/MSCA.
- B) The repo is scrubbed of every historical mention of ZonMw or broader coverage.
- C) The landing page and marketing copy are refreshed immediately.
 > Recommendation: A — it targets the live defect without damaging provenance or widening the WF. B is overreach; C is separate positioning work.
 > **Selected: A**

**Q2: What should happen to launch-blocker language?**
- A) Replace breadth-gap framing with truthfulness/usefulness within the chosen wedge.
- B) Keep breadth-gap framing but remove the ZonMw example.
- C) Remove launch-blocker language entirely without replacement.
 > Recommendation: A — the backlog still needs a truthful prioritization logic. B preserves the wrong premise; C risks a planning vacuum.
 > **Selected: A**

**Q3: How should the mission be handled in this WF?**
- A) Leave `docs/mission.md` unchanged unless a concrete contradiction is found.
- B) Add supported-program names directly into the mission.
- C) Rewrite the mission around NWO/ERC/MSCA coverage.
 > Recommendation: A — minimal and evidence-based. B and C would turn a product-scope lock into unnecessary mission drift.
 > **Selected: A**

**Q4: What is the correct closure mode if the stale promises are all in docs only?**
- A) Accept docs-only WF closure as complete.
- B) Add a small code/product change so the WF feels more substantive.
- C) Keep the WF open until a future positioning refresh happens too.
 > Recommendation: A — this WF is about product truthfulness in docs and backlog. B and C create fake dependencies.
 > **Selected: A**

**Q5: What must this WF avoid implying?**
- A) That broader coverage remains committed later.
- B) That NWO/ERC/MSCA support is already perfect in every respect.
- C) Both A and B.
 > Recommendation: C — the docs should reject fake future breadth while also staying honest about remaining usefulness/truthfulness work inside the wedge.
 > **Selected: C**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor served by this workflow?**
- A) Repo owner and future agents using live docs for planning truth.
- B) End-user researchers directly interacting with the app.
- C) External funders reviewing the product.
 > Recommendation: A — this is an internal product-scope and planning hygiene workflow, not a user-facing feature slice.
 > **Selected: A**

**Q2: What harmful behavior are we trying to stop first?**
- A) Future planning inheriting stale breadth commitments from active docs.
- B) Users misunderstanding the current UI behavior.
- C) Engineers adding new call YAMLs without enough tests.
 > Recommendation: A — this is the direct effect of the stale backlog and decision wording.
 > **Selected: A**

**Q3: Which actor should be treated as the main "consumer" of the backlog edits?**
- A) Future workflow planning sessions.
- B) Frontend copywriting sessions.
- C) Database migration planning.
 > Recommendation: A — the active backlog is a planning control surface first.
 > **Selected: A**

**Q4: What is the planning risk if this workflow is skipped?**
- A) A future WF will incorrectly prioritize broader call-family expansion as launch-critical.
- B) The current APIs will become incompatible.
- C) The canonical call YAMLs will stop ingesting.
 > Recommendation: A — that is the concrete stale-planning risk visible in `docs/parking_lot.md`.
 > **Selected: A**

**Q5: How should end-user value be framed inside this brainstorm?**
- A) Indirectly: truthful scope enables better product decisions for the real wedge.
- B) Directly: this WF delivers new researcher-facing capability.
- C) Not at all: ignore product value entirely.
 > Recommendation: A — it keeps the workflow honest without pretending it ships a user-facing feature.
 > **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction?**
- A) Docs-only cleanup of active SSOT/backlog artifacts plus a recorded scope-lock decision.
- B) Docs cleanup plus landing-page copy refresh in the same WF.
- C) A broader repo-wide terminology sweep.
 > Recommendation: A — smallest correct slice, strongest traceability, lowest scope drift.
 > **Selected: A**

**Q2: Which live artifact class should be prioritized first in later phases?**
- A) Active backlog and decision logic.
- B) Historical completed WF artifacts.
- C) Generic reference docs.
 > Recommendation: A — those are the current control surfaces that still imply the wrong product commitment.
 > **Selected: A**

**Q3: How should historical artifacts be handled?**
- A) Leave them unchanged unless they are still acting as live SSOT.
- B) Rewrite them to align with the new strategy.
- C) Delete the most misleading ones.
 > Recommendation: A — preserves provenance and keeps this WF small.
 > **Selected: A**

**Q4: Should this WF create a replacement backlog item for broader expansion someday?**
- A) No; the permanent cut should remove that path rather than rename it.
- B) Yes; park it as low-priority future optionality.
- C) Yes; move it to maintenance.
 > Recommendation: A — the instruction is explicit: not now or later.
 > **Selected: A**

**Q5: What should happen if a new candidate edit set expands past a few active docs?**
- A) Split the work into smaller task slices in later phases.
- B) Keep widening the WF so all stale wording is fixed at once.
- C) Stop the WF entirely.
 > Recommendation: A — matches the 3-file discipline while preserving momentum.
 > **Selected: A**

## Section 5 — Constraints

**Q1: What is the top execution constraint for this WF?**
- A) Minimal edits with strong traceability.
- B) Maximal wording consistency across the whole repo.
- C) Fastest possible closure regardless of doc quality.
 > Recommendation: A — this matches the explicit task framing.
 > **Selected: A**

**Q2: How should the 3-file limit shape later implementation?**
- A) Split the docs work into small tasks rather than widening a single edit batch.
- B) Ignore the limit because docs are low risk.
- C) Edit only one file and leave contradictions elsewhere.
 > Recommendation: A — respects repo rules without leaving the core contradiction unresolved.
 > **Selected: A**

**Q3: What should happen if mission wording appears adjacent but not actually contradictory?**
- A) Leave it alone.
- B) Rewrite it for consistency.
- C) Add supported-program names just to be safe.
 > Recommendation: A — avoid unnecessary mission drift.
 > **Selected: A**

**Q4: How should "future broader coverage" wording be treated?**
- A) As a defect in active docs because it conflicts with the permanent cut.
- B) As harmless optionality.
- C) As something to revisit during launch planning.
 > Recommendation: A — otherwise the scope lock is not real.
 > **Selected: A**

**Q5: What kind of WF is this unless new evidence says otherwise?**
- A) Docs-only WF.
- B) Docs-plus-code WF.
- C) Strategy memo only, outside workflow.
 > Recommendation: A — cleanest fit to the request and current repo state.
 > **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the most likely under-edit risk?**
- A) Leaving one active artifact still implying broader promised-program coverage.
- B) Accidentally changing runtime behavior.
- C) Breaking YAML ingestion.
 > Recommendation: A — this is the real failure mode for a docs-only scope-lock WF.
 > **Selected: A**

**Q2: What is the most likely over-edit risk?**
- A) Rewriting historical artifacts and damaging provenance.
- B) Adding too many tests.
- C) Over-specifying backend contracts.
 > Recommendation: A — the repo contains many completed artifacts with historical breadth wording that should remain historical.
 > **Selected: A**

**Q3: What ambiguity needs explicit closure in later phases?**
- A) What exact wording replaces the old "remaining promised-program gap" blocker logic.
- B) Whether to add a fourth supported funder soon.
- C) Whether to redesign the app shell.
 > Recommendation: A — that replacement logic is the main content decision for live backlog cleanup.
 > **Selected: A**

**Q4: What should happen if a live doc outside the initial set still acts as SSOT for scope promises?**
- A) Add it to the WF only if it is truly active/current, otherwise defer.
- B) Ignore it to preserve narrow scope.
- C) Expand the WF to rewrite all related docs immediately.
 > Recommendation: A — fail closed on live contradictions, but do not widen into historical cleanup.
 > **Selected: A**

**Q5: What is the right stance on mission drift risk?**
- A) Low but explicitly checked.
- B) Zero; do not even inspect the mission.
- C) High enough to force immediate mission rewrite.
 > Recommendation: A — evidence-based and conservative.
 > **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the smallest successful deliverable?**
- A) Record the scope lock and remove active stale breadth commitments from backlog/decision/memory docs.
- B) Also refresh landing-page/product copy in the same WF.
- C) Also add a new supported call to prove the wedge.
 > Recommendation: A — that is the exact narrow slice needed.
 > **Selected: A**

**Q2: Which artifacts are in-bounds for the MVP by default?**
- A) Active docs used for current planning truth.
- B) Active docs plus historical completed artifacts.
- C) Anything that mentions supported calls anywhere in the repo.
 > Recommendation: A — keeps the effort minimal and traceable.
 > **Selected: A**

**Q3: How should the mission be handled at MVP scope?**
- A) Checked, then preserved unless contradiction is proven.
- B) Rewritten to name the wedge explicitly.
- C) Expanded to describe all current product tradeoffs.
 > Recommendation: A — minimal and correct.
 > **Selected: A**

**Q4: What is explicitly excluded from MVP?**
- A) New call coverage, UX work, review-quality work, code changes.
- B) Only code changes.
- C) Only landing-page changes.
 > Recommendation: A — the workflow needs a hard non-goal fence.
 > **Selected: A**

**Q5: When should this Phase 0 artifact be considered ready for planning?**
- A) Once the scope lock, target live artifacts, risks, and non-goals are explicit and traceable.
- B) Only after the actual docs are edited.
- C) Only after a full repo-wide copy audit.
 > Recommendation: A — Phase 0 is for planning clarity, not execution.
 > **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: What is the hard stance on ZonMw?**
- A) Not now or later; out of scope.
- B) Deferred until after launch.
- C) Keep unmentioned but possible.
 > Recommendation: A — this is the explicit strategic decision.
 > **Selected: A**

**Q2: What should this WF not do with broader program expansion?**
- A) Do not preserve it in backlog logic or positioning as future commitment.
- B) Keep it in low-priority backlog as optional.
- C) Move it to historical notes as a likely next step.
 > Recommendation: A — anything else weakens the scope cut.
 > **Selected: A**

**Q3: What kind of work is out of bounds even if adjacent?**
- A) Feature, UX, review-quality, ingestion, and landing-page/code work.
- B) Only backend code work.
- C) Only frontend code work.
 > Recommendation: A — the non-goal fence should be broad and explicit.
 > **Selected: A**

**Q4: What should happen to historical artifacts with old wording?**
- A) Leave them as historical record unless they still function as live SSOT.
- B) Rewrite them all to avoid inconsistency.
- C) Remove references to them from the repo.
 > Recommendation: A — preserves traceability.
 > **Selected: A**

**Q5: What counts as scope drift for this WF?**
- A) Absorbing broader positioning refresh or replacement roadmap work beyond the active scope-lock docs.
- B) Fixing an active contradictory SSOT file.
- C) Recording the decision in memory for future sessions.
 > Recommendation: A — B and C are required hygiene, not drift.
 > **Selected: A**
