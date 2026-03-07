<!-- docs/prds/prd-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-07

Type: feature

## 0. User Stories (MVP)

- US1: As a call-definition maintainer, I want `MSCA-PF-2025` onboarded as one official-source-grounded canonical call, so that PeerLens gains one real new promised call instead of more framework churn.
- US2: As a call-definition maintainer, I want a hard per-call upload gate for the official `MSCA-PF-2025` structure source and evaluation criteria/elements source, so that no substantive YAML authoring happens from recollection or inference.
- US3: As a product owner, I want deterministic validation, local ingest, and one narrow runtime proof for `MSCA-PF-2025`, so that the repo can demonstrate real call expansion rather than planning-only progress.
- US4: As an engineer maintaining the onboarding path, I want any compatibility work discovered during `MSCA-PF-2025` onboarding to stay limited to the smallest direct fix needed for this one call, so that the WF does not expand into cross-call hardening.

## Deferred Stories (Not in MVP)

- DS1: Additional MSCA calls, years, or stages beyond `MSCA-PF-2025`.
- DS2: Frontend redesign, nested review-surface redesign, or broad UX expansion.
- DS3: Generic multi-call onboarding framework work not directly required to land `MSCA-PF-2025`.
- DS4: Cross-call hardening, policy/governance cleanup, or platform-wide refactors.

## 1. In Scope

- Add one new promised canonical call target for `MSCA-PF-2025` at `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`. (US1, US2)
- Enforce the hard source upload gate before any substantive `MSCA-PF-2025` YAML structure, proposal-node, or evaluation criteria/elements authoring begins. (US2)
- Record official-source traceability for `MSCA-PF-2025` in a per-call manifest with durable provenance metadata and hash-based evidence. (US1, US2)
- Validate the resulting canonical call definition deterministically and prove it can be ingested locally without schema ambiguity. (US1, US3)
- Capture one minimal runtime proof showing `MSCA-PF-2025` can be exercised through the intended product path selected during implementation planning, using the new canonical call definition rather than a mock-only stand-in. (US3)
- Allow only the smallest compatibility fix directly required to make `MSCA-PF-2025` fit the existing path safely, with regression evidence scoped to that touched seam. (US4)

## 2. Out of Scope

- Authoring a second call, backup call, or family-wide MSCA expansion. (DS1)
- Frontend redesign, generalized nested-surface support work, or review UX overhaul unless explicitly re-scoped after a blocker. (DS2)
- New onboarding abstractions, governance/policy work, or framework cleanup that does not directly unblock `MSCA-PF-2025`. (DS3, DS4)
- Substantive `MSCA-PF-2025` YAML authoring before the official source documents are uploaded in Phase 3. (US2, DS3)

## 3. User / System Flow

### Happy path

1. Operator confirms WF scope remains exactly one promised canonical call, `MSCA-PF-2025`, with no second-call or broad-hardening expansion allowed. (US1, US4)
2. Operator uploads the official `MSCA-PF-2025` narrative/application-structure source and the official evaluation/assessment criteria/elements source before substantive YAML authoring starts. (US2)
3. Maintainer records source provenance and hashes in the `MSCA-PF-2025` manifest, then authors the canonical YAML strictly from those uploaded official sources. (US1, US2)
4. Validation tooling checks the canonical YAML deterministically and fails closed on schema or contract violations before ingest. (US1, US3)
5. Local ingest path loads `msca_pf_2025_full.yaml` successfully and makes the call available to the existing runtime surface chosen for proof. (US1, US3)
6. The workflow executes one deterministic runtime proof against the intended product path and captures evidence that `MSCA-PF-2025` behaves as a real supported call through that path. (US3)
7. If a narrow compatibility change was required, regression coverage proves the fix is confined to the minimal seam needed for `MSCA-PF-2025`. (US4)

### Failure path A — missing official uploads

1. Phase 3 reaches substantive `MSCA-PF-2025` authoring without both required official source classes uploaded. (US2)
2. Workflow stops before YAML structure or criteria/elements authoring and requests the missing official source document(s). (US2)
3. No speculative canonical YAML content is treated as valid progress until the upload gate is satisfied. (US2)

### Failure path B — call fit requires broad redesign

