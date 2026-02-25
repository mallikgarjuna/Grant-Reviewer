# Utility Runner — Maintenance Quick Fix (Non-WF)

This file is a workflow instruction.
Reference it in chat (Codex, Antigravity, or any coding agent) using `@docs/workflow/util-maintenance-quick-fix.md`.
Do NOT modify this file during execution.

---

## Purpose

Handle small, non-WF repo maintenance safely (docs/tooling/refactor) without minting a WF ID or touching WF artifacts.

---

## Trigger (Use This When)

- change is not a product initiative; no WF artifact chain
- no new row in `docs/index.md` WF registry needed
- want a clean “edit -> verify -> commit” loop

If unclear: ask user to confirm "maintenance vs WF initiative".

---

## Rules (Strict)

1. Do NOT work on `main`.
2. Do NOT mint a WF ID.
3. Do NOT create/move WF artifacts (`docs/brainstorms|prds|tasks|walkthroughs`).
4. Keep scope tight; no drive-by refactors.
5. Verify proportionally (targeted commands; no heroics).
6. Commit once changes are correct (or commit per logical chunk if needed).

---

## Steps

1. Confirm maintenance scope + acceptance criteria (1-3 bullets).
2. Confirm branch name is `fix/<slug>` or `chore/<slug>` (create if missing).
3. Implement changes.
4. Verify:
   - run the most relevant checks for the touched area (lint/tests/build)
   - summarize pass/fail evidence
5. Commit:
   - message: `docs:` / `chore:` / `fix:` (no WF prefix)
6. Report what changed + what was verified + any follow-ups.

---

## How To Invoke In Chat

```text
Use @docs/workflow/util-maintenance-quick-fix.md

Goal: <1 sentence>
Scope: <2-4 bullets>
Constraints: non-WF maintenance; do not touch docs/index.md WF rows; commit after changes.

Run the maintenance quick-fix runner end-to-end.
```
