# WF-0038 — PeerLens Review Engine Pipeline v1 PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-28

## 0. User Stories (MVP)

- US1: As a researcher, I want section-level diagnostics grounded in evaluation criteria/elements and expectations, so I can revise a draft before submission.
- US2: As a researcher, I want a strict vs diagnostic view over the same computed findings, so I can focus on blockers first without losing coverage.
- US3: As the product, I want deterministic, expectation-grounded output that remains compatible with the existing `ReviewCard` surface, so we can adopt the new engine without breaking downstream consumers.
- US4: As an auditor/operator, I want review runs to be replayable and traceable to the exact call configuration and engine version used, so results remain defensible over time.

## Deferred Stories (Not in MVP)

- DS1: As a user, I want automatic rewriting of my text (explicitly out of scope for v1 core engine).
- DS2: As a user, I want default numeric scoring / ranking simulation.
- DS3: As a user, I want full-proposal coherence evaluation across all sections.
- DS4: As a consumer, I want Pass 1 `Observation v1` exposed as a UI/API/analytics contract.

## 1. In Scope

- Define a universal, call-agnostic Grant Review Engine Pipeline v1 that runs with no funder-specific branching/adapters.
- Freeze the canonical engine input envelope (`ReviewRequest v1`) and atomic output contract (`DiagnosticFinding v1`, trace-first).
- Freeze deterministic mode semantics (`STRICT` vs `DIAGNOSTIC`) as projection-only.
- Freeze a deterministic mapping contract from `DiagnosticFinding v1[]` → existing `ReviewCard[]` for compatibility.
- Define stress-test acceptance cases (NWO/ERC/MSCA archetypes) that prove “no funder branching” and config expressibility.

## 2. Out of Scope

- No engine funder/program adapters (no “if ERC then…”); all variability is in declarative call configuration.
- No call-config-defined custom semantics (no custom `finding_kind`, no custom `observation_kind`, no scripted logic/DSL).
- No exposure of Pass 1 `Observation v1` outside the engine boundary (not UI/API/analytics).
- No auto-rewriting in core outputs (analytical-only: problem + why + fix direction).
- No default numerical scoring; scoring (if ever added) must be optional/isolated and must not contaminate evaluation logic.

## 3. User / System Flow

### Happy path (section-level review)

1. User selects a funding call + review stage/step + proposal section and provides section text. (US1)
2. System builds `ReviewRequest v1` including:
   - `mode_ref` (`DIAGNOSTIC` by default),
   - `stage_ref` (stage/step),
   - `subject_ref` (node + field),
   - `call_config_snapshot` + `call_config_ref` (human + digest),
   - `submission.primary_text` and optional `dependency_context` (only when declared dependencies exist). (US1, US4)
3. Engine runs the universal two-pass pipeline:
   - Pass 1: normalize anchored `Observation v1` (internal-only).
   - Pass 2: evaluate expectations/constraints and emit ordered `DiagnosticFinding v1[]` (trace-first). (US1, US2, US4)
4. Compatibility adapter deterministically maps findings to `ReviewCard[]` (1 card per expectation per subject). (US3)
5. UI/API surfaces results using existing `ReviewCard` semantics; mode is reflected as a deterministic projection (strict vs diagnostic). (US2, US3)

### Failure path 1: missing dependency context (declared)

1. Call config declares a dependency edge for an expectation, but the required `dependency_context` is absent/empty. (US1)
2. Engine emits a `DiagnosticFinding v1` with `assessment_status = NOT_ASSESSABLE` and an explicit reason (still trace-first, anchored). (US1, US4)
3. In `STRICT` mode, the finding is surfaced iff it is `severity == ERROR` (blocking). (US2)

### Failure path 2: call-config digest mismatch / replayability violation

1. `call_config_snapshot` does not match `call_config_ref.digest`. (US4)
2. Engine rejects the request deterministically with a contract error (no partial evaluation). (US4)

### Failure path 3: expectation mapping failure in compatibility adapter

1. A `primary_expectation_ref` in findings cannot be resolved to the persisted expectation identity required by `ReviewCard`. (US3)
2. System treats this as an integrity/contract failure and aborts the review (no partial cards; no silent drop; no best-guess). (US3, US4)

## 4. Functional Requirements

