# WF-0034 — Phase 0.1 Chat Reference (2026-02-26)

Purpose: lightweight reference to the originating Phase 0.1 discussion so deferred items can point somewhere concrete.

Context:
- WF: `WF-0034` (`wf/WF-0034-unify-review-execution-core`)
- Topic: unify internal execution pipeline while keeping separate external API contracts
- Endpoints:
  - `POST /reviews` (single-node)
  - `POST /api/structured-review` (multi-node)

Key decisions captured in chat:
- Keep both external endpoints (do not deprecate `/reviews` in WF-0034).
- Treat “deprecate `POST /reviews` by migrating single-node UX onto structured” as a follow-on item (parked in `docs/parking_lot.md` as P2 #23).
