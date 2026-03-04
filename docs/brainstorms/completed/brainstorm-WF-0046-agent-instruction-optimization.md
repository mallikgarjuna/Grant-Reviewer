# WF-0046 — Agent Instruction Optimization Brainstorm

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-04

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1–3 "Contract Notes / Non-obvious constraints" bullets and link to the relevant Q&A section header.

---

## Repo Reality Snapshot (Read-Only, 2026-03-04)

1. **`AGENTS.md` (30 lines)** — project-level SSOT, read by both Codex and Antigravity.
2. **`GEMINI.md` in repo (30 lines)** — byte-identical duplicate of `AGENTS.md`, pure waste.
3. **`~/.gemini/GEMINI.md` (361 lines)** — user-global rules loaded every prompt by Antigravity; ~70% duplicates project docs in `docs/workflow/README.md` and `docs/guides/`.
4. **`~/.codex/AGENTS.md`** — does not exist; Codex runs fine with only project-level `AGENTS.md`.
5. **Project docs coverage** — `docs/guides/workflow-system.md`, `docs/guides/engineering-standards.md`, `docs/guides/knowledge-base.md` already cover workflow, git, testing, and KB rules.

---

## 1. Problem Statement

- **Primary problem:** Agent context window is wasted on duplicate/redundant instruction files (token waste) AND multiple instruction files create confusion about which rules apply (inconsistent behavior). Both dimensions are equally important.
- **Who experiences it:** The coding agents (Antigravity/Codex) — loaded with redundant context they must parse. This has measurable impact via context utilization.
- **Why now:** Adversarial comparison with Ralph Wiggum methodology identified context hygiene as the #1 improvement opportunity for this project's workflow system.
- **Blast radius:** Low — agents work fine today; this is optimization, not a fix for broken behavior. Codex has been shipping WFs without user-global rules.
- **Scope:** Cross-project — the user-global file at `~/.gemini/GEMINI.md` loads on every Antigravity session across all projects, not just Grant-Reviewer.

**Contract Notes:**
- The user-global config is NOT in the repo — it's at `~/.gemini/GEMINI.md`, outside version control.
- Codex has no equivalent user-global file and works fine, proving the 361-line file is not essential.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 1)

---

## 2. Desired Outcome

- **Primary success metric:** Consolidate to a single instruction file (`AGENTS.md`) as the only SSOT per project — all duplicates removed.
- **What becomes easier:** Onboarding a new coding agent — just point it at `AGENTS.md`, done. No hunting across `~/.gemini/`, repo-root `GEMINI.md`, or project docs.
- **Expected behavior change:** None visible — agents should work exactly as before, just with less overhead. This is optimization, not behavior change.
- **Verification method:** One SSOT file exists, all duplicates deleted, agent still follows project conventions through a normal WF cycle.
- **What becomes possible:** Easily switch between coding agents (Codex, Antigravity, Claude Code, etc.) — same `AGENTS.md` works for all.

**Contract Notes:**
- Success = no regression in agent behavior + fewer instruction sources.
- The tiny `~/.gemini/GEMINI.md` safety net (~10 lines) is the only exception to "single file" — it protects non-Grant-Reviewer projects.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 2)

---

## 3. Target User / Actor

- **Primary user:** The coding agents (Antigravity, Codex, etc.) — they read `AGENTS.md` to understand how to behave in this project.
- **Agents supported:** Antigravity + Codex (current), plus any future agent — achieved naturally by keeping `AGENTS.md` agent-agnostic (no tool-specific references).
- **Developer workflow:** Edit `AGENTS.md` in the repo root — quick, visible, version-controlled. No more hunting across `~/.gemini/` or duplicate files.
- **Multi-developer:** Single-developer project for now; optimize for your workflow.
- **Agent-specific directives:** None — keep `AGENTS.md` fully agent-agnostic. Agent-specific behaviors come from each agent's own system.

**Contract Notes:**
- Agent-agnostic `AGENTS.md` automatically achieves future-agent support at zero extra cost.
- No `if Antigravity:` or `if Codex:` sections — any universal convention file should work for any LLM-based coding agent.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 3)

---

## 4. Rough Idea (Unstructured Thinking)

