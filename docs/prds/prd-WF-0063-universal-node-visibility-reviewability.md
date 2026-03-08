<!-- docs/prds/prd-WF-0063-universal-node-visibility-reviewability.md -->
# WF-0063 — Universal Node Visibility Reviewability PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-08

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher using the universal structured submit flow, I want to see the full official proposal structure for a call, so that I can draft against the real application form instead of a criteria-trimmed subset.
- US2: As a researcher submitting for review, I want primary reviewed sections clearly distinguished from supporting sections, so that I understand what is actually evaluated in the first path.
- US3: As a call-definition maintainer, I want official supporting nodes modeled without fake evaluation criteria/elements mappings, so that YAML stays source-grounded.
- US4: As an engineer maintaining structured-call contracts, I want the visibility/reviewability split to land first on `MSCA-PF-2025` without changing current expectation-backed calls by default, so that the correction is safe and traceable.

## Deferred Stories (Not in MVP)

- DS1: A general context-aware review engine where supporting nodes actively inform primary review outputs.
- DS2: A broad cross-call migration that opts many existing calls into supporting-node behavior in the same WF.
- DS3: Rich scoring, card-generation, or compliance semantics for supporting nodes beyond explicit fail-closed handling.
- DS4: New draft-persistence backends, reviewer UX redesign, or authoring-tool redesign unrelated to the contract correction.

## 1. In Scope

- Add one explicit node-role field to the canonical call-definition contract so official proposal structure and primary reviewability stop sharing one overloaded signal. (US1, US2, US3, US4)
- Keep `node_expectations` as the only source-grounded mapping surface for evaluation criteria/elements and do not invent mappings for non-primary nodes. (US2, US3)
- Return all official proposal nodes in node list/tree contracts regardless of whether they carry expectations. (US1, US4)
- Expose visible-but-non-primary nodes to the UI via the API contract and render them with explicit visual distinction from primary reviewed nodes. (US1, US2, US4)
- Keep the first submit/compliance path primary-only and fail closed if supporting nodes are passed as primary review submission content. (US2, US4)
- Define review-detail/output labeling seams for `primary evaluated` versus `supporting context`, while keeping supporting-context participation disabled by default in MVP. (US2, US4)
- Prove the contract on `MSCA-PF-2025`, including visible Part B2 sections and abstract handling, without broad default-behavior flips for other calls. (US1, US3, US4)

## 2. Out of Scope

- Redesigning the full review engine to consume supporting nodes as automatic context for scoring or card generation. (DS1, DS3)
- Re-authoring many existing calls or forcing universal supporting-node rollout in the same WF. (DS2)
- Inventing stronger evaluation criteria/elements mappings for `abstract`, Part B2 sections, or other non-primary nodes without official source grounding. (DS3)
- Solving every conditional-node policy or agency-specific nuance beyond the minimum proof-call-safe behavior needed for `MSCA-PF-2025`. (DS2, DS3)
- Treating the first path as persistent multi-channel draft management; any broader draft-storage redesign is deferred. (DS4)

## 3. User / System Flow

### Happy path

1. Maintainer authors or updates a call definition so every official proposal node remains in YAML and each node has an explicit `node_role` of `PRIMARY` or `SUPPORTING`, with `PRIMARY` reserved for criterion-grounded reviewable content. (US3, US4)
2. Maintainer opts the proof call into split visibility behavior through an explicit call-level/runtime enablement seam; non-opted-in calls retain current behavior. (US4)
3. Validation loads the YAML and enforces that supporting nodes do not gain invented `node_expectations`, while existing expectation-backed primary nodes continue to validate as before. (US3, US4)
4. `GET /calls/{call_id}/nodes` and `GET /calls/{call_id}/nodes?view=tree` return the full official structure, including nodes without expectations, plus the new role metadata needed by the frontend for opted-in calls. (US1, US4)
5. The universal submit UI renders all visible official nodes for the opted-in proof call, keeps structural containers visible as grouping-only, and allows drafting only content-bearing `PRIMARY` and `SUPPORTING` nodes. (US1, US2)
6. When the researcher submits for primary review, the client builds the primary review payload from `PRIMARY` nodes only; supporting-node content remains out of the primary submit/compliance boundary. (US2, US4)
7. Backend validation rejects any attempt to include `SUPPORTING` nodes in the primary review submission payload or compliance payload. (US2, US4)
8. Review creation and review detail expose explicitly which nodes were `primary evaluated`; the reserved `supporting context` output seam remains empty unless a later explicit context path is introduced. (US2, US4)
9. `MSCA-PF-2025` proves the contract by showing `abstract` and Part B2 sections in the UI without fake expectations while preserving existing primary review behavior for Part B1 Sections 1-3 and preserving current behavior for non-opted-in calls. (US1, US2, US3, US4)

