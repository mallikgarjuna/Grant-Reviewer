# PeerLens Architecture Chat — Review Engine

## Locked Decisions

### Product Identity

- Surgical Pre-Submission Diagnostic Tool (primary)
- Competitive positioning later (secondary)
- Optimized for researcher trust (slow, rigorous, credible)

### Scope

- Section-level diagnostics first
- No full-proposal engine yet

### Output Philosophy

- Analytical-only output in v1 (problem + why + fix direction)
- No rewriting in core engine
- Findings must be traceable to expectations
- Precision > performance
- Traceability > flashiness
- Gap detection > praise

### Core Principle (Non-Negotiable)

- Qualitative evaluation is primary
- Numerical scoring is optional and secondary
- Scoring must never contaminate core evaluation logic

### Key Architectural Principle

- Separate WHAT is evaluated from HOW evaluation is executed.
  - Calls define WHAT (expectations, constraints, weights).
  - Engine defines HOW (validation, analysis, diagnostics).
  - Modes define WHICH components are activated.

### Architecture Purity Constraints

- Design for cognitive invariants, not funders
- Single canonical review engine
- Calls are declarative (no funder-specific conditionals in engine)
- Extend via configuration, not mutation

### Universal Review Primitives (Invariants)

- Structural validation
- Compliance validation
- Expectation satisfaction analysis
- Evidence sufficiency check
- Cross-section alignment (only when dependencies exist)
- Feasibility / risk audit
- Differentiation detection (later phase)

### Pipeline Goal

Design a universal Grant Review Engine Pipeline that:

- Works across NWO / ERC / MSCA without funder-specific logic
- Operates purely on declarative call configuration
- Is deterministic and expectation-driven
- Produces DiagnosticFinding v1 as its atomic output
- Can be extended without modifying core engine logic

### Atomic Output

- DiagnosticFinding v1 (structured, severity-based, expectation-grounded)

### Out of Scope (for now)

- Default numerical scoring
- Ranking simulation
- Competitive comparison
- Full-proposal coherence audit
- Auto-rewriting

---

## Mental Model

The engine reviews expectations.
Calls define expectations.
Modes are execution profiles.

---

## Decision Queue

1. Finalize DiagnosticFinding v1 schema constraints
2. Define call-agnostic pipeline v1
3. Define execution profiles (modes)
4. Map DiagnosticFinding v1 to existing ReviewCard

---

## Recent Decisions (WF-0038, 2026-02-28)

- `DiagnosticFinding v1` is **trace-first** (required traceability/determinism fields).
- Interactive Q&A: each question includes 2–4 options + assistant recommendation.
- Log discipline: decisions + Q&A are WF-tagged in `docs/logs/decisions.md` and `docs/logs/qa_history.md`.
- Adversarial critique standard: 3 risks must cover (authoring, runtime, downstream) and include a recommended mitigation/guardrail.
- Call-agnostic pipeline v1: **two-pass** model (Pass 1 normalized observations; Pass 2 maps observations → `DiagnosticFinding v1`).

---

## Architecture Exit Criteria

Architecture phase is complete when:

- WHAT vs HOW separation is fully stable
- DiagnosticFinding v1 schema is frozen
- Call-agnostic pipeline v1 is defined
- Scoring layer is isolated and optional
- Adversarial stress test finds no structural contradictions
- Implementation blueprint can be described without new architecture decisions
