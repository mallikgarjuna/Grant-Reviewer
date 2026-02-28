# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: brainstorm
Version: v0.6
Status: Draft Complete
Last Updated: 2026-02-28

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md`

## Contract Safety (SSOT)

- This brainstorm is SSOT for the contracts/decisions that Phase 1+ will rely on.
- The Q&A transcript is rationale only; if a contract appears only in Q&A, promote it into this brainstorm and log it.
- Open questions must stay visible here (not buried in Q&A) to prevent false completeness.

## Objective

Design a universal, call-agnostic Grant Review Engine Pipeline that works across NWO / ERC / MSCA with **no funder-specific branching** in the engine. All variability lives in declarative call configuration. The engine produces `DiagnosticFinding v1` as its atomic output.

## Inputs / Current Truth

- Source of truth (architecture snapshot): `docs/reference/architecture_chat.md`
- Evaluation terminology: use “evaluation criteria/elements” (not “rubric”)

## Repo Reality Snapshot (Read-Only) (2026-02-28)

- Current persisted/user-facing atomic output in the product is `ReviewCard` (linked to `NodeExpectation`), not `DiagnosticFinding`.
- `DiagnosticFinding v1` currently exists only as an architecture concept/logged decisions (no code-level schema/type yet).
- Call ingestion has an explicit V2 schema (`backend/app/schemas/call_definitions_v2.py`) that models evaluation criteria/elements and `NodeExpectation` links to elements.
- Domain model docs assert “no scoring, no rewriting” and expectation-linked `ReviewCard` outputs as the MVP shape (`docs/reference/domain_model.md`).
- Multiple prior WFs touched review execution and `ReviewCard` semantics, so mapping `DiagnosticFinding v1 → ReviewCard` must be treated as a compatibility contract.

Open questions this snapshot raises:
- Does `DiagnosticFinding v1` replace `ReviewCard` internally, or is it an intermediate artifact that maps 1:1 (or N:1) onto `ReviewCard`?
- What is the authoritative identifier for “expectation” in v1 findings: `NodeExpectation` id, YAML expectation id, or a new stable expectation logical id?
- How do we preserve “trace-first” determinism across call ingestion versions (V2 schema) without leaking funder concepts into the engine?

## Locked Decisions (Snapshot)

- Product identity: surgical pre-submission diagnostic tool; optimized for researcher trust.
- v1 scope: section-level diagnostics first (no full-proposal engine yet).
- Output philosophy: analytical-only findings (problem + why + fix direction), no rewriting; traceable to expectations; precision/traceability > performance/flash.
- Qualitative evaluation is primary; numerical scoring is optional/secondary and isolated (must not contaminate core logic).
- One canonical, call-agnostic engine: calls define WHAT; engine defines HOW; modes define WHICH components are activated; extend via configuration, not mutation; atomic output is `DiagnosticFinding v1`.

## Glossary (v1 architecture terms)

- **Call-config (call configuration)**: the declarative, funder/program-specific *data* that defines WHAT to evaluate for a specific call (evaluation criteria/elements, expectations, constraints, dependencies, and activation by stage/step). The engine must not contain funder branching; call variability lives here.
- **Engine adapters**: funder/program-specific code paths (e.g., “if ERC then…”), shims, or plug-ins inside the engine that alter evaluation behavior. These are explicitly forbidden for WF-0038 (coupling risk); any variability must be expressed via call-config.
- **Modes**: engine-defined execution profiles (not call-defined semantics) that toggle which invariant components run and how results are surfaced (e.g., stricter vs more exploratory output) without changing the underlying call-config semantics.
- **Pass 1 / Pass 2 (two-pass pipeline)**:
  - **Pass 1 (Observations)**: produce anchored, normalized “facts about the submission” (no expectation scoring/labeling); output is `Observation v1`.
  - **Pass 2 (Findings)**: evaluate observations against call-config expectations/constraints and emit `DiagnosticFinding v1` (with kind, severity, assessment status, and trace).
- **Stage vs Step (“review stage”)**: a call-config notion for which requirements/expectations are active at a given point (e.g., `STEP_1` vs `STEP_2`). The engine does not branch by funder; it uses stage/step only as an input that selects WHAT is active in the call-config.
- **WHAT unit vs HOW unit**:
  - **WHAT unit**: the call-defined thing being evaluated (v1: an `expectation_id`, mapped to evaluation criteria/elements and constraints).
  - **HOW unit**: the engine mechanism used to evaluate (e.g., `observation_kind`, `check_id`, pipeline components). HOW must remain call-agnostic and stable.
- **Dependency**: an explicit call-config edge that states an expectation requires context from another section/node (for cross-section alignment). Missing required dependency context yields explicit `NOT_ASSESSABLE` findings rather than silent skipping.
- **Anchors**: required, typed references that justify a claim. Every finding must have ≥1 anchor:
  - `TEXT_SPAN` (quote/offsets), or
  - `STRUCTURAL_LOCATOR` (node/logical location + field), or
  - `DERIVED` (computed, still pointing to a structural locator).
- **Two modes (“strict” vs “diagnostic”)**: intended engine-defined profiles:
  - **Strict (blocking-focused)**: emphasize high-precision `ERROR`/blocking findings; minimize lower-severity exploratory notes.
  - **Diagnostic (full coverage)**: emit the complete set of expectation-grounded findings (including lower-severity notes) consistent with the call-config and invariant kinds.

## Decisions Approved (This Chat, 2026-02-28)

1. `DiagnosticFinding v1` is trace-first (required traceability/determinism fields).
2. Interactive Q&A format is standardized: each question includes explicit options + assistant recommendation.
3. WF-tagging discipline: all architecture decisions + Q&A entries are tagged with the WF id.
4. Adversarial critique standard: 3 risks must cover (a) config authoring, (b) runtime execution, (c) downstream consumption/governance; each risk includes a recommended mitigation/guardrail.
5. Call-agnostic pipeline v1: two-pass model (Pass 1 normalized observations; Pass 2 maps observations → `DiagnosticFinding v1`).

## Contract Notes (Non-obvious)

- SSOT rule: this brainstorm defines contracts; Q&A transcript is rationale only (promote any contract found only in Q&A into this doc + log it).
- No adapter rule: engine contains no funder/program branching; all variability lives in declarative call-config.
- Finding identity rule: at most one finding per (`primary_expectation_ref`, `subject_ref`, `check_id`) to prevent duplication/drift.

## Exit Criteria (Status)

Already satisfied (principle-level):
- WHAT vs HOW separation is stated and treated as a core design constraint.
- Scoring is explicitly isolated/optional (no contamination of core evaluation).

Missing / not yet frozen:
- `DiagnosticFinding v1` schema is frozen (constraints specified precisely enough to implement without further architecture decisions).
- Call-agnostic pipeline v1 is fully defined (stage contracts + required artifacts across both passes).
- Adversarial stress test finds no structural contradictions (for at least NWO / ERC / MSCA configurations).
- Implementation blueprint can be described without new architecture decisions.

## Next Architectural Decisions (Queue)

- Freeze `DiagnosticFinding v1` field-level constraints (required vs optional, enums, referential integrity expectations).
- Define “Observation v1” catalog/vocabulary and its determinism/trace guarantees (Pass 1 output).
- Specify how call configuration declares expectations, constraints, and evaluation criteria/elements (WHAT) without encoding funder-specific semantics.
- Define execution profiles (modes) as activation sets over the two-pass pipeline.
- Map `DiagnosticFinding v1` to the existing `ReviewCard` surface (downstream compatibility contract).

## Remaining Open Decisions (Phase 1)

These are intentionally deferred to Phase 1 (PRD) so Phase 2 task planning can proceed without new architecture decisions:

- Mode activation sets: exact component toggles + output filtering rules for `strict` vs `diagnostic`.
- Canonical engine input envelope: a single serialized “review request” shape (fields + normalization) covering target subject + optional dependency context.
- `DiagnosticFinding v1 → ReviewCard` mapping spec: deterministic 1:1 field mapping and any required adapter invariants.
- Stress-test matrix concretization: select representative NWO/ERC/MSCA call-config archetypes and enumerate contradiction checks against frozen contracts.

---

## 1. Problem Statement (Section 1)

### Decisions (selected)

- Primary user harm to eliminate: untraceable diagnostics (findings must be defensible and expectation/anchor-grounded).
- MVP input boundary: single section + explicitly declared dependency context (only when call config declares dependencies).
- v1 success state: complete set of expectation-grounded findings across invariant kinds (not “only blockers” or “only top few”).
- Scoring promise: optional and explicitly separate metadata only (never driving evaluation logic).
- Definition of call-agnostic (strict): same engine; call config defines expectations/constraints; modes only toggle components (no call-defined semantics or funder adapters).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 1)

---

## 2. Desired Outcome (Section 2)

### Decisions (selected)

- Determinism definition: deterministic structured fields (identity/kind/severity/anchors/order), while explanatory text may vary within bounded patterns.
- Success metric tradeoff: two-tier—high precision for `ERROR`/blocking findings; allow more exploratory lower-severity notes with stricter framing.
- When to emit “higher-order” kinds (evidence/alignment/feasibility): only when call config declares relevant expectations/dependencies.
- Ordering contract: sort by severity desc, then call-defined expectation order, then `check_id` tie-break for stability.
- Compatibility: engine SSOT output is `DiagnosticFinding v1`; mapping to `ReviewCard` is an explicit downstream adapter/compatibility contract.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 2)

---

## 3. Target User / Actor (Section 3)

### Decisions (selected)

- Primary target user: researchers (self-diagnosis pre-submission); other consumers are secondary.
- False positives tolerance: moderate with clear labeling (especially at lower severity).
- Missing dependency context: explicit NOT_ASSESSABLE-style findings that explain what’s missing and why it blocks assessment.
- Primary enabled action: rewrite/improve the section outside the engine using fix direction.
- Explainability per finding: “because” rationale with explicit expectation + anchor references (auditable, not essay-length).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 3)

---

## 4. Rough Idea Exploration (Section 4)

### Decisions (selected)

- Mode location: engine-defined execution profile selecting invariant components (no semantic drift; call-agnostic).
- Call-config WHAT unit: Expectation (stable call-defined `expectation_id`) mapping to evaluation criteria/elements + constraints; findings trace to expectations.
- Dependencies representation: explicit dependency edges declared by expectations, not global blobs or inference.
- Pass boundary: Pass 1 Observations are anchored facts; Pass 2 performs expectation evaluation + severity and emits findings.
- Missing dependency context: represent as a finding with explicit assessment status/reason (not silent skip; not separate artifact).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 4)

---

## 5. Constraints (Section 5)

### Decisions (selected)

- Call-config expressiveness constraint: call config may define expectations/constraints/dependencies only; it may not define new semantics (no custom kinds/checks).
- Explainability constraint: every finding must include at least one anchor; anchors are always required.
- Versioning constraint: `DiagnosticFinding v1` is frozen and backward-compatible until an intentional `v2`.
- Stage constraint: stage influences WHAT via call config (which expectations are active), not engine branching.
- Non-assessable constraint: must be explicit and trace-first per finding (status/reason + anchors), not silent omission or separate summary.

### Frozen v1 mini-contracts (risk-audit closure)

- Stable expectation reference:
  - `primary_expectation_ref` uses the call-defined `expectation_id` (string), not a runtime DB id.
  - Every finding includes `call_config_ref` so expectation identity is stable-within-version and auditable across time.
- `call_config_ref` includes both human and digest forms:
  - `{call_code}@{semver}` + `{digest}`.
- Severity + assessment:
  - `severity` enum: `ERROR`, `WARNING`, `NOTE` (non-numeric).
  - Severity policy may consider (deterministically): expectation strength, criterion weight/importance, and declared risk intent/impact signals in call config (without introducing call-defined custom semantics).
  - `assessment_status` enum: `ASSESSED` | `NOT_ASSESSABLE`; when `NOT_ASSESSABLE`, a reason is required.
- Anchor definition (required for all findings):
  - `TEXT_SPAN` OR `STRUCTURAL_LOCATOR` OR `DERIVED` (derived anchors still point to a structural locator).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 5)

---

## 6. Risks / Unknowns (Section 6)

### Decisions (selected)

- Riskiest unknown for re-architecture risk: expectation identity/versioning stability across call-config versions.
- Biggest coupling pressure point: severity policy (where policy can leak into engine defaults).
- Biggest determinism failure mode: non-deterministic anchor selection.
- Most likely downstream misuse risk: leaking Observations as a user-facing/consumer-facing contract (bypassing findings).
- First adversarial stress test target: demonstrate one NWO + one ERC + one MSCA call config can drive the same pipeline stages with no special-casing.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 6)

---

## 7. MVP Definition (Section 7)

### Decisions (selected)

- v1 “engine done” definition: end-to-end call config → two-pass pipeline → `DiagnosticFinding v1` list (trace-first) for one section.
- Modes MVP: ship two engine-defined modes — strict (blocking-focused) and diagnostic (full coverage); calls may not define semantics.
- NOT_ASSESSABLE policy: emit NOT_ASSESSABLE findings only when call config declares an explicit dependency edge.
- Compatibility MVP: define and freeze a deterministic mapping spec from `DiagnosticFinding v1` → `ReviewCard` as a v1 contract.
- Exit-criteria stress test MVP: a written stress-test matrix (NWO/ERC/MSCA call configs + expected invariants + contradiction checks).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 7)

---

## 8. Explicit Non-Goals (Section 8)

### Decisions (selected)

- Explicitly out-of-scope for this WF: full-proposal coherence audit across all sections (scope-explosion vector).
- Purity guardrails (explicit forbiddance): no funder-specific engine branching/adapters, and no call-config-defined custom semantics (custom kinds/checks).
- Observation non-goal: Observations are never exposed outside the engine boundary (no UI/API/analytics contract).
- Scoring non-goal: no default numeric score computation.
- Evolution non-goal: no per-call schema/output variants and no backwards-incompatible `DiagnosticFinding v1` changes without an explicit version bump.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0038-peerlens-review-engine-pipeline-v1.md` (Section 8)

