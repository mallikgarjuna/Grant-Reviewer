# WF-0038 — PeerLens Review Engine Pipeline v1

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-28

This file archives the detailed “Brainstorming Q&A” transcript for this WF.

Main brainstorm (decisions + frozen contracts): `docs/brainstorms/brainstorm-WF-0038-peerlens-review-engine-pipeline-v1.md`

---

## Section 1 — Problem Statement (Q&A)

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

## Section 2 — Desired Outcome (Q&A)

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
> Recommendation: A — preserves atomic-output and keeps compatibility as an explicit boundary.
> **Selected: A**

---

## Section 3 — Target User / Actor (Q&A)

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

## Section 4 — Rough Idea Exploration (Q&A)

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

## Section 5 — Constraints (Q&A)

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

## Section 6 — Risks / Unknowns (Q&A)

**Q1: What is the riskiest unknown that could force a re-architecture after we freeze v1 schemas?**
- A) Anchor model isn’t sufficient/consistent across all finding kinds.
- B) Expectation identity/versioning across call-config versions can’t stay stable.
- C) Two-pass boundary leaks semantics (observations behave like findings).
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
> Recommendation: B — anchors are the backbone; if anchors vary, identical findings become non-auditable.
> **Selected: B**

**Q4: What is the most likely downstream misuse risk (breaking the atomic-output philosophy)?**
- A) UI shows Observations directly (bypassing findings).
- B) UI or analytics uses `related_expectation_refs[]` as equal weight (reintroduces multi-primary semantics).
- C) Consumers invent scores from severity counts and treat them as ranking.
> Recommendation: A — once observations leak, you’ve created a second output contract that will drift.
> **Selected: A**

**Q5: What must be validated first with an adversarial stress test?**
- A) NWO/ERC/MSCA call configs can drive the same pipeline with no special-casing.
- B) Missing dependency context produces explicit NOT_ASSESSABLE findings with correct trace/anchors.
- C) Findings are stable in identity/kind/severity/anchors/order across repeated runs.
> Recommendation: A — directly tests the call-agnostic universality objective.
> **Selected: A**

---

## Section 7 — MVP Definition (Q&A)

**Q1: If we had to declare v1 engine done in one line, what must exist?**
- A) End-to-end: call config → two-pass pipeline → `DiagnosticFinding v1` list (trace-first) for one section.
- B) Only Pass 2 (findings) is defined; Pass 1 observations are deferred.
- C) Only structure/compliance kinds ship; other kinds deferred.
> Recommendation: A — matches atomic-output + two-pass decisions; B/C leave the pipeline definition incomplete.
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
> Recommendation: A — keeps dependency handling explicit and call-agnostic.
> **Selected: A**

**Q4: What is the MVP for `DiagnosticFinding v1 → ReviewCard` compatibility?**
- A) A deterministic mapping spec (field-to-field contract) is defined and frozen in v1.
- B) Mapping is best effort and left to downstream consumers.
- C) No mapping; findings replace cards immediately.
> Recommendation: A — compatibility is a top-risk seam; best effort will fail downstream.
> **Selected: A**

**Q5: What is the MVP boundary for adversarial stress test to satisfy exit criteria?**
- A) Written stress-test matrix: NWO/ERC/MSCA + expected invariants + contradiction checks.
- B) Narrative assurance only.
- C) Only a single call (NWO).
> Recommendation: A — exit criteria requires a real adversarial stress test.
> **Selected: A**

---

## Section 8 — Explicit Non-Goals (Q&A)

**Q1: Which tempting capability must be explicitly declared out-of-scope for WF-0038 (even if it’s easy)?**
- A) Auto-rewriting / generating improved text.
- B) Competitive ranking / simulation / fundability score.
- C) Full-proposal coherence audit across all sections.
> Recommendation: C — easiest path to scope explosion beyond section-first.
> **Selected: C**

**Q2: What must we explicitly forbid to protect call-agnostic purity?**
- A) Any funder-specific branching/adapters inside the engine.
- B) Call-config-defined custom semantics (custom kinds/checks).
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
- A) Per-call schema/output variants.
- B) Backwards-incompatible `DiagnosticFinding v1` changes without a version bump.
- C) Both A and B.
> Recommendation: C — prevents silent drift across calls and preserves long-term traceability.
> **Selected: C**
