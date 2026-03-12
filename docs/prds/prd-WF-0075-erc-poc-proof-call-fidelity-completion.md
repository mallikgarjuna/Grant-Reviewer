<!-- docs/prds/prd-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-12

## 0. User Stories (MVP)

- US1: As a maintainer, I want `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` to preserve all official page-43 subordinate prompts across `1.a`, `1.b`, and `1.c`, so that the ERC PoC proof-call is honestly fidelity-complete.
- US2: As a maintainer, I want fail-closed proof that distinguishes absent-by-source, fully encoded, and partially encoded subordinate-prompt states, so that a partially encoded real proof-call cannot pass as complete.
- US3: As a maintainer, I want WF-0074 compatibility posture and runtime-boundary honesty preserved while completing the proof-call, so that this workflow does not silently reopen mechanism/governance or overclaim runtime impact.

## Deferred Stories (Not in MVP)

- As a runtime owner, I want structured-review execution to consume subordinate prompts directly during review generation.
- As a maintainer, I want repo-wide migration of remaining flat canonical YAMLs with official subordinate prompts.
- As a schema owner, I want broader call-definition or ontology redesign for subordinate-prompt modeling.

## 1. In Scope

- Complete `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` so `1.a`, `1.b`, and `1.c` each preserve the official subordinate prompts/questions from `wp_horizon-erc-2026_en.pdf` page 43. `(US1)`
- Add a source-grounded, fail-closed proof seam for the real ERC PoC proof-call that can classify subordinate-prompt coverage as absent-by-source, fully encoded, or partially encoded. `(US2)`
- Add the narrowest supporting test, checklist, or authoring-contract clarification required to enforce that three-state distinction for this proof-call without reopening WF-0074. `(US2) (US3)`
- Preserve WF-0074's approved temporary compatibility posture for existing flat canonical YAMLs and preserve the expectations-only runtime boundary. `(US3)`

## 2. Out of Scope

- Any runtime-consumption change that makes structured-review generation use subordinate prompts. `(US3)`
- Repo-wide enforcement that all existing flat canonical YAMLs must now fail immediately. `(US3)`
- Generic schema, ontology, or multi-call migration work beyond the ERC PoC proof-call and its minimum closure proof. `(US3)`
- UI, BFF, or researcher-facing runtime behavior changes. `(US3)`

## 3. User / System Flow

- Happy path
  - The maintainer compares page 43 of `wp_horizon-erc-2026_en.pdf` against the current ERC PoC canonical YAML and confirms `1.b` and `1.c` are still missing subordinate prompts while `1.a` is already encoded. `(US1)`
  - The maintainer updates `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` using the existing typed `subordinate_prompts` structure so `1.a`, `1.b`, and `1.c` all preserve the official page-43 prompts with stable IDs and source locators. `(US1)`
  - The maintainer runs targeted validation and coverage proof for the real proof-call, producing evidence that each official page-43 prompt maps to an exact YAML path or prompt ID. `(US1) (US2)`
  - The proof seam verifies the three-state distinction: elements with no subordinate prompts by source are treated as absent-by-source, the ERC PoC page-43 elements pass only when fully encoded, and partial encoding fails closed. `(US2)`
  - The maintainer records closure evidence and confirms no claim was made beyond WF-0074's temporary compatibility posture or expectations-only runtime boundary. `(US3)`
- Failure path 1
  - `1.b` or `1.c` remains flat or omits one official page-43 subordinate prompt, so the targeted proof fails and the proof-call cannot be labeled fidelity-complete. `(US1) (US2)`
- Failure path 2
  - The validation seam proves only schema validity or dry-run success but cannot map source prompts to exact YAML paths, so closure remains blocked as insufficient completeness evidence. `(US2)`
- Failure path 3
  - A proposed fix tightens runtime consumption or broadens flat-call rejection beyond the approved WF-0074 posture, so the change is rejected as scope drift. `(US3)`

## 4. Functional Requirements

- FR1 (US1): `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` must encode typed `subordinate_prompts` for the official evaluation elements `1.a`, `1.b`, and `1.c` from `wp_horizon-erc-2026_en.pdf` page 43.
- FR2 (US1): Every ERC PoC subordinate prompt added for `1.a`, `1.b`, and `1.c` must carry stable prompt IDs plus source traceability metadata sufficient to map back to page 43.
- FR3 (US2): The implementation must provide a replayable proof seam that checks completeness of official page-43 subordinate prompts against the real ERC PoC proof-call, not only a fixture or synthetic example.
- FR4 (US2): The proof seam must fail closed when a source prompt present on page 43 is missing from the canonical YAML for `1.a`, `1.b`, or `1.c`.
- FR5 (US2): The proof seam must distinguish three states explicitly: absent-by-source, fully encoded, and partially encoded.
- FR6 (US2): MVP verification must include at least one negative case showing that omission of an official `1.b` or `1.c` subordinate prompt causes closure failure.
- FR7 (US3): Any supporting doc/checklist/governance edit must be narrowly corrective, preserve WF-0074 as prior truth, and must not reopen the already-landed subordinate-prompt mechanism or bounded compatibility posture.
- FR8 (US3): No PRD, implementation, or verification step may claim runtime review-generation impact while the activated snapshot seam remains limited to `schema_version` plus `expectations`.
- FR9 (US3): Closure evidence must include a baseline-anchored scope proof using `main...HEAD` and cite the approved WF-0074 boundary artifacts for compatibility posture, proof-call policy, and runtime-boundary honesty.

## 5. Data & API Contracts