1. During planning or implementation, `MSCA-PF-2025` exposes a product-path incompatibility that would require frontend redesign, cross-call runtime expansion, or multi-surface platform changes. (US3, US4)
2. Workflow documents the blocker and either limits work to the smallest direct compatibility fix for this one call or pauses for explicit re-scope. (US4)
3. The WF does not silently absorb broader product work under the label of onboarding. (US4)

### Failure path C — canonical validation or ingest fails

1. The source-grounded `MSCA-PF-2025` YAML fails deterministic validation or local ingest. (US1, US3)
2. Workflow reports the exact failing contract, schema, or ingest seam and blocks readiness advancement until corrected. (US1, US3)
3. Runtime proof is not accepted when validation or ingest remains unresolved. (US3)

## 4. Functional Requirements

- FR1 (US1): The WF must deliver exactly one new promised canonical call, `MSCA-PF-2025`, and must not expand to another call without a separate workflow decision.
- FR2 (US2): `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml` must not receive substantive structure, proposal-node, or evaluation criteria/elements authoring until both required official source classes are uploaded in-workflow.
- FR3 (US2): The required official source classes are the official `MSCA-PF-2025` narrative/application-structure source and the official evaluation/assessment criteria/elements source; supplemental reviewer guidance or annexes are optional only when needed to resolve ambiguity.
- FR4 (US1, US2): `MSCA-PF-2025` must have a per-call source manifest capturing provenance metadata, local source-copy references if used, usage labels, and SHA256 hashes as the durable traceability anchor.
- FR5 (US1): The canonical artifact target for this WF is `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`.
- FR6 (US1, US3): The canonical YAML must pass deterministic validation before any runtime proof is considered valid.
- FR7 (US1, US3): The call must pass local ingest using the repo's existing ingest path without schema ambiguity or silent fallback behavior.
- FR8 (US3): The WF must define and execute at least one deterministic runtime proof that exercises `MSCA-PF-2025` through one intended product path using the real canonical call definition.
- FR8a (US3, US4): MVP runtime-proof evidence must include the exact proof seam exercised, the real `MSCA-PF-2025` canonical artifact used, the deterministic pass/fail result, and any narrow compatibility seam relied on.
- FR8b (US2, US3): Runtime proof is invalid unless the upload gate, validation gate, and ingest gate have already passed for the same canonical artifact.
- FR9 (US3): The runtime proof must be minimal but real; planning-only, dry-run-only, or mock-only evidence is insufficient for WF completion.
- FR9a (US3, US4): Phase 2 planning must lock exactly one existing product-path seam as the MVP runtime proof surface before implementation begins; if no single existing seam is viable without broad redesign, the WF must stop and surface that blocker.
- FR10 (US4): Any compatibility fix discovered during `MSCA-PF-2025` onboarding must stay limited to the smallest direct change required for this call to land safely.
- FR11 (US4): If the required compatibility work exceeds a narrow seam and becomes broader redesign, the WF must stop and surface that as a blocker instead of expanding scope implicitly.
- FR11a (US3, US4): A proposed MVP proof seam that requires coordinated expansion across more than one major product surface is presumed out of scope and must be treated as a blocker candidate unless proven to be the minimum direct fix for `MSCA-PF-2025`.
- FR12 (US4): Any compatibility fix accepted into scope must include regression evidence proving the touched seam remains stable for existing behavior.
- FR13 (US1, US2, US3): Success claims for this WF must be phrased as one new promised canonical call landed, not as generic agency/family coverage growth.

## 5. Data & API Contracts

### 5.1 Source intake contract

- `MSCA-PF-2025` authoring requires two official source classes before substantive YAML content work: one structure/narrative source and one evaluation criteria/elements source. (US2, FR2, FR3)
- The upload gate applies immediately before substantive authoring, not only before finalizing the YAML. (US2, FR2)
- If one document appears to cover both structure and criteria/elements, the workflow must still fail closed and require supplemental official evidence whenever that document does not ground both surfaces unambiguously; default planning assumption remains two source classes. (US2, FR3)

### 5.2 Canonical artifact contract

