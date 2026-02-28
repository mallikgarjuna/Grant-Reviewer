# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-02-28

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

---

## 1. Problem Statement (Section 1)

### Decisions (selected)

- Primary user harm to eliminate: untraceable diagnostics (findings must be defensible and expectation/anchor-grounded).
- MVP input boundary: single section + explicitly declared dependency context (only when call config declares dependencies).
- v1 success state: complete set of expectation-grounded findings across invariant kinds (not “only blockers” or “only top few”).
- Scoring promise: optional and explicitly separate metadata only (never driving evaluation logic).
- Definition of call-agnostic (strict): same engine; call config defines expectations/constraints; modes only toggle components (no call-defined semantics or funder adapters).

**Brainstorming Q&A:**

**Q1: What is the primary user harm this WF must eliminate (most important failure to prevent)?**
- A) Untraceable diagnostics (cannot justify a finding to a specific expectation/anchor).
- B) Funder/program coupling (engine behavior changes by funder logic rather than config).
- C) Non-determinism (same inputs yield materially different findings).
> Recommendation: A — trust collapses first when findings aren’t defensible; B/C matter, but trace-first is the audit spine.
> **Selected: A**

**Q2: What is the strict MVP input boundary for v1 reviews?**
- A) Single section text + call config only (no other sections).
- B) Single section text + explicitly declared dependency context (only when call config declares dependencies).
- C) Multi-section bundle always (engine always consumes multiple sections).
> Recommendation: B — preserves section-first scope while allowing declared dependencies without branching.
> **Selected: B**

**Q3: What is the primary “success state” for a v1 run (in one sentence)?**
- A) Produce only blocking compliance/structure findings (hard constraints).
- B) Produce a complete set of expectation-grounded findings across kinds (structure/compliance/expectations/evidence/etc.) for the section.
- C) Produce a small, prioritized subset of the most severe findings only.
> Recommendation: B — aligns with diagnostic coverage + traceability; “prioritized subset” is downstream filtering.
> **Selected: B**

**Q4: What is the user-visible promise about scoring in v1?**
- A) No scores are produced anywhere.
- B) Scores may exist only as optional, explicitly separate metadata (never driving evaluation logic).
- C) Lightweight scores are first-class but “advisory.”
> Recommendation: B — matches the non-contamination constraint while keeping an explicit optional layer.
> **Selected: B**

**Q5: What is the crisp definition of “call-agnostic” for this WF (pick the strictest acceptable)?**
- A) Same engine binary; call config selects expectations/constraints; modes only toggle components.
- B) Same engine binary; call config may also define custom finding kinds/observation types.
- C) Same engine binary; funder adapters are allowed as long as they’re “thin.”
> Recommendation: A — B/C reintroduce coupling via custom semantics or adapters.
> **Selected: A**

---

## 2. Desired Outcome (Section 2)

### Decisions (selected)

- Determinism definition: deterministic structured fields (identity/kind/severity/anchors/order), while explanatory text may vary within bounded patterns.
- Success metric tradeoff: two-tier—high precision for `ERROR`/blocking findings; allow more exploratory lower-severity notes with stricter framing.
- When to emit “higher-order” kinds (evidence/alignment/feasibility): only when call config declares relevant expectations/dependencies.
- Ordering contract: sort by severity desc, then call-defined expectation order, then `check_id` tie-break for stability.
- Compatibility: engine SSOT output is `DiagnosticFinding v1`; mapping to `ReviewCard` is an explicit downstream adapter/compatibility contract.

**Brainstorming Q&A:**

**Q1: What does “deterministic” mean for v1 outputs?**
- A) Fully deterministic including generated text (same inputs → identical text).
- B) Deterministic structured fields (ids/kind/severity/anchors/order), while explanatory text may vary within bounded templates.
- C) Only deterministic at the aggregate level (same “themes” but not stable per-finding identity).
> Recommendation: B — preserves auditability without pretending LLM prose is byte-identical.
> **Selected: B**

