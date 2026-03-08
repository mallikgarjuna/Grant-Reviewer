<!-- docs/brainstorms/completed/brainstorm-WF-0063-universal-node-visibility-reviewability.md -->
# WF-0063 — Universal Node Visibility Reviewability Brainstorm

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1-3 "Contract Notes / Non-obvious constraints" bullets and link to the relevant Q&A section header.

---

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Preflight Intake)

Current problem framing:

- PeerLens has a structural fidelity gap in the universal submit/review flow for real funding calls, exposed clearly by `MSCA-PF-2025`.
- The current UI effectively treats `node_expectations` as the gate for whether a proposal node appears at all, so only directly criteria-linked sections render.
- In `MSCA-PF-2025`, that causes Part B1 Sections 1-3 to appear while hiding other official proposal nodes such as the abstract and Part B2 Sections 4-8 even though they are part of the real application structure.
- This is a modeling problem, not just a frontend bug: `node_expectations` is currently overloaded to mean official structure, UI visibility, and direct reviewability at once.
- The obvious quick fix, adding fake expectations to non-primary sections just to force visibility, would corrupt the meaning of expectations and violate the source-grounded authoring posture.

Contract Notes / Non-obvious constraints:

- Official proposal structure and criteria-linked reviewability are distinct concepts and should not be collapsed into one YAML field. See Preflight Intake in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- The initiative must preserve strict source-grounded evaluation criteria/elements mapping for primary reviewed sections. See Preflight Intake in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.

Who experiences it?

- Researchers using universal submit for real structured calls experience a misleadingly incomplete application form when official supporting/context sections are hidden.
- Call authors and maintainers also experience pressure to misuse `node_expectations` purely to force visibility.

Why does it matter now?

- `MSCA-PF-2025` exposes that the current contract cannot faithfully represent official call structure without either hiding real nodes or corrupting evaluation semantics.
- This must be corrected before more real multi-agency calls are onboarded on top of the same flawed visibility/reviewability coupling.

Section 1 decisions:

- Primary WF problem: split structural visibility, primary reviewability, and supporting/context semantics into separate concepts.
- Narrow first user pain: researchers cannot see the real application structure for a selected call.
- Framing: universal contract problem with `MSCA-PF-2025` as the proof example.
- Current wrong behavior: hiding nodes that materially affect interpretation or completeness is a product defect.
- Boundary: this WF will not invent new evaluation criteria/elements mappings for unsupported nodes.

Contract Notes / Non-obvious constraints:

- The WF should claim a universal contract correction, not an MSCA-only patch, but the first proof target remains `MSCA-PF-2025`. See Section 1 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- The user-facing defect is structural incompleteness, not yet a promise of richer scored review for supporting nodes. See Section 1 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
---

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 2)

Desired end state:

- Official visible/supporting nodes appear in the UI without fake expectations.
- Call authors can model full official proposal structure without abusing criteria-linked expectations as a visibility hack.
- Researchers can see and draft the real proposal structure in one place.
- The product becomes able to use supporting nodes later for context/compliance without redefining primary review semantics in this WF.
- MVP success is a universal contract direction plus one proof call that can represent visible-but-non-primary nodes safely.

Contract Notes / Non-obvious constraints:

- Success for this WF is structural and contractual correctness first, not expanded scored feedback coverage. See Section 2 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- Future context-aware use of supporting nodes is enabled, but not promised as fully solved in this workflow. See Section 2 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.

---

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 3)

Primary actor:

- Researchers using the universal submit flow for real structured calls are the primary user affected in MVP scope.
- Secondary actors are call authors/maintainers who currently face pressure to misuse `node_expectations` to force visibility.

Current behavior:

- Researchers select a structured call and are shown only directly expectations-backed sections rather than the full official structure.
- Call authors must choose between structural fidelity and semantic fidelity when authoring non-primary nodes.

Current frustration:

- Researchers cannot trust the UI to reflect the actual application form.
- Maintainers risk encoding fake review semantics just to surface required supporting sections.

Contract Notes / Non-obvious constraints:

- Researcher-facing correctness is the primary user problem; authoring relief is important but secondary in MVP prioritization. See Section 3 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- This WF targets the universal structured-call path rather than internal-only admin tooling. See Section 3 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.

---

## 4. Rough Idea (Unstructured Thinking)

Current directional thinking:

