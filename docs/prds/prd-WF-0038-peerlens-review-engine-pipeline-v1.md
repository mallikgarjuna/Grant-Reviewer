# WF-0038 — PeerLens Review Engine Pipeline v1 PRD

Artifact: prd
Version: v0.2
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
2. System treats this as an integrity/contract failure (no silent drop, no best-guess). (US3, US4)

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
  - `digest` (string)
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
  - Integrity rule: unmapped expectation refs are a contract failure (no silent drop, no best-guess).
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

- NWO archetype:
  - N1: missing required field ⇒ `STRUCTURE/COMPLIANCE` + `STRUCTURAL_LOCATOR` anchor
  - N2: word/format constraint ⇒ deterministic `WARNING|ERROR`
  - N3: evidence sufficiency only when declared
- ERC archetype:
  - E1: excellence expectations ⇒ `EXPECTATION_SATISFACTION`
  - E2: no feasibility/alignment unless declared
  - E3: stage/step activation selects WHAT only
- MSCA archetype:
  - M1: declared dependency missing ⇒ `NOT_ASSESSABLE` with reason (blocking surfaced in `STRICT` if `ERROR`)
  - M2: alignment requires declared dependencies
  - M3: feasibility only when declared

## 9. Telemetry (Minimal)

- Emit run-level metadata: `review_request_id`, `engine_ref`, `call_config_ref`, `mode_ref`, `stage_ref`, `subject_ref`, counts by `finding_kind/severity/assessment_status`.
- Explicitly do not log raw proposal text as part of telemetry by default (keep privacy posture consistent with product promises).

## 10. Deferred / Not in MVP

- Any public API/UI exposure of `DiagnosticFinding v1` as a first-class contract (v1 remains compatibility-mapped to `ReviewCard` externally).
- Any exposure of `Observation v1`.
- Numeric scoring or ranking.
- Full-proposal multi-section coherence as a default (beyond explicitly declared dependencies).

## 11. Open Questions

- None for v1 PRD stability; remaining work is task planning and implementation under frozen contracts.

## 12. Changelog

- v0.1 (2026-02-28): Initial PRD from brainstorm (contracts for modes, `ReviewRequest v1`, `DiagnosticFinding v1`, mapping, stress tests).
- v0.2 (2026-02-28): Applied Phase 1 runner risk-audit edits: added US/FR traceability, flows, data/contracts sectioning, module boundaries, and testing/telemetry decisions; marked Ready for Tasks.

## 2. Goals (v1)

- Produce a complete set of expectation-grounded diagnostics for a single section (`subject_ref`), with dependency context accepted only when explicitly declared by the call configuration.
- Guarantee traceability by construction: every finding is anchored and links to call-defined evaluation criteria/elements and a single primary expectation.
- Guarantee determinism for structured fields (identity/kind/severity/anchors/order) for identical inputs + `call_config_ref` + `engine_ref`.
- Preserve WHAT vs HOW separation:
  - Call config defines WHAT (evaluation criteria/elements, expectations, constraints, dependencies, stage activation).
  - Engine defines HOW (observation catalog, checks, mapping rules).
  - Modes define WHICH outputs are surfaced (projection only; no semantic drift).

## 3. Non-Goals (v1)

- No funder/program adapters, plug-ins, or engine branches (e.g., “if ERC then…”).
- No call-config-defined custom semantics (no custom finding kinds, no custom observation kinds, no scripted logic/DSL).
- No exposing Pass 1 artifacts: `Observation v1` is internal-only (not UI/API/analytics).
- No auto-rewriting in core outputs (analytical-only: problem + why + fix direction).
- No default numerical scoring; any scoring-like metadata must remain explicitly separate and must not contaminate evaluation logic (v1 does not introduce it).

## 4. Frozen v1 Contracts (PRD-level)

### 4.1 Modes — activation sets (Strict vs Diagnostic)

Mode semantics are projection-only (filter-only), not evaluation semantics.

- `DIAGNOSTIC` returns the full ordered `DiagnosticFinding v1[]` produced by the canonical pipeline over the active expectation set.
- `STRICT` returns a deterministic subset of the same ordered `DiagnosticFinding v1[]` using a fixed, engine-defined predicate:
  - include iff `severity == ERROR` (even if `assessment_status == NOT_ASSESSABLE`, so blocking missing-context remains visible).
