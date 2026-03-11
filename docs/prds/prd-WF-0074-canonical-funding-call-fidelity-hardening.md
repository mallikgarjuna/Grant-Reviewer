<!-- docs/prds/prd-WF-0074-canonical-funding-call-fidelity-hardening.md -->
# WF-0074 — Canonical Funding Call Fidelity Hardening

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-11

## 0. User Stories (MVP)

- US1: As an internal operator authoring a canonical funding call YAML, I want the schema and starter template to represent subordinate official assessment prompts as first-class structured data, so that new or re-authored calls can preserve evaluative fidelity instead of flattening it.
- US2: As an internal operator following repo authoring guidance, I want the authoring workflow docs and checklist to fail closed when official sources contain subordinate evaluative prompts, so that flattening stops being the default behavior.
- US3: As a maintainer protecting current canonical calls, I want an explicit compatibility posture, targeted tests, and one proof-call example, so that fidelity hardening is concrete without forcing a repo-wide migration or pretending the runtime already consumes the new structure.

## Deferred Stories (Not in MVP)

- As a researcher, I want runtime review output to immediately consume subordinate prompt structure end to end in this same WF.
- As a maintainer, I want the full existing canonical call corpus re-authored to the new fidelity contract.
- As a maintainer, I want a generic multi-level evaluation ontology beyond the subordinate prompt structure needed for source-grounded review authoring.

## 1. In Scope

- Hardening the canonical call authoring contract for future or re-authored calls through the smallest governing surfaces:
  - `backend/app/schemas/call_definitions_v2.py`
  - `backend/data/calls/templates/call_definition_v2_template.yaml`
  - authoring docs and onboarding checklist surfaces
  - targeted tests
  - one proof-call example
- Making subordinate official assessment prompts representable as structured data under evaluation elements when the source includes them.
- Explicitly documenting and testing a compatibility posture for existing flat canonical YAMLs.
- Explicitly inspecting the activated snapshot / engine contract seam rooted at `backend/app/services/structured_reviewer_service.py` and `backend/app/engine/contracts.py`, then locking the MVP claim boundary accordingly.
- Keeping Phase 2 planning narrow enough to prefer implementation slices that touch `<=3` files where feasible.

## 2. Out of Scope

- Broad review-engine redesign or prompt-pipeline redesign.
- Re-authoring the entire existing canonical call corpus.
- Inventing subordinate evaluative prompts that are not present in official sources.
- General ontology or knowledge-graph work.
- Researcher-facing UI changes.

## 3. User / System Flow

### Happy Path

1. Maintainer inspects the current authoring and runtime seams and confirms that call-definition V2 currently supports only flat evaluation elements while the structured-review snapshot currently carries only `schema_version` plus `expectations`. (US1, US3)
2. Maintainer extends the authoring schema to represent subordinate official assessment prompts as structured data attached to an evaluation element without breaking existing flat YAML parsing. (US1, US3)
3. Maintainer updates the starter template to demonstrate the new prompt-level fidelity shape as the default copy-forward pattern. (US1)
4. Maintainer updates authoring workflow docs and checklist language so that when official sources contain subordinate prompts, flattening them into one broad element description is a contract violation rather than an acceptable shortcut. (US2)
5. Maintainer adds targeted tests that prove the new structure validates, malformed shapes fail closed, and the chosen compatibility posture for legacy flat YAMLs is explicit and enforced. (US1, US2, US3)
6. Maintainer authors one proof-call example that exercises the new subordinate-prompt shape on a real canonical YAML by default, or documents a fixture fallback rationale if a real call would widen scope disproportionately. (US3)
7. Maintainer records the runtime-impact boundary for this WF: because the inspected snapshot seam currently carries only `expectations`, MVP closure claims authoring-contract hardening and proof of representability/default behavior, not full review-quality improvement from runtime consumption. (US3)

### Failure Paths

1. If the schema adds a new structured field but the template and docs/checklist still teach flattening, the WF is not closure-ready because the repo default remains lossy. (US1, US2)
2. If a proof-call example requires inventing prompts, changing unrelated runtime behavior, or silently widening into multi-call migration work, the WF must stop and narrow back to one justified proof artifact. (US3)
3. If compatibility handling for existing flat YAMLs is left implicit, or tests do not show whether they remain tolerated or rejected, the hardening remains blocked. (US3)

## 4. Functional Requirements