---

## Refinement Pass (Exit Criteria Closure) (2026-02-28)

This pass tightens remaining ambiguity to move closer to the architecture exit criteria in `docs/reference/architecture_chat.md`:
- “DiagnosticFinding v1 schema is frozen”
- “Call-agnostic pipeline v1 is defined”
- “Adversarial stress test finds no structural contradictions”

### Decisions (selected)

- “Schema frozen” bar: enumerate field-level contract + invariants (not code/types).
- “Observation v1” bar: small fixed `observation_kind` catalog + required fields per kind (anchored + subject-scoped) to keep Pass 2 deterministic.
- “Pipeline defined” bar: define stage contracts (inputs/outputs), determinism/ordering rules, failure handling, and NOT_ASSESSABLE policy (no implementation internals).
- Compatibility: `DiagnosticFinding v1 → ReviewCard` mapping is 1:1 and deterministic.
- Stress test: add a 3-archetype (NWO/ERC/MSCA) matrix against invariants + “no engine branching” checks.

**Brainstorming Q&A:**

**Q1: What does “DiagnosticFinding v1 schema is frozen” mean operationally in this brainstorm?**
- A) Freeze only constraints/principles (fields implied, not enumerated).
- B) Enumerate exact required/optional fields (names + meanings), but not invariants.
- C) Enumerate fields + field-level invariants (cardinality, allowed enums, required refs), still no implementation.
> Recommendation: C — exit criteria requires “implement without new architecture decisions”.
> **Selected: C**

