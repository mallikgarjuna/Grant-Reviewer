# Project Workflow System

This folder defines the structured workflow used to move from idea → shipped code.

The workflow is artifact-driven and versioned.
Every meaningful initiative is tracked using a Workflow ID (WF-XXXX).

---

# Workflow Phases

- Phase 0 — Ideation (Brainstorm)
- Phase 1 — Definition (Brainstorm → PRD)
- Phase 2 — Planning (PRD → Tasks)
- Phase 3 — Execution (Task Implementation)
- Done

Runner shortcuts:
- Phase 0: `docs/workflow/phase-0-run-start-and-brainstorm-ideation.md` (includes brainstorm review gate + revise)
- Phase 1/2: `docs/workflow/phase-12-run-planning.md` (one unified runner; Phase ID = 1 or 2)
- Phase 3: `docs/workflow/phase-3-run-implement-execution.md`

Phase 0 input confirmation convention:
- Before running Phase 0.0, confirm `Title` / `Type` / `Slug` via 2–3 structured options each, with one recommended option.

Deferred work convention:
- If a discussion produces a deferred/follow-up item, park it in `docs/parking_lot.md` with enough context to pick later, and reference the originating WF/chat (at minimum: `WF-XXXX`, date, and commit ID if available).

End-of-phase convention:
- At the end of each phase run, provide next steps/options with explicit copy-pasteable prompt blocks, and recommend starting a new chat/session if context is getting long or the next phase is a separate workflow run.

Each initiative progresses sequentially.
Backtracking is allowed (see below).

## What “Good” Looks Like (Quick)

Trigger: read before starting a phase; ensures artifacts are implementable.

- Brainstorm: tight MVP + non-goals; include a short, timeboxed **Repo Reality Snapshot** when repo context will prevent overfitting or verify key assertions; for `Type: page`, may include `## Appendix — Page Spec (MVP)` (optional).
- PRD: includes **User Stories (MVP)** + **Deferred Stories**, plus a short **Testing Decisions (TDD)** section.
- PRD: functional requirements use stable IDs (`FR1`, `FR2`, ...) and are referenced by contracts/tasks.
- PRD: deep modules called out (small interface, lots hidden; stable seams).
- Tasks: each task includes `Slice:` + `User Stories:` + `PRD Requirements:` mapping (or `N/A`), and there is an early tracer-bullet task.
- Implementation: TDD is mandatory for behavior changes/bug fixes (red/green/refactor; mock boundaries only): `docs/guides/tdd/README.md`.

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

<brainstorm/prd/task/walkthrough>-WF-XXXX-<slug>.md

Examples:

brainstorm-WF-0007-landing-page.md
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
- docs/prds/
- docs/tasks/
- docs/walkthroughs/
- docs/logs/decisions.md
- docs/index.md
- docs/workflow/

*(Note: Every artifact directory contains a `completed/` subdirectory. When a workflow is marked `Done`, its artifacts must be moved into their respective `completed/` folders to keep the root workspace clean for active workflows).*

---

# docs/index.md (Workflow Registry)

The index is a link registry, not a narrative log.

Table format (WF registry):

| WF ID | Slug / Feature | Brainstorm | PRD | Task File | Walkthrough | Status |

Rules:

- Each workflow has exactly one row.
- Links must point to the correct artifact paths.
- Status must reflect current phase:
  - Phase 0
  - Phase 1
  - Phase 2
  - Phase 3
  - Done
- Update status only when phase changes.

Keep it minimal. No descriptions.

Migration note:
- During migration, `docs/index.md` contains both a legacy task registry and a WF registry. Add new initiatives to the WF registry only.

---

# Main Branch Policy (Strict)

## Rule

- NEVER commit directly to `main`.
- WF initiative work occurs on a WF branch: `wf/WF-XXXX-<slug>`.
- Non-WF maintenance work occurs on a maintenance branch: `fix/<slug>` or `chore/<slug>` (no WF ID).
- `main` is updated only by merging branches (WF or maintenance).

## When To Use Maintenance Branches (Trigger)

Use a maintenance branch when the change:

- is repo hygiene / docs / tooling / refactor with no WF artifact chain
- does not need a new `docs/index.md` WF row
- should not mint a WF ID

If unsure, ask: "Is this a WF initiative or a maintenance change?"

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

When Phase 3 is complete and Status = Done:

- Merge wf/WF-XXXX-<slug> into main.
- Optionally delete the workflow branch.
- Do NOT squash away meaningful task commits.

For maintenance branches:

- Merge via PR as usual.
- Keep commits readable; squashing OK if you prefer.

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

Brainstorm → PRD → Tasks → Implementation

Rules:

- PRD must be derived ONLY from Brainstorm.
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

WF initiative commits must start with WF ID:

WF-0007: implement hero section
WF-0007: add empty state handling
WF-0007: revise PRD risk audit

This keeps implementation traceable to workflow artifacts.

Maintenance commits do NOT need WF IDs (use normal prefixes, e.g. `docs:`, `chore:`, `fix:`).

# Glossary / Code Phrases

The following are standard operational code phrases documented in `AGENTS.md` that orchestrate workflows:

- **`verify workflow`**: verification pass (status check, git diff review, lint/build execution, pass/fail summary). Trigger: user says "verify workflow".
- **`workflow preflight`**: WF closure readiness review (artifacts synced, phase gates met, next phase ready). Trigger: user says "workflow preflight".

---

# Maintenance Runner (Optional)

Trigger: small non-WF change; want a safe, consistent loop.

Use: `docs/workflow/util-maintenance-quick-fix.md`

---

# Guiding Principle

Discipline over speed.
Clarity over verbosity.
Artifacts over memory.

The workflow exists to reduce rework,
not to create bureaucracy.

If documentation becomes heavier than implementation,
simplify — but never remove phase boundaries.
