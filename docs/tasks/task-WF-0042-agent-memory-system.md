# Task WF-0042: Agent Memory System Setup

## Goal
Implement a persistent agent memory system natively in `docs/memory/` based on Claude's code memory concept.

## Working Notes
- Goal is to allow the agent to incrementally document findings and gotchas without prompting.

## Checklist
- [x] Create branch `wf/WF-0042-agent-memory-system`
- [x] Add WF-0042 to `docs/index.md`
- [x] Scaffold `docs/memory/` structure (index.md, domain, tools)
- [x] Extract existing Project Gotchas from `AGENTS.md` and place them into new memory files
- [x] Add explicit "Memory Management" instruction to `AGENTS.md` making it proactive ("Don't wait to be asked. Don't wait for session end.")
- [x] Verify everything looks good and commit