- Canonical YAML contract `(US1) (FR1) (FR2)`
  - `evaluation_criteria[*].evaluation_elements[*].subordinate_prompts` remains the required typed shape for this re-authored proof-call.
  - Each prompt item must preserve stable identity and source metadata for page-43 traceability.
  - `elem_approach_methodology` and `elem_pi_strategic_leadership` must no longer remain flat-only elements once WF-0075 lands.
- Coverage-proof contract `(US2) (FR3) (FR4) (FR5) (FR6)`
  - Input must include a source-grounded expectation set for page-43 prompts under `1.a`, `1.b`, and `1.c`.
  - Output must classify each relevant element as `absent_by_source`, `fully_encoded`, or `partially_encoded`.
  - `partially_encoded` must be treated as a failing state for the ERC PoC proof-call because page 43 does contain subordinate prompts for all three elements.
  - The proof artifact must identify exact YAML prompt IDs or paths for successful matches and exact missing prompt labels for failures.
- Validation/state-transition contract `(US2) (US3) (FR3) (FR8) (FR9)`
  - Dry-run or schema validation may support closure, but cannot substitute for source-to-YAML completeness proof.
  - A proof-call state may transition from `partially_encoded` to `fully_encoded` only when all page-43 prompts are preserved and the negative partial-coverage check fails as expected.
  - Compatibility state for unrelated existing flat canonical YAMLs remains unchanged by this WF unless separately re-approved.

## 6. Components / Modules

- Canonical call artifact
  - `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
  - Responsibility: preserve the real ERC PoC evaluation criteria/elements and official subordinate prompts faithfully.
- Validation / proof seam
  - Existing call-ingest or call-validation test/script seam, plus the narrowest new targeted coverage check if current validation cannot classify absent/complete/partial states.
  - Responsibility: prove page-43 prompt coverage for the real proof-call fail closed.
- Authoring governance surfaces
  - Existing checklist / authoring guidance or equivalent narrow contract seam only if needed to make the three-state distinction explicit outside tests.
  - Responsibility: preserve WF-0074 governance without widening to repo-wide migration or runtime claims.
- Design tree (dependencies + ordering)
  - 1. Confirm page-43 prompt inventory and current YAML gap.
  - 2. Complete the canonical YAML for `1.b` and `1.c`.
  - 3. Add or tighten the fail-closed proof seam for absent/complete/partial classification.
  - 4. Apply only minimal corrective governance wording if proof semantics would otherwise remain ambiguous.
  - 5. Re-run targeted validation and closure evidence collection.
- Deep modules / public seams
  - Prefer one narrow proof interface that accepts source-grounded expectations and the real call artifact, hiding matching details internally while exposing deterministic pass/fail and classification output.

## 7. Edge Cases

- Page 43 has subordinate prompts for all three ERC PoC elements, so `absent_by_source` must not be accepted for `1.a`, `1.b`, or `1.c` in this proof-call. `(US1) (US2)`
- A proof that only asserts prompt counts, without verifying exact prompt identity or source mapping, is insufficient because counts could still pass with wrong prompt content. `(US2)`
- If an element outside page-43 subordinate-prompt scope genuinely has no subordinate prompts in source, the proof seam must allow `absent_by_source` without treating it as partial encoding. `(US2)`
- If the narrowest corrective wording would accidentally imply repo-wide rejection of legacy flat canonical YAMLs, that wording is invalid for MVP because it reopens WF-0074 compatibility posture. `(US3)`
- If a proposed proof seam depends on runtime review-generation outputs, it is over-scoped and must be rejected. `(US3)`

## 8. Testing Decisions (TDD)

- Public seam first
  - Write a targeted failing test or equivalent executable proof that demonstrates the current ERC PoC proof-call is still `partially_encoded` because `1.b` and `1.c` lack official page-43 subordinate prompts. `(US2) (FR3) (FR4) (FR5) (FR6)`
  - Implement the minimal canonical YAML completion and proof logic needed to make the full-coverage case pass. `(US1) (US2)`
- Test seams
  - Real canonical YAML: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
  - Source-grounded prompt expectation seam derived from page 43 of `wp_horizon-erc-2026_en.pdf`
  - Existing call-ingest / validation seam only if it can be reused without widening scope
- What to mock
  - Mock only external boundaries if necessary for deterministic source-loading or file-system isolation; do not mock the canonical YAML content or the completeness-classification logic itself.
- Minimal test types
  - Unit or narrow integration-ish proof for three-state classification and negative partial-coverage behavior. `(US2) (FR4) (FR5) (FR6)`
  - Targeted call-validation / dry-run regression for the completed ERC PoC proof-call. `(US1) (FR1) (FR2)`
  - Boundary-preservation regression or citation-based proof that unrelated flat canonical YAML compatibility and expectations-only runtime scope remain unchanged. `(US3) (FR7) (FR8) (FR9)`

## 9. Telemetry (Minimal)

- Record deterministic proof outputs sufficient to show:
  - page-43 source prompts considered,
  - exact matched YAML prompt IDs/paths,
  - classification result per relevant element,
  - failing prompt names when partial coverage is detected.
- No new runtime telemetry is required for MVP.

## 10. Deferred / Not in MVP

- Structured-review runtime consumption of subordinate prompts.
- Broad retrofit of flat canonical YAMLs outside the ERC PoC proof-call.
- Any UI or API changes that surface subordinate prompts to researchers.
- Generic authoring-contract redesign beyond the minimal corrective clarification, if any.

## 11. Open Questions (if any)

- Can the existing validation or ingestion test seam be reused directly for source-to-YAML completeness proof, or is one new targeted coverage checker required?
- Is a narrow checklist/authoring wording clarification still needed after the proof seam lands, or will executable coverage proof alone make the absent/complete/partial distinction explicit enough?

## 12. Changelog

- v0.1 (2026-03-12): Initial PRD from brainstorm.