- FR1 (US1, US4): Accept a canonical `ReviewRequest v1` envelope that is replayable (`call_config_snapshot` required) and call-agnostic (no funder branching).
- FR2 (US2): Implement modes as projection-only:
  - `DIAGNOSTIC` returns the full ordered `DiagnosticFinding v1[]`.
  - `STRICT` filters deterministically to `severity == ERROR` from the same computed set.
- FR3 (US1, US4): Enforce a two-pass pipeline boundary:
  - Pass 1 emits anchored `Observation v1` (internal-only).
  - Pass 2 emits `DiagnosticFinding v1[]` (atomic output).
- FR4 (US1, US4): Freeze `DiagnosticFinding v1` as trace-first:
  - required trace spine fields,
  - required typed anchors for all findings,
  - single-primary expectation reference with deterministic aggregation identity.
- FR5 (US1, US2, US4): Deterministic ordering for findings:
  - sort by `severity` desc, then call-defined expectation order, then `check_id` tie-break.
  - define call-defined expectation order as the explicit ordering in `call_config_snapshot` for that subject (list order is authoritative).
- FR6 (US3): Deterministic mapping from findings to existing `ReviewCard[]`:
  - 1 `ReviewCard` per (`subject_ref.node_logical_id`, `primary_expectation_ref`),
  - severity-to-rating mapping,
  - assessability roll-up rules,
  - integrity failure on unresolved expectation mapping.
- FR7 (US3): Prevent contract leakage:
  - `Observation v1` must not be exposed as an API/UI/analytics contract in v1.
- FR8 (US1, US4): Stage/step influences WHAT via call configuration activation only (no engine semantic branching).
- FR9 (US4): Enforce schema growth discipline:
  - admit new top-level `DiagnosticFinding v1` fields only if call-invariant and not derivable.
- FR10 (US1, US4): Stress-test acceptance must pass for NWO/ERC/MSCA archetypes without funder branching or call-defined semantics.

## 5. Data & API Contracts

### 5.1 Engine input — `ReviewRequest v1` (FR1)

Replayability boundary is locked: every request embeds the call-config snapshot.

`ReviewRequest v1` must include:

- `review_request_id` (string/uuid)
- `engine_ref` (string)
- `mode_ref` (`STRICT|DIAGNOSTIC`)
- `call_config_ref`:
  - `call_code_at_version` (string; `{call_code}@{semver}`)
  - `digest` (string): `sha256` of the canonical JSON serialization of `call_config_snapshot` (UTF-8, stable key ordering, and stable list ordering).
- `call_config_snapshot` (object; must match `call_config_ref.digest`)
- `stage_ref`: `{ stage, step }`
- `subject_ref`:
  - `node_logical_id` (string)
  - `field` (string)
- `submission`:
  - `primary_text` (string)
  - `dependency_context` (optional map): only for dependencies explicitly declared in call config; values are `{ node_logical_id, field, text }`
  - `locale` (optional string)

Hard boundary:

- Findings reference expectations via call-config `expectation_id` (string) scoped by `call_config_ref`, not runtime DB ids.

### 5.4 Error contracts (FR1, FR6)

The engine must distinguish deterministic contract failures from execution failures.

- Contract errors (reject request; no partial findings/cards):
  - `CALL_CONFIG_DIGEST_MISMATCH`
  - `MALFORMED_REVIEW_REQUEST`
  - `EXPECTATION_REF_UNRESOLVABLE` (mapping integrity failure in adapter)
- Execution failures (engine failed to evaluate despite valid contract):
  - `ENGINE_EXECUTION_FAILED`
  - `TIMEOUT`

### 5.2 Engine atomic output — `DiagnosticFinding v1` (FR4, FR5)

Each finding is single-primary, trace-first, and anchored.

Minimum required trace spine:

- `finding_kind` (required; frozen enum v1): `STRUCTURE | COMPLIANCE | EXPECTATION_SATISFACTION | EVIDENCE_SUFFICIENCY | ALIGNMENT | FEASIBILITY`
- `severity` (required; frozen enum v1): `ERROR | WARNING | NOTE` (non-numeric)
- `assessment_status` (required): `ASSESSED | NOT_ASSESSABLE` (required reason when `NOT_ASSESSABLE`)
- `criterion_ref`, `element_ref`
- `primary_expectation_ref` (string)
- `check_id` (string)
- `subject_ref` (structured)
- `call_config_ref` (human + digest)
- `engine_ref` (string)
- `anchors[]` (required, ≥1): typed union `TEXT_SPAN | STRUCTURAL_LOCATOR | DERIVED` (derived anchors still point to a structural locator)

