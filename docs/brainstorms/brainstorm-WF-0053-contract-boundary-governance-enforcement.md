# WF-0053 — Contract Boundary Governance Enforcement

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-04

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions.
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If Q&A introduces new contract content, promote it here and log it in `docs/logs/decisions.md`.

## Repo Reality Snapshot (Read-Only)

Date: 2026-03-04

- CI already enforces contract-gate marker selection with strict marker validation: `.github/workflows/ci.yml` runs `pytest ... -m contract_gate --strict-markers -q`.
- Recent workflow memory explicitly warns about namespace drift and requires CI selector updates when new contract namespaces are added.
- WF-0052 is completed with compatibility/digest coverage and contract-gate inclusion evidence; follow-on hardening can stay narrowly additive.
- Current contract boundary surfaces include strict nested handling for `stage_gating`, `prompt_knobs`, and `reviewer_policy`; gaps are now governance coupling and fail-closed process enforcement.
- Existing docs and walkthrough evidence are strong, but PR/CI policy linkage for boundary-file changes is not yet codified as a strict merge gate in one bounded WF.

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Preflight + Section 1)

- Problem: contract-boundary protections exist, but governance coupling around boundary changes is still permissive enough to allow process drift.
- Primary affected actor: maintainers/reviewers responsible for merge safety and contract stability.
- Why now: follow-on hardening items are identified and should be codified before additional boundary expansions.
- Contract Notes / Non-obvious constraints:
  - This WF focuses on enforcement and coupling, not runtime product semantics.
  - Existing strict-marker CI guard is baseline behavior; WF-0053 should treat it as a governance invariant.
  - Any new policy must be fail-closed for boundary-affecting change classes.

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 2)

- Primary success signal: boundary-affecting changes are blocked unless required contract-gate and artifact evidence is present.
- Secondary success signal: one explicit negative CI smoke proves fail-closed behavior for missing coupling conditions.
- Compatibility hardening is included as bounded follow-on: one WF-0052 matrix extension for omitted-vs-explicit-default digest equivalence across `stage_gating`, `prompt_knobs`, and `reviewer_policy`.
- Good-enough threshold: deterministic, auditable, and reviewable enforcement paths with no manual interpretation needed.
- Contract Notes / Non-obvious constraints:
  - Enforced outcomes must be objective and machine-checkable, not reviewer convention.
  - Existing strict-marker baseline remains mandatory and is not optional in variants.

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 3)

- Primary actor: release owners/CI maintainers who approve merges and must guarantee contract safety.
- Secondary actor: contributors touching boundary files who need deterministic pass/fail guidance.
- Behavior change expected: contributors include required evidence in the same PR rather than relying on reviewer memory.
- Contract Notes / Non-obvious constraints:
  - Governance UX should bias toward clear remediation messages when checks fail.
  - Ownership remains at merge policy layer, not endpoint runtime behavior.

## 4. Rough Idea (Unstructured Thinking)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 4)

- Define a canonical boundary-change trigger set and pair it with required evidence checks in CI/PR.
- Keep enforcement in existing pipeline shape where possible; add only minimal new guard rails.
- Include one explicit negative smoke that fails when required coupling is missing, demonstrating fail-closed policy.
- Keep matrix extension isolated and deterministic to avoid broad test churn.
- Contract Notes / Non-obvious constraints:
  - Prefer additive governance checks over replacing existing contract-gate execution.
  - Avoid introducing new runtime contracts in this workflow.

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 5)

- Timebox: fit within a small hardening slice aligned to current branch cadence.
- Technical constraint: do not destabilize CI runtime materially; keep checks deterministic and bounded.
- Policy constraint: merge safety must be fail-closed for in-scope boundary-change classes.
- Documentation constraint: artifact traceability must remain explicit in workflow docs.
- Boundary trigger inventory (candidate, to be finalized in PRD):
  - Request-boundary contract models/schemas (engine contracts and request validator surfaces).
  - Contract-gate test selectors/markers and CI contract-gate invocation wiring.
  - Workflow artifacts providing contract traceability evidence (task + walkthrough).
- Contract Notes / Non-obvious constraints:
  - Keep scope to governance and bounded compatibility hardening only.
  - Preserve existing boundary semantics and error contracts.

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 6)

- Major risk: overbroad boundary-file triggers causing noisy failures and policy fatigue.
- Major risk: under-scoped trigger set allowing silent governance bypass.
- Major risk: artifact-coupling rules becoming advisory due to weak negative enforcement.
- Validation need: confirm fail-closed behavior with one deterministic negative case in CI path.
- Contract Notes / Non-obvious constraints:
  - Trigger set should be explicit and reviewable, not heuristic-only.
  - Negative evidence is required to prove enforcement semantics.

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 7)

- Must-have slice:
  - Boundary-file change detection + required evidence coupling policy.
  - CI/PR fail-closed behavior for missing required evidence.
  - One negative smoke proving fail-closed enforcement.
  - One bounded WF-0052 compatibility matrix equivalence case.
- Explicitly excluded from MVP:
  - Runtime pipeline behavior changes.
  - Broad contract model redesign.
  - Multi-dimensional producer realism expansion beyond one targeted case.
- Acceptance checklist (all required):
  - Positive path: in-scope boundary changes with required evidence pass CI.
  - Negative path: missing required coupling fails CI deterministically (fail-closed smoke).
  - Marker guard: unregistered marker usage fails under strict-marker enforcement.
  - Compatibility add-on: one multi-surface omitted-vs-explicit-default digest-equivalence case is covered and documented.
- Contract Notes / Non-obvious constraints:
  - MVP enforces policy correctness first; optimization can follow.

## 8. Explicit Non-Goals

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0053-contract-boundary-governance-enforcement.md` (Section 8)

- No redesign of reviewer outputs, evaluation logic, or call-definition authoring semantics.
- No new frontend UX or non-governance product surfaces.
- No replacement of existing contract-gate suite; only governance coupling hardening.
- No broad test-matrix explosion in this WF.
- Contract Notes / Non-obvious constraints:
  - Deferred items should move to future WF artifacts, not be silently included.

## Open Questions / Deferred

- Decide canonical boundary-file trigger map (Phase 1: PRD contract section).
- Decide mandatory artifact bundle for trigger hits (Phase 1: FRs + acceptance checks).
- Decide exact negative CI smoke implementation point (Phase 2 task slicing).
- Optional producer realism hardening beyond one added digest-equivalence case (future WF unless capacity remains).