### Failure path A — supporting node submitted as primary review content

1. A client includes a `SUPPORTING` node in the primary submit or compliance payload. (US2, US4)
2. Backend validation fails closed with a deterministic contract error instead of silently accepting or ignoring that node as primary reviewed content. (US2, US4)
3. No review record or compliance result treats the supporting node as primary-evaluated evidence. (US2, US4)

### Failure path B — visibility still coupled to expectations

1. A list/tree/render path still filters visibility by `has_expectations` and hides official `SUPPORTING` nodes such as `abstract` or Part B2 sections in `MSCA-PF-2025`. (US1, US4)
2. Contract tests fail because all official nodes must remain present in node list/tree outputs and render eligibility for opted-in calls must derive from node-role-aware structural completeness, not expectation presence alone. (US1, US4)
3. Non-opted-in calls must continue to exhibit current behavior; the proof call is not considered parity-complete until both behaviors are covered deterministically. (US1, US4)

### Failure path C — supporting-context semantics leak into primary review

1. Runtime or copy implies a `SUPPORTING` node influenced primary review output even though no explicit supporting-context path was activated. (US2, US4)
2. Review-detail and response semantics must show no `supporting context` participation for that review, and tests must block any silent context leakage. (US2, US4)
3. The workflow treats such leakage as a blocking semantic regression rather than a UX-only issue. (US2, US4)

## 4. Functional Requirements

- FR1 (US1, US2, US3, US4): `ProposalNodeDefinitionV2` must gain a new field `node_role: Literal["PRIMARY", "SUPPORTING"]` with backward-compatible default `PRIMARY`.
- FR1a (US4): Split visibility/reviewability behavior must be guarded by an explicit call-level or runtime enablement seam in MVP; non-opted-in calls must preserve current behavior until explicitly migrated.
- FR2 (US2, US3, US4): `node_expectations` remains the only source-grounded evaluation criteria/elements mapping surface; this WF must not add invented expectations to supporting nodes.
- FR3 (US2, US3): Any node marked `SUPPORTING` in MVP must have an empty `node_expectations` list unless a later explicitly approved contract says otherwise.
- FR4 (US1, US4): Official node visibility must derive from presence in the call-definition structure plus API node outputs, not from `has_expectations`.
- FR5 (US1, US4): `GET /calls/{call_id}/nodes` and `GET /calls/{call_id}/nodes?view=tree` must continue returning all official nodes and must add `node_role` to each node summary/tree item.
- FR6 (US1, US2): Existing `has_expectations` remains available as a compatibility hint, but frontend visibility/render eligibility for this WF must no longer depend on it alone.
- FR7 (US1, US2, US4): For calls explicitly opted into the split contract, the first submit UI path must render both `PRIMARY` and `SUPPORTING` nodes, with explicit visual distinction between `primary reviewed` and `supporting/non-primary`.
- FR7a (US1, US2, US4): Structural container nodes remain visible/grouping-only and are never editable or submittable in the first path, regardless of role rollout state.
- FR8 (US1, US2): In the first path, supporting content nodes are `read/write but non-submittable for primary review`; they may exist in local draft/UI state, but are excluded from the primary submission boundary.
- FR9 (US2, US4): MVP does not add a separate persisted supporting-context request path; supporting-context submission remains deferred until a later WF defines it explicitly.
- FR10 (US2, US4): Primary review submission and compliance payloads must accept only `PRIMARY` nodes and must fail closed on any `SUPPORTING` node IDs/content.
- FR11 (US2, US4): Review creation, persistence, and detail must preserve the distinction between `primary evaluated` content and reserved `supporting context` content.
- FR12 (US2, US4): Review-detail/output contracts must add explicit labeling seams for `primary evaluated` and `supporting context`, with `supporting context` empty by default in MVP unless a later explicit context mode populates it.
- FR13 (US1, US4): `MSCA-PF-2025` must keep all official nodes in YAML and surface `abstract` plus Part B2 Sections 4-8 in the UI even though they remain non-primary in the first path.
- FR14 (US1, US4): `MSCA-PF-2025` Section 9 conditional handling must remain source-grounded and conditional; this WF must not universalize its applicability.
- FR15 (US2, US3, US4): Existing expectation-backed calls must preserve current behavior until they explicitly opt into `SUPPORTING` nodes; no broad universal flip is allowed before proof-call parity is demonstrated.
- FR16 (US4): Parity sign-off for this WF requires aligned behavior across YAML authoring, node list/tree API responses, submit/compliance payload boundaries, and review-detail labeling.

