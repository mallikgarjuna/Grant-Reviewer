# Phase 0.0 — Start Workflow (Mint WF ID + Branch + Register)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-0-0-start-workflow.md.
Do NOT modify this file during execution.

---

## Purpose

Create a new workflow session with:

- Unique incremental Workflow ID (WF-XXXX)
- Standardized artifact files
- New git branch
- Entry in docs/index.md

This ensures every initiative is isolated and traceable.

---

## Phase Gate (Always)

Before minting a new workflow:

- Ensure your working tree is clean (`git status --short`).
- If you have uncommitted work from a previous phase/initiative, **save and commit it first** so workflows do not interleave.

After completing Phase 0.0:

- Ensure the created baseline artifacts and the WF row update in `docs/index.md` are **saved and committed** before starting Phase 0.1.

---

## Required Inputs (provided in chat)

- Title (short human-readable name)
- Type: page OR feature
- Slug (lowercase, hyphen-separated)

Example:
Title: Landing Page MVP
Type: page
Slug: landing-page

---

## WF ID Minting Rules

WF IDs are incremental and zero-padded:

WF-0001
WF-0002
WF-0003

Determine next ID by:

1. Inspect docs/index.md
2. If the WF registry already has rows:
   - Find highest WF-XXXX
   - Increment by 1
3. If the WF registry has no rows yet:
   - Find the highest legacy Task ID (use the integer part, e.g., `8.1` → `8`)
   - Start WF numbering at the next integer (e.g., `8.x` → `WF-0009`)

---

## Standard Filename Convention

All artifacts must follow:

<brainstorm/spec/prd/task/walkthrough>-WF-XXXX-<slug>.md

---

## Files To Create

Brainstorm:
docs/brainstorms/brainstorm-WF-XXXX-<slug>.md



PRD:
docs/prds/prd-WF-XXXX-<slug>.md

Tasks:
docs/tasks/task-WF-XXXX-<slug>.md

Walkthrough:
docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md

---

## Placeholder Header (All Files)

# WF-XXXX — <Title>

Artifact: brainstorm | prd | task | walkthrough
Version: v0.0
Status: Not started
Last Updated: YYYY-MM-DD

---

## Git Branch Creation (Mandatory)

Create new branch:

wf/WF-XXXX-<slug>

Branch policy:
- Create the workflow branch from the latest `main` (not from another in-progress WF branch).
- If you must depend on unmerged work, keep it explicit (stacked PR) and document it in the PR description.

Suggested commands (PR-based flow):

```sh
git switch main
git pull --ff-only
git switch -c wf/WF-XXXX-<slug>
git push -u origin wf/WF-XXXX-<slug>
```

Immediately commit the created artifact files:

Commit message:
WF-XXXX: start workflow (<slug>)

This establishes clean branch baseline.

---

## Update docs/index.md

Table format:

| WF ID | Slug / Feature | Brainstorm | PRD | Task File | Walkthrough | Status |

Add new row:

| WF-XXXX | <slug> | [Brainstorm](relative-path) | [PRD](relative-path) | [Tasks](relative-path) | [Walkthrough](relative-path) | Phase 0 |

Rules:

- Use proper relative markdown links
- Do NOT modify other rows
- Status starts as: Phase 0

---

## How to Invoke in Codex Chat

Use @docs/workflow/phase-0-0-start-workflow.md.

Provide:

Title: <Title>
Type: <page|feature>
Slug: <slug>

Steps:

1. Determine next WF ID
2. Create artifact files
3. Create git branch wf/WF-XXXX-<slug>
4. Commit artifacts
5. Update docs/index.md
6. Stop

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Run Phase 0.1 (interactive brainstorm): `@docs/workflow/phase-0-1-brainstorm.md`
   - **Provide an explicit, copy-pasteable prompt block** for the user to start this phase.
2. Sanity-check the new baseline artifacts (headers + links in `docs/index.md`), then commit a small fix if needed.
