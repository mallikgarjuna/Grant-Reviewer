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
| **`run phase [N]`** | Execute WF phase runner (0=brainstorm, 1=spec, 2=PRD, 3=tasks, 4=implement). |
| **`go ahead`** | Explicit approval to proceed to the next phase/step. |
| **`critical review`** | Senior-level review of current work with actionable findings. |
| **`diff`** | Show changes on the current branch vs `main`. |

## Knowledge & Memory

| Phrase | Action |
|--------|--------|
| **`remember this`** `: [rule]` | Codify a new rule → `AGENTS.md` (workflow) or `docs/lessons.md` (project gotcha). |
| **`log this`** `: [decision/Q&A]` | Record a decision or clarification in `docs/logs/`. |
| **`update docs`** | Sync all doc artifacts (index, walkthrough, decisions, prompt history). |

## Session & Shipping

| Phrase | Action |
|--------|--------|
| **`status`** | Print project status: active WF, parking lot snapshot, recent changes. |
| **`what's next`** | Suggest top 2 next actions (WF steps or parking lot picks). |
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
| Inspect branch delta against `main` | **`diff`** |
| Persist new standing workflow rule | **`remember this`** |
| Capture decision/clarification in logs | **`log this`** |
| Sync all docs after work changes | **`update docs`** |
| Quick project snapshot and next priorities | **`status`**, **`what's next`** |
| End session without merge | **`wrap up`** |
| Complete PR-based merge flow to `main` | **`ship it`** |
