# Deep Modules

Deep module = a module where the public interface is small/simple relative to the amount of functionality it provides.
Shallow module = interface complexity is proportional to (or worse than) the complexity it hides.

Concept reference: "A Philosophy of Software Design" (John Ousterhout).

## Mental Model

Depth is "hidden complexity per unit of interface".

Deep module (good):

```
[ simple interface ]
====================
| lots of behavior |
| lots hidden here |
====================
```

Shallow module (bad):

```
[ complex interface ]
=====================
| little value hid. |
=====================
```

Why it helps TDD:

- stable interface to test against
- fewer mocks
- fewer files touched per change (often)

## Smells (Shallow Modules)

- logic scattered across call sites
- "utility soup" with no owning module
- modules that are mostly glue/re-exports

## Practical Questions

- If I add one new behavior, do I have to touch many call sites?
- Does the module force callers to know lots of details?
- Are my tests brittle because the seam is too small/too leaky?

If yes, you probably need a deeper module with a clearer seam.

## How To Get Deeper (Without Over-Engineering)

- Pick a stable "public seam" (service entrypoint, repository, HTTP handler boundary) and concentrate behavior behind it.
- Collapse micro-helpers into an owned module with a clear interface.
- Prefer "one thing well" modules over generic utils.
