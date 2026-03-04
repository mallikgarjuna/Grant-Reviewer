# WF-0053 — Contract Boundary Governance Enforcement

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Preflight

### Step 1 — Long-Form Problem Intake

**Q1: Should we use the agent-recommended long-form narrative as WF-0053 intake baseline?**
- A) Use the narrative as-is. (Recommended)
- B) Use a shortened variant and defer constraints detail.
- C) Rewrite from scratch.
> Recommendation: A — It preserves concrete current-vs-desired behavior, bounded scope, and explicit non-goals. B loses precision for auditability. C adds churn without better signal.
> **Selected: A**

Captured intake baseline:
- Existing contract-boundary tests are strong, but governance coupling remains permissive for boundary-file change scenarios.
- Desired state is fail-closed PR/CI coupling requiring contract-gate evidence and artifact updates for boundary changes.
- Scope remains bounded to governance enforcement, with one targeted compatibility hardening add-on.

### Step 2 — Repo Reality Snapshot (Read-Only)

Observed evidence:
- `.github/workflows/ci.yml` already runs `pytest tests/engine/test_review_request_contracts.py -m contract_gate --strict-markers -q`.
- `docs/memory/tools/testing.md` records marker-selection fail-closed strategy and strict-marker enforcement as explicit guardrails.
- `docs/memory/tools/workflow.md` records contract-gate namespace drift risk and required immediate CI selector updates for new namespaces.
- `docs/tasks/completed/task-WF-0052-producer-compatibility-stress-real-snapshots.md` and corresponding walkthrough confirm WF-0052 completion and deterministic compatibility/digest evidence.
- Contract boundary surfaces are implemented in `backend/app/engine/contracts.py` and validated via `backend/tests/engine/test_review_request_contracts.py`, with room for governance coupling hardening.

Open questions from snapshot:
1. What is the canonical boundary-file map that should trigger governance coupling?
2. Which artifact updates are mandatory when boundary files change?
3. Should fail-closed CI smoke be implemented as a standalone job or in the existing backend job?
4. What minimum negative case best proves coupling is enforced, not advisory?

## Section 1 — Problem Statement

**Q1: What is the primary failure mode WF-0053 must eliminate first?**
- A) Boundary changes merge without required contract-gate + artifact coupling. (Recommended)
- B) Marker misuse (`--strict-markers`) bypass risk.
- C) Digest equivalence coverage gaps only.
> Recommendation: A — This is the highest merge-risk governance hole. B is already largely protected and should be retained as invariant. C is useful hardening but not the top failure mode.
> **Selected: A**

**Q2: Which actor's pain should define MVP success?**
- A) CI maintainers/release owners enforcing merge safety. (Recommended)
- B) Feature engineers adding call/config changes.
- C) All contributors equally.
> Recommendation: A — They own pass/fail policy and release safety outcomes. B is a secondary beneficiary. C dilutes MVP focus.
> **Selected: A**

**Q3: Which scope framing best prevents scope creep?**
- A) Governance-only: PR/CI coupling + fail-closed proof, no runtime behavior changes. (Recommended)
- B) Governance + selective runtime validator hardening.
- C) Full contract + runtime + docs overhaul.
> Recommendation: A — Keeps this WF bounded and verifiable. B adds behavior drift risk. C is too broad for a hardening slice.
> **Selected: A**

**Q4: What should count as "problem solved" at Phase 0 level?**
- A) A clear policy model where boundary-affecting changes are objectively blocked unless required checks/artifacts are present. (Recommended)
- B) Just adding one more CI test with no policy definition.
- C) Only updating docs guidance.
> Recommendation: A — Governance requires enforceable policy and objective checks. B and C alone cannot guarantee fail-closed outcomes.
> **Selected: A**

**Q5: Where does the WF-0052 matrix extension sit in problem framing?**
- A) In-scope but secondary: compatibility-hardening add-on after governance coupling. (Recommended)
- B) Co-primary with governance coupling.
- C) Out of scope for WF-0053.
> Recommendation: A — Keeps primary focus on governance coupling while still landing one high-value compatibility reinforcement.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: Which success metric is mandatory for governance readiness?**
- A) Boundary-change PRs fail unless required policy evidence is present. (Recommended)
- B) Policy is documented but not auto-enforced.
- C) Manual reviewer checklist only.
> Recommendation: A — Required for deterministic merge safety. B and C are advisory and drift-prone.
> **Selected: A**

**Q2: What behavior change do we want from contributors?**
- A) Include contract-gate evidence + required artifact updates in the same PR when touching boundary files. (Recommended)
- B) Rely on reviewer feedback cycles to add evidence later.
- C) Leave evidence optional if tests pass elsewhere.
> Recommendation: A — Minimizes rework and closes governance gaps upfront. B and C increase merge ambiguity.
> **Selected: A**

