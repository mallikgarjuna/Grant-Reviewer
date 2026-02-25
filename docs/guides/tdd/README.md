# TDD Guide (Repo-Local)

Source (upstream reference): `mattpocock/skills` -> `tdd/`.

Trigger: use when a task changes behavior, adds a new feature, or fixes a bug and you want red/green/refactor discipline.

---

## Loop (Red/Green/Refactor)

1. **Red**: add a failing test that expresses the next behavior.
2. **Green**: write the smallest change to pass.
3. **Refactor**: only after green; keep behavior constant.

Avoid “write all tests first then all code” (horizontal slicing). Prefer thin vertical slices.

---

## TDD Philosophy

TDD is a way to discover design by proving behavior incrementally.
The unit of progress is a tiny `RED->GREEN` loop that delivers behavior, not a big batch of tests followed by a big batch of implementation.

### Anti-Pattern: Horizontal Slices (Wrong)

Wrong: treat RED as "write all tests" and GREEN as "write all code".

Failure mode: you design signatures/data shapes in tests before proving behavior, then fight the mismatch.

Prefer vertical slices via tracer bullets:

```text
WRONG (horizontal):
RED:   test1, test2, test3, ...
GREEN: impl1, impl2, impl3, ...

RIGHT (vertical):
RED->GREEN: test1 -> impl1
RED->GREEN: test2 -> impl2
RED->GREEN: test3 -> impl3
...
```

---

## What To Test

Test behavior through the most public stable interface available:

- HTTP route / API boundary
- CLI entrypoint
- service function (public surface)

Avoid tests that depend on internal implementation details or private helpers.

---

## Mocking Policy (Strict)

Mock only at system boundaries:

- network calls
- filesystem
- time
- external services (auth/payments/LLM provider)

Do NOT mock your own modules to “make testing easy”. Fix the interface instead.

See `mocking.md`.

---

## Deep Modules

Prefer “deep modules”: small public interface, lots of encapsulated logic behind it.

Outcome: stable seams to test, fewer mocks, less churn.

See `deep-modules.md`.

---

## Interface Design

Design interfaces that make tests straightforward:

- pass dependencies in (DI), avoid hidden globals/singletons
- return values (don’t only log/print)
- keep a stable public surface

See `interface-design.md`.

---

## Refactor Discipline

Refactor only after green.

See `refactoring.md`.

---

## Quick Checklist (Per Task)

- Do I have a failing test that matches acceptance criteria?
- Does the test hit the most public stable interface available?
- Am I mocking only boundaries (not my own modules)?
- Did I refactor only after green?
