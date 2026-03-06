# Documentation Sanitization Policy

Last reviewed: 2026-03-06
Status: Active (phased rollout)

## Purpose
Keep workflow/process documentation stable over time by separating policy from tool-vendor specifics.

## Rule Set
1. Core process docs MUST be tool-agnostic and model-agnostic.
2. Tool/model names are allowed only in adapter/reference/history docs.
3. Historical records (decisions, walkthroughs, chat logs) may include tool names for traceability.

## Core Docs (Tool-Agnostic Required)
- `AGENTS.md`
- `docs/workflow/README.md`

## Adapter/Reference Docs (Tool Names Allowed)
- `docs/reference/README_agent_instructions.md`
- `docs/reference/agent_collaboration_strategy.md`
- `.github/copilot-instructions.md`
- `GEMINI.md`

## CI Enforcement
The CI `Docs Sanitization Guard` enforces that core docs do not include these agent/model terms:
- `antigravity`
- `gemini`
- `codex`
- `gpt`
- `claude`
- `cursor`
- `copilot`

## Rollout Plan
- Phase A (completed): enforce core docs (`AGENTS.md`, `docs/workflow/README.md`).
- Phase B (completed): sanitize workflow docs and enforce all `docs/workflow/*.md` files.
