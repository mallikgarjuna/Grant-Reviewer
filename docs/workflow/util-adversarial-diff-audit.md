# Utility — Adversarial Diff Audit (No Edits)

This file is a workflow instruction utility.
Reference it in chat (any coding agent) using `@docs/workflow/util-adversarial-diff-audit.md`.
Do NOT modify files while executing this utility.

---

## Purpose

Provide one canonical, adversarial review contract for branch diffs so all relevant Part B gates use the same quality bar.

---

## Input

- A diff range (required). Preferred: `main...HEAD`.
- Optional scope profile:
  - `execution` (full technical audit; default)
  - `planning` (artifact/planning-focused)
  - `ideation` (workflow/process-focused)

---

## Mandatory Review Focus Areas

Always cover these six dimensions:

1. architecture violations vs `AGENTS.md`
2. broken invariants
3. security issues
4. edge cases
5. missing tests
6. hidden coupling

---

## Output Contract (Exact)

Return findings in this exact structure:

1. potential bugs
2. missing tests
3. design issues
4. suggested fixes
5. refactored version with comments (only for high-impact snippets; keep minimal and actionable)

Rules:
- Every finding must include severity (`blocking` or `non-blocking`).
- Every finding must include a concrete target (file/path/test area).
- If a section has no findings, write `none`.

---

## Profile Guidance

- `execution`:
  - Use `main...HEAD` by default.
  - Apply all six focus areas strictly.
- `planning`:
  - Prioritize architecture violations, invariants, missing tests, hidden coupling.
  - Security/edge-case analysis is required but scoped to planning artifacts/contracts.
- `ideation`:
  - Prioritize architecture/process invariants and hidden coupling in the proposed workflow.
  - Security/edge-case analysis is required but scoped to strategy/risk assumptions.