## 5. Data & API Contracts

### 5.1 Canonical YAML contract

- `backend/app/schemas/call_definitions_v2.py` must recognize `node_role` on `ProposalNodeDefinitionV2` with enum values `PRIMARY` and `SUPPORTING`. (US3, US4, FR1)
- `node_role` is the authoritative authoring signal for primary-vs-supporting intent; `node_expectations` remains authoritative only for criteria/elements linkage. (US2, US3, FR1, FR2)
- In MVP, supporting nodes must validate only when `node_expectations == []`; this creates an explicit fail-closed boundary against fake mappings. (US2, US3, FR3)
- Omitted `node_role` must behave as `PRIMARY` for backward compatibility so existing calls keep current behavior until explicitly migrated. (US4, FR1, FR15)
- The proof-call-first rollout must use one explicit call-level or runtime enablement seam to activate split visibility behavior; `node_role` presence alone is insufficient to flip runtime behavior repo-wide. (US4, FR1a, FR15)
- `MSCA-PF-2025` must encode Part B1 Sections 1-3 as `PRIMARY` and the official non-primary nodes (`abstract`, Part B2 Sections 4-8, and conditional Section 9 when present) as `SUPPORTING` unless later source-grounded evidence changes that classification. (US1, US2, US3, FR13, FR14)

### 5.2 Node list/tree response contract

- `backend/app/schemas/api.py` node response types must add `node_role` to `NodeSummary` and `NodeTreeNode`. (US1, US4, FR5)
- Node list/tree contracts remain structurally complete: every official node in YAML must appear in list/tree output regardless of `node_expectations`. (US1, US4, FR4, FR5)
- `has_expectations` stays in the response for compatibility and debugging, but callers must not treat it as the only renderability signal once `node_role` is available. (US1, US2, US4, FR6)
- Visible-but-non-primary nodes are exposed by the pair `node_role == "SUPPORTING"` and `has_expectations == false`; no synthetic expectations are introduced to force visibility. (US1, US3, FR2, FR5, FR6)
- Opted-in-call render behavior and non-opted-in-call legacy behavior must both be representable from the response contract without ambiguous fallback logic. (US4, FR1a, FR5, FR15)

### 5.3 Submit/compliance request contract

- The existing primary review request path remains the only review-submission path in MVP. (US2, US4, FR8, FR9, FR10)
- Primary submit/compliance payloads must be interpreted as `PRIMARY`-only content, whether they are keyed by node IDs, node logical IDs, or derived rendered-node lists. (US2, US4, FR10)
- Backend request validation must reject any submitted node whose canonical `node_role` is `SUPPORTING`, with a deterministic contract error rather than silent dropping. (US2, US4, FR10)
- Supporting content nodes may remain in client-side draft state for UI continuity, but no persisted review request, compliance check, or review record may treat them as primary-submitted content in MVP. Structural containers remain non-editable and never enter draft state as content-bearing fields. (US1, US2, US4, FR7a, FR8, FR9, FR10)
- No parallel `supporting_nodes` or `context_nodes` request branch is added in this WF; a separate context path is deferred until it has an explicit contract and review-output semantics. (US2, US4, FR9)

### 5.4 Review-detail/output contract

- Review-detail response must preserve the existing primary-path semantics while adding explicit output fields for role-aware participation. (US2, US4, FR11, FR12)
- MVP contract direction:
  - `primary_evaluated_node_logical_ids: list[str]`
  - `supporting_context_node_logical_ids: list[str] = []`
  - optional role-aware notes/copy derived from those fields
  These fields are reserved role-aware output seams that label participation explicitly instead of forcing consumers to infer it from cards alone. (US2, US4, FR11, FR12)
- In MVP, `supporting_context_node_logical_ids` must remain empty for normal primary-path reviews because no supporting-context submission path exists yet. (US2, US4, FR9, FR12)
- Review-detail/UI copy must distinguish at least:
  - `Primary evaluated`
  - `Supporting context`
  - `Visible but not part of this review`
  so the product does not imply that supporting nodes were silently reviewed. (US2, US4, FR11, FR12)
- Supporting nodes must not silently alter primary criterion-grounded review outputs, card generation, or submitted-node coverage accounting unless a later explicit traced contract authorizes that behavior. (US2, US4, FR11, FR12)

### 5.5 Compatibility and rollout contract

