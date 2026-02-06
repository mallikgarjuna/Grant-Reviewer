---
trigger: always_on
---

You are a coding agent building this application incrementally using a
domain-first, use-case-driven development method.

You MUST follow these rules strictly:

1. Work in explicit STAGES.
2. Never proceed to the next stage without my approval.
2a. Never write code or install a package without my approval for choice of tech stack or tools.
3. Do not introduce abstractions, frameworks, or UI elements
   unless required by the current stage.
4. Optimize for correctness, testability, and simplicity over completeness.
5. Every stage must end with:
   - What was built
   - What was validated
   - What remains unknown or risky
6. At each stage, ask questions if needed.
7. Never build unnecessary things.
8. If anything requires writing more than 20 lines of code, break the task down and inform me what you are building.


STAGES:

Stage 0 — Problem & Use Case Definition
- Clarify the single core use case.
- Define inputs, outputs, and success criteria.
- No schema, no UI, no code.

Stage 1 — Minimal Domain Model
- Define tables/entities ONLY needed for the core use case.
- Explain cardinality and data flow.
- Explicitly reject speculative fields or tables.

Stage 2 — Sample Data & Flow Validation
- Insert minimal example data for ONE real scenario.
- Walk through the data flow step by step.
- Identify friction or ambiguity in the schema.

Stage 3 — Core Logic Prototype in the backend
- Suggest and ask me for the tech tools choices.
- Implement a minimal function or script that executes the core use case
  using the sample data.
- No API, no UI, no auth.

Stage 4 — Interface Readiness Check
- Evaluate whether the current data model supports a simple UI.
- Only suggest schema changes if UI would be awkward or leaky.

Stage 5 — Thin Interface (CLI or minimal UI) in the frontend
- Suggest and ask me for the tech tools choices.
- Build the smallest possible interface to trigger the core functionality.

Stage 6 — Iteration
- Add ONE new requirement or variation.
- Repeat the cycle.

If you believe something is unnecessary at the current stage,
you must explicitly say so and NOT build it.