- The canonical output path is `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`. (US1, FR5)
- The canonical YAML must encode only source-grounded evaluable proposal structure, evaluation criteria/elements, and enforceable constraints for `MSCA-PF-2025`. (US1, US2, FR2, FR5, FR6)
- The artifact must not contain speculative placeholder structure or criteria/elements introduced before the upload gate is satisfied. (US2, FR2)

### 5.3 Traceability manifest contract

- `MSCA-PF-2025` must maintain one per-call source manifest under `backend/data/calls/sources/` with provenance notes, usage labels, SHA256 hashes, and relevant official-source metadata. (US1, US2, FR4)
- Source binaries remain local workflow artifacts rather than durable git-tracked evidence; manifest metadata and hashes are the durable traceability layer. (US2, FR4)

### 5.4 Validation and ingest contract

- `MSCA-PF-2025` validation must fail closed on schema or contract violations before ingest proceeds. (US1, US3, FR6)
- Local ingest must prove the canonical YAML can be loaded by the existing ingest/runtime path without ad hoc per-run manual patching. (US1, US3, FR7)
- A failed validation or ingest result blocks runtime proof acceptance and readiness advancement. (US3, FR6, FR7, FR8)

### 5.5 Runtime proof contract

- Runtime proof must use the real `MSCA-PF-2025` canonical call definition rather than a synthetic fixture that bypasses the new call path. (US3, FR8, FR9)
- Runtime proof evidence must record the exact seam exercised, the canonical artifact under test, the deterministic result, and any narrow compatibility seam used to make that proof succeed. (US3, US4, FR8a)
- Runtime proof cannot count toward WF completion unless the same canonical artifact has already satisfied the upload gate, validation gate, and ingest gate. (US2, US3, FR8b)
- The proof surface may be narrow, but it must be deterministic, repeatable, and tied to one explicit product-path seam selected in implementation planning. (US3, FR8)
- If the selected proof surface requires a compatibility fix, the proof must demonstrate the fix at that seam and the corresponding regression evidence. (US3, US4, FR10, FR12)

## 6. Components / Modules

- `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`
  - Canonical call definition delivered by this WF once the source gate is satisfied. (FR2, FR5, FR6)
- `backend/data/calls/sources/msca_pf_2025_full.sources.md`
  - Per-call traceability manifest for official-source provenance and hash evidence. (FR4)
- One selected existing validation/ingest path and only its directly supporting modules
  - Deterministic contract-validation and local-ingest seams that must accept the new call without ambiguity without broad backend expansion. (FR6, FR7, FR11a)
- One existing runtime proof seam selected in Phase 2
  - The single MVP proof path that must demonstrate `MSCA-PF-2025` is operationally real without broad redesign; Phase 2 must freeze this seam before implementation tasking proceeds and treat multi-surface expansion as a blocker candidate first. (FR8, FR8a, FR9, FR9a, FR10, FR11a)
- Narrow compatibility seam, if forced
  - The smallest touched module boundary required to make the selected runtime proof work safely for `MSCA-PF-2025`. (FR10, FR11, FR12)

Design tree / dependencies / ordering:
1. Freeze the scope claim: one promised canonical call, `MSCA-PF-2025`, with the upload gate preserved. (FR1, FR2, FR13)
2. Gather and verify official source inputs, then define the per-call manifest requirements. (FR3, FR4)
3. Author the canonical YAML only after the upload gate is satisfied, then validate and ingest it. (FR5, FR6, FR7)
4. Select one narrow runtime proof seam and implement only the smallest compatibility fix required, if any; if the seam implies multi-surface expansion, stop and treat it as a blocker candidate first. (FR8, FR8a, FR9, FR10, FR11, FR11a)
5. Add regression evidence for any touched compatibility seam and capture the final proof bundle. (FR12)

Deep module guidance:

- Keep `MSCA-PF-2025` onboarding source-first; do not hide missing source grounding behind placeholder YAML scaffolding.
- Prefer one explicit proof seam over diffuse "support everywhere" claims.
- Localize any compatibility fix to the smallest seam required for `MSCA-PF-2025` rather than introducing generic onboarding abstractions.

Suggested file-path clusters (coarse only):

- canonical call and source manifest under `backend/data/calls/`
- the selected existing validation/ingest seam plus only the directly supporting modules it already depends on
- one existing runtime proof surface frozen in Phase 2 as the sole MVP evidence path
- targeted regression tests near the touched validation, ingest, or runtime seam

