# WF-0046 — Agent Instruction Optimization Q&A

Artifact: brainstorm-qna
Version: v0.1
Status: In Progress
Last Updated: 2026-03-04

---

## Section 1 — Problem Statement

**Q1: What is the primary problem?**
- A) Agent context window is wasted on duplicate/redundant instruction files → worse reasoning quality
- B) Multiple instruction files create confusion about which rules apply → inconsistent agent behavior
- C) Both A and B equally
> Recommendation: C — Our analysis confirmed both token waste AND rule duplication. The 361-line user-global config is ~70% redundant with project docs, wasting context AND creating ambiguity about which source of truth applies.
> **Selected: C**

**Q2: Who experiences the problem?**
- A) The developer (you) — dealing with inconsistent agent behavior across sessions
- B) The coding agents (Antigravity/Codex) — loaded with redundant context they must parse
- C) Both — but B has measurable impact (context utilization), A is more subjective
> Recommendation: B — The agents are the ones whose reasoning quality degrades when context is bloated. The developer experiences this indirectly through worse output quality.
> **Selected: B**

**Q3: Why does it matter *now*?**
- A) We recently compared with Ralph Wiggum and identified context hygiene as the #1 improvement
- B) We switched to multi-agent workflow (Codex + Antigravity) and need a single SSOT
- C) The user-global file has grown to 361 lines without pruning and needs housekeeping
> Recommendation: A — The Ralph Wiggum analysis was the catalyst that surfaced this as the highest-leverage improvement. B and C are true but secondary motivations.
> **Selected: A**

**Q4: What is the blast radius of the current state?**
- A) Low — agents work fine, this is optimization only
- B) Medium — agent quality noticeably degrades in long sessions due to context bloat
- C) High — agents are making mistakes because of conflicting instructions
> Recommendation: A — Codex has been successfully shipping WFs (WF-0038 through WF-0045) without any user-global rules, proving the 361-line file is not essential for correct behavior.
> **Selected: A**

**Q5: Is this problem specific to this project or cross-project?**
- A) This project only — just clean up Grant-Reviewer's config files
- B) Cross-project — the user-global file affects all Antigravity projects
- C) Both, but focus on this project first and create a portable pattern
> Recommendation: B — The user-global config at `~/.gemini/GEMINI.md` loads on every Antigravity session regardless of project. Changes there affect all projects.
> **Selected: B**

---

## Section 2 — Desired Outcome

**Q1: What is the primary measurable change that defines success?**
- A) Reduce total agent instruction tokens loaded per-prompt by ≥50%
- B) Consolidate to a single instruction file (`AGENTS.md`) as the only SSOT per project
- C) Improve agent output quality in long sessions (hard to measure objectively)
> Recommendation: B — Measurable, concrete, achievable. You can verify by simply counting instruction files. Token reduction follows naturally from consolidation.
> **Selected: B**

**Q2: What becomes easier after this exists?**
- A) Onboarding a new coding agent — just point it at `AGENTS.md`, done
- B) Editing agent rules — one file to update instead of hunting across 3 locations
- C) Both A and B
> Recommendation: A — The simplicity of "one file, any agent" is the strongest value proposition. B is a nice side effect.
> **Selected: A**

**Q3: What behavior change do we expect from agents?**
- A) No visible behavior change — agents should work exactly as before, just with less overhead
- B) Better reasoning in long sessions due to freed context window
- C) More consistent behavior since there's one rules source instead of three
> Recommendation: A — This is optimization, not behavior change. Setting expectations correctly avoids scope creep into "agent quality" work.
> **Selected: A**

**Q4: How do we verify success?**
- A) Token count before/after (count instruction lines loaded per session)
- B) One SSOT file exists, all duplicates deleted, agent still follows project conventions
- C) Run a typical WF cycle and compare agent behavior qualitatively
> Recommendation: B — Concrete and verifiable. Binary pass/fail.
> **Selected: B**

