# WF-0044 — P1 #12: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-02

## 0. User Stories (MVP)

- US1: As a call-definition maintainer, I want a strict per-call upload gate for official application-form and assessment-criteria sources, so that no YAML authoring happens without traceable evidence.
- US2: As a call-definition maintainer, I want canonical v2 `erc_cog_2026_full` generated and ingest-validated, so that ERC CoG can run through the current runtime and API contracts safely.
- US3: As a call-definition maintainer, I want minimal-change source-grounded re-authoring of baseline calls (`nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`) with refreshed manifests, so that existing behavior stays stable while traceability improves.
- US4: As a reviewer-engine maintainer, I want structured pipeline v1 to honor call-definition `reviewer_policy`, so that call/agency constraints are enforced consistently in structured review output.

## Deferred Stories (Not in MVP)

- DS1: Generalized assisted extraction/parsing tooling for source documents.
- DS2: Expansion to non-scoped calls (e.g., MSCA/ZonMw and other agencies).
- DS3: Broad refactor of call-yaml docs beyond narrow, generalizable clarifications.

## 1. In Scope

- Enforce a hard, per-call source intake gate before substantive authoring or re-authoring begins. (US1)
- Create canonical v2 file `erc_cog_2026_full` and validate with dry-run + real local DB ingest. (US2)
- Re-author scoped existing calls using minimal-change policy and refresh one `.sources.md` manifest per call with required metadata. (US3)
- Add/adjust structured pipeline v1 integration so `reviewer_policy` is applied with scoped deterministic behavior (`PROMPT_ONLY`, `POST_CHECK`, `BLOCKING`). (US4)
- Run planned verification paths for baseline calls and primary target acceptance checks. (US2, US3, US4)

## 2. Out of Scope

- Any call expansion outside WF-0044 scoped set. (DS2)
- Committing source PDFs/DOCX into git history. (US1, DS1)
- Fundamental redesign of reviewer engine contracts beyond `reviewer_policy` wiring in structured pipeline v1. (DS3)
- UI redesign unrelated to required contract-safety behavior. (DS3)

## 3. User / System Flow

- Happy path:
1. Operator collects official application-form and criteria sources for one call and records both origin path/context and local copied path + hash metadata. (US1)
2. Authoring proceeds only after gate completeness is confirmed for that call; YAML/manifest are updated with minimal-change discipline where required. (US1, US3)
3. For `erc_cog_2026_full`, canonical v2 YAML is authored and validated via dry-run + local DB ingest. (US2)
4. Structured review pipeline executes with `reviewer_policy` from call definition applied according to mode and scope. (US4)
5. Verification bundle confirms baseline calls remain ingestable and structured behavior remains contract-safe. (US2, US3, US4)

- Failure path A (missing source gate):
1. Source package is incomplete (missing application-form or criteria source). (US1)
2. Workflow blocks substantive authoring and logs gate failure for user follow-up. (US1)

- Failure path B (schema/ingest failure):
1. Canonical YAML fails dry-run or real ingest checks. (US2, US3)
2. Workflow reports exact contract/schema violations and halts readiness advancement. (US2, US3)

- Failure path C (`reviewer_policy` contract drift):
1. Structured pipeline ignores or misapplies policy mode/scope. (US4)
2. Deterministic checks fail (`BLOCKING` not blocking, `POST_CHECK` missing warning, or scoping mismatch), blocking release readiness. (US4)

## 4. Functional Requirements

- FR1 (US1): Workflow must require both official application-form source(s) and official assessment-criteria source(s) before substantive authoring for each call.
- FR2 (US1): Each call must maintain one traceability manifest file `backend/data/calls/sources/<call>.sources.md` with at least `Path`, `SHA256`, `Used for`, official URL/source page if available, and provided/downloaded date.
- FR3 (US1, US3): Source storage policy must preserve external/original path context and local copied path under `backend/data/calls/source_files/WF-0044/<call_code>/...` without committing source binaries to git.
- FR4 (US2): Create canonical v2 file `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml` with v2 schema keys and no v1/v2 key mixing.
- FR5 (US3): Re-author baseline scoped calls with minimal-change policy: refresh traceability and only apply source-proven corrections while preserving stable `proposal_nodes[*].id` unless clearly wrong.
- FR6 (US2, US3): Baseline calls and primary target must pass `ingest_call.py --dry-run`; scoped calls requiring acceptance must also pass real local DB ingest.
- FR7 (US4): Structured pipeline v1 must consume call-definition `reviewer_policy` with deterministic behavior for `PROMPT_ONLY`, `POST_CHECK`, and `BLOCKING`.
- FR8 (US4): `reviewer_policy` scoping fields (`applies_to_stage`, `applies_to_node_ids`) must be enforced per node/stage execution in structured requests.
- FR9 (US4): Existing structured endpoint contracts for `nwo_veni_2025_preproposal` must remain non-regressed.
- FR10 (US2): Primary target acceptance for `erc_cog_2026_full` includes one successful local structured-review API request returning review cards.
- FR11 (US4): `BLOCKING` reviewer-policy violations in structured pipeline must emit a stable, contract-safe failure category and return no partial cards.

## 5. Data & API Contracts