**Q2: What is the minimum `Observation v1` output contract we must freeze now to keep Pass 2 deterministic?**
- A) Only `observation_kind` + anchors; everything else ad hoc.
- B) Small fixed catalog of observation kinds + required fields per kind (including `subject_ref` + anchors).
- C) Full observation catalog for all invariant checks.
> Recommendation: B — enough for deterministic mapping without pretending we know every future observation.
> **Selected: B**

**Q3: What is the “Call-agnostic pipeline v1 is defined” bar for this brainstorm?**
- A) Name the stages only (Pass 1, Pass 2).
- B) Define stage contracts: inputs/outputs + determinism/ordering rules + failure handling + NOT_ASSESSABLE policy.
- C) Define full stage internals (algorithms, prompts).
> Recommendation: B — contracts are required; internals drift into implementation.
> **Selected: B**

**Q4: What does “mapping DiagnosticFinding v1 → ReviewCard” mean as a compatibility contract?**
- A) 1:1 mapping: each finding corresponds to one ReviewCard.
- B) N:1 mapping: multiple findings may roll up to one ReviewCard.
- C) 1:N mapping: one finding may fan out to multiple ReviewCards.
> Recommendation: A — simplest, most deterministic, least room for downstream ambiguity.
> **Selected: A**

**Q5: What is the minimum adversarial stress test artifact we must add to satisfy exit criteria?**
- A) Matrix of 3 call-config archetypes (NWO/ERC/MSCA) × invariants × expected finding kinds, plus “no engine branching” checks.
- B) Single narrative test plan paragraph.
- C) Full test suite design (cases, inputs, expected outputs per case).
> Recommendation: A — concrete enough to expose contradictions without drifting into implementation.
> **Selected: A**