- Split structural visibility, primary reviewability, and supporting/context-only usage into separate concepts.
- Keep every official proposal section representable as a node.
- Keep direct criterion-grounded review strict and source-justified rather than manufacturing mappings for visibility.
- Allow supporting sections to contribute context, completeness, or compliance signals without pretending they are primary scored sections.
- Prove the model on `MSCA-PF-2025` first, not by broad multi-call migration.
- Treat the first slice as a contract clarification and product-correctness move, not a full engine redesign.

## Repo Reality Snapshot (Read-Only)

- `frontend/src/lib/submit/renderModel.ts` currently renders only nodes where `has_expectations` is true, so visibility is hard-coupled to expectations today.
- `frontend/src/components/submit/UniversalSubmitForm.tsx` builds submission and compliance payloads from the same rendered node set, so UI visibility and review payload composition are coupled in one flow.
- WF-0035 explicitly scoped the universal submit UI to flat nodes and treated nested/hierarchical structures as unsupported MVP territory; later work added proof-call support rather than a general visibility/reviewability split.
- Existing backend/API contracts expose `has_expectations` as a derived hint, but there is no separate concept for visible-but-non-primary nodes.
- Prior repo ideas already point toward richer cross-node semantics (`requires_context_from` in parking lot), which suggests the current contract is too shallow for supporting/context-only sections.

Open questions suggested by repo snapshot:

- Should the new contract be introduced in YAML only first, or end-to-end through API/UI in the same WF?
- How much backward compatibility is required for already ingested calls and tests that assume `has_expectations` drives renderability?
- Should context-only nodes be submitted in the same request shape as primary nodes or a separate payload branch?
- Is the first slice MSCA-only proof of concept or a universal contract change with MSCA as proof target?
- How should review outputs represent “considered as context” versus “directly evaluated” without confusing researchers?

Section 4 decisions:

- Simplest direction: separate node roles so official nodes can be visible without all being primary reviewed nodes.
- First proof target: `MSCA-PF-2025`.
- Preserve strict criteria-grounded primary review semantics while creating room for supporting/context-only nodes.
- Keep all official proposal nodes representable in YAML and preserve structural completeness in node tree/list contracts independent of whether a node has expectations.
- Defer full review-engine redesign and advanced context behavior to later phases/workflows.

Contract Notes / Non-obvious constraints:

- The rough idea must stay contract-level and MVP-focused; it should not commit to a large cross-agency migration plan yet. See Section 4 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- The first contract correction should be architectural, not funder-semantic: official-node visibility must stop depending on `node_expectations`. Added from review-and-harden pass.

---

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 5)

Constraints:

- Repo-safe and narrow: do not turn this into a broad engine overhaul.
- Preserve backward compatibility where feasible for current structured calls, API contracts, and tests.
- Avoid bulk multi-call reauthoring/migration in the first slice.
- Do not introduce speculative criteria/elements mappings for non-primary nodes.
- Keep the first deliverable small enough to validate quickly on one proof call.
- Rollout must be proof-call-first: preserve current behavior for existing expectation-backed calls before any broader universal flip.
- Supporting/context-only nodes must fail closed semantically: they must not silently alter primary criterion-grounded review outputs unless a later explicit traced contract authorizes that behavior.
- Initial UI behavior must distinguish primary-reviewable nodes from supporting/non-primary nodes rather than silently presenting one undifferentiated input class.

Contract Notes / Non-obvious constraints:

- Existing contracts and tests assume `has_expectations` is meaningful, so any split must manage compatibility carefully. See Section 5 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- Official source grounding remains a hard boundary even if product UX wants broader visibility. See Section 5 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- “Repo-safe” specifically means no broad default-behavior flip until proof-target parity is demonstrated. Added from Part B risk audit.
- Proof-call-first scope also means the first path should keep primary review submission semantics explicit; visible supporting nodes must not be silently accepted as if they were primary reviewed content. Added from review-and-harden pass.

---

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 6)

Key risks:

- The team may over-generalize into full context-aware engine design before proving the minimal contract split.
- Supporting nodes may accidentally inherit primary review semantics in code or copy, confusing researchers.
- Backward compatibility may be more fragile than expected because current frontend/backend logic assumes visibility follows expectations.
- The first slice may reveal that “supporting/context-only” needs a clearer review-output vocabulary than currently assumed.
- The proof target may surface hidden coupling in submit/compliance/review-detail paths beyond the current understanding.
- Conditional or agency-specific supporting-node rules may be accidentally universalized from the MSCA proof target too early.

Contract Notes / Non-obvious constraints:

- The most fragile assumption is that visibility can be split cleanly from reviewability without deeper payload/output consequences; Phase 1 must validate that explicitly. See Section 6 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.