- Contract C1 (US1, FR1, FR2): Per-call intake contract requires two source classes (application-form and criteria/evaluation criteria elements sources), each traceable in the manifest with hash and usage labeling.
- Contract C2 (US1, FR3): Manifest entries record both origin context and local copied file path; source binaries remain outside versioned artifacts by policy.
- Contract C3 (US2, FR4, FR6): `ingest_call.py` continues hard-failing mixed v1/v2 key usage; canonical CoG output must be v2-valid and ingest-safe.
- Contract C4 (US3, FR5): Minimal-change re-authoring contract preserves existing stable node identifiers and universal structured review contracts unless a source-proven correction demands change.
- Contract C5 (US4, FR7, FR8): Structured pipeline accepts and applies reviewer policy mode + scope deterministically:
  - `PROMPT_ONLY`: prompt influence only, no deterministic block/warn side effects.
  - `POST_CHECK`: completion permitted with deterministic warning signal on violation.
  - `BLOCKING`: deterministic failure signal and no partial cards on violation.
- Contract C6 (US4, FR9, FR10): API-level behavior remains stable for existing call contracts; new CoG call code must satisfy the same structured response contract shape.
- Contract C7 (US2, US4, FR10, FR11): Structured API acceptance checks target `POST /api/structured-review` with `call_code=erc_cog_2026_full`; `BLOCKING` policy failures return deterministic failure semantics without partial card payloads.

## 6. Components / Modules

- `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
  - Responsibility: canonical v2 CoG call definition. (FR4, FR6, FR10)
- `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
  - Responsibility: minimal-change traceability-grounded refresh if source contradiction found. (FR5, FR6)
- `backend/data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml`
  - Responsibility: minimal-change re-authoring from official sources. (FR5, FR6)
- `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
  - Responsibility: minimal-change re-authoring from official sources. (FR5, FR6)
- `backend/data/calls/legacy/erc/erc_cog_2026_full_official.yaml`
  - Responsibility: legacy mirror retained but refreshed for traceability parity. (FR5)
- `backend/data/calls/sources/*.sources.md`
  - Responsibility: per-call traceability manifests with required metadata. (FR2, FR3)
- Structured review engine service modules (`backend/app/services/...structured...`)
  - Responsibility: apply `reviewer_policy` during structured execution with deterministic enforcement semantics. (FR7, FR8, FR9)
- Validation tooling (`backend/scripts/ingest_call.py`)
  - Responsibility: schema and ingest preflight/validation command surface. (FR6)

Design tree (dependencies + ordering):
1. Finalize source intake checklist + manifest requirements. (FR1-FR3)
2. Update scoped manifests and minimal-change YAML corrections for baseline calls. (FR5-FR6)
3. Author canonical CoG v2 and validate dry-run/real ingest. (FR4, FR6, FR10)
4. Wire and verify structured pipeline `reviewer_policy` handling with scoped deterministic behavior. (FR7-FR9)

Deep module boundaries:
- YAML definitions remain declarative policy/config surfaces.
- Ingestion validates schema/version contract boundaries.
- Structured service enforces runtime policy semantics while preserving API compatibility.

## 7. Edge Cases

- E1 (US1, FR1): Official sources arrive in mixed formats (`PDF`, `DOCX`, text) but gate completion still requires full content coverage, not extension-specific rules.
- E2 (US1, FR2): Official URL unavailable; manifest still requires explicit provenance notes and hash/usage metadata.
- E3 (US2, FR4): Accidental v1 fields (`funding_agency.short_name`) introduced in v2 file must hard-fail validation.
- E4 (US3, FR5): Source contradiction requiring node text change must avoid unstable ID churn unless ID is clearly incorrect.
- E5 (US4, FR7): `POST_CHECK` violation found after generation must warn deterministically without converting success to hard failure.
- E6 (US4, FR8): Multi-node structured request where policy applies only to subset of nodes/stages must avoid cross-node policy bleed.

## 8. Testing Decisions (TDD)

- TDD seam S1 (US2, US3, FR4-FR6): `ingest_call.py` dry-run + real local DB ingest for scoped calls.
  - Boundary mocking: none for ingest validation; use real parser/DB path in local environment.
  - Prove-it tests: pass/fail outcomes for each scoped call command.
- TDD seam S2 (US4, FR7-FR9): structured reviewer-policy deterministic behavior tests.
  - Boundary mocking: LLM output boundary only when needed to deterministically trigger forbidden-term paths.
  - Prove-it tests: prompt inclusion for `PROMPT_ONLY`, warning path for `POST_CHECK`, blocking path for `BLOCKING`, and scope filtering by stage/node.
- TDD seam S4 (US2, US4, FR10-FR11): API contract test for `erc_cog_2026_full` structured request path.
  - Prove-it tests: successful minimal-node review-card response for happy path and deterministic no-partial-cards failure path for `BLOCKING` violations.
- TDD seam S3 (US1, FR1-FR3): manifest completeness and source-gate checklist verification.
  - Prove-it checks: each scoped call has required source classes and manifest fields with hash + usage labeling.

## 9. Telemetry (Minimal)

- Log structured policy enforcement outcomes with stable signals (prompt-only applied, warning emitted, blocking failure triggered) without adding noisy per-token metrics.
- Keep ingest validation command output as the primary operational readiness signal for this WF.

## 10. Deferred / Not in MVP

- Automated source-document extraction/transformation pipelines.
- Policy DSL redesign beyond existing `reviewer_policy` schema.
- Broader cross-agency migration program beyond scoped calls.

## 11. Open Questions (if any)

- None for MVP. Defaults locked in this PRD revision:
  - Local copied source files stay gitignored for WF-0044 scope while manifests retain dual-path + SHA256 traceability.
  - Baseline verification remains ingest-focused, with targeted structured reviewer-policy tests for contract confidence.

## 12. Changelog

- v0.1 (2026-03-02): Initial PRD from brainstorm.
- v0.2 (2026-03-02): Applied risk-audit edits for deterministic structured-policy failure contract, explicit API acceptance seam, and locked MVP defaults; marked Ready for Tasks.