- Superset invariant: for identical inputs + `call_config_ref` + `engine_ref`, `STRICT(findings)` is a subset of `DIAGNOSTIC(findings)`.

### 4.2 Canonical engine input envelope — `ReviewRequest v1`

Replayability boundary is locked: every request embeds the call-config snapshot.

`ReviewRequest v1` must include:

- `review_request_id` (string/uuid): stable request identity for audit/idempotency at the engine boundary.
- `engine_ref` (string): engine identity/version.
- `mode_ref` (`STRICT|DIAGNOSTIC`).
- `call_config_ref` (required):
  - `call_code_at_version` (string; e.g., `{call_code}@{semver}`)
  - `digest` (string)
- `call_config_snapshot` (required): the exact declarative call configuration used for the run; must match `call_config_ref.digest`.
- `stage_ref` (required): `{ stage, step }` (selectors of WHAT is active; stage influences WHAT via call config, not engine branching).
- `subject_ref` (required):
  - `node_logical_id` (string)
  - `field` (string; e.g., `narrative_text`)
- `submission` (required):
  - `primary_text` (string): text for `subject_ref`
  - `dependency_context` (optional map): only for dependencies explicitly declared in call config; values are `{ node_logical_id, field, text }`
  - `locale` (optional string)

Hard boundary:

- Call-defined expectation identity in findings is the call-config `expectation_id` (string) scoped by `call_config_ref` (not runtime DB ids).

### 4.3 `DiagnosticFinding v1` (atomic output) — frozen invariants

Each finding is single-primary, trace-first, and anchored.

Required fields (minimum trace spine):

- `finding_kind` (required; frozen enum v1): `STRUCTURE | COMPLIANCE | EXPECTATION_SATISFACTION | EVIDENCE_SUFFICIENCY | ALIGNMENT | FEASIBILITY`
- `severity` (required; frozen enum v1): `ERROR | WARNING | NOTE` (non-numeric)
- `assessment_status` (required): `ASSESSED | NOT_ASSESSABLE` (required reason when `NOT_ASSESSABLE`)
- `primary_expectation_ref` (string): call-defined `expectation_id` (scoped by `call_config_ref`)
- `criterion_ref`, `element_ref` (call-config references into evaluation criteria/elements)
- `check_id` (string): engine-defined check identity
- `subject_ref` (structured)
- `call_config_ref` (human + digest)
- `engine_ref` (string)
- `anchors[]` (required, ≥1): typed union `TEXT_SPAN | STRUCTURAL_LOCATOR | DERIVED` (derived anchors still point to a structural locator)

Deterministic aggregation identity (locked):

- One finding per (`primary_expectation_ref`, `subject_ref`, `check_id`).

Deterministic ordering (locked):

- Sort by `severity` desc (`ERROR > WARNING > NOTE`), then call-defined expectation order, then `check_id` as tie-break.

### 4.4 `DiagnosticFinding v1 → ReviewCard` deterministic mapping contract

Mapping is a pure compatibility adapter; engine SSOT remains `DiagnosticFinding v1`.

Cardinality (locked):

- Exactly 1 `ReviewCard` per (`subject_ref.node_logical_id`, `primary_expectation_ref`), aggregating all findings in that group deterministically.
- Group only by `primary_expectation_ref` (ignore `related_expectation_refs[]` for grouping/counting).

Field mapping rules (v1):

- `ReviewCard.node_expectation_id`:
  - Deterministically resolve `primary_expectation_ref` under `call_config_ref` to the persisted expectation identity the product stores.
  - Integrity rule: unmapped expectation refs are a contract failure (no silent drop, no best-guess).
- `ReviewCard.rating`:
  - Map group max severity: `ERROR → CRITICAL`, `WARNING → WARNING`, `NOTE → NOTE` (no `SUCCESS` in v1).
- `ReviewCard.assessment_status`:
  - `ASSESSED` if any grouped finding is `ASSESSED`; else `NOT_ASSESSABLE`.
- `ReviewCard.not_assessable_reason`:
  - If card status is `NOT_ASSESSABLE`: deterministic join of unique reasons from grouped findings (stable ordering).
  - Else null.