---

## Frozen Contracts (Architecture-Level; v1)

### `DiagnosticFinding v1` (atomic output) — frozen contract (field-level)

Required (every finding):
- `finding_kind`: one of `STRUCTURE|COMPLIANCE|EXPECTATION_SATISFACTION|EVIDENCE_SUFFICIENCY|ALIGNMENT|FEASIBILITY`
- `severity`: one of `ERROR|WARNING|NOTE` (non-numeric)
- `assessment_status`: one of `ASSESSED|NOT_ASSESSABLE` (when `NOT_ASSESSABLE`, a human-readable reason is required)
- `primary_expectation_ref`: call-defined `expectation_id` (string)
- `criterion_ref` and `element_ref`: the evaluation criterion/element references the expectation is grounded in
- `check_id`: stable engine check identifier (HOW)
- `subject_ref`: the evaluated unit (minimum: `{call_code, node_logical_id, field_id?}`; `field_id` is optional but required when an anchor uses a sub-field structural locator)
- `anchors[]`: ≥1 typed anchor (`TEXT_SPAN|STRUCTURAL_LOCATOR|DERIVED`)
- `call_config_ref`: includes `{call_code}@{semver}` and `{digest}`
- `engine_ref`: includes `{engine_semver}` and `{build_id}` (immutable)