**Q2: What is the primary success metric tradeoff for v1?**
- A) Maximize precision (minimize false positives), even if it misses some issues.
- B) Maximize recall (find as many issues as possible), tolerating some false positives.
- C) Two-tier: high-precision for `ERROR`/blocking findings; allow more exploratory “notes” at lower severity.
> Recommendation: C — preserves trust where it matters most while still being diagnostically useful.
> **Selected: C**

**Q3: When should the engine emit findings for `EVIDENCE_SUFFICIENCY`, `ALIGNMENT`, `FEASIBILITY`?**
- A) Always, for every call/section.
- B) Never in v1; only structure/compliance/expectation satisfaction.
- C) Only when the call config (WHAT) declares relevant expectations/dependencies for those invariants.
> Recommendation: C — prevents generic advice from masquerading as expectation-grounded diagnostics.
> **Selected: C**

**Q4: What is the deterministic ordering contract for findings returned to downstream consumers?**
- A) Sort by `severity` desc, then by call-defined expectation order, then by `check_id`.
- B) Sort purely by call-defined expectation order.
- C) Sort by pipeline stage/kind order.
> Recommendation: A — severity-first is user-meaningful; expectation order preserves call intent; `check_id` tie-break ensures stability.
> **Selected: A**

**Q5: What is the desired outcome for compatibility with today’s `ReviewCard` world?**
- A) Engine’s SSOT output is `DiagnosticFinding v1`; mapping to `ReviewCard` is a downstream adapter/compat contract.
- B) Engine outputs both `DiagnosticFinding` and `ReviewCard` as peers.
- C) `ReviewCard` remains SSOT; `DiagnosticFinding` is only an internal intermediate.
> Recommendation: A — preserves the atomic-output decision and keeps compatibility as an explicit boundary.
> **Selected: A**

---

## 3. Target User / Actor (Section 3)

### Decisions (selected)

- Primary target user: researchers (self-diagnosis pre-submission); other consumers are secondary.
- False positives tolerance: moderate with clear labeling (especially at lower severity).
- Missing dependency context: explicit NOT_ASSESSABLE-style findings that explain what’s missing and why it blocks assessment.
- Primary enabled action: rewrite/improve the section outside the engine using fix direction.
- Explainability per finding: “because” rationale with explicit expectation + anchor references (auditable, not essay-length).

**Brainstorming Q&A:**

**Q1: Who is the primary target user for v1 engine outputs (not UI)?**
- A) Researchers (self-diagnosis pre-submission).
- B) Internal reviewers/consultants (expert service workflow).
- C) Admin/operators (quality control).
> Recommendation: A — aligns with researcher-trust positioning; B/C are secondary consumers.
> **Selected: A**

**Q2: What is the user’s tolerance for false positives in v1?**
- A) Very low: anything questionable must be framed as “uncertain” or omitted.
- B) Moderate: lower-severity findings can be suggestive but must be clearly labeled.
- C) High: more is better; user will sift.
> Recommendation: B — consistent with the two-tier precision policy.
> **Selected: B**

**Q3: What is the user’s tolerance for missing context when dependencies exist?**
- A) Never acceptable: engine must block if required dependency context is missing.
- B) Acceptable with NOT_ASSESSABLE findings that explain what’s missing.
- C) Acceptable silently; engine proceeds anyway.
> Recommendation: B — preserves section-first flow while staying honest and traceable.
> **Selected: B**

**Q4: What is the primary user action we want to enable after reading findings?**
- A) Rewrite the section (outside engine) guided by fix direction.
- B) Decide whether to submit at all (go/no-go).
- C) Compare against peers/competition.
> Recommendation: A — matches “no rewriting in engine” while still driving improvement.
> **Selected: A**

**Q5: What is the required explainability level per finding?**
- A) Short label only (fast scan).
- B) “Because” rationale with explicit expectation + anchor references (auditable).
- C) Full essay with extended justification.
> Recommendation: B — satisfies trace-first without bloating.
> **Selected: B**

---

## 4. Rough Idea Exploration (Section 4)

### Decisions (selected)

