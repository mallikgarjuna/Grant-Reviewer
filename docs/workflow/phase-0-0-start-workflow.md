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

<brainstorm/spec/prd/tasks/walkthrough>-WF-XXXX-<slug>.md

---

## Files To Create

Brainstorm:
docs/brainstorms/brainstorm-WF-XXXX-<slug>.md

Spec:
If Type = page:
docs/specs/pages/spec-WF-XXXX-<slug>.md
If Type = feature:
docs/specs/features/spec-WF-XXXX-<slug>.md

PRD:
docs/prds/prd-WF-XXXX-<slug>.md

Tasks:
docs/tasks/tasks-WF-XXXX-<slug>.md

Walkthrough:
docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md

---

## Placeholder Header (All Files)

# WF-XXXX — <Title>

Artifact: brainstorm | spec | prd | tasks | walkthrough  
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

Immediately commit the created artifact files:

Commit message:
WF-XXXX: start workflow (<slug>)

This establishes clean branch baseline.

---

## Update docs/index.md

Table format:

| WF ID | Slug / Feature | Brainstorm | Spec | PRD | Task File | Walkthrough | Status |

Add new row:

| WF-XXXX | <slug> | [Brainstorm](relative-path) | [Spec](relative-path) | [PRD](relative-path) | [Tasks](relative-path) | [Walkthrough](relative-path) | Phase 0 |

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
