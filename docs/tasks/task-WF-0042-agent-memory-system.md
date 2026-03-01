# Task WF-0042: Agent Memory System Setup

## Goal
Implement a persistent agent memory system natively in `docs/memory/` based on Claude's code memory concept.

## Working Notes
- Goal is to allow the agent to incrementally document findings and gotchas without prompting.

## Checklist
- [x] Create git branch `wf/WF-0042-agent-memory-system`
- [x] Read `AGENTS.md`
- [x] Create `docs/memory/index.md` with domain and tools categories
- [x] Extract existing gotchas from `AGENTS.md` to `docs/memory/tools/`
- [x] Update `AGENTS.md` core directives for memory management
- [x] Re-architect code phrases SSOT and update memory
- [x] Add scanning of old documentation for memory items
- [x] Merge findings into `docs/memory/` and update index
- [x] Deduplicate and prune outdated logic
- [x] Verify using the walkthrough
- [x] Mark WF-0042 as `Done` in `docs/index.md`
