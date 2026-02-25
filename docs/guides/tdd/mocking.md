# Mocking (Boundary Rule)

Mock boundaries:

- HTTP clients / external APIs
- filesystem I/O
- time/clock
- queues/email/SMS providers
- LLM provider calls

Don’t mock your own internal modules. If you feel forced to, fix the seam:

- introduce a deeper module with a small interface
- pass boundary dependencies in (DI)