**Q3: What proves fail-closed behavior best for this WF?**
- A) One deterministic negative CI smoke where missing coupling fails the workflow. (Recommended)
- B) Team agreement that checks should fail.
- C) Local-only script demonstration.
> Recommendation: A — CI-level proof is objective and durable. B/C are not enforceable controls.
> **Selected: A**

**Q4: How should strict-marker guard be treated in outcomes?**
- A) Mandatory invariant in governance baseline; no relaxation. (Recommended)
- B) Optional in main CI, required only in nightly.
- C) Defer to local test discipline.
> Recommendation: A — Marker correctness is core to test-intent integrity. B/C allow silent risk.
> **Selected: A**

**Q5: What is good-enough compatibility add-on scope?**
- A) Exactly one multi-surface omitted-vs-explicit-default digest equivalence case (`stage_gating` + `prompt_knobs` + `reviewer_policy`). (Recommended)
- B) Full matrix expansion across all surfaces.
- C) Skip compatibility add-on entirely.
> Recommendation: A — High signal with bounded effort. B is oversized for MVP. C leaves known gap unaddressed.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor?**
- A) Release owner / CI maintainer. (Recommended)
- B) Backend engineer modifying contract boundaries.
- C) Documentation maintainer.
> Recommendation: A — Owns enforcement policy and merge gate behavior.
> **Selected: A**

**Q2: Who is the primary secondary actor?**
- A) Backend engineer changing boundary files. (Recommended)
- B) Product reviewer.
- C) Frontend contributor.
> Recommendation: A — Directly impacted by trigger/coupling checks.
> **Selected: A**

**Q3: Which actor behavior must improve first?**
- A) Proactive inclusion of required governance evidence before review. (Recommended)
- B) Faster post-failure fixes only.
- C) Manual coordination in chat before commits.
> Recommendation: A — Prevents avoidable review churn and merge delays.
> **Selected: A**

**Q4: What friction should governance minimize?**
- A) Ambiguous failure reasons; provide deterministic, actionable failures. (Recommended)
- B) Number of checks regardless of clarity.
- C) Artifact link verbosity only.
> Recommendation: A — Clear remediation preserves throughput while staying strict.
> **Selected: A**

**Q5: How should ownership be expressed?**
- A) Policy-owned at CI/PR layer with contributor compliance expectations. (Recommended)
- B) Reviewer-owned only with optional CI hints.
- C) Contributor-owned only with optional reviewer checks.
> Recommendation: A — Centralized enforcement with distributed responsibility is the most robust.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: Simplest implementation direction?**
- A) Add boundary-trigger-to-required-evidence coupling in CI/PR with explicit fail conditions. (Recommended)
- B) Build a new governance microservice.
- C) Expand runtime validator logic to infer policy.
> Recommendation: A — Smallest viable enforcement change at the correct layer.
> **Selected: A**

**Q2: Where should fail-closed negative proof live?**
- A) Existing CI workflow as explicit smoke path/check. (Recommended)
- B) Separate optional workflow.
- C) Local dev script only.
> Recommendation: A — Ensures every PR experiences the same enforcement semantics.
> **Selected: A**

**Q3: How to integrate strict-marker misuse validation?**
- A) Keep strict-marker in main contract-gate run and treat failures as hard stop. (Recommended)
- B) Move to advisory report.
- C) Remove because redundant.
> Recommendation: A — Preserves guard against unregistered marker drift.
> **Selected: A**

**Q4: How to include WF-0052 extension without scope blow-up?**
- A) Add exactly one deterministic test case and corresponding artifact evidence. (Recommended)
- B) Add several matrix classes now.
- C) Delay all matrix work.
> Recommendation: A — Maintains momentum and boundedness.
> **Selected: A**

**Q5: How should artifact coupling be handled?**
- A) Treat artifact updates as required evidence for boundary-triggered changes. (Recommended)
- B) Keep artifacts optional.
- C) Enforce only for major changes by reviewer discretion.
> Recommendation: A — Traceability is governance-critical and should be objective.
> **Selected: A**

## Section 5 — Constraints

**Q1: Time constraint posture?**
- A) Tight MVP slice this WF; defer extras. (Recommended)
- B) Medium expansion if convenient.
- C) Open-ended hardening.
> Recommendation: A — Needed to keep delivery predictable.
> **Selected: A**

**Q2: Technical constraint on CI runtime?**
- A) Add bounded deterministic checks without materially increasing CI variance. (Recommended)
- B) Accept broad runtime growth.
- C) Skip enforcement to keep CI fast.
> Recommendation: A — Balances reliability and signal.
> **Selected: A**

**Q3: Policy constraint on enforcement semantics?**
- A) Fail-closed for in-scope boundary changes. (Recommended)
- B) Warn-only initially.
- C) Mixed mode by reviewer choice.
> Recommendation: A — Warn-only modes are too weak for merge safety.
> **Selected: A**

