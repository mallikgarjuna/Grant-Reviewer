<!-- docs/brainstorms/brainstorm-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: brainstorm
Version: v0.1
Status: Draft
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

- The repo now has strong machinery around call definitions, structured review, and contract enforcement, but only four canonical calls.
- Those four calls cover only two agencies: NWO and ERC.
- WF-0044 already consumed the bundled backlog scope around ERC CoG migration plus baseline validation for existing canonical calls; repeating that scope would be fake progress.
- WF-0059 and WF-0060 improved or corrected one ERC proof path, but they do not increase agency diversity or prove broader canonical coverage.
- The real product-risk question is whether PeerLens can onboard another real official-source call without collapsing into more framework work.

### Repo Reality Snapshot (Read-Only) (2026-03-07)

- Canonical call inventory is still limited to:
  - `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
  - `backend/data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml`
  - `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
  - `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
- Parking-lot P1 #11 is stale as-written because WF-0044 already delivered its core bundle: ERC CoG canonical migration plus baseline validation / source-gated refreshes for the named existing canonical calls.
- Parking-lot P1 #12 is closer to the real remaining gap: add one new non-NWO call for agency diversity, with MSCA preferred before ZonMw.
- Current product claims would still be weak if this WF only re-tunes ERC/NWO internals again; that is more framework orbit, not real call-data expansion.
- Source-gating remains hard SSOT: no substantive YAML authoring/re-authoring for a call until that call's official source documents are explicitly uploaded in-workflow.

### Open Questions Suggested by Repo Snapshot

- Which single new official-source call best increases credible coverage with the least framework churn: MSCA first (recommended) or ZonMw first?
- What is the smallest validation bar that proves a new call is real product progress rather than another ingest-only artifact?
- Does the selected call fit current structured-review surfaces without forcing a nested-UI/platform redesign into this WF?
- What source set must be uploaded for the first target call before any YAML authoring can start?

## 1. Problem Statement

- The product risks overstating readiness because technical defenses are ahead of real canonical call breadth.
- The next WF must answer a concrete product question: can we add one more real official-source call that meaningfully broadens trust in multi-call support?
- The backlog wording that bundles multiple call re-authorings together is too broad and partially obsolete after WF-0044.

Contract notes / non-obvious constraints:
- This WF must not become another "strengthen the framework first" loop.
- A WF that touches several calls at once is likely to hide incomplete source grounding and violate the repo's one-call-at-a-time discipline.
- The right unit of progress here is one new canonical call from official sources, fully validated, not another meta-workflow around onboarding.

## 2. Desired Outcome

- One new official-source canonical call exists from a new agency not already represented in canonical coverage.
- That call passes the agreed validation baseline and can be ingested locally without schema ambiguity.
- The WF produces evidence that PeerLens can expand call coverage through the existing product path rather than only through internal framework work.

Contract notes / non-obvious constraints:
- Recommended first target is one MSCA call because it increases agency diversity with the least ambiguity in the current backlog direction.
- Validation should be strong enough to prove product value, but not silently broaden into frontend redesign or cross-call hardening.
- Existing canonical calls are not in-scope for re-authoring in this WF unless the new target depends on a direct compatibility fix.

## 3. Target User / Actor

- Primary actor: internal developer/operator onboarding a new real funding call as code.
- Secondary actor: product/demo owner who needs evidence that the system is becoming a credible multi-call reviewer rather than a narrow single-family tool.
- End-user value remains downstream and real: researchers only benefit if the new call is grounded in official source truth and survives validation.

## 4. Rough Idea (Unstructured Thinking)

- Split the stale broad backlog ambition into smaller WFs and start with one call only.
- Use this WF to onboard one new call from official source documents, create the traceability manifest, validate it, ingest it locally, and capture the minimum proof that the call is operationally real.
- Prefer a call that does not force unrelated platform rewrites. If the chosen call immediately demands major nested-UI or runtime redesign, that is a scoping warning, not a license to expand this WF.

## 5. Constraints

- Hard scope: one call only.
- Hard source gate: before substantive YAML authoring, explicitly stop and request that call's official application-form/instructions plus assessment/evaluation source documents.
- Do not bundle frontend work, cross-call runtime hardening, ops/governance cleanup, or a second call.
- Keep implementation tasks small enough that later Phase 2 / Phase 3 work can still respect the repo's bounded-step discipline.

Contract notes / non-obvious constraints:
- Pre-authoring planning is allowed before uploads; YAML authoring is not.
- If the selected call would force more than one major surface change at once, the call is probably the wrong Phase 3 target for this WF.

## 6. Risks / Unknowns

- Biggest risk: calling this "real expansion" while secretly spending most of the WF on new onboarding machinery.
- Another risk: choosing a call whose source structure forces broad UI/runtime redesign, which would make delivery look busy but not increase validated coverage safely.
- There is also a backlog-governance risk: if P1 #11 is treated as still-current literally, the WF could bloat into another multi-call umbrella.

## Open Questions / Deferred

- Select the exact first target call in Phase 0.1. Recommendation: MSCA first.
- Defer any second new call to a follow-on WF.
- Defer any product-wide call onboarding framework cleanup unless Phase 3 reveals a narrow blocker that must be fixed for the selected call.

## 7. MVP Definition

- Smallest valid slice:
  - choose one new target call from a new agency,
  - enforce source upload gate,
  - author one canonical YAML plus traceability manifest from official sources,
  - make its validation / local ingest pass,
  - capture the minimum smoke-proof that it is a real supported call path.

## 8. Explicit Non-Goals

- Re-authoring all existing canonical calls again.
- Bundling multiple new calls into one WF.
- Frontend redesign, universal nested-call support expansion, or review-detail redesign unless directly forced by the selected call and explicitly re-approved.
- Cross-call runtime hardening, contract-governance expansion, CI/ops cleanup, or policy framework work.
- Any vague "call onboarding platform" work without a concrete new call delivered.
