<!-- docs/brainstorms/brainstorm-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-07

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** for WF-0061.
- The Q&A transcript is rationale only; if a decision becomes real, it must be promoted here.
- This WF exists to test real product readiness via additional official-source call coverage, not to expand framework/governance work.

---

## Preflight Checklist

### Step 1 — Long-Form Problem Intake

- WF-0061 should prove real product progress by adding exactly one new official-source canonical call, not by doing more framework, governance, or generic hardening work.
- The repo has strong machinery and several corrected canonical calls, but validated coverage is still too narrow to support broad product confidence.
- Current canonical coverage is still only NWO and ERC, so the remaining gap is another real call that broadens trust in the product's claimed support surface.
- This workflow should answer one concrete question: can PeerLens onboard one more real call safely through the intended product path, using official sources, without collapsing into another meta-workflow?
- The selected target for this workflow is `MSCA Postdoctoral Fellowships 2025` (`MSCA-PF-2025`) because it expands credible coverage more than more NWO/ERC rework would.
- Real progress means moving `MSCA-PF-2025` from absent to official-source-grounded canonical coverage with validation evidence; fake progress means more machinery, frontend redesign, broad cross-call hardening, batch expansion, or speculative YAML authoring without official source uploads.
- Hard constraint: no substantive `MSCA-PF-2025` YAML structure or criteria authoring until the user uploads the official narrative/application-structure source and the official evaluation/assessment-criteria source for that exact call.

### Repo Reality Snapshot (Read-Only) (2026-03-07)

