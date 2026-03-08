<!-- docs/brainstorms/brainstorm-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for the product-scope decision in this WF.
- The Q&A transcript is rationale only; it must not introduce new product-scope commitments.
- If later discussion reveals a scope contract not captured here, promote it into this brainstorm and log it in `docs/logs/decisions.md`.

---

## Repo Reality Snapshot (Read-Only)

- `docs/mission.md` is funder-agnostic and does not itself promise ZonMw or broader call-family expansion.
- `docs/parking_lot.md` is the main live contradiction: it still treats a remaining promised-program gap as the launch blocker and names ZonMw or equivalent as the example target.
- `docs/logs/decisions.md` AD 65.1 still says broader promised-program breadth is deferred, which becomes strategically misleading if the cut is permanent.
- `docs/memory/domain/project_docs.md` is the correct place to record the new scope-lock rule for future sessions.
- Historical/completed artifacts contain older breadth language, but rewriting them in this WF would damage provenance and create scope drift.

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 1)

PeerLens has a real product-scope decision that is not yet reflected consistently in live docs and backlog logic.

PeerLens is now permanently focused on NWO, ERC, and MSCA funding calls. ZonMw and equivalent broader expansion are out of scope, not deferred. Current live docs still imply:
- ZonMw or equivalent broader coverage is planned
- the remaining promised-program call gap is a launch blocker
- broader call-family coverage remains part of the product commitment

This creates product-truthfulness risk. After narrowing scope, the real product question is no longer "what extra promised call must we add?" but whether PeerLens is useful and honest within the NWO/ERC/MSCA wedge.

Contract Notes / Non-obvious constraints:
- Classify this as a goals-level product-scope lock with positioning and backlog consequences, not a mission rewrite.
- Do not silently convert a permanent cut into "deferred for later" language.
- Do not treat historical breadth references as current commitments.

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 2)

After this workflow:
- live product docs and backlog consistently position PeerLens as focused on NWO/ERC/MSCA only
- no active doc treats ZonMw or equivalent breadth as planned or required for launch
- launch-readiness language shifts from breadth promises to truthfulness and usefulness within the chosen wedge
- mission wording remains unchanged unless a later mission check finds a concrete contradiction

Contract Notes / Non-obvious constraints:
- Success is documentation truthfulness, not broader coverage.
- The active backlog should stop describing breadth expansion as the remaining promised blocker.
- This WF succeeds even if no product code changes happen.

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 3)

Primary actors for this workflow:
- repo owner making product-scope decisions
- future agents using docs and backlog as planning SSOT
- future product/docs work that would otherwise inherit stale breadth assumptions

Current harmful behavior:
- future planning passes can still infer that ZonMw or equivalent breadth is expected
- active backlog prioritization can still treat broader coverage as the remaining launch blocker
- positioning work can inherit outdated breadth promises even if the product wedge is already narrower

Contract Notes / Non-obvious constraints:
- This WF serves internal product-truthfulness and planning hygiene first, not end-user feature delivery.
- The relevant audience is any future session that reads live docs as current product truth.

## 4. Rough Idea (Unstructured Thinking)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 4)

Use a docs-only workflow to lock the scope decision and remove stale breadth logic from active planning artifacts.

Preferred direction:
- keep `docs/mission.md` stable unless evidence proves real drift
- rewrite only the live backlog/decision/memory surfaces that still imply broader promised-program coverage
- initial active-doc target set: `docs/parking_lot.md`, `docs/logs/decisions.md`, and `docs/memory/domain/project_docs.md`; inspect `docs/mission.md` for mission check only unless a concrete contradiction is found
- preserve historical/completed artifacts as historical evidence rather than retroactive SSOT

Contract Notes / Non-obvious constraints:
- Do not bundle landing-page changes, review-quality work, or call-authoring work into this WF.
- If `docs/logs/decisions.md` is updated, prefer a new superseding dated decision entry or clearly additive note; do not silently rewrite historical approved decision text unless the wording sits outside the dated historical record.
- If a live doc is not current SSOT or active planning input, default to leaving it alone.

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 5)

- Keep edits minimal.
- Respect the 3-file limit by splitting later execution into small tasks.
- Preserve traceability; do not erase historical references just because they are now obsolete strategically.
- Keep `docs/mission.md` stable unless a mission check proves a concrete contradiction.
- No new features, no call expansion, no review-quality or UX work in this WF.
- Remove false future-breadth commitments without implying the current NWO/ERC/MSCA wedge is already fully complete or sufficient in every product dimension.

Contract Notes / Non-obvious constraints:
- This is a docs-only WF unless later planning reveals a truly required live product-copy dependency.
- Any "future broader expansion" wording should be treated as a defect, not a neutral placeholder.

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 6)

- A live doc outside the initial target set may still imply broader promised-program coverage.
- Under-editing active decision language could leave contradictory signals, for example "permanent cut" in one artifact and "deferred breadth" in another.
- Over-editing historical artifacts would weaken provenance and create scope drift.
- Backlog rewrite quality matters: removing the old blocker language without naming the new truthfulness/usefulness wedge would leave a planning vacuum.
- Mission drift risk is low but not zero; it should be checked explicitly rather than assumed away.

Contract Notes / Non-obvious constraints:
- Historical wording may stay historically true; the problem is when active artifacts still speak in the present tense.
- If Phase 1 discovers more than a small active-doc set, the work should be split rather than widened casually.

## Open Questions / Deferred

- Whether `docs/mission.md` needs any current-phase interpretation note after the mission check. Default: no.
- Whether any non-SSOT reference docs should be updated in this WF, or deferred to a later positioning cleanup.
- Exact replacement wording for the old "remaining promised-program gap" launch-blocker framing in the active backlog.

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 7)

Smallest successful slice:
- create a WF that explicitly records the permanent NWO/ERC/MSCA scope lock
- update active backlog/decision/memory docs so they no longer imply ZonMw, broader promised-program expansion, or breadth-based launch blocking
- preserve mission text unless a clear contradiction is found
- leave historical/completed artifacts unchanged

Explicitly excluded:
- new funding calls
- UX or review-quality work
- landing-page/code updates
- broad repo-wide wording cleanup beyond the active SSOT/backlog surface

Contract Notes / Non-obvious constraints:
- A docs-only closure is acceptable and preferred if it removes the misleading commitments cleanly.
- This WF should not manufacture follow-on breadth work just to replace the removed backlog item.
- Verification seam for later phases: mission check, targeted stale-language scan across active docs, and historical-provenance preservation check.

## 8. Explicit Non-Goals

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0066-peerlens-scope-lock-nwo-erc-msca.md` (Section 8)

- No ZonMw now or later.
- No "deferred for later" reframing.
- No expansion beyond NWO/ERC/MSCA.
- No feature work, ingestion work, or review-quality/UX work in this WF.
- No historical rewrite of completed WFs/logs just to normalize old wording.

Contract Notes / Non-obvious constraints:
- If a proposed edit would make old artifacts look cleaner but reduces historical honesty, reject it.
- If this WF starts absorbing broader positioning or launch-copy redesign, that is scope drift.
