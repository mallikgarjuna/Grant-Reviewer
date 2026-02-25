# Deep Modules

Deep module = small public API + lots of encapsulated logic.

Why it helps TDD:

- stable interface to test against
- fewer mocks
- fewer files touched per change (often)

Smells:

- logic scattered across call sites
- “utility soup” with no owning module
- modules that are mostly glue/re-exports