Optional:
- `related_expectation_refs[]`: trace-only cross-links (same-kind only)
- Explanatory text fields (short): problem + why + fix direction (must not contain rewriting)

Invariants:
- Single-primary trace: exactly 1 `primary_expectation_ref` per finding.
- Related refs must not cross `finding_kind` boundaries.
- Determinism: structured fields (ids/kind/severity/anchors/order) must be stable for identical inputs + call_config_ref + engine_ref.
- Self-describing trace: `criterion_ref` and `element_ref` are required and must match the declared mapping for `primary_expectation_ref` under `call_config_ref` (mismatch = invalid output).
- Aggregation determinism: at most one finding per (`primary_expectation_ref`, `subject_ref`, `check_id`).
- Ordering determinism: sort by severity (`ERROR > WARNING > NOTE`), then call-defined expectation order, then `check_id`.

### `Observation v1` (Pass 1 output) — minimal frozen contract

All observations (required):
- `observation_kind` (strict catalog; engine-defined)
- `primary_expectation_ref`: call-defined `expectation_id` (string); observations are expectation-scoped but do not assign severity or satisfied/unsatisfied labels
- `subject_ref` (minimum: `{call_code, node_logical_id, field_id?}`)
- `anchors[]` (≥1; same typed anchor union as findings)
- `call_config_ref` + `engine_ref`

