# Tests (Guidelines)

Goal: tests should survive refactors and describe behavior, not implementation.

## Good Tests

- Express user-visible behavior via a public interface.
- Fail for a clear reason.
- Have minimal setup; prefer helpers/fixtures over repeated boilerplate.
- Prove acceptance criteria (not “it calls function X”).

## Bad Tests

- Couple to internal helpers/private functions.
- Assert intermediate steps instead of outcomes.
- Require heavy mocking of your own code to run.
- Encode incidental details (call ordering, log strings) unless truly required.

Practical rule: if a test breaks after a refactor with no behavior change, it is probably too coupled.