**Q5: What becomes possible that wasn't before?**
- A) Easily switch between coding agents (Codex, Antigravity, Claude Code) — same `AGENTS.md` works for all
- B) Version-control all agent rules in the repo (currently user-global is outside git)
- C) Both A and B
> Recommendation: A — Agent portability is the most forward-looking benefit.
> **Selected: A**

---

## Section 3 — Target User / Actor

**Q1: Who is the primary user of `AGENTS.md`?**
- A) The coding agents (they read it to understand how to behave)
- B) The developer (you, as a reference for what rules apply)
- C) Both equally
> Recommendation: A — Agents are the consumers; the developer is the author.
> **Selected: A**

**Q2: Which coding agents must be supported?**
- A) Antigravity (Gemini) only — it's the one with the bloat problem
- B) Antigravity + Codex (the two you currently use)
- C) Any future agent (make it fully agent-agnostic, no tool-specific references)
> Recommendation: B — Both read `AGENTS.md` already. C comes free if we keep it agent-agnostic (Q5:A).
> **Selected: B + C** (user: "and also C if it's not complicated" — since agent-agnostic Q5:A makes C free)

**Q3: What is the developer's current behavior when editing agent rules?**
- A) Edit `AGENTS.md` in the repo root — quick, visible, version-controlled
- B) Hunt across `~/.gemini/GEMINI.md`, repo `GEMINI.md`, and `AGENTS.md`
- C) Mostly ignore the rules and rely on convention/muscle memory
> Recommendation: A — This is the desired and current preferred behavior.
> **Selected: A**

**Q4: Does the `AGENTS.md` need to work for developers other than you?**
- A) No — single-developer project, optimize for your workflow
- B) Yes — other contributors may use different agents
- C) Maybe later, but not now
> Recommendation: A — Single-developer project.
> **Selected: A**

**Q5: Should `AGENTS.md` contain agent-specific directives?**
- A) No — keep it fully agent-agnostic; agent-specific behaviors come from each agent's own system
- B) Yes — include labeled sections per agent
- C) Minimal — only if a directive is critical and no agent-agnostic equivalent exists
> Recommendation: A — Maximizes portability.
> **Selected: A**

---

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest approach to consolidation?**
- A) Grab-and-trim: Extract ~10 unique rules from user-global, add to `AGENTS.md`, delete duplicates
- B) Full rewrite from scratch using Ralph's ~60-line principle
- C) Layered: minimal `AGENTS.md` + separate `docs/guides/agent-conventions.md`
> Recommendation: A — Minimal work, immediate result, lowest risk.
> **Selected: A**

**Q2: What should `AGENTS.md` contain after consolidation?**
- A) Project identity + "Read if needed" links to `docs/guides/` (current style, ~30 lines)
- B) All rules inline, self-contained (~60-80 lines, Ralph-style)
- C) Hybrid: core rules inline + links (~40-50 lines)
> Recommendation: A — Proven by current AGENTS.md; rules live in project docs.
> **Selected: A**

**Q3: What happens to `~/.gemini/GEMINI.md`?**
- A) Trim to ~10 lines: universal behavioral guardrails only
- B) Delete entirely
- C) Replace with one-liner pointing to project AGENTS.md
> Recommendation: A — Safety net for non-Grant-Reviewer projects.
> **Selected: A**

**Q4: Which rules from user-global are genuinely unique?**
- A) Only behavioral guardrails: "wait for signal", "LGTM ≠ proceed", "3-file limit", "describe approach first"
- B) Also communication style rules
- C) Also error handling and engineering best practices
> Recommendation: A — Audited earlier in chat; everything else is in project docs.
> **Selected: A**

**Q5: What happens to repo-root `GEMINI.md`?**
- A) Delete — byte-identical duplicate of `AGENTS.md`
- B) Keep as symlink
- C) Replace with one-liner
> Recommendation: A — Pure waste, confirmed identical.
> **Selected: A**

---

## Section 5 — Constraints

**Q1: Time constraint?**
- A) Ship in a single session — small scope (3 files)
- B) Spread across 2-3 sessions
- C) No time pressure
> Recommendation: A — 3 files changed total. > **Selected: A**