- Canonical call inventory is still limited to:
  - `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
  - `backend/data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml`
  - `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
  - `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
- Parking-lot P1 #11 is stale as-written because WF-0044 already delivered its core bundle: ERC CoG canonical migration plus baseline validation / source-gated refreshes for the named existing canonical calls.
- Parking-lot P1 #12 is the closest backlog anchor for this WF, but its older "MSCA first" phrasing is now resolved here as one locked target: `MSCA-PF-2025`.
- Current product claims would still be weak if this WF only re-tunes ERC/NWO internals again; that is more framework orbit, not real call-data expansion.
- Source-gating remains hard SSOT: no substantive YAML authoring/re-authoring for a call until that call's official source documents are explicitly uploaded in-workflow.

### Open Questions Suggested by Repo Snapshot

- Does `MSCA-PF-2025` fit current structured-review surfaces without forcing a nested-UI/platform redesign into this WF?
- What is the smallest deterministic proof bar that proves `MSCA-PF-2025` is real product progress rather than another ingest-only artifact?
- Are the official `MSCA-PF-2025` narrative/application-structure source and evaluation/assessment-criteria source sufficient for grounded authoring, or will a reviewer guide/annex also be needed as a supplement?

## 1. Problem Statement

- The product risks overstating readiness because technical defenses are ahead of real canonical call breadth.
- The next WF must answer a concrete product question: can we add one more real official-source call that meaningfully broadens trust in multi-call support?
- `WF-0061` is specifically about `MSCA-PF-2025`, not a generic "maybe MSCA someday" placeholder.
- The backlog wording that bundles multiple call re-authorings together is too broad and partially obsolete after WF-0044.
- Fake progress in this WF means any work that does not move one official-source `MSCA-PF-2025` call toward validated canonical coverage.
- If `MSCA-PF-2025` exposes a broader product blocker, default response is to stop and either apply only the smallest compatibility fix truly required for this one call or explicitly pause for re-scope.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 1)

Contract notes / non-obvious constraints:
- This WF must not become another "strengthen the framework first" loop.
- A WF that touches several calls at once is likely to hide incomplete source grounding and violate the repo's one-call-at-a-time discipline.
- The right unit of progress here is one new canonical call from official sources, fully validated, not another meta-workflow around onboarding.
- Phase 0/1/2 planning may proceed before uploads, but Phase 3 must stop and request `MSCA-PF-2025` source documents before any substantive YAML authoring.
- Broader fixes are allowed only when they are the smallest compatibility change required to land `MSCA-PF-2025`; they are not permission to reopen platform scope.

## 2. Desired Outcome

- `MSCA-PF-2025` exists as one new promised official-source canonical call not already represented in current canonical coverage.
- That call has one expected canonical artifact target: `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`.
- The call passes the agreed validation baseline, ingests locally without schema ambiguity, and has one deterministic operational proof that it can be exercised through the intended product path.
- The WF produces enough evidence to show real call expansion happened, not just YAML drafting or planning churn.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 2)

Contract notes / non-obvious constraints:
- `WF-0061` is not complete if it stops at planning-only or dry-run-only evidence.
- Minimum proof bar is: canonical YAML validation pass, local ingest pass, and at least one deterministic verification proving the call can be exercised through the intended product path selected in later planning.
- Runtime proof should be minimal but real; do not inflate this into full cross-surface parity work.
- Existing canonical calls are not in-scope for re-authoring in this WF unless `MSCA-PF-2025` depends on a direct compatibility fix.

## 3. Target User / Actor

- Primary actor: internal developer/operator onboarding a new real funding call as code.
- Secondary actor: product/demo owner who needs evidence that the system is becoming a credible multi-call reviewer rather than a narrow single-family tool.
- End-user value remains downstream and real: researchers only benefit if the new call is grounded in official source truth and survives validation.
- The target user for this WF is not a general admin UX audience; this is a product-readiness and call-onboarding proof workflow.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 3)

Contract notes / non-obvious constraints:
- Optimize for operator trust and product-proof value, not UI breadth.
- Success depends on evidence that the system can support one more real call safely through the intended product path, not on exposing every possible user-facing convenience.

## 4. Rough Idea (Unstructured Thinking)

- Split the stale broad backlog ambition into smaller WFs and start with one call only.
- Use this WF to onboard `MSCA-PF-2025` from official source documents, create the traceability manifest, validate it, ingest it locally, and capture the minimum proof that the call is operationally real.
- Prefer a call that does not force unrelated platform rewrites. If the chosen call immediately demands major nested-UI or runtime redesign, that is a scoping warning, not a license to expand this WF.
- Default implementation direction is to add one canonical MSCA file and only the smallest direct compatibility fix needed to support it safely.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 4)

Contract notes / non-obvious constraints:
- There is no secondary “framework deliverable” in this WF.
- If `MSCA-PF-2025` cannot fit the current product path without broad redesign, that is a planning warning to surface early rather than an excuse to absorb more scope.

## 5. Constraints

- Hard scope: one call only.
- Hard source gate: before substantive YAML authoring, explicitly stop and request the official `MSCA-PF-2025` application/narrative-structure source and the official evaluation/assessment-criteria source. Reviewer guide or annexes are optional supplements if needed.
- Do not bundle frontend work, cross-call runtime hardening, ops/governance cleanup, or a second call.
- Keep implementation tasks small enough that later Phase 2 / Phase 3 work can still respect the repo's bounded-step discipline.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 5)

Contract notes / non-obvious constraints:
- Pre-authoring planning is allowed before uploads; YAML authoring is not.
- If `MSCA-PF-2025` would force more than one major surface change at once, this WF should stop and surface that as a blocker instead of quietly widening scope.
- Compatibility fixes must stay limited to the smallest change needed to land this one call safely.
- Any compatibility fix discovered during implementation must carry scoped regression evidence; do not accept an unverified “necessary fix.”

## 6. Risks / Unknowns

- Biggest risk: calling this "real expansion" while secretly spending most of the WF on new onboarding machinery.
- Another risk: choosing a call whose source structure forces broad UI/runtime redesign, which would make delivery look busy but not increase validated coverage safely.
- There is also a backlog-governance risk: if P1 #11 is treated as still-current literally, the WF could bloat into another multi-call umbrella.
- Another concrete unknown is how much of `MSCA-PF-2025` fits the current structured-review path without requiring broader runtime or UX expansion.
- The upload-gate discipline itself is a guardrail: without the official sources, any early YAML confidence would be false confidence.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md` (Section 6)

Contract notes / non-obvious constraints:
- Ambiguity should be treated as a blocker candidate in Phase 0.2, not hand-waved into later phases.
- The risk response is to tighten scope and evidence requirements, not to increase framework ambition.

## Open Questions / Deferred

- Defer any second new call to a follow-on WF.
- Defer any product-wide call onboarding framework cleanup unless Phase 3 reveals a narrow blocker that must be fixed for the selected call.

## 7. MVP Definition

- Smallest valid slice:
  - land one new promised canonical call: `MSCA-PF-2025`,
  - enforce source upload gate,
  - author one canonical YAML plus traceability manifest from official sources for `MSCA-PF-2025`,
  - make its validation / local ingest pass,
  - capture the minimum deterministic operational proof that it is a real supported call through the intended product path selected in later planning.

## 8. Explicit Non-Goals

- Re-authoring all existing canonical calls again.
- Bundling multiple new calls into one WF.
- Frontend redesign, universal nested-call support expansion, or review-detail redesign unless directly forced by the selected call and explicitly re-approved.
- Cross-call runtime hardening, contract-governance expansion, CI/ops cleanup, or policy framework work.
- Any vague "call onboarding platform" work without a concrete new call delivered.
