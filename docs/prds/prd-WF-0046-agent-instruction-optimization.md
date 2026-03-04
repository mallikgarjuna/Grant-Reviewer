# WF-0046 — Agent Instruction Optimization PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## 0. User Stories (MVP)

- US1: As a coding agent, I want a single, consolidated `AGENTS.md` file as my SSOT, so that I don't waste context window on redundant instructions.
- US2: As a developer, I want to remove duplicate instruction files (`GEMINI.md`) and trim the user-global file (`~/.gemini/GEMINI.md`), so that onboarding new agents is simple and confusing rule overlaps are eliminated.
- US3: As a developer, I want to back up the current `~/.gemini/GEMINI.md` and document deferred architectural improvements in the parking lot, so that no context or future plans are lost during this optimization.

## Deferred Stories (Not in MVP)

- US4: As a developer, I want to embed rule enforcement in git hooks/Makefiles.
- US5: As a developer, I want to adopt Ralph-style fresh-context execution across workflow phases.

## 1. In Scope

- Auditing `~/.gemini/GEMINI.md` against existing project docs (`docs/guides/`, `docs/workflow/README.md`).
- Extracting unique behavioral guardrails from `~/.gemini/GEMINI.md` to `AGENTS.md`.
- Deleting the repository-level `GEMINI.md` file.
- Backing up and trimming `~/.gemini/GEMINI.md` to <=15 lines (protecting other projects).
- Adding deferred stories (D and G) to `docs/parking_lot.md`.
- Verifying file line limits post-optimization.

## 2. Out of Scope

- Redesigning `docs/guides/` content.
- Creating an agent-specific file like `~/.codex/AGENTS.md`.
- Refactoring how project docs reference agent rules.
- Building pre-commit hook file size caps.
- Retaining the "Acknowledge" heartbeat policy in the global file.

## 3. User / System Flow

- Happy path
  1. (US1, US2) Agent audits configurations, extracts unique global rules, updates `AGENTS.md`.
  2. (US2) Agent deletes repo `GEMINI.md`.
  3. (US3) Agent backs up `~/.gemini/GEMINI.md` to `/tmp`.
  4. (US2) Agent trims `~/.gemini/GEMINI.md` to 10-15 lines of global behavioral safety nets.
  5. (US3) Agent updates `docs/parking_lot.md` with deferred items.
  6. (US1, US2) Agent verifies line counts and missing files.

- Failure path 1: Backup of `~/.gemini/GEMINI.md` fails (US3).
  - Remediation: Halt trimming until manual or alternative backup strategy succeeds.

- Failure path 2: Extracted unique rules cause `AGENTS.md` to exceed 45 lines (US1, US2).
  - Remediation: Further synthesize rules or drop less critical ones to fit constraint.

## 4. Functional Requirements

- FR1 (US1, US2): Update `AGENTS.md` to include ONLY project-specific rules not already documented, maintaining <= 45 lines.
- FR2 (US2): Delete the file `GEMINI.md` from the repo root.
- FR3 (US3): Copy `~/.gemini/GEMINI.md` to `/tmp/GEMINI.md.bak`.
- FR4 (US2): Trim `~/.gemini/GEMINI.md` to include <= 15 lines.
- FR5 (US3): Append parking lot stories D (code-based enforcement) and G (loop-style Phase 3) to `docs/parking_lot.md`.
- FR6 (US1, US2): Verify implementation by asserting `wc -l AGENTS.md` <= 45, `wc -l ~/.gemini/GEMINI.md` <= 15, and `ls GEMINI.md` fails (not found).

## 5. Data & API Contracts

- N/A. The exact file formats (`AGENTS.md`, `~/.gemini/GEMINI.md`) and their target lengths bounds (<=45 lines and <=15 lines respectively) serve as the contract for this task. (US1, US2) (FR1, FR4)

## 6. Components / Modules

- Repo Configuration (`AGENTS.md`, `GEMINI.md`)
- Global Configuration (`~/.gemini/GEMINI.md`)
- Project Docs (`docs/parking_lot.md`)

## 7. Edge Cases

- (US1, US2) If `~/.gemini/GEMINI.md` is not present or inaccessible, the agent must alert the user instead of proceeding with trimming.
- (US2) If `GEMINI.md` doesn't exist in the repo root, consider it already deleted and continue.

## 8. Testing Decisions (TDD)

- Validation step:
  - Run `wc -l AGENTS.md` to confirm length <= 45. (FR6)
  - Run `wc -l ~/.gemini/GEMINI.md` to confirm length <= 15. (FR6)
  - Run `ls GEMINI.md` and expect `No such file or directory`. (FR6)

## 9. Telemetry (Minimal)

- None.

## 10. Deferred / Not in MVP

- Code-based enforcement (git hooks/Makefile).
- Ralph-style fresh-context execution across workflow phases.

## 11. Open Questions (if any)

- None.

## 12. Changelog

- v0.1 (2026-03-04): Initial PRD from brainstorm