- Calls that omit `node_role` remain behaviorally equivalent to current expectation-backed behavior because omission resolves to `PRIMARY`. (US4, FR1, FR15)
- `MSCA-PF-2025` is the proof-call-first opt-in path for `SUPPORTING` nodes and parity checks. (US1, US4, FR13, FR15, FR16)
- The explicit call-level/runtime enablement seam, not `node_role` presence alone, is the MVP rollout gate for `MSCA-PF-2025`. (US4, FR1a, FR15)
- Readiness to expand beyond the proof call requires deterministic parity evidence across:
  - canonical YAML validation,
  - node list/tree response completeness,
  - primary submit/compliance rejection of supporting nodes,
  - review-detail/output role labeling,
  - proof-call opt-in behavior versus non-opted-in legacy behavior. (US4, FR16)

## 6. Components / Modules

- `backend/app/schemas/call_definitions_v2.py`
  - Introduce `node_role` and YAML-level validation that supporting nodes stay expectations-free in MVP. (FR1, FR3)
- Canonical call YAML under `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`
  - Proof-call authoring seam for explicit `PRIMARY` versus `SUPPORTING` node roles while keeping all official nodes in structure. (FR13, FR14, FR15)
- `backend/app/schemas/api.py`, `backend/app/services/node_tree_service.py`, and response assembly in `backend/main.py`
  - Expose role-aware node list/tree outputs and role-aware review-detail fields without removing compatibility fields such as `has_expectations`. (FR5, FR11, FR12)
- `frontend/src/lib/submit/renderModel.ts` and `frontend/src/components/submit/UniversalSubmitForm.tsx`
  - Stop deriving opted-in-call renderability from `has_expectations` alone; render all official nodes for opted-in calls, keep structural containers grouping-only, and enforce primary-path submission from `PRIMARY` nodes only. (FR6, FR7, FR7a, FR8, FR10)
