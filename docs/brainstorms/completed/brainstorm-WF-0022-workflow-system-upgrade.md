# WF-0022 — Workflow System Upgrade

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-21

## 1. Problem Statement
The current WF workflow system is mature but has architectural constraints that limit scaling:
- **File Sprawl**: 21 files make context-loading expensive for agents.
- **Phase 4 Risk**: Phase 4 lacks the Part A/B/C verification discipline present in Phases 1-3.
- **Maintenance Debt**: The cheat-sheet (`how-to-use-workflow-actions.md`) duplicates runner logic manually.
- **Lifecycle Runners**: `run-lifecycle-auto.md` contradicts the required A/B/C patterns and risks token exhaustion.

## 2. Desired Outcome
An optimized, hardened workflow system that enforces phase gates strictly, reduces duplicate instructions, standardizes agent invocation, and establishes an archival strategy for completed WFs.

## 3. Target User / Actor
- AI Coding Agents (Antigravity, Codex) reading instructions to execute tasks.
- Project Maintainer guiding the agents.

## 4. MVP Definition & Rough Idea (The 3-Tier Execution Plan)
Based on explicit user approval, the upgrade will proceed in 3 tiers:
- **Tier 1 (Quick Wins)**: Fix minor bugs (typos, duplicate lines, numbering gaps). Strip the cheat-sheet down to only phase-runner prompts to enforce "Runners are Routers" (L23, L27).
- **Tier 2 (Risk Mitigation)**: Create a proper Phase 4 runner with Part A (implement), Part B (verify), and Part C (walkthrough + PR). Fix `run-lifecycle-auto.md` to require Part A/B/C explicitly.
- **Tier 3 (Refactor & Archival)**: Consolidate `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` into a single parametric `universal-phase-runner.md`. Establish the `docs/archive/WF-XXXX/` convention for old artifacts.

## 5. Constraints & Non-Goals
- Must not change the fundamental phases (Brainstorm → Spec → PRD → Tasks → Implementation).
- Must remain compatible with existing WF artifacts.

## Traceability Statement
- Built based on context generated in `workflow_review.md` and explicitly agreed to by the user.
