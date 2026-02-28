# Code Phrases

Quick-reference shortcuts you can use in any conversation with the agent.

## Backlog Management

| Phrase | Action |
|--------|--------|
| **`park this`** `: [description]` | Add item to parking lot under the right P0/P1/P2 table. |
| **`pick P[x] #[n]`** | Promote a parking lot item into a new WF. |
| **`move P[x] #[n] to P[y]`** | Re-prioritize a parking lot item between tiers. |

## Workflow & Execution

| Phrase | Action |
|--------|--------|
| **`context refresh`** | Re-ground agent context from current project state before deciding the next action. |
| **`new chat kickoff`** | Generate a reusable 3-line starter for opening a new chat with clear scope/constraints. |
| **`interactive Q&A`** | Run an iterative clarification loop: ask 1–5 questions at a time, each with 2–3 options + one recommended option with rationale; continue until decisions are made or the user says stop. |
| **`repo reality check`** | Re-ground on repo + recent WF activity (status + relevant diffs + current WF registry), then propose 2–3 next-step options with one recommended option and rationale. |
| **`run phase [N]`** | Execute WF phase runner (`0` runs `0.0 + 0.1` end-to-end, `1` PRD, `2` tasks, `3` implement). |
| **`go ahead`** | Explicit approval to proceed to the next phase/step. |
| **`critical review`** | Senior-level review of current work with actionable findings. |
| **`workflow preflight`** | Critical review of current WF readiness, required actions before starting next WF, recommended order, and whether to start a new chat. |
| **`diff`** | Show changes on the current branch vs `main`. |
| **`verify workflow`** | Run a verification bundle for the current workflow (composed phrase): `status` + `diff` + targeted checks (lint/build/tests used in this WF) + concise pass/fail summary. |

## Knowledge & Memory

| Phrase | Action |
|--------|--------|
| **`remember this`** `: [rule]` | Codify a new rule → `AGENTS.md` (workflow) or `docs/lessons.md` (project gotcha). |
| **`log this`** `: [decision/Q&A]` | Record a decision or clarification in `docs/logs/`. |
| **`update docs`** | Sync all doc artifacts (index, walkthrough, decisions, prompt history). |
| **`docs cleanup`** | Run a docs-closure checklist before next WF: align WF status across artifacts, remove stale draft/phase labels, update relevant logs (`prompt_history`/`decisions` as needed), run `pre-commit`, and commit docs-only changes with WF ID + slug. |

## Session & Shipping

| Phrase | Action |
|--------|--------|
| **`status`** | Print project status: active WF, parking lot snapshot, recent changes. |
| **`what's next`** | Suggest top 2 next actions (WF steps or parking lot picks). |
| **`next move`** | Composed shortcut: run `repo reality check` first; if a WF is active, run `workflow preflight`; run `verify workflow` only when implementation/code changed since last verification; then return exactly 2 next actions with one recommended, one-line rationale each, and a copy-paste prompt block if runner-based. |
| **`wrap up`** | End-of-session save: update docs, commit, push. Does **not** merge. |
| **`ship it`** | Push feature branch → Create PR → Merge (remote + delete branch) → Sync local `main`. |

## Phrase Selection Guide (When to Use What)

| If you need... | Use this phrase |
|--------|--------|
| Add/reprioritize backlog items | **`park this`**, **`pick P[x] #[n]`**, **`move P[x] #[n] to P[y]`** |
| Understand current project reality before deciding | **`context refresh`** |
| Start a fresh conversation with clear inputs | **`new chat kickoff`** |
| Approve continuation of current plan | **`go ahead`** |
| Advance artifact pipeline by phase | **`run phase [N]`** |
| Deep quality/risk analysis of implementation | **`critical review`** |
| Decide if current WF is cleanly closed before moving to the next WF | **`workflow preflight`** |
| Inspect branch delta against `main` | **`diff`** |
| Persist new standing workflow rule | **`remember this`** |
| Capture decision/clarification in logs | **`log this`** |
| Sync all docs after work changes | **`update docs`** |
| Run final doc hygiene before starting next WF | **`docs cleanup`** |
| Quick project snapshot and next priorities | **`status`**, **`what's next`** |
| End session without merge | **`wrap up`** |
| Complete PR-based merge flow to `main` | **`ship it`** |

## Composition Guideline

When a new phrase overlaps existing phrases, define and execute it as a composed shortcut (reuse existing phrase behaviors first, then add only the minimal extra checks/reporting).
