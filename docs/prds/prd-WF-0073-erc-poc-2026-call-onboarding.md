<!-- docs/prds/prd-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-11

## 0. User Stories (MVP)

- US1: As an internal operator, I want a source-grounded `ERC-2026-PoC` call definition and source manifest in the repo, so that this one call can be onboarded without inventing structure or evaluation elements.
- US2: As an internal operator, I want `ERC-2026-PoC` to validate, ingest, and appear through existing call exposure seams, so that researchers can select it through the existing product path.
- US3: As an internal operator, I want one backend structured-review smoke proof for `ERC-2026-PoC`, so that launch readiness is based on runtime evidence rather than YAML-only claims.

## Deferred Stories (Not in MVP)

- As a researcher, I want new call-specific UI affordances or copy tailored to ERC PoC.
- As an operator, I want generic multi-call onboarding automation for future agencies/programmes.
- As an operator, I want split visibility/reviewability enabled for this call.

## 1. In Scope

- One-call onboarding for `ERC-2026-PoC` only.
- Planning for one canonical call artifact at `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` and one source manifest at `backend/data/calls/sources/erc_poc_2026_full.sources.md`.
- Official-source grounding from:
  - `af_he-erc-poc_en.pdf` for proposal/application structure.
  - `wp_horizon-erc-2026_en.pdf` section `2.1.6.1` for evaluation criteria/elements and overall call parameters.
  - `information-for-applicants_he-erc-poc_en.pdf` for proposal-structure detail, page limits, and single-step process cross-checks.
- Phase 2 planning should stay aggressively small and prefer implementation slices that touch `<=3` files where feasible.
- Runtime proof seam is existing backend `POST /api/structured-review`, not a new frontend or BFF workflow.

## 2. Out of Scope

- Any platform-general onboarding framework work.
- Any new agency/programme onboarding beyond `ERC-2026-PoC`.
- New frontend flows, researcher-facing redesign, or marketing copy.
- Re-authoring existing ERC calls unless a narrowly proven compatibility fix is required for `ERC-2026-PoC` activation.
- Split visibility/reviewability opt-in, unless official PoC source evidence later proves it is required.
- End-to-end browser proof; this WF’s default proof claim stops at backend structured-review smoke.

## 3. User / System Flow

### Happy Path

1. Operator confirms the authoritative source set for `ERC-2026-PoC`: application form, ERC work programme, and applicant guidance. (US1)
2. Operator authors a source traceability manifest with durable file references, `SHA256`, and explicit `Used for` rows for structure and evaluation criteria/elements. (US1)
3. Operator authors the canonical call definition using only evaluable proposal structure, evaluation criteria/elements, and enforceable constraints from the official sources. (US1)
4. System dry-runs the call ingest and returns a clean validation summary with no unresolved references. (US2)
5. System ingests the call into the target DB and exposes it through current calls listing and node metadata seams. (US2)
6. Operator runs one backend `POST /api/structured-review` smoke request against `ERC-2026-PoC` and records deterministic evidence. (US3)
7. Workflow records pass/fail evidence for manifest, dry-run, ingest, exposure, and structured-review smoke before any readiness claim. (US1, US2, US3)

### Failure Paths

1. If the official sources do not support a claimed node, evaluation element, or activation behavior, authoring stops and the claim is removed or deferred rather than guessed. (US1)
2. If dry-run or ingest fails because `ERC-2026-PoC` needs a compatibility seam, implementation narrows to the smallest repo fix required for this call and adds targeted regression coverage before proceeding. (US2)
3. If the call ingests but `POST /api/structured-review` fails or produces non-replayable evidence, launch readiness remains blocked. (US3)

## 4. Functional Requirements

