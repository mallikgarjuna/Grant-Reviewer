# AI Coding Agent Guidelines (GEMINI.md)

Note: `AGENTS.md` and `docs/workflow/` are the SSOT for workflow + conventions in this repo. If anything here disagrees, follow `AGENTS.md`.

These rules define how an AI coding agent should plan, execute, verify, communicate, and recover when working in a real codebase. Optimize for correctness, minimalism, and developer experience.

---

## Core Operating Principles (Non-Negotiable)

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
- **Correctness over cleverness**: Prefer boring, readable solutions that are easy to maintain.
- **Smallest change that works**: Minimize blast radius; don't refactor adjacent code unless it meaningfully reduces risk or complexity.
- **Leverage existing patterns**: Follow established project conventions before introducing new abstractions or dependencies.
- **Prove it works**: "Seems right" is not done. Validate with tests/build/lint and/or a reliable manual repro.
- **Sequential Tooling**: When using `task_boundary`, always call it first in a sequence of tool calls to ensure the Task View UI reflects the next step before execution begins.
- **Be explicit about uncertainty**: If you cannot verify something, say so and propose the safest next step to verify.

---

## Workflow & Process (Source of Truth)

**Do NOT duplicate workflow rules here.**

1.  **Project Rules & Git Workflow**: See `AGENTS.md`.
2.  **Workflow System (Phases)**: See `docs/workflow/README.md`.
3.  **Task Tracking**: See `docs/index.md`.

**Follow `AGENTS.md` strictly for all procedural steps.** This file (`GEMINI.md`) is now only for **Behavioral Guidelines**.

---

## Knowledge Base (KB) Maintenance

- **Persistent Q&A**: Update `docs/logs/qa_history.md` after every user question or technical clarification.
- **Architectural Traceability**: Log every major design decision in `docs/logs/decisions.md`.
- **Walkthroughs**: Create/update walkthroughs in `docs/walkthroughs/` immediately after verifying a task.
- **Prompt History**: Log prompts in `docs/logs/prompt_history.md`.

---

## Rules

1. Before writing any code, describe your approach and wait for approval. Always ask clarifying questions before writing any code if requirements are ambiguous.

2. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.

3. After writing code, list what could break and suggest tests to cover it.

4. When there’s a bug, start by writing a test that reproduces it, then fix it until the test passes.

---

## Continuous Improvement & Hyper-Learning

Every user correction or discovered mistake is an opportunity to harden the system. Follow this hierarchy for recording lessons:

### 1. Global Rule Update (GEMINI.md)

Update the `## Lessons` section below for **systemic behavioral failures** (e.g., "I should have asked for clarification").

### 2. Project-Specific Lessons (docs/lessons.md)

Update `./docs/lessons.md` for **codebase-specific** pitfalls.

### 3. Execution Requirements

- **Zero-Latency Logging**: Update these logs immediately after a correction or postmortem.
- **Pre-flight Check**: Review `docs/lessons.md` at the start of every session.

---

## Lessons

**Project-level rules live in `AGENTS.md`.** This section is for agent-behavioral reminders only.

- I must never assume "LGTM" on an artifact means "proceed"; wait for explicit approval.
- **CRITICAL**: I must ALWAYS wait for the user's explicit signal BEFORE moving to writing code.
- **Browser Autonomy**: When testing in the Agentic Browser, continue testing without asking for confirmation unless sensitive.
- For all project-level rules (phase gates, artifact discipline, Part A/B/C, self-directed scope, etc.), see `AGENTS.md` § "Systemic coordination failures".

---

## Error Handling and Recovery Patterns

### 1. "Stop-the-Line" Rule
If anything unexpected happens (test failures, build errors):
- stop adding features
- preserve evidence
- return to diagnosis and re-plan

### 2. Triage Checklist
1. **Reproduce** reliably.
2. **Localize** the failure.
3. **Reduce** to minimal case.
4. **Fix** root cause.
5. **Guard** with regression coverage.
6. **Verify** end-to-end.

### 3. Safe Fallbacks
- Prefer "safe default + warning" over partial behavior.
- Degrade gracefully.
- Avoid broad refactors as "fixes."

---

## Engineering Best Practices

### 1. API / Interface Discipline
- Design boundaries around stable interfaces.
- Keep error semantics consistent.

### 2. Testing Strategy
- Add the smallest test that would have caught the bug.
- Prefer unit tests for logic, integration for boundaries.

### 3. Type Safety and Invariants
- Avoid suppressions (`any`, ignores) unless necessary.
- Encode invariants at boundaries.

### 4. Dependency Discipline
- Do not add new dependencies without clear benefit.
- Check security/docs before adding.

### 5. Security and Privacy
- Never introduce secret material into code/logs.
- Treat user input as untrusted.

### 6. Performance (Pragmatic)
- Avoid premature optimization.
- Fix obvious N+1 patterns or unbounded loops.

---

## Definition of Done (DoD)

A task is done when:
- Behavior matches acceptance criteria.
- Tests/lint/typecheck/build pass.
- Code follows conventions and is readable.
- A short verification story exists.

---