---

## Open Questions / Deferred

- Exact field names and schema shape for the node-role split. Deferred to Phase 1.
- Whether supporting nodes travel in the same request payload branch as primary nodes or a separate context path. Deferred to Phase 1.
- How review detail should represent “considered as context” versus “directly evaluated.” Deferred to Phase 1.
- Whether `abstract` and each MSCA Part B2 section should all share one supporting-role policy or be differentiated further. Deferred to Phase 1.
- Whether the first implementation slice touches YAML only, UI only, or an end-to-end contract seam. Deferred to Phase 1.
- How conditional supporting nodes (for example MSCA Section 9) should be represented without over-generalizing the proof target. Deferred to Phase 1.
- What exact parity checks are required across YAML, API, submit/compliance payloads, and review-detail labeling before any rollout expands beyond the proof target. Deferred to Phase 1.
- Whether the first proof-call UI renders supporting nodes as read/write but non-submittable in the primary review path, or hides submission affordances behind a later context mode. Deferred to Phase 1.

---

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 7)

If we had to ship in 2-3 days:

- Smallest functional slice:
  - define a universal contract direction that separates official node visibility from primary reviewability,
  - prove it on `MSCA-PF-2025`,
  - allow the proof call to represent visible-but-non-primary sections safely without fake expectations.
- Structural completeness invariant for MVP:
  - official nodes remain present in YAML,
  - node tree/list contracts remain structurally complete regardless of expectations,
  - the first UI path distinguishes visible supporting nodes from primary reviewable nodes.
- Must preserve:
  - source-grounded primary review semantics for B1 Sections 1-3,
  - no invented criteria/elements mappings for abstract or Part B2 Sections 4-8.
- Explicitly excluded from MVP:
  - broad multi-call migration,
  - final context-aware engine behavior,
  - new scored review-card semantics for supporting sections,
  - solving all agency-specific nuances.
- Phase 1 validation seams must explicitly cover:
  - YAML/authoring contract,
  - API visibility contract,
  - submit/compliance payload boundary,
  - review-detail/output labeling for primary-evaluated versus supporting-context content.

Contract Notes / Non-obvious constraints:

- MVP success is a safe proof of the contract split, not completion of the full supporting-node behavior model. See Section 7 in `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md`.
- “Proof call” is not enough by itself; parity and fail-closed rollout rules must be explicit before broader adoption. Added from Part B risk audit.

---

## 8. Explicit Non-Goals

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md` (Section 8)

Non-goals:

- Do not redesign the full universal review engine end-state in this WF.
- Do not reauthor many calls at once.
- Do not invent new scoring logic or fake expectations for unsupported sections.
- Do not promise that all visible nodes will generate criterion-grounded review cards.
- Do not solve every conditional/agency-specific nuance, including broader non-MSCA supporting-node policies, in the first slice.

---

## 9. Parked Scope Creep (Tracked Follow-up, Not MVP)

The following ideas are valid but explicitly parked so WF-0063 stays a proof-call-first contract correction rather than expanding into engine redesign:

- Richer three-axis modeling beyond MVP:
  - structural visibility,
  - direct criterion reviewability,
  - supporting/secondary context semantics.
- A future explicit contract with fields or equivalents such as:
  - `is_visible_in_ui`,
  - `is_primary_review_node`,
  - `is_supporting_node`.
- A future supporting-context execution path where visible supporting nodes can influence interpretation, completeness, cross-node checks, or reviewer reasoning without pretending they are primary scored sections.
- A future universal supporting-node policy beyond the `MSCA-PF-2025` proof call, once parity is proven and the semantics are explicitly traced.

Why parked here:

- WF-0063 only needs to separate structural visibility from primary reviewability safely.
- Adding a richer supporting-context engine now would create scope creep across submit/compliance/review-detail and likely push this WF into review-engine redesign.
- The current WF already reserves the seam (`supporting context`) and keeps it fail-closed in MVP, which is the safe stopping point for this branch.

Traceability / references:

- Architect recommendation carried in chat on 2026-03-08: separate structural visibility, direct criterion reviewability, and supporting/secondary context; do not overload `node_expectations`.
- This brainstorm Sections 1, 4, 5, and 7.
- `docs/prds/completed/prd-WF-0063-universal-node-visibility-reviewability.md`:
  - Deferred Stories `DS1`, `DS3`
  - Functional Requirements `FR9`, `FR11`, `FR12`
  - Deferred / Not in MVP
- Parked for future prioritization in `docs/parking_lot.md`.
