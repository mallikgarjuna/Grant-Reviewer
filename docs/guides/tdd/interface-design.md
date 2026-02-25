# Interface Design For TDD

Design for testability:

- prefer inputs -> outputs where possible
- isolate side effects behind boundaries
- pass dependencies in; avoid hidden globals/singletons

Pick the seam that makes behavior easy to express in a test:

- HTTP handler (integration-ish)
- service entrypoint
- repository boundary (data-oriented behavior)