- FR1 (US1): `CallDefinitionV2` planning must introduce a first-class structured field for subordinate official assessment prompts under an evaluation element rather than relying on longer free-text descriptions.
- FR2 (US1): The new subordinate-prompt structure must be additive enough that existing flat canonical YAMLs can remain temporarily ingest-valid during MVP unless later tasks explicitly choose a narrower rejection policy with proof.
- FR3 (US1, US2): The starter template must show at least one evaluation element encoded with subordinate prompt structure so copied examples no longer normalize flattening.
- FR4 (US2): The authoring workflow docs must define when subordinate prompt encoding is required: if official source material contains review-relevant prompts/questions beneath an evaluation element, authors must preserve them explicitly instead of collapsing them into summary prose.
- FR5 (US2): `docs/call-yaml/onboarding-checklist.md` must include a fail-closed fidelity check that asks whether the official source contains subordinate prompts and whether each prompt has been preserved or explicitly justified as absent by source.
- FR6 (US3): The PRD and later tasks must treat compatibility posture as an explicit contract with tests: existing flat YAMLs are temporarily tolerated for backward compatibility, while new or re-authored calls that expose subordinate official prompts must use the new structure.
- FR7 (US3): The workflow must inspect the runtime seam at `backend/app/services/structured_reviewer_service.py` before claiming review-quality impact and must treat `backend/app/engine/contracts.py` as insufficient evidence by itself.
- FR8 (US3): Because the inspected snapshot seam currently builds `call_config_snapshot` from only `schema_version` and `expectations`, MVP implementation must not claim that subordinate prompt fidelity is consumed by the structured-review engine in this WF unless a later task adds and proves the narrowest necessary snapshot seam.
- FR9 (US3): One proof-call example must exercise the new structure concretely, preferring one real canonical YAML surface by default; fixture fallback is allowed only with an explicit scope-control rationale.
- FR10 (US1, US2, US3): Targeted tests must fail closed for malformed subordinate-prompt structures, authoring-contract regressions, and ambiguity in the compatibility posture, including at least one regression check against an existing real flat canonical YAML.
- FR11 (US1, US2, US3): Phase 2 planning must keep implementation bounded to schema, template, authoring docs/checklist, targeted tests, and one proof-call example unless the runtime seam inspection yields a separately justified narrow snapshot update.

## 5. Data & API Contracts

- Contract A (US1, FR1, FR2): Schema contract
  - Target seam: `backend/app/schemas/call_definitions_v2.py`
  - Required shape: each `evaluation_element` may carry a structured subordinate-prompt collection for official prompt/question fidelity.
  - Validation rules:
    - subordinate prompts must be structured data, not arbitrary unknown fields;
    - malformed subordinate-prompt items fail validation;
    - legacy flat evaluation elements remain valid during MVP compatibility mode.

- Contract B (US1, FR3): Template contract
  - Target seam: `backend/data/calls/templates/call_definition_v2_template.yaml`
  - Required behavior: template example must teach one evaluation element with subordinate prompt fidelity, not only flat `description`.
  - Validation rule: template shape must remain valid under the updated schema.

- Contract C (US2, FR4, FR5): Authoring workflow and checklist contract
  - Target seams: `docs/call-yaml/authoring-workflow.md` and `docs/call-yaml/onboarding-checklist.md`.
  - Required behavior:
    - docs define when subordinate prompts are required by source;
    - checklist includes an explicit fidelity-preservation gate;
    - docs/checklist do not present minimal ingestable YAML as sufficient when official prompts exist.
  - State transition: `source reviewed` -> `subordinate prompts identified or explicitly absent by source` -> `authoring approved`.

- Contract D (US3, FR6, FR10): Compatibility posture contract
  - Required rule: existing flat canonical YAMLs are tolerated temporarily for backward compatibility, but the new fidelity structure is mandatory for new or re-authored calls when official subordinate prompts exist.
  - Required proof: tests or verification artifacts must show both sides of that posture, including at least one existing real flat canonical YAML regression target.

- Contract E (US3, FR7, FR8): Runtime seam inspection contract
  - Inspection targets: `backend/app/services/structured_reviewer_service.py`, `backend/app/engine/contracts.py`, and any directly adjacent validator/projection seam needed to support the claim.
  - Current observed state from brainstorm-backed inspection: the structured-review payload snapshot is built from only `schema_version` and `expectations`.
  - MVP claim boundary: authoring-contract hardening is in scope; runtime consumption is deferred unless a later narrow task proves an added snapshot seam.