Deterministic identity + aggregation:

- At most one finding per (`primary_expectation_ref`, `subject_ref`, `check_id`).

Deterministic ordering:

- Sort by `severity` desc (`ERROR > WARNING > NOTE`), then call-defined expectation order, then `check_id`.

### 5.3 Compatibility mapping — `DiagnosticFinding v1[] → ReviewCard[]` (FR6)

Mapping is a pure compatibility adapter; engine SSOT remains `DiagnosticFinding v1`.

Cardinality (locked):

- Exactly 1 `ReviewCard` per (`subject_ref.node_logical_id`, `primary_expectation_ref`).

Field mapping rules (v1):

- `ReviewCard.node_expectation_id`:
  - Resolve `primary_expectation_ref` under `call_config_ref` to the persisted expectation identity the product stores.
  - Integrity rule: unmapped expectation refs are a contract failure and aborts the review (no partial cards; no silent drop; no best-guess).
- `ReviewCard.rating`:
  - Map group max severity: `ERROR → CRITICAL`, `WARNING → WARNING`, `NOTE → NOTE` (no `SUCCESS` in v1).
- `ReviewCard.assessment_status`:
  - `ASSESSED` if any grouped finding is `ASSESSED`; else `NOT_ASSESSABLE`.
- `ReviewCard.not_assessable_reason`:
  - If card status is `NOT_ASSESSABLE`: deterministic join of unique reasons from grouped findings (stable ordering).
  - Else null.
- `ReviewCard.feedback_text`:
  - Deterministic Markdown rendering from grouped findings using a fixed template; analytical-only (problem + why + fix direction), expectation/anchor grounded.

## 6. Components / Modules

This PRD is architecture-only; module list is a boundary map for Phase 2 tasks.

Suggested design tree (high level):

1. Call-config activation selector (WHAT): selects active expectations/constraints for `stage_ref`.
2. Pass 1 observation extractor (HOW): emits anchored `Observation v1` (internal-only; strict catalog).
3. Pass 2 finding evaluator (HOW): emits ordered `DiagnosticFinding v1[]` (trace-first).
4. Mode projector: filters findings for `STRICT` vs `DIAGNOSTIC` without changing evaluation semantics.
5. Compatibility adapter: maps findings to persisted/user-facing `ReviewCard[]` deterministically.

Deep modules (stable seams, minimal interfaces):

- `ReviewRequest` validator: rejects digest mismatch and malformed envelopes deterministically.
- Anchor selection + normalization: guarantees stable anchors for identical inputs.
- Finding aggregation/orderer: enforces single-primary identity and stable ordering.
- ReviewCard mapper: the only module allowed to know about the existing `ReviewCard` persistence surface.

Coarse file-path suggestions (non-binding):

- `backend/app/engine/review_request.py` (envelope typing/validation)
- `backend/app/engine/observations/` (Pass 1)
- `backend/app/engine/findings/` (Pass 2 + aggregation + ordering)
- `backend/app/engine/modes.py` (projection-only)
- `backend/app/engine/compat/review_card_mapper.py` (mapping contract)

## 7. Edge Cases

- Missing dependency context for declared dependencies must yield explicit `NOT_ASSESSABLE` findings (not silent skip).
- `STRICT` mode must not hide blocking missing-context (surface if `severity == ERROR`).
- Anchor determinism: avoid multiple equally-plausible anchors without a deterministic selection rule.
- Expectation identity/versioning: `primary_expectation_ref` stability is scoped by `call_config_ref` (human + digest).
- Downstream misuse: consumers must not infer “no strict findings” as compliance; Observations must not leak.

## 8. Testing Decisions (TDD)

TDD required for behavior changes (Phase 3).

Test seams (public interfaces):

- `ReviewRequest v1` validation (digest match, required fields, declared dependency constraints). (FR1)
- Finding determinism:
  - stable ordering under identical inputs,
  - stable aggregation identity (`primary_expectation_ref`, `subject_ref`, `check_id`). (FR4, FR5)
- Mode projection:
  - `STRICT` is a pure filter of `DIAGNOSTIC` output (subset invariant). (FR2)
