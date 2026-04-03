# Memory Management

Maintain a structured memory system rooted at `docs/memory/`.

*Concept inspired by: [How to Give Claude Code Memory](https://substack.com/@huryn/note/c-216337711?)*

## Load Posture

- Start here when memory is relevant.
- Treat this file as the active memory router.
- Treat the linked memory leaves as on-demand references unless the current task explicitly needs them.

## Active Router

- [domain/architecture.md](domain/architecture.md) — Core architectural decisions and conventions
- [domain/project_docs.md](domain/project_docs.md) — Documentation rules and code phrase reference-heavy history
- [domain/product_planning.md](domain/product_planning.md) — Launch-wedge planning rules for production MVP
- [domain/yaml_definitions.md](domain/yaml_definitions.md) — Call YAML naming, source gating, and scoping rules
- [tools/backend.md](tools/backend.md) — Backend script paths and environment requirements
- [tools/frontend.md](tools/frontend.md) — Frontend tooling and nvm requirements
- [tools/sqlmodel.md](tools/sqlmodel.md) — SQLModel session gotchas
- [tools/testing.md](tools/testing.md) — Database isolation rules for tests
- [tools/workflow.md](tools/workflow.md) — Workflow/chat-hygiene reference history