- `ReviewCard.feedback_text`:
  - Deterministic Markdown rendering from grouped findings using a fixed template; analytical-only (problem + why + fix direction), expectation/anchor grounded.

## 5. Stress-Test Matrix (acceptance cases)

Each archetype must be expressible with only: call-defined evaluation criteria/elements + expectations + constraints + dependencies + stage activation. No engine special-casing by funder/program.

### 5.1 NWO archetype (multi-criteria, compliance/format pressure)

- N1 Structure/compliance anchorability: missing required subsection/field yields `STRUCTURE` or `COMPLIANCE` with `STRUCTURAL_LOCATOR` anchor.
- N2 Constraint severity: word/format limit declared as a constraint yields deterministic `WARNING|ERROR` based on call-config strength/intent signals (no funder defaults).
- N3 Evidence sufficiency only when declared: `EVIDENCE_SUFFICIENCY` findings appear only if the call config declares evidence-related expectations.

### 5.2 ERC archetype (dominant excellence framing; avoids generic advice)

- E1 Excellence expectations: methodology/state-of-the-art expectations yield `EXPECTATION_SATISFACTION` findings grounded in declared expectations.
- E2 No “free” feasibility/alignment: `FEASIBILITY/ALIGNMENT` findings must not appear unless expectations/dependencies explicitly declare them.
- E3 Stage/step activation: changing `stage_ref` switches active expectations purely via call config; engine output changes only because WHAT changed.

### 5.3 MSCA archetype (template-like; cross-section alignment + dependencies)

- M1 Explicit NOT_ASSESSABLE: when call-config declares a dependency edge and context is missing, emit `NOT_ASSESSABLE` findings with explicit reason; `STRICT` must still surface those if `severity==ERROR`.
- M2 Alignment only via dependencies: `ALIGNMENT` findings require declared dependency edges (no inferred “global context”).
- M3 Feasibility only via declared expectations: feasibility diagnostics appear only when explicitly declared.

### 5.4 Cross-archetype determinism checks (must pass)

- Same `ReviewRequest v1` yields identical structured finding fields + ordering (text may vary only within bounded templates).
- No Observations leak beyond the engine boundary under any mode.

## 6. Adversarial critique — top 3 risks + mitigations (lifecycle-based)

### 6.1 Config authoring risk (highest coupling pressure)

Risk: call authors smuggle semantics (custom checks/kinds) or produce unstable expectation identity/versioning, breaking call-agnostic traceability.

Guardrails:

- Enforce expressiveness cap (expectations/constraints/dependencies/stage activation only).
- Require `call_config_ref` (human+digest) and require `call_config_snapshot` per run.
- Require stable `expectation_id` rules within a call-config version; changes require semver bump + digest change.

### 6.2 Runtime execution risk (determinism/trace collapse)

Risk: non-deterministic anchor selection or finding splitting/aggregation yields unrepeatable outputs, undermining trust.

Guardrails:

- Anchors mandatory for all findings and all observation kinds.
- Deterministic aggregation key is fixed: (`primary_expectation_ref`, `subject_ref`, `check_id`).
- Deterministic ordering is fixed: severity desc → call-defined expectation order → `check_id`.

### 6.3 Downstream consumption / governance risk (misuse of outputs)

Risk: consumers treat “no strict findings” as compliance; leak Observations; or convert severity counts into pseudo-scores/ranking.

Guardrails:

- Mode is explicit in the request; “absence of findings” must be treated as non-equivalent to compliance.
- Observations are explicitly non-contractual and must not be exposed.
- Analytics/governance must use `DIAGNOSTIC` outputs; `STRICT` is a UX projection only.

## 7. Phase 1 Output (this PRD)

This PRD freezes:

- Mode activation sets (filter-only strict vs diagnostic).
- Canonical engine input envelope (`ReviewRequest v1`) including mandatory `call_config_snapshot`.
- Deterministic `DiagnosticFinding v1 → ReviewCard` mapping (1 card per expectation per subject).
- NWO/ERC/MSCA stress-test matrix with pass/fail invariants.
- Lifecycle adversarial risks + guardrails.