**Q4: Documentation constraint?**
- A) Required artifact updates must remain part of merge evidence chain. (Recommended)
- B) Optional docs if CI passes.
- C) Docs updated later in batches.
> Recommendation: A — Prevents traceability decay.
> **Selected: A**

**Q5: Scope constraint on runtime behavior?**
- A) No runtime semantics changes in this WF. (Recommended)
- B) Allow small behavior changes if easy.
- C) Add runtime refactor opportunity work.
> Recommendation: A — Keeps contracts stable and isolates governance work.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: Most fragile assumption?**
- A) Boundary-trigger map can be defined narrowly enough to avoid noise but broad enough to prevent bypass. (Recommended)
- B) Contributors will always self-police artifact updates.
- C) Docs alone will drive compliance.
> Recommendation: A — Trigger quality determines practical enforcement value.
> **Selected: A**

**Q2: Highest implementation risk?**
- A) False positives/negatives in change detection and coupling checks. (Recommended)
- B) Unit test authoring complexity only.
- C) Branch naming confusion.
> Recommendation: A — Directly impacts trust in governance gates.
> **Selected: A**

**Q3: What must be validated early?**
- A) One deterministic fail-closed negative path in CI. (Recommended)
- B) Broad narrative docs update.
- C) Optional local scripts.
> Recommendation: A — Early proof prevents policy becoming aspirational.
> **Selected: A**

**Q4: Primary rework cause to avoid?**
- A) Over-scoped governance that spills into runtime contract redesign. (Recommended)
- B) Too few meeting notes.
- C) Delayed commit squashing.
> Recommendation: A — Scope discipline prevents costly phase resets.
> **Selected: A**

**Q5: Compatibility-risk handling approach?**
- A) Add one targeted multi-surface digest-equivalence test and stop there for MVP. (Recommended)
- B) Expand broad matrix now.
- C) Defer all compatibility testing.
> Recommendation: A — Best trade-off between risk reduction and scope.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: If limited to 3 days, what must exist?**
- A) Boundary-trigger coupling + fail-closed CI proof + one matrix add-on case. (Recommended)
- B) Governance plus broad producer-realism expansion.
- C) Docs-only plus future ticket.
> Recommendation: A — Complete minimum enforceable slice.
> **Selected: A**

**Q2: What can wait?**
- A) Additional matrix classes and deeper producer realism hardening. (Recommended)
- B) Any CI policy checks.
- C) Artifact traceability updates.
> Recommendation: A — Keeps MVP bounded without losing enforcement essentials.
> **Selected: A**

**Q3: What must not be included now?**
- A) Runtime behavior refactor/redesign. (Recommended)
- B) Deterministic CI checks.
- C) Workflow artifact linkage.
> Recommendation: A — Out-of-scope and risky for this phase.
> **Selected: A**

**Q4: What is the minimum acceptance evidence set?**
- A) Passing positive path + one explicit negative fail-closed CI smoke + updated WF artifacts. (Recommended)
- B) Positive path only.
- C) Docs assertions only.
> Recommendation: A — Required for confidence and traceability.
> **Selected: A**

**Q5: Which slice ordering is preferred?**
- A) Governance coupling first, then bounded matrix case. (Recommended)
- B) Matrix first, governance later.
- C) Parallel broad changes.
> Recommendation: A — Reduces merge-risk earliest.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: Which tempting expansion is explicitly deferred?**
- A) Comprehensive producer-realism hardening across many classes. (Recommended)
- B) Any compatibility testing.
- C) CI governance checks.
> Recommendation: A — Valuable but larger than current MVP.
> **Selected: A**

**Q2: What product scope is explicitly out?**
- A) Frontend/UI behavior work. (Recommended)
- B) CI policy coupling.
- C) Contract-gate test selection.
> Recommendation: A — Not related to this governance slice.
> **Selected: A**

**Q3: What backend scope is explicitly out?**
- A) Runtime review engine semantic changes. (Recommended)
- B) CI policy changes.
- C) Contract matrix test additions.
> Recommendation: A — Keeps this WF governance-only.
> **Selected: A**

**Q4: What process pattern is explicitly rejected?**
- A) Advisory-only governance without hard CI enforcement. (Recommended)
- B) Deterministic fail-closed checks.
- C) Required artifact traceability.
> Recommendation: A — Advisory models regress under schedule pressure.
> **Selected: A**

**Q5: What should move to future WF if needed?**
- A) Additional governance abstractions beyond MVP coupling and smoke proof. (Recommended)
- B) Core MVP checks.
- C) Existing strict-marker guard.
> Recommendation: A — Preserves momentum and avoids overengineering.
> **Selected: A**