Naming constraint:
- `observation_kind` values encode only the invariant dimension (STRUCTURE/COMPLIANCE/…); they must not encode pass/fail or severity semantics.
- A `*_SIGNAL` does not imply pass/fail; it is only a typed container for anchored observations.

Minimal `observation_kind` catalog (v1; extend only by engine versioned change):
- `STRUCTURE_SIGNAL`
- `COMPLIANCE_SIGNAL`
- `EXPECTATION_SIGNAL`
- `EVIDENCE_SIGNAL`
- `ALIGNMENT_SIGNAL`
- `FEASIBILITY_SIGNAL`
- `DEPENDENCY_CONTEXT_MISSING` (must include `missing_subject_ref` and the dependency edge identifier)

### Call-agnostic Pipeline v1 — stage contracts (no internals)

Inputs (minimum):
- Call-config (WHAT) + `call_config_ref`
- Engine mode (`strict` or `diagnostic`)
- Stage/step selector (e.g., `STEP_1|STEP_2|...`) that activates WHAT via call-config
- Target `subject_ref` content (single section)
- Dependency context inputs only when explicitly declared by dependency edges in call-config

Pass 1 (Observations):
- Produces `Observation v1[]` (anchored, expectation-scoped facts about the submission), no severity, and no satisfied/unsatisfied labels.

Pass 2 (Findings):
- Consumes observations + call-config expectations/constraints/dependencies and emits `DiagnosticFinding v1[]`.
- Missing dependency context: emits explicit NOT_ASSESSABLE findings (only when dependency edge is declared).

Failure handling (architecture-level):
- Invalid/missing call-config: fail-fast (no partial findings).
- Missing dependency context when required: not a pipeline failure; results in NOT_ASSESSABLE findings.

Additional v1 determinism constraints:
- Severity policy tie-break: if any policy input implies `ERROR`, severity is `ERROR`; else if any implies `WARNING`, severity is `WARNING`; else `NOTE`. Call-config may tune thresholds/inputs, but may not add new severity levels.
- `check_id` stability: `check_id` is engine-defined and mode-invariant; call-config cannot introduce or rename checks.

---

## Adversarial Stress Test Matrix (v1; written artifact)

Archetypes (config-only; no engine branching):
- **NWO-like**: strong compliance/structural constraints + section expectations; limited cross-section dependencies.
- **ERC-like**: stage/step-specific activation of expectations (e.g., Step 1 vs Step 2), strict policy constraints, and emphasis on criterion scoping.
- **MSCA-like**: multi-criterion expectations with explicit dependencies (alignment + feasibility concerns), still section-first.

Matrix expectations (must hold for all three):
- Same engine pipeline stages execute (two-pass), no funder branching/adapters.
- Findings remain trace-first and deterministic (structured fields stable).
- `finding_kind` remains within frozen enum; no call-defined kinds/check semantics.
- Missing declared dependency context produces NOT_ASSESSABLE findings with anchors and trace (not silence).
- Severity remains non-numeric and policy-driven via call-config metadata, not funder code.
- Contradiction checks: (a) any requirement forces engine branching/adapters, (b) any requirement demands new `finding_kind`/custom check semantics, (c) any requirement cannot be expressed as expectation/constraint/dependency/stage activation in call-config.
