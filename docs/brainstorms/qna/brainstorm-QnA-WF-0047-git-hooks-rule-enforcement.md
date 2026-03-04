# WF-0047 — Git Hooks Rule Enforcement Q&A

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-04

**Brainstorming Q&A:**

**Q1: How should we mechanically enforce the `AGENTS.md` line count and commit conventions?**
- A) Integrate as custom `repo: local` hooks inside the existing `.pre-commit-config.yaml`.
- B) Provide a `Makefile` script that developers must run manually.
- C) Write standalone bash scripts directly in `.git/hooks/`.
 > Recommendation: Option A. Since the `.pre-commit-config.yaml` is already present, adding a local python/bash hook keeps all enforcement centralized and easy for all developers to install (`pre-commit install`).
 > **Selected: Option A**

**Q2: What specific commit convention rules do we want to enforce?**
- A) Standard Conventional Commits (e.g., `feat:`, `fix:`, `chore:`).
- B) Project-specific prefix rules (e.g., `WF-XXXX: <message>`).
- C) Both A and B (e.g., must start with `WF-XXXX: ` or a standard type).
 > Recommendation: Option B. The project heavily relies on tracking work via `WF-XXXX` for traceability. Enforcing a `WF-XXXX: ` prefix is highly valuable for this specific repo, whereas standard conventional commits might be orthogonal to the parking lot/WF tracking system.
 > **Selected: Option B**

**Q3: How should the hook react if the user is merging a PR (`Merge branch '...'`) or reverting a commit (`Revert "..."`)?**
- A) Skip validation for merge/revert commits entirely (standard practice).
- B) Force human editors to rewrite merge/revert commit messages to include the `WF-XXXX:` prefix.
- C) Do not enforce `WF-XXXX:` strictly, just print a warning for any commit.
 > Recommendation: Option A. It is standard practice to let Git's default `Merge branch...` and `Revert...` commits bypass prefix rules, as rewriting them destroys traceability to the original branch/commit.
 > **Selected: Option A**

**Q4: What should happen if `AGENTS.md` is exactly 45 lines?**
- A) Pass (the rule is `<= 45` lines).
- B) Fail (the rule is `< 45` lines).
 > Recommendation: Option A. The parking lot task specifies `(<= 45 lines)`, so 45 lines should be a passing state.
 > **Selected: Option A**

**Q5: What is the smallest functional slice (MVP) for this workflow?**
- A) Implement both the python hook scripts (`check_agents_md.py`, `check_commit_msg.py`) and wire them into `.pre-commit-config.yaml` to enforce the rules locally.
- B) Implement the local hooks AND set up a GitHub Actions CI workflow to enforce the same rules on the remote server.
- C) Implement only the `AGENTS.md` check for now, and leave the commit message check for a future workflow.
 > Recommendation: Option A. The immediate pain is agents looping locally. Local `pre-commit` hooks solve this directly. CI enforcement (Option B) can be a separate ops task in the future if developers start bypassing the local hooks.
 > **Selected: Option A**