- Mode location: engine-defined execution profile selecting invariant components (no semantic drift; call-agnostic).
- Call-config WHAT unit: Expectation (stable call-defined `expectation_id`) mapping to evaluation criteria/elements + constraints; findings trace to expectations.
- Dependencies representation: explicit dependency edges declared by expectations, not global blobs or inference.
- Pass boundary: Pass 1 Observations are anchored facts; Pass 2 performs expectation evaluation + severity and emits findings.
- Missing dependency context: represent as a finding with explicit assessment status/reason (not silent skip; not separate artifact).

**Brainstorming Q&A:**

**Q1: Where should mode live in the system (definition-level)?**
- A) Mode is an engine execution profile that selects which invariant components run (no semantics).
- B) Mode is call-config-defined (per call can define its own modes).
- C) Mode is user-defined at runtime (free-form toggles).
> Recommendation: A — keeps semantics stable and call-agnostic.
> **Selected: A**

**Q2: What is the canonical WHAT unit that call config declares, which findings trace to?**
- A) Expectation (`expectation_id`) mapping to evaluation criteria/elements + constraints.
- B) EvaluationElement only (expectations become narrative).
- C) Check only (engine check ids become WHAT).
> Recommendation: A — aligns with trace-first and single-primary.
> **Selected: A**

**Q3: How should dependencies be represented (call-agnostic) for cross-section alignment?**
- A) Expectations can declare `requires_context_from` other sections (explicit dependency edges).
- B) A generic “global context” blob is always provided.
- C) Dependencies are inferred by the engine.
> Recommendation: A — explicit, deterministic, and avoids hidden coupling/inference.
> **Selected: A**

**Q4: What is the strict boundary between Observation (Pass 1) and Finding (Pass 2)?**
- A) Pass 1 only states anchored facts; Pass 2 performs expectation evaluation + severity.
- B) Pass 1 can already label failures/severity; Pass 2 just formats.
- C) Pass 1 is unstructured notes; Pass 2 does everything.
> Recommendation: A — preserves WHAT vs HOW separation and keeps severity policy centralized in Pass 2.
> **Selected: A**

**Q5: How do we handle NOT_ASSESSABLE outcomes in v1 (given dependency missing)?**
- A) As a finding with a dedicated status/reason field (still trace-first).
- B) As absence of findings (silent skip).
- C) As a separate assessment-status artifact outside findings.
> Recommendation: A — silent skip violates trust; separate artifact undermines the atomic-output contract.
> **Selected: A**

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

**Brainstorming Q&A:**

**Q1: What is the hard constraint on call-config expressiveness (to prevent funder logic smuggling)?**
- A) Call config may define expectations/constraints/dependencies only; it may not define new semantics (no custom kinds/checks).
- B) Call config may define custom checks (still declarative) as long as engine interprets them.
- C) Call config can include scripted logic in a restricted DSL.
> Recommendation: A — B/C are funder-logic-in-disguise and erode call-agnostic purity.
> **Selected: A**

**Q2: What is the hard constraint on engine outputs for explainability?**
- A) Every finding must include at least one anchor; anchors are always required.
- B) Only content-related findings need anchors; structure/compliance can omit.
- C) Anchors optional; rely on narrative.
> Recommendation: A — prevents hand-wavy outputs and preserves trace-first defensibility.
> **Selected: A**

**Q3: What is the constraint on versioning/compatibility for `DiagnosticFinding v1`?**
- A) Frozen schema + strict backward compatibility until a deliberate `v2`.
- B) Additive evolution allowed freely in v1 (fields can be added/renamed as needed).
- C) Per-call schema variants (v1 differs by call).
> Recommendation: A — avoids downstream breakage and prevents coupling through per-call variants.
> **Selected: A**

**Q4: What is the constraint on how review stage affects evaluation?**
- A) Stage influences WHAT via call config (expectations/elements active per stage), not engine branching.
- B) Stage is an engine mode that changes evaluation semantics.
- C) Stage is inferred from the input section.
> Recommendation: A — preserves call-agnostic behavior and keeps stage declarative.
> **Selected: A**