**Q2: Technical constraint on `~/.gemini/GEMINI.md`?**
- A) Plain text file, freely editable — no constraints
- B) May be cached by Antigravity
- C) Unknown
> Recommendation: A. > **Selected: A**

**Q3: Does anything depend on the 361-line user-global being large?**
- A) No — Codex proves project works without it
- B) Possibly
- C) Unknown
> Recommendation: A. > **Selected: A**

**Q4: Other projects using `~/.gemini/GEMINI.md`?**
- A) Grant-Reviewer is primary; others lower priority
- B) Multiple active projects
- C) Unknown
> Recommendation: A. > **Selected: A**

**Q5: External dependency on repo `GEMINI.md`?**
- A) No — only read by agent at session start
- B) Possibly — check CI/hooks
- C) Unknown
> Recommendation: A. > **Selected: A**

---

## Section 6 — Risks / Unknowns

**Q1: Most fragile assumption?**
- A) That no rules beyond 4 guardrails are uniquely critical
- B) That Antigravity works same with 10-line user-global
- C) That `AGENTS.md` is sufficient for all agent types
> Recommendation: A — Mitigation: audit before deleting. > **Selected: A**

**Q2: What could cause rework?**
- A) Agent behavior regression → add back missed rule (low cost)
- B) Antigravity not reading `AGENTS.md` same as `GEMINI.md`
- C) Project docs missing a critical rule
> Recommendation: A. > **Selected: A**

**Q3: What must be validated early?**
- A) Line-by-line audit of user-global against project docs
- B) Test agent behavior after changes
- C) Both A then B
> Recommendation: A. > **Selected: A**

**Q4: Rollback strategy?**
- A) Git history + backup copy in `/tmp/`
- B) Keep `.bak` file
- C) No rollback needed
> Recommendation: A. > **Selected: A**

**Q5: Traceability risk?**
- A) None — Lessons content already in project logs
- B) Yes — some rules not captured elsewhere
- C) Small risk — mitigate with diff log
> Recommendation: A. > **Selected: A**

---

## Section 7 — MVP Definition

**Q1: If limited to one session, what must exist?**
- A) AGENTS.md updated + repo GEMINI.md deleted + user-global trimmed to ~10 lines
- B) Just delete GEMINI.md and trim user-global
- C) Only AGENTS.md + GEMINI.md delete, defer user-global
> Recommendation: A — The complete deliverable. > **Selected: A**

**Q2: Explicit ordered checklist?**
- A) Audit → Grab rules → Delete GEMINI.md → Trim user-global → Verify
- B) Delete → Trim → Add rules → Verify
- C) Rewrite from scratch → Delete → Verify
> Recommendation: A — Safest order. > **Selected: A**

**Q3: Add parking lot stories D and G in this WF?**
- A) Yes — born from this analysis
- B) No — keep scope minimal
- C) Add only D
> Recommendation: A. > **Selected: A**

**Q4: What can explicitly wait?**
- A) Any improvement to docs/guides/ content — out of scope
- B) Testing long-session improvement
- C) Both
> Recommendation: A. > **Selected: A**

**Q5: Verification for "done"?**
- A) ls GEMINI.md → not found; wc -l AGENTS.md ≤ 45; wc -l ~/.gemini/GEMINI.md ≤ 15
- B) Run test WF session
- C) Both
> Recommendation: A — Concrete, scriptable. > **Selected: A**

---

## Section 8 — Explicit Non-Goals

**Q1: Redesign docs/guides/?**
- A) No — out of scope > **Selected: A**

**Q2: Create ~/.codex/AGENTS.md?**
- A) No — Codex works fine without it > **Selected: A**

**Q3: Refactor how project docs reference agent rules?**
- A) No — not broken > **Selected: A**

**Q4: Implement file size caps (Story F) enforcement?**
- A) No — one-line note, no hook > **Selected: A**

**Q5: Keep the "Acknowledge" heartbeat policy?**
- A) Drop it — questionable value, wastes tokens > **Selected: A**
