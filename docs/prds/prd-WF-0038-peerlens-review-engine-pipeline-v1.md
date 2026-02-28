# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: prd
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-28

## 1. Summary

Design a universal, call-agnostic review engine pipeline (no funder-specific branching) where all variability lives in declarative call configuration. The engine’s atomic output is `DiagnosticFinding v1` (trace-first, deterministic). A deterministic compatibility contract maps `DiagnosticFinding v1[]` to today’s persisted/user-facing `ReviewCard[]`.

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