**Q5: What is the constraint on non-assessable handling?**
- A) Non-assessable must be explicit and trace-first (still a finding with status/reason + anchors).
- B) Non-assessable can be omitted if the user didn’t provide required context.
- C) Non-assessable is returned as a separate summary object, not per expectation.
> Recommendation: A — omission is silent failure; separate summaries violate the atomic-output contract.
> **Selected: A**

---

## 6. Risks / Unknowns (Section 6)

### Decisions (selected)

- Riskiest unknown for re-architecture risk: expectation identity/versioning stability across call-config versions.
- Biggest coupling pressure point: severity policy (where policy can leak into engine defaults).
- Biggest determinism failure mode: non-deterministic anchor selection.
- Most likely downstream misuse risk: leaking Observations as a user-facing/consumer-facing contract (bypassing findings).
- First adversarial stress test target: demonstrate one NWO + one ERC + one MSCA call config can drive the same pipeline stages with no special-casing.

**Brainstorming Q&A:**

**Q1: What is the riskiest unknown that could force a re-architecture after we freeze v1 schemas?**
- A) Anchor model isn’t sufficient/consistent across all finding kinds.
- B) Expectation identity/versioning across call-config versions can’t stay stable.
- C) Two-pass boundary leaks semantics (observations start behaving like findings).
> Recommendation: B — if expectation identity/versioning is unstable, trace-first collapses across time and across calls.
> **Selected: B**

**Q2: What is the biggest coupling pressure point (where funder-specific logic tends to sneak back in)?**
- A) Dependency modeling (cross-section alignment rules).
- B) Severity policy (what counts as ERROR vs WARNING vs NOTE).
- C) Not-assessable logic and missing-context handling.
> Recommendation: B — severity is where policy hides; if it isn’t strictly call-config-driven, funder semantics will leak into engine defaults.
> **Selected: B**

**Q3: What is the biggest determinism failure mode in practice?**
- A) Non-deterministic aggregation/splitting of findings across runs.
- B) Non-deterministic anchor selection.
- C) Non-deterministic ordering of checks/observations.
> Recommendation: B — anchors are the backbone; if anchors vary, identical findings become non-auditable even if ids are stable.
> **Selected: B**

**Q4: What is the most likely downstream misuse risk (breaking the atomic-output philosophy)?**
- A) UI shows Observations directly (bypassing findings).
- B) UI or analytics uses `related_expectation_refs[]` as equal weight (reintroduces multi-primary semantics).
- C) Consumers invent scores from severity counts and treat them as ranking.
> Recommendation: A — once observations leak, you’ve effectively created a second output contract that will drift and undermine trust.
> **Selected: A**

**Q5: What must be validated first with an adversarial stress test (to satisfy exit criteria)?**
- A) One NWO + one ERC + one MSCA call config can drive the same pipeline stages without any special-casing.
- B) No dependency provided produces explicit NOT_ASSESSABLE findings with correct trace/anchors.
- C) Findings remain stable in identity/kind/severity/anchors/order across repeated runs.
> Recommendation: A — directly tests the call-agnostic universality objective.
> **Selected: A**

---

## 7. MVP Definition (Section 7)

### Decisions (selected)

- v1 “engine done” definition: end-to-end call config → two-pass pipeline → `DiagnosticFinding v1` list (trace-first) for one section.
- Modes MVP: ship two engine-defined modes — strict (blocking-focused) and diagnostic (full coverage); calls may not define semantics.
- NOT_ASSESSABLE policy: emit NOT_ASSESSABLE findings only when call config declares an explicit dependency edge.
- Compatibility MVP: define and freeze a deterministic mapping spec from `DiagnosticFinding v1` → `ReviewCard` as a v1 contract.
- Exit-criteria stress test MVP: a written stress-test matrix (NWO/ERC/MSCA call configs + expected invariants + contradiction checks).

**Brainstorming Q&A:**

**Q1: If we had to declare v1 engine done in one line, what must exist?**
- A) End-to-end: call config → two-pass pipeline → `DiagnosticFinding v1` list (trace-first) for one section.
- B) Only Pass 2 (findings) is defined; Pass 1 observations are deferred.
- C) Only structure/compliance kinds ship; other kinds deferred.
> Recommendation: A — matches atomic-output + two-pass decisions; B/C leave the pipeline definition incomplete (exit criteria miss).
> **Selected: A**