- Review-detail BFF/UI seams under `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` and `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Surface role-aware labels so researchers can tell `primary evaluated` apart from `supporting context` or `not part of this review`. (FR11, FR12)
- Backend/frontend contract tests around nodes API, submit/compliance validation, and review-detail output
  - Prove proof-call parity and fail-closed semantics. (FR10, FR16)

Design tree / dependencies / ordering:
1. Freeze the YAML contract decision: `node_role` exists, defaults to `PRIMARY`, and supporting nodes remain expectations-free. (FR1, FR3, FR15)
2. Freeze the proof-call-first rollout gate: one explicit call-level/runtime enablement seam activates split behavior for `MSCA-PF-2025` only. (FR1a, FR15)
3. Apply the proof-call authoring update to `MSCA-PF-2025` while preserving all official nodes in YAML. (FR13, FR14, FR15)
4. Expose `node_role` through list/tree API responses without removing `has_expectations`. (FR5, FR6)
5. Update the submit render model/UI to render all official nodes for opted-in calls, keep structural containers grouping-only, and submit only `PRIMARY` nodes. (FR6, FR7, FR7a, FR8, FR10)
6. Preserve current behavior for non-opted-in calls. (FR1a, FR15, FR16)
7. Add submit/compliance fail-closed validation against `SUPPORTING` nodes. (FR10)
8. Add review-detail/output labeling seams and parity tests. (FR11, FR12, FR16)

Deep module guidance:

- Keep the authoritative split small: `node_role` is the new semantic field; do not add a broad family of overlapping booleans to YAML in this WF.
- Keep rollout explicit: use one call-level/runtime opt-in seam rather than inferring universal behavior from `node_role` presence alone.
- Treat node list/tree completeness as the visibility contract; the UI should not need fake expectations or synthetic nodes.
- Distinguish `structural container` from `supporting content`; only content-bearing nodes can be editable in the first path.
- Keep supporting-context behavior fail-closed: reserved output fields may exist, but no supporting context participates in primary review until a later explicit request path exists.
- Prefer derived API flags only where they reduce UI branching materially; the core compatibility boundary is still the canonical `node_role`.

Suggested file-path clusters (coarse only):

- call-definition schema and canonical MSCA YAML under `backend/app/schemas/` and `backend/data/calls/canonical/msca/`
- nodes/review-detail response assembly under `backend/app/services/` and `backend/main.py`
- submit rendering and review detail UI under `frontend/src/lib/submit/`, `frontend/src/components/submit/`, and `frontend/src/app/app/reviews/`
- contract tests under `backend/tests/` and frontend page/component tests

## 7. Edge Cases

- A supporting node accidentally gains `node_expectations`; YAML validation must fail rather than treating that as a harmless visibility hack. (US3, US4, FR2, FR3)
- A frontend path still filters visible nodes by `has_expectations` and hides `abstract` or Part B2 sections in `MSCA-PF-2025`; parity tests must fail. (US1, US4, FR4, FR6, FR13, FR16)
- A crafted request submits supporting-node IDs directly to the review or compliance boundary; backend must reject it deterministically. (US2, US4, FR10)
- Review detail labels a supporting node as reviewed because it appeared in UI draft state; this is a semantic regression and must be blocked. (US2, US4, FR11, FR12)
- A future call omits `node_role`; defaulting to `PRIMARY` must preserve current behavior rather than silently hiding nodes or inventing supporting semantics. (US4, FR1, FR15)
- A future call defines `SUPPORTING` nodes but forgets to opt into split behavior; runtime must preserve legacy behavior rather than silently broadening visibility. (US4, FR1a, FR15)
- A structural container is accidentally rendered as an editable field in the first path; UI and contract tests must block that regression. (US1, US2, US4, FR7a, FR16)
- `MSCA-PF-2025` Section 9 appears for non-Global-Fellowship cases or disappears for applicable cases because the supporting-node rollout over-generalized conditional logic; proof-call tests must keep conditional behavior source-grounded. (US1, US4, FR14, FR16)
- A later implementation tries to treat some Part B2 nodes as “quasi-primary” without source-grounded evidence; Phase 2 tasks must keep this as a deferred question unless grounded proof is added. (US3, US4, FR2, FR14, FR15)

## 8. Testing Decisions (TDD)

- This WF changes behavior at the contract/UI boundary, so implementation must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public test seams must cover canonical YAML validation, nodes list/tree responses, submit/compliance validation, and review-detail/BFF output. (US1, US2, US3, US4, FR1-FR16)
- Mock only external boundaries. Do not mock the role-classification logic, node list/tree shaping, or submit filtering logic that this WF is explicitly correcting. (US2, US4)
- Minimum automated coverage required:
  - schema tests proving `node_role` accepts only `PRIMARY` or `SUPPORTING`, defaults to `PRIMARY`, and rejects supporting nodes with non-empty expectations. (US3, US4, FR1, FR3, FR15)
  - proof-call YAML tests proving `MSCA-PF-2025` keeps all official nodes and classifies Part B1 versus supporting nodes as planned. (US1, US3, US4, FR13, FR14)
  - rollout-gate tests proving `MSCA-PF-2025` opt-in activates split visibility behavior while non-opted-in calls preserve current behavior. (US4, FR1a, FR15, FR16)
  - nodes API tests proving list/tree responses include all official nodes and expose `node_role` alongside `has_expectations`. (US1, US4, FR4, FR5, FR6, FR16)
  - submit render-model/UI tests proving supporting content nodes render visibly, structural containers remain grouping-only, display labels stay distinct, and only `PRIMARY` nodes enter primary submit construction. (US1, US2, US4, FR6, FR7, FR7a, FR8)
  - backend request-validation tests proving supporting-node submission to primary review/compliance fails closed. (US2, US4, FR10)
  - review-detail tests proving primary-path reviews expose `primary_evaluated_node_logical_ids`, keep `supporting_context_node_logical_ids` empty by default, and never imply silent supporting-context participation. (US2, US4, FR11, FR12)
  - parity tests proving YAML, API, submit/compliance, and review-detail seams all agree for `MSCA-PF-2025`. (US1, US2, US4, FR16)

## 9. Telemetry (Minimal)

- Add only minimal diagnostics needed to distinguish:
  - proof-call render of supporting nodes,
  - rejection of supporting-node primary submissions,
  - review-detail role-label population.
- Telemetry is not an MVP deliverable unless one small diagnostic is required to prove or debug parity across the touched seams.

## 10. Deferred / Not in MVP

- Separate persisted supporting-context submission mode.
- Automatic use of supporting nodes in scoring, card generation, or prompt context.
- Broad migration of older calls to explicit `SUPPORTING` nodes.
- Finer-grained classifications inside Part B2 unless official source-grounded evidence later justifies it.

## 11. Open Questions (if any)

- The exact researcher-facing copy for the three UI labels (`primary reviewed`, `supporting`, `not part of this review`) is still open, but the contract distinction itself is not.
- Whether a later WF should persist supporting-node drafts server-side or keep them local until a real context mode exists is deferred and not blocking for this PRD.
- The exact name/location of the call-level/runtime opt-in seam is left to Phase 2 tasking, but the behavior contract is fixed: explicit proof-call opt-in, no broad default flip.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
- v0.2 (2026-03-08): Applied risk-audit edits for explicit proof-call rollout gating, structural-container first-path behavior, and opt-in versus legacy parity coverage; marked Ready for Tasks.