- Contract F (US3, FR9): Proof-call contract
  - Preferred artifact: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` as the default real canonical YAML proof-call surface because it exposed the motivating fidelity defect.
  - Fallback: one dedicated fixture or equivalent proof artifact only if a real canonical YAML would widen scope disproportionately, with rationale captured in-task.
  - Required proof: schema validation plus evidence that the example demonstrates subordinate prompt encoding clearly enough to guide future authors.

## 6. Components / Modules

- Authoring schema layer
  - Responsibility: represent canonical evaluation criteria/elements with subordinate official prompt fidelity while preserving strict validation.
  - Suggested path: `backend/app/schemas/call_definitions_v2.py`

- Authoring template layer
  - Responsibility: teach the new shape by default through the starter YAML.
  - Suggested path: `backend/data/calls/templates/call_definition_v2_template.yaml`

- Authoring governance layer
  - Responsibility: define fail-closed authoring workflow steps and checklist gates for preserving subordinate official prompts.
  - Suggested paths: `docs/call-yaml/authoring-workflow.md` and `docs/call-yaml/onboarding-checklist.md`.

- Test layer
  - Responsibility: prove representability, malformed-shape rejection, compatibility posture, and proof-call validity.
  - Suggested paths: schema tests, template validation tests, one existing-flat-call compatibility regression test, and proof-call validation tests only.

- Proof-call layer
  - Responsibility: make the contract concrete on one representative authored surface.
  - Suggested path: one real canonical call YAML by default; exact file chosen in Phase 2.

- Runtime seam boundary
  - Responsibility: bound claims about downstream review behavior by the inspected snapshot/engine contract seam.
  - Suggested paths: `backend/app/services/structured_reviewer_service.py`, `backend/app/engine/contracts.py`, and directly adjacent validator/projection seams only if needed for claim verification.

### Design Tree

1. Lock the compatibility posture and runtime-claim boundary from the inspected snapshot seam.
2. Add subordinate-prompt representability in the schema.
3. Update the template to teach the new shape.
4. Update authoring docs and checklist to fail closed on flattening.
5. Add targeted tests for schema, template, compatibility posture, and proof-call validation.
6. Author one proof-call example on the narrowest representative surface.
7. Defer runtime-consumption work unless a later task explicitly proves that a narrow snapshot seam is required and still within scope.

## 7. Edge Cases

- If an official source has atomic evaluation elements but no subordinate prompts, authors may omit the new structure with an explicit source-grounded rationale. (US2, FR4)
- If subordinate prompts exist only in a reviewer guide or equivalent official evaluation source, the authoring contract still treats them as in-scope fidelity data. (US1, US2, FR4)
- If an author tries to encode inferred or normalized prompts not present in source documents, validation or checklist review must reject that authoring path. (US2, US3, FR5, FR9)
- If existing flat YAMLs become invalid unintentionally under the new schema, the compatibility posture is broken and MVP fails. (US3, FR2, FR6)
- If the proof-call surface would force unrelated runtime or migration work, the WF must fall back to the narrowest acceptable proof artifact and record the rationale explicitly. (US3, FR9, FR11)

## 8. Testing Decisions (TDD)

- Behavior changes to schema validation or authoring-contract enforcement must begin with failing tests at the relevant public seam.
- Public seams to test:
  - schema validation for subordinate-prompt shape;
  - template validation against the updated schema;
  - authoring docs/checklist contract checks if the repo already has an executable seam for them, otherwise targeted diff-backed verification;
  - proof-call validation.
- Boundary mocking rule: do not mock schema parsing or proof-call validation; mock only expensive or external boundaries if a narrow runtime seam inspection test becomes necessary later.
- Minimum test types:
  - US1: unit or model-validation tests for the new subordinate-prompt schema contract.
  - US2: targeted validation or contract tests for template/docs/checklist fail-closed behavior.
  - US3: backward-compat validation test(s) for at least one existing real flat canonical YAML posture plus proof-call validation test(s).
- Required negative checks:
  - malformed subordinate-prompt structures are rejected;
  - flattening remains visibly disallowed by the updated docs/checklist when subordinate prompts exist;
  - legacy flat YAML examples remain valid only where the compatibility posture says they do;
  - no test in this WF overclaims runtime consumption unless a snapshot seam change is explicitly added.

## 9. Telemetry (Minimal)

- Reuse existing validation output and test evidence; do not add new telemetry infrastructure for this WF.
- If the runtime seam inspection becomes a tested proof point, record only deterministic evidence that the snapshot shape still excludes subordinate prompt data unless explicitly widened.

## 10. Deferred / Not in MVP

- Engine or prompt pipeline changes that consume subordinate prompts during structured review.
- Repo-wide migration of historical flat canonical YAMLs.
- New researcher-facing explanations or review-card traceability UI.
- Generic taxonomy or ontology work beyond the new subordinate-prompt fidelity structure.

## 11. Open Questions (if any)

- none

## 12. Changelog

- v0.1 (2026-03-11): Initial PRD from brainstorm.
- v0.2 (2026-03-11): Applied risk-audit fixes by pinning the checklist seam, defaulting the proof-call to `erc_poc_2026_full.yaml`, requiring a real flat-call compatibility regression target, and marking the PRD ready for tasks.