## 7. Edge Cases

- Official uploads arrive, but one source does not actually ground the needed structure or criteria/elements; the workflow must request supplemental official evidence before authoring ambiguous sections. (US2, FR3)
- `MSCA-PF-2025` can validate but not ingest due to a runtime assumption tailored to existing calls; this may justify only a narrow compatibility fix, not a broader redesign. (US3, US4, FR7, FR10, FR11)
- Runtime proof works only through a mocked or manual shortcut; this does not satisfy the operational-proof requirement. (US3, FR8, FR9)
- The only viable proof seam crosses multiple major product surfaces; this is a blocker candidate and cannot be normalized as ordinary MVP scope without explicit narrow-fix justification. (US3, US4, FR9a, FR11a)
- A proposed fix improves multiple calls opportunistically but is not required to land `MSCA-PF-2025`; this is out of scope and must be deferred. (US4, FR10, FR11)
- Source binaries exist locally but are not safe to commit; traceability must still remain durable through manifest metadata and hashes. (US2, FR4)

## 8. Testing Decisions (TDD)

- `WF-0061` changes behavior by adding a new real canonical call, so implementation must follow RED -> GREEN -> REFACTOR at the touched seam. (US1, US3, US4)
- Public test seams must cover canonical validation, local ingest, and the selected runtime proof boundary for `MSCA-PF-2025`. (US1, US3, FR6, FR7, FR8)
- Mock only true external boundaries when needed for determinism; do not mock away the canonical-call contract, ingest path, or the selected runtime proof seam itself. (US3, FR8, FR9)
- Minimum verification required:
  - upload-gate coverage proving substantive `MSCA-PF-2025` authoring stops until the required official source classes are present. (US2, FR2, FR3)
  - validation coverage proving `msca_pf_2025_full.yaml` fails closed on contract errors and passes once source-grounded content is correct. (US1, US2, US3, FR2, FR6)
  - local ingest verification proving `MSCA-PF-2025` loads through the repo's real ingest path. (US1, US3, FR7)
  - ordered-gate coverage proving runtime proof cannot count when upload-gate, validation, or ingest has failed for the same canonical artifact. (US2, US3, FR8b)
  - one deterministic runtime proof exercising the chosen product seam with the real `MSCA-PF-2025` call definition. (US3, FR8, FR9)
  - proof-evidence coverage proving the runtime-proof artifact records the exercised seam, canonical artifact, deterministic result, and any narrow compatibility seam used. (US3, US4, FR8a)
  - blocker-boundary coverage proving a proposed fix that exceeds narrow compatibility scope is surfaced as a stop/escalation condition rather than silently absorbed into the WF. (US4, FR9a, FR10, FR11, FR12)
  - multi-surface blocker coverage proving a proof seam that spans more than one major product surface is treated as a blocker candidate unless justified as the minimum direct fix. (US3, US4, FR11a)
  - regression coverage for any narrow compatibility fix required to support that runtime proof. (US4, FR10, FR12)

## 9. Telemetry (Minimal)

- Add only minimal diagnostics needed to distinguish validation failure, ingest failure, and runtime-proof failure for `MSCA-PF-2025`.
- Telemetry is not an MVP deliverable unless a touched seam cannot be verified or debugged deterministically without one small diagnostic.

## 10. Deferred / Not in MVP

- Second-call or multi-call expansion.
- Frontend redesign or generalized nested-surface support.
- Platform-wide onboarding abstractions or governance work.
- Broader cross-call hardening not directly required by `MSCA-PF-2025`.

## 11. Open Questions (if any)

- None blocking. Phase 2 must lock the single MVP runtime proof seam before implementation starts; if no narrow existing seam is viable, the WF stops for re-scope instead of broadening.

## 12. Changelog

- v0.1 (2026-03-07): Initial PRD from brainstorm.
- v0.2 (2026-03-07): Applied risk-audit edits for fail-closed source intake, explicit single-seam runtime-proof planning, and scope-boundary test coverage; marked Ready for Tasks.
- v0.3 (2026-03-07): Applied review-and-harden edits for ordered gate enforcement, proof-evidence contract, and explicit multi-surface blocker handling while preserving single-call scope.