- FR1 (US1): The planning output must keep the WF bounded to one-call onboarding and activation for `ERC-2026-PoC` only.
- FR2 (US1): The onboarding plan must use the uploaded official sources as the authoring basis and treat the ERC work programme as the primary source for evaluation criteria/elements.
- FR3 (US1): The canonical call plan must encode `ERC-2026-PoC` as a single-step call and must not inherit StG/CoG stage semantics without PoC-specific source proof.
- FR4 (US1): The canonical call plan must model only evaluable narrative proposal content and enforceable constraints; administrative-only portal mechanics stay out of call-definition scope.
- FR5 (US1): The proposal structure plan must preserve official source-section traceability and include the PoC proposal content required for evaluation, including idea, innovation potential, approach/methodology, PI strategic leadership/project management, ethics issues, and support-letter dependencies.
- FR6 (US1): The evaluation plan must use the sole criterion of excellence with exactly three evaluation elements: breakthrough innovation potential, approach and methodology, and PI strategic leadership/project management.
- FR7 (US1): The planning output must preserve the official PoC constraints relevant to review interpretation, including 10-page Part B limit, one evaluation step, and two 2026 cut-offs with the first on 2026-03-17.
- FR8 (US2): The source manifest plan must require both mandatory source classes, explicit `Used for` traceability, and durable `SHA256` metadata before authoring counts as valid.
- FR9 (US2): The implementation plan must validate `erc_poc_2026_full.yaml` through existing ingest/dry-run tooling before DB ingest.
- FR10 (US2): The implementation plan must verify that `ERC-2026-PoC` appears through existing calls listing and node metadata exposure seams after ingest.
- FR11 (US2): Any compatibility code change discovered during onboarding must be localized to the smallest activation/exposure seam required for this one call.
- FR12 (US3): The implementation plan must include one backend `POST /api/structured-review` smoke verification for `ERC-2026-PoC` with replayable evidence metadata.
- FR13 (US1, US2, US3): No proceed, readiness, or ship recommendation is valid unless manifest, dry-run, ingest, exposure, and structured-review smoke evidence each resolve to explicit pass/fail status.
- FR14 (US1, US2, US3): Phase 2/3 artifacts must maintain one verification matrix for manifest, dry-run, ingest, exposure, and structured-review smoke; every row must name the exact seam, command or test ID, expected outcome, result, and evidence reference.

## 5. Data & API Contracts

- Contract A (US1, FR2, FR8): Source manifest contract
  - Output path: `backend/data/calls/sources/erc_poc_2026_full.sources.md`
  - Required fields: source file path, source class, `SHA256`, `Used for`, and notes on source authority.
  - Validation rule: manifest is incomplete if either proposal/application structure or evaluation criteria/elements source class is missing.

- Contract B (US1, FR3, FR4, FR5, FR6, FR7): Canonical call-definition contract
  - Output path: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`
  - Shape: existing `CallDefinitionV2` contract.
  - Required authored content: call identity, proposal nodes, evaluation criteria/elements, node expectations, guidance text, compliance rules, content constraints, and source-section metadata where applicable.
  - Validation rules:
    - single-step semantics only;
    - no unsupported split-role opt-in by default;
    - no administrative-only sections as reviewable proposal nodes;
    - evaluation elements remain source-grounded and non-overlapping.

- Contract C (US2, FR9, FR10): Ingest and exposure contract
  - Dry-run seam: existing backend ingest script and summary output.
  - DB ingest seam: existing backend ingest path.
  - Exposure seam: existing calls listing API and node metadata API.
  - State transition: `not present` -> `validated` -> `ingested` -> `exposed`.
  - Evidence rule: exposure proof must record the exact endpoint or command used for calls listing and node metadata, plus expected call identity in the response.

- Contract D (US3, FR12, FR13): Structured-review smoke contract
  - Entry point: existing backend `POST /api/structured-review`.
  - Minimum request shape: one valid `ERC-2026-PoC` submission payload aligned to authored node IDs.
  - Expected result: successful structured-review response without call-contract errors.
  - Evidence rule: command/test ID, payload fixture reference, and expected outcome must be recorded.

- Contract E (US1, US2, US3, FR13, FR14): Verification matrix contract
  - Required proof items: source manifest gate, dry-run ingest, DB ingest, call exposure, node metadata exposure, structured-review smoke.
  - Required row fields: proof item, exercised seam, command or test ID, expected outcome, result, evidence reference, notes.
  - Gate rule: no readiness claim is valid while any required row is missing or unresolved.

## 6. Components / Modules

- `docs/` planning artifacts
  - Responsibility: keep scope, risks, decisions, and status explicit before implementation.
  - Suggested paths: `docs/prds/prd-WF-0073-erc-poc-2026-call-onboarding.md`, `docs/tasks/task-WF-0073-erc-poc-2026-call-onboarding.md`, `docs/logs/decisions.md`.

- Source traceability layer
  - Responsibility: record official-source provenance with fail-closed manifest gating.
  - Suggested paths: `backend/data/calls/sources/erc_poc_2026_full.sources.md`.

- Canonical call-definition layer
  - Responsibility: express PoC proposal structure, evaluation criteria/elements, and enforceable constraints.
  - Suggested paths: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`.
  - Boundary rule: Host Institution Support Letter and Ethics Issues Table stay as submission dependencies expressed through guidance/compliance metadata, not reviewable proposal nodes.

