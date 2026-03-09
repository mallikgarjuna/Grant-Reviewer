<!-- docs/reference/code_phrases.md -->
# Code Phrases

Quick-reference shortcuts you can use in any conversation with the agent.

## Backlog Management

| Phrase | Action |
|--------|--------|
| **`park this`** `: [description]` | Add item to parking lot under the right P0/P1/P2 table. |
| **`pick P[x] #[n]`** | Promote a parking lot item into a new WF. |
| **`move P[x] #[n] to P[y]`** | Re-prioritize a parking lot item between tiers. |
| **`refresh parking lot`** | Reconcile `docs/parking_lot.md` against recent WF work and current repo reality: remove or rewrite solved/stale items, renumber affected rows, and update rationale/dependency notes when needed. Use after completing a WF or anytime backlog reality may have drifted. |

## Workflow & Execution

| Phrase | Action |
|--------|--------|
| **`context refresh`** | Re-ground agent context from current project state before deciding the next action. |
| **`new chat kickoff`** | Generate a reusable 3-line starter for opening a new chat with clear scope/constraints. |
| **`interactive Q&A`** | Run an iterative clarification loop: ask 1–5 questions at a time, each with 2–4 options + one recommended option with rationale; continue until decisions are made or the user says stop. For WF brainstorms, write the detailed Q&A blocks into `docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md` and keep the main brainstorm concise with links. |
| **`adversarial critique`** | For a proposed decision: list the top 3 architectural risks/failure modes (authoring, runtime, downstream), and include a recommended mitigation/guardrail for each. |
| **`mission check`** | Audit `docs/mission.md` for drift against the current product direction. Keep `Mission` and `Vision` stable unless strategy changed. Update only `MVP Goal`, `Product Goals`, and `MVP Success Criteria` when this is just a new phase. Make the smallest necessary edit, explain whether the change is mission-level, goals-level, or no change, and flag any downstream docs that should also be updated. |
| **`repo reality check`** | Re-ground on repo + recent WF activity (status + relevant diffs + current WF registry), then propose 2–3 next-step options with one recommended option and rationale. |
| **`run phase [N]`** | Execute WF phase runner (`0` runs `0.0 + 0.1` end-to-end, `1` PRD, `2` tasks, `3` implement). |
| **`go ahead`** | Explicit approval to proceed to the next phase/step. |
| **`critical review`** | Senior-level review of current work with actionable findings. |
| **`workflow preflight`** | Critical review of current WF readiness, required actions before starting next WF, recommended order, and whether to start a new chat. If current changes touch auth/proxy/sign-in/BFF boundaries, include an explicit reminder to run both auth validation lanes (`test_bypass` + `clerk`). |
| **`phase 3 closeout`** | Composed Phase-3 endgame shortcut. Execute this exact order: `verify workflow` -> `update docs` -> `docs cleanup` -> `log this` (WF closure decision + follow-on boundary rationale) -> `reorganize memory` -> `refresh parking lot` -> `workflow preflight`. After completing all seven, stop and ask for explicit user approval before running `ship it`. Fail-closed rules: if any verification/doc hygiene step fails, stop, report blocker, and do not continue to later steps. |
| **`diff`** | Show changes on the current branch vs `main`. |
| **`verify workflow`** | Run a verification bundle for the current workflow (composed phrase): `status` + `diff` + targeted checks (lint/build/tests used in this WF) + concise pass/fail summary. |
| **`verify auth lanes`** | Run auth automation matrix for this repo: Playwright bypass smoke (`AUTH_MODE=test_bypass`) and Clerk auth checks (`AUTH_MODE=clerk`), then report pass/fail per lane and what was skipped (for example missing Clerk test credentials). |

## Knowledge & Memory

| Phrase | Action |
|--------|--------|
| **`reorganize memory`** | `read docs/memory/`, deduplicate, merge, sort by date, and summarize. |
| **`remember this`** `: [rule]` | Codify a new rule → `AGENTS.md` (workflow) or `docs/lessons.md` (project gotcha). |
| **`log this`** `: [decision/Q&A]` | Record a decision or clarification in `docs/logs/`. |
| **`update docs`** | Sync all doc artifacts (index, walkthrough, decisions, prompt history). |
| **`docs cleanup`** | Run a docs-closure checklist before next WF: align WF status across artifacts, remove stale draft/phase labels, update relevant logs (`prompt_history`/`decisions` as needed), run `pre-commit`, and commit docs-only changes with WF ID + slug. |

## Session & Shipping

| Phrase | Action |
|--------|--------|
| **`status`** | Print project status: active WF, parking lot snapshot, recent changes. |
| **`what's next`** | Suggest top 2 next actions (WF steps or parking lot picks). |
| **`next move`** | Composed shortcut: run `repo reality check` first; if a WF is active, run `workflow preflight`; run `verify workflow` only when implementation/code changed since last verification; when auth-related files changed, also recommend `verify auth lanes`; then return exactly 2 next actions with one recommended, one-line rationale each, and a copy-paste prompt block if runner-based. |
| **`wrap up`** | End-of-session save: update docs, commit, push. Does **not** merge. |
| **`ship it`** | Push feature branch → Create PR → Merge (remote + delete branch) → Sync local `main`. |

## Communication

| Phrase | Action |
|--------|--------|
| **`ELI5`** `: [topic]` | Explain Like I'm 5: break down the topic into the simplest possible terms using plain language, analogies, and zero jargon. |

## Phrase Selection Guide (When to Use What)

| If you need... | Use this phrase |
|--------|--------|
| Add/reprioritize/reconcile backlog items | **`park this`**, **`pick P[x] #[n]`**, **`move P[x] #[n] to P[y]`**, **`refresh parking lot`** |
| Understand current project reality before deciding | **`context refresh`** |
| Audit whether product positioning or MVP framing has drifted | **`mission check`** |
| Start a fresh conversation with clear inputs | **`new chat kickoff`** |
| Approve continuation of current plan | **`go ahead`** |
| Advance artifact pipeline by phase | **`run phase [N]`** |
| Deep quality/risk analysis of implementation | **`critical review`** |
| Decide if current WF is cleanly closed before moving to the next WF | **`workflow preflight`** |
| Run full Phase 3 closure checklist with a mandatory stop before shipping | **`phase 3 closeout`** |
| Inspect branch delta against `main` | **`diff`** |
| Validate auth/session flows in both bypass and real Clerk mode | **`verify auth lanes`** |
| Persist new standing workflow rule | **`remember this`** |
| Run memory maintenance | **`reorganize memory`** |
| Capture decision/clarification in logs | **`log this`** |
| Sync all docs after work changes | **`update docs`** |
| Run final doc hygiene before starting next WF | **`docs cleanup`** |
| Quick project snapshot and next priorities | **`status`**, **`what's next`** |
| End session without merge | **`wrap up`** |
| Complete PR-based merge flow to `main` | **`ship it`** |
| Get a simple, jargon-free explanation of a concept | **`ELI5`** |

## Composition Guideline

When a new phrase overlaps existing phrases, define and execute it as a composed shortcut (reuse existing phrase behaviors first, then add only the minimal extra checks/reporting).
