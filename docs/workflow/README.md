# Project Workflow System

This folder defines the structured workflow used to move from idea → shipped code.

The workflow is artifact-driven and versioned.
Every meaningful initiative is tracked using a Workflow ID (WF-XXXX).

---

# Workflow Phases

- Phase 0 — Brainstorm
- Phase 1 — Brainstorm → Spec
- Phase 2 — Spec → PRD
- Phase 3 — PRD → Tasks
- Phase 4 — Task Implementation
- Done

Each initiative progresses sequentially.
Backtracking is allowed (see below).

## Phase Gate (Always)

Before starting a new phase, ensure the previous phase’s primary artifact(s) are **saved and committed** on the WF branch. This prevents running later phases against uncommitted or half-edited inputs.

After completing a phase, **commit any artifacts you created/edited in that phase** before proceeding to the next phase.

---

# Workflow ID System

All initiatives use an incremental ID:

WF-0001  
WF-0002  
WF-0003

Rules:

- IDs are zero-padded (4 digits).
- IDs are minted only in Phase 0.0.
- Do NOT manually invent IDs.
- Do NOT reuse IDs.
- Each WF ID corresponds to exactly one branch.

WF IDs connect all artifacts across phases.

WF ID starting point (migration rule):
- If there are no existing WF rows yet, start WF numbering after the highest legacy Task ID.
  - Example: if the last legacy Task ID is `8.x`, the first WF should be `WF-0009`.

---

# Standard Filename Convention

All artifacts must follow this format:

<brainstorm/spec/prd/task/walkthrough>-WF-XXXX-<slug>.md

Examples:

brainstorm-WF-0007-landing-page.md  
spec-WF-0007-landing-page.md  
prd-WF-0007-landing-page.md  
task-WF-0007-landing-page.md  
walkthrough-WF-0007-landing-page.md

Slug rules:

- lowercase
- hyphen-separated
- short and descriptive

---

# Folder Structure

- docs/brainstorms/
- docs/specs/pages/
- docs/specs/features/
- docs/prds/
- docs/tasks/
- docs/walkthroughs/
- docs/logs/decisions.md
- docs/index.md
- docs/workflow/

---

# docs/index.md (Workflow Registry)

The index is a link registry, not a narrative log.

Table format (WF registry):

| WF ID | Slug / Feature | Brainstorm | Spec | PRD | Task File | Walkthrough | Status |

Rules:

- Each workflow has exactly one row.
- Links must point to the correct artifact paths.
- Status must reflect current phase:
  - Phase 0
  - Phase 1
  - Phase 2
  - Phase 3
  - Phase 4
  - Done
- Update status only when phase changes.

Keep it minimal. No descriptions.

Migration note:
- During migration, `docs/index.md` contains both a legacy task registry and a WF registry. Add new initiatives to the WF registry only.

---

# Main Branch Policy (Strict)

## Rule

- NEVER commit directly to `main`.
- All work must occur on a workflow branch:
  wf/WF-XXXX-<slug>
- `main` is updated only by merging completed workflow branches.

## Workflow Branch Naming

wf/WF-XXXX-<slug>

Example:
wf/WF-0007-landing-page

## When to Create Branch

Branch is created during Phase 0.0.
Always create the workflow branch from the latest `main` (PR-based flow).

Phase 0.0 must:

1. Mint WF ID
2. Create artifact files
3. Create workflow branch
4. Commit baseline artifacts

## Merging Policy

When Phase 4 is complete and Status = Done:

- Merge wf/WF-XXXX-<slug> into main.
- Optionally delete the workflow branch.
- Do NOT squash away meaningful task commits.

---

# Versioning Rules (All Artifacts)

Each artifact file must contain:

Version: v0.x (while iterating)  
Version: v1.0 (when locked for next phase)

On every meaningful revision:

- Bump version
- Update Last Updated date
- Append to Changelog section

Do NOT create separate files per version.
Git history is the snapshot system.

---

# Artifact Hierarchy (Source of Truth Order)

Brainstorm → Spec → PRD → Tasks → Implementation

Rules:

- PRD must be derived ONLY from Spec.
- Tasks must be derived ONLY from PRD.
- Do NOT regenerate downward artifacts from older phases.
- Do NOT skip upward in the chain.

Artifacts flow downward only.

---

# Backtracking Rule (Critical)

If implementation reveals missing requirements:

1. Step back exactly ONE phase.
2. Update the artifact.
3. Bump version.
4. Update docs/index.md status if needed.
5. Continue forward again.

Do NOT jump multiple phases backward unless absolutely necessary.

---

# Decisions Log

All architecture, API, and scope-impacting decisions must be recorded in:

docs/logs/decisions.md

Each entry must include:

- Date
- WF ID
- Context
- Decision
- Why
- Tradeoff

Do NOT log minor wording or cosmetic edits.

---

# Commit Convention (Required)

All commits must start with WF ID:

WF-0007: implement hero section  
WF-0007: add empty state handling  
WF-0007: revise PRD risk audit

This keeps implementation traceable to workflow artifacts.

---

# Guiding Principle

Discipline over speed.
Clarity over verbosity.
Artifacts over memory.

The workflow exists to reduce rework,
not to create bureaucracy.

If documentation becomes heavier than implementation,
simplify — but never remove phase boundaries.