- Ingest/activation layer
  - Responsibility: validate and ingest the call through existing backend seams.
  - Suggested paths: existing ingest script/config paths only if needed for this call.
  - Change policy: attempt call-local config/activation fixes first; only widen to broader ERC runtime seams if narrower fixes fail.

- Exposure/runtime verification layer
  - Responsibility: confirm call listing, node metadata availability, and backend structured-review smoke behavior.
  - Suggested paths: existing API/test seams only if required for this call.

### Design Tree

1. Planning and source-traceability decisions.
2. Source manifest authoring.
3. Canonical call-definition authoring.
4. Dry-run and DB ingest verification.
5. Exposure verification.
6. Backend structured-review smoke verification.
7. Narrow compatibility fix only if a prior verification step proves it necessary.

## 7. Edge Cases

- If the application form includes administrative sections that are mandatory for portal submission but not reviewer-assessed narrative content, they must remain out of reviewable node scope. (US1, FR4)
- If official text creates ambiguity between proposal structure guidance and evaluation elements, the ERC work programme remains primary for evaluation criteria/elements and the applicant guide acts as a cross-check. (US1, FR2, FR6)
- If PoC proposal structure includes mandatory attachments such as the Host Institution Support Letter or Ethics Issues Table, planning must distinguish authored call-definition scope from submission-side dependencies. (US1, FR5)
- If existing ERC runtime assumptions expect multi-step semantics, the WF must fail closed and isolate the smallest call-specific compatibility seam instead of mutating all ERC calls together. (US2, FR3, FR11)
- If the first cut-off date of 2026-03-17 is threatened by unresolved verification failures, readiness must remain blocked rather than replaced with YAML-only completion claims. (US2, US3, FR13)

## 8. Testing Decisions (TDD)

- Behavior changes discovered during implementation must start with a failing test or reproducible failing verification at the relevant public seam.
- Public seams to test:
  - ingest dry-run command,
  - DB ingest command,
  - calls listing exposure,
  - node metadata exposure,
  - backend `POST /api/structured-review`.
- Boundary mocking rule: mock only external or expensive boundaries; prefer real call-definition parsing and real DB/test-environment seams where the repo already supports them.
- Minimal test types:
  - US1: authoring/validation checks for manifest and call-definition integrity.
  - US2: integration-ish ingest and exposure verification.
  - US3: integration-ish backend structured-review smoke request.
- Required negative checks:
  - source-manifest gate fails closed when a mandatory source class, `SHA256`, or `Used for` traceability field is missing;
  - `ERC-2026-PoC` does not accidentally inherit multi-step ERC stage behavior.
- If a narrow compatibility fix is required, add regression coverage exactly at the touched seam before broadening verification.

## 9. Telemetry (Minimal)

- Reuse existing backend logs/command outputs for ingest and structured-review smoke verification.
- Capture deterministic verification evidence pointers rather than introducing new telemetry infrastructure for this WF.

## 10. Deferred / Not in MVP

- Browser-level end-to-end proof.
- Assisted extraction from uploaded full proposal documents.
- Generic ERC PoC submission helpers or templates beyond canonical call onboarding.
- Additional smoke scenarios beyond one successful structured-review proof.

## 11. Open Questions (if any)

- Whether existing backend exposure/runtime seams accept `ERC-2026-PoC` without any call-specific compatibility fix.

## 12. Changelog

- v0.1 (2026-03-11): Initial PRD from brainstorm.
- v0.2 (2026-03-11): Applied risk-audit fixes by adding a verification matrix contract, locking support-letter and ethics handling as non-reviewable submission dependencies, requiring fail-closed negative checks, and preferring call-local compatibility seams.