- **Approach:** Grab-and-trim — extract the ~10 genuinely unique rules from `~/.gemini/GEMINI.md`, add them to `AGENTS.md`, delete all duplicates.
- **`AGENTS.md` after consolidation:** Keep current style (~30 lines): project identity + "Read if needed" links to `docs/guides/`. Rules live in project docs, not in AGENTS.md.
- **`~/.gemini/GEMINI.md` after:** Trim to ~10 lines — only universal behavioral guardrails that protect ALL projects (no project-specific content).
- **Unique rules to extract:** Only behavioral guardrails not covered by project docs: "wait for signal before coding", "LGTM ≠ proceed to next phase", "3-file limit", "describe approach first".
- **Repo `GEMINI.md`:** Delete — confirmed byte-identical duplicate of `AGENTS.md`.

**Contract Notes:**
- `AGENTS.md` should NOT grow significantly — the grab-and-trim should add only rules that aren't already in `docs/guides/` or `docs/workflow/README.md`.
- The ~10-line user-global and the ~30-line `AGENTS.md` are the only two instruction files that should exist post-WF.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 4)

---

## 5. Constraints

- **Time:** Ship in a single session — small scope (3 files changed: `AGENTS.md`, delete `GEMINI.md`, trim `~/.gemini/GEMINI.md`).
- **Technical:** `~/.gemini/GEMINI.md` is plain text, freely editable — no technical constraints.
- **Dependencies:** None — Codex proves the project works fine without the 361-line user-global.
- **Other projects:** Grant-Reviewer is the primary project; the ~10-line user-global safety net covers others.
- **External:** No external dependency on `GEMINI.md` in the repo (no CI, tooling, or hooks reference it).
- **Line caps (Part B fix):** `AGENTS.md` ≤ 45 lines; `~/.gemini/GEMINI.md` ≤ 15 lines. Use these as concrete "done" thresholds.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 5)

---

## 6. Risks / Unknowns

- **Most fragile assumption:** That no rules in the 361-line user-global are uniquely critical beyond the 4 behavioral guardrails. **Mitigation:** Line-by-line audit before deleting.
- **Rework risk:** Discovering an agent behavior regression after trimming → need to add back a missed rule. **Mitigation:** Low cost to fix (add one line).
- **Validate early:** Do a line-by-line audit of user-global against project docs before deleting anything.
- **Rollback strategy:** Git history + backup copy of the 361-line file in `/tmp/` before trimming.
- **Traceability risk:** None — the Lessons section content is already documented in project logs (`decisions.md`, `lessons.md`).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 6)

---

## Open Questions / Deferred

- **Parking lot Story D (code-based enforcement):** Move enforceable conventions into git hooks / Makefile → deferred to a future WF after this optimization proves value.
- **Parking lot Story G (loop-style Phase 3):** Adopt Ralph-style fresh-context execution → deferred to architectural exploration WF.

---

## 7. MVP Definition

- **Deliverable:** `AGENTS.md` updated with unique rules from user-global + repo `GEMINI.md` deleted + `~/.gemini/GEMINI.md` trimmed to ~10 lines.
- **Ordered checklist:**
  1. Audit user-global rules against project docs
  2. Grab unique rules into `AGENTS.md`
  3. Delete repo `GEMINI.md`
  4. Back up `~/.gemini/GEMINI.md` to `/tmp/GEMINI.md.bak` (Part B fix)
  5. Trim `~/.gemini/GEMINI.md` to ≤15 lines
  6. Add parking lot stories D and G to `docs/parking_lot.md`
  7. Verify: `ls GEMINI.md` → not found, `wc -l AGENTS.md` ≤ 45, `wc -l ~/.gemini/GEMINI.md` ≤ 15
- **Explicitly excluded:** Any changes to `docs/guides/` content; long-session behavior testing.

**Contract Notes:**
- Parking lot stories D and G get added in this WF since they were born from this analysis.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 7)

---

## 8. Explicit Non-Goals

- **NOT redesigning `docs/guides/`** — out of scope, they work fine.
- **NOT creating `~/.codex/AGENTS.md`** — Codex works fine without user-global.
- **NOT refactoring how project docs reference agent rules** — not broken.
- **NOT building file size cap enforcement (Story F)** — add a one-line note in `AGENTS.md`, no pre-commit hook.
- **NOT keeping the "Acknowledge" heartbeat policy** — drop it as part of trimming user-global to ≤15 lines (in scope as a deletion, not as designing a replacement). (Part B fix: clarified scope.)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0046-agent-instruction-optimization.md` (Section 8)