- Mapping determinism:
  - 1 card per expectation per subject,
  - correct severity-to-rating mapping,
  - integrity failure on unresolved expectation mapping. (FR6)

Stress-test matrix (acceptance cases) (FR10):

- NWO archetype (multi-criteria, compliance/format pressure):
  - N1: missing required subsection/field ⇒ `STRUCTURE` or `COMPLIANCE` with `STRUCTURAL_LOCATOR` anchor.
  - N2: word/format limit constraint ⇒ deterministic `WARNING|ERROR` (strength/intent driven; no funder defaults).
  - N3: `EVIDENCE_SUFFICIENCY` findings appear only when evidence-related expectations are declared in call config.
- ERC archetype (dominant excellence framing; avoids generic advice):
  - E1: excellence expectations (e.g., methodology/state-of-the-art) ⇒ `EXPECTATION_SATISFACTION` findings grounded in declared expectations.
  - E2: no “free” `FEASIBILITY/ALIGNMENT` findings unless expectations/dependencies explicitly declare them.
  - E3: stage/step activation changes WHAT via call config only; engine does not branch by funder/program.
- MSCA archetype (template-like; cross-section alignment + dependencies):
  - M1: declared dependency missing ⇒ `NOT_ASSESSABLE` finding with explicit reason (blocking surfaced in `STRICT` if `severity == ERROR`).
  - M2: `ALIGNMENT` findings require declared dependency edges (no inferred “global context”).
  - M3: feasibility diagnostics appear only when explicitly declared.

Cross-archetype determinism checks:

- Same `ReviewRequest v1` yields identical structured finding fields + ordering; narrative text may vary only within bounded templates.
- No Observations leak beyond the engine boundary (compile-time/API schema boundary + runtime tests).
- Anchor determinism: same inputs must yield the same anchors (type + locator + offsets/hashes where applicable).

## 9. Telemetry (Minimal)

- Emit run-level metadata: `review_request_id`, `engine_ref`, `call_config_ref`, `mode_ref`, `stage_ref`, `subject_ref`, counts by `finding_kind/severity/assessment_status`.
- Explicitly do not log raw proposal text as part of telemetry by default (keep privacy posture consistent with product promises).
- Anchor redaction rule: telemetry must not emit raw `TEXT_SPAN` content; log structural locators + offsets and/or stable hashes only.

## 10. Deferred / Not in MVP

- Any public API/UI exposure of `DiagnosticFinding v1` as a first-class contract (v1 remains compatibility-mapped to `ReviewCard` externally).
- Any exposure of `Observation v1`.
- Numeric scoring or ranking.
- Full-proposal multi-section coherence as a default (beyond explicitly declared dependencies).

## 10.1 Risks (Adversarial, v1)

Config authoring risk:

- Risk: call authors smuggle semantics (custom checks/kinds) or produce unstable expectation identity/versioning, breaking call-agnostic traceability.
- Guardrails: enforce expressiveness cap; require `call_config_ref` (human+digest) and `call_config_snapshot` per run; require stable ids and semver bumps on change.

Runtime execution risk:

- Risk: non-deterministic anchor selection or finding splitting/aggregation yields unrepeatable outputs, undermining trust.
- Guardrails: anchors mandatory; deterministic aggregation identity; deterministic ordering; anchor selection rules must be deterministic and test-covered.

Downstream consumption / governance risk:

- Risk: consumers treat “no strict findings” as compliance; leak Observations; or convert severity counts into pseudo-scores/ranking.
- Guardrails: explicit mode labeling; “absence ≠ compliance” governance; Observations remain internal-only; analytics uses `DIAGNOSTIC` output.

## 11. Open Questions

- None for v1 PRD stability; remaining work is task planning and implementation under frozen contracts.

## 12. Changelog

- v0.1 (2026-02-28): Initial PRD from brainstorm (contracts for modes, `ReviewRequest v1`, `DiagnosticFinding v1`, mapping, stress tests).
- v0.2 (2026-02-28): Applied Phase 1 runner risk-audit edits: added US/FR traceability, flows, data/contracts sectioning, module boundaries, and testing/telemetry decisions; marked Ready for Tasks.
- v0.3 (2026-02-28): Incorporated adversarial audit follow-ups: removed duplicated legacy PRD block, clarified digest canonicalization and expectation ordering source, clarified mapping failure abort semantics, expanded stress-test matrix and determinism tests, and added anchor redaction rules for telemetry.
