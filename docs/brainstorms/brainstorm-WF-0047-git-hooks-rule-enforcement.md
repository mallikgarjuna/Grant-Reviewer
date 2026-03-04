# WF-0047 — Git Hooks Rule Enforcement Brainstorm

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-04

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0047-git-hooks-rule-enforcement.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1–3 “Contract Notes / Non-obvious constraints” bullets and link to the relevant Q&A section header.

---

## Repo Reality Snapshot (Read-Only)

Date: 2026-03-04
- The `AGENTS.md` file exists and is currently 37 lines (well under the target <= 45 line limit).
- The repository already uses the `pre-commit` framework (`.pre-commit-config.yaml` is present and active for basic checks).
- There is no `Makefile` currently at the repository root.
- Git commit convention rules are not mechanically enforced (no `commit-msg` hook is active).
- Standard git hook sample files exist in `.git/hooks/` but custom scripts must integrate with the existing `pre-commit` setup or bypass it.

---

## 1. Problem Statement

What problem are we solving?
- We rely on AI agents reading `AGENTS.md` and following conventions like prompt length (< 45 lines) and git commit prefixes (e.g., `WF-XXXX:`). Using LLM tokens and instructions to enforce structural formatting is unreliable and expensive.
- Contract Notes / Non-obvious constraints:
  - We will mechanically enforce these rules using `pre-commit` local hooks rather than a standalone `Makefile` or loose bash scripts. [Ref: Q1]
  - The commit prefix regex must strictly match `^WF-\d{4}: ` (case-sensitive) to prevent loose rule following.

Who experiences it?
- The project maintainer and the AI agents looping during coding tasks.

Why does it matter now?
- Context bloat and instruction parsing failures lead to skipped rules, requiring manual developer intervention and wasting tokens.

---

## 2. Desired Outcome

What changes after this exists?

What becomes easier or faster?

What becomes possible?

---

## 3. Target User / Actor

Who is this for?
- Developing agents (AI) and human developers committing to the repository.

What is their current behavior?
- Agents try to remember to prefix commits with `WF-XXXX:` but often forget when context windows shift or instructions are ignored.
- Agents rewrite `AGENTS.md` and accidentally exceed the length limit, breaking the strict rule.

What frustration or inefficiency exists?
- The human developer has to intervene, correct the commit messages, or manually revert `AGENTS.md` bloat, which takes time and breaks flow state.
- Contract Notes / Non-obvious constraints:
  - The hook must validate that commit messages start with `WF-\d{4}: ` (or similar regex). [Ref: Q2]
  - The `check_commit_msg.py` script must exit 0 immediately if the commit message begins with `Merge branch` or `Revert`. [Ref: Q3]

---

## 4. Rough Idea (Unstructured Thinking)

Free-form thinking.
- Introduce two custom python scripts in `scripts/hooks/`:
  - `check_agents_md.py`: Reads `AGENTS.md` and fails if it exceeds 45 lines.
  - `check_commit_msg.py`: Reads the commit message file (`.git/COMMIT_EDITMSG`) and fails if it doesn't match the `WF-XXXX:` pattern.
- Wire these scripts into `.pre-commit-config.yaml` using `repo: local`.
- `check_agents_md.py` runs on the `pre-commit` stage.
- `check_commit_msg.py` runs on the `commit-msg` stage.

No architecture constraints.
No implementation details yet.

---

## 5. Constraints

Technical constraints?
- Must run cross-platform (using `pre-commit` python/bash hooks).
- Python scripts must use only the standard library (`sys`, `re`, `os`, etc.) to guarantee execution in `pre-commit`'s isolated `repo: local` environment.

Time constraints?
- Fast delivery (MVP), focused squarely on local agent looping.

Dependencies?
- Requires `.pre-commit-config.yaml` to be updated.

External requirements?
- Git parsing logic (ignoring `Merge branch` and `Revert`) must be reliable. [Ref: Q3]

---

## 6. Risks / Unknowns

What assumptions are we making?
- The Python virtual environment or system Python is available to run `.pre-commit-config.yaml` `repo: local` plugins.
- Agents or developers will not bypass hooks manually via `git commit -n` (if they do, it's out of scope for local hooks).

What might fail?
- String matching for commit messages might incorrectly flag legitimate commits if regex parsing is too brittle.
- Off-by-one errors in line counting (e.g. empty newlines at EOF) could trigger false positives for `AGENTS.md` exactly at 45 lines. [Ref: Q4: Exactly 45 lines passes]

What needs validation?
- Exactly how the commit-msg file path is injected into the hook running under `pre-commit`.

---

## Open Questions / Deferred

- Remote CI enforcement (e.g. GitHub Actions to block naked `git push --no-verify`) is explicitly deferred to a future Ops workflow if needed. [Ref: Q5]

---

## 7. MVP Definition

If we had to ship in 2–3 days:
What is the smallest functional slice?
- Implementation of two python scripts: `scripts/hooks/check_agents_md.py` and `scripts/hooks/check_commit_msg.py`.
- Integration into `.pre-commit-config.yaml` using `repo: local` hooks for the `pre-commit` and `commit-msg` stages. [Ref: Q5]

What can be explicitly excluded?
- CI pipeline enforcement (GitHub Actions / Hooks).
- Generic conventional commits checking (`feat:`, `fix:`, etc). [Ref: Q2]

---

## 8. Explicit Non-Goals

What are we NOT solving in this workflow?
- Remote/cloud CI pipeline enforcement.
- Validation of any other markdown files constraints besides `AGENTS.md`.

What future ideas should be postponed?
- Implementing an entire `Makefile` abstraction layer.