**Q2: What is the strict MVP surface area for modes (execution profiles)?**
- A) Exactly 1 mode in v1 (default).
- B) 2 modes: strict and diagnostic.
- C) Modes are fully call-defined.
> Recommendation: B — supports the two-tier precision policy without letting calls define semantics.
> **Selected: B**

**Q3: What is the MVP policy for dependency-driven NOT_ASSESSABLE findings?**
- A) Emit NOT_ASSESSABLE findings only when the call config declares a dependency edge.
- B) Emit NOT_ASSESSABLE whenever the engine thinks context might help.
- C) Never emit NOT_ASSESSABLE in v1 (block the run instead).
> Recommendation: A — keeps dependency handling explicit and call-agnostic; B invites inference/coupling; C is too blocking.
> **Selected: A**

**Q4: What is the MVP for `DiagnosticFinding v1 → ReviewCard` compatibility?**
- A) A deterministic mapping spec (field-to-field contract) is defined and frozen in v1.
- B) Mapping is best effort and left to downstream consumers.
- C) No mapping; findings replace cards immediately.
> Recommendation: A — compatibility is a top-risk seam; best effort will fail downstream.
> **Selected: A**

**Q5: What is the MVP boundary for adversarial stress test to satisfy exit criteria?**
- A) A written stress-test matrix: NWO/ERC/MSCA call configs + expected pipeline invariants + contradiction checks.
- B) Only a narrative assurance (it’s call-agnostic by design).
- C) Only a single call (NWO) is used for stress testing in v1.
> Recommendation: A — exit criteria requires an adversarial stress test; B/C won’t satisfy it.
> **Selected: A**

---

## 8. Explicit Non-Goals (Section 8)

### Decisions (selected)

- Explicitly out-of-scope for this WF: full-proposal coherence audit across all sections (scope-explosion vector).
- Purity guardrails (explicit forbiddance): no funder-specific engine branching/adapters, and no call-config-defined custom semantics (custom kinds/checks).
- Observation non-goal: Observations are never exposed outside the engine boundary (no UI/API/analytics contract).
- Scoring non-goal: no default numeric score computation.
- Evolution non-goal: no per-call schema/output variants and no backwards-incompatible `DiagnosticFinding v1` changes without an explicit version bump.

**Brainstorming Q&A:**

**Q1: Which tempting capability must be explicitly declared out-of-scope for WF-0038 (even if it’s easy)?**
- A) Auto-rewriting / generating improved text.
- B) Competitive ranking / simulation / fundability score.
- C) Full-proposal coherence audit across all sections.
> Recommendation: C — easiest path to scope explosion beyond section-first.
> **Selected: C**

**Q2: What must we explicitly forbid to protect call-agnostic purity?**
- A) Any funder-specific branching/adapters inside the engine.
- B) Call-config-defined custom semantics (custom finding kinds / custom observation kinds / custom checks).
- C) Both A and B.
> Recommendation: C — forbidding only one still allows semantic coupling via the other path.
> **Selected: C**

**Q3: What should be an explicit non-goal for v1 regarding Observations?**
- A) Observations are never exposed outside the engine boundary (no UI/API/analytics contract).
- B) Observations can be optionally exposed for debugging.
- C) Observations are first-class and visible in the UI.
> Recommendation: A — prevents a second drifting output contract that undermines atomic output.
> **Selected: A**

**Q4: What should be an explicit non-goal for v1 regarding scoring?**
- A) Any default numeric score computation.
- B) Any score storage anywhere (even optional metadata).
- C) Any severity levels at all (only narrative).
> Recommendation: A — matches scoring-optional while preserving severity-based findings.
> **Selected: A**

**Q5: What should be an explicit non-goal for v1 regarding call-config evolution?**
- A) Per-call schema variants or per-call output variants.
- B) Backwards-incompatible changes to `DiagnosticFinding v1` without a version bump.
- C) Both A and B.
> Recommendation: C — prevents silent drift across calls and preserves long-term traceability.
> **Selected: C**
