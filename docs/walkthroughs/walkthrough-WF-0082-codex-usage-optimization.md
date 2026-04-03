<!-- docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization

Artifact: walkthrough
Version: v0.1
Status: In progress
Last Updated: 2026-04-03

## Baseline Default-Load Estimate

Method:

- Estimated tokens are approximated with `round(char_count / 4)` using a deterministic `python3` one-liner over the included files.
- Baseline likely repo-local default-load path for this WF: `AGENTS.md` + `docs/index.md` + `docs/memory/index.md`.

Included surfaces:

| Surface | Chars | Estimated tokens |
| :--- | ---: | ---: |
| `AGENTS.md` | 2939 | 735 |
| `docs/index.md` | 31734 | 7934 |
| `docs/memory/index.md` | 994 | 248 |

Baseline result:

- Combined estimated tokens: `8917`
- Dominant cost center: `docs/index.md`

Replay command:

```sh
python3 - <<'PY'
from pathlib import Path
files=['AGENTS.md','docs/index.md','docs/memory/index.md']
for f in files:
    text=Path(f).read_text()
    print(f'{f}\tchars={len(text)}\test_tokens~={round(len(text)/4)}')
print('combined_est_tokens', round(sum(len(Path(f).read_text()) for f in files)/4))
PY
```

## Surface Inventory

| Surface path | Role | Load posture | Estimated cost | Action | Rationale |
| :--- | :--- | :--- | ---: | :--- | :--- |
| `AGENTS.md` | Tiny always-on repo instruction surface | always_on | 735 | revise | Mostly healthy, but still contains one broad trigger that points too many tasks at `docs/index.md`. |
| `docs/index.md` | Project dashboard and workflow router | always_on | 7934 | compact | Highest-cost likely entrypoint; should route to active work and archive surfaces instead of embedding large registries inline. |
| `docs/memory/index.md` | Memory router | on_demand | 248 | keep | Already small and useful as an index; likely needs wording/routing support, not size reduction. |
| `docs/memory/domain/project_docs.md` | Durable project-doc rules and history | on_demand | 4106 | revise | Valuable content, but currently reads like an active first-load rule surface rather than a reference-heavy memory leaf. |
| `docs/memory/tools/workflow.md` | Workflow/chat-hygiene rules and history | on_demand | 4106 | revise | Similar to `project_docs.md`: important reference material, but should be framed as on-demand guidance rather than default context. |
| `docs/guides/*` and `docs/workflow/*` | Detailed procedural references | archival | n/a | keep | Useful when explicitly triggered, but should not be treated as default first-load context for this WF. |

## Task Progress Notes

- Task 1 established the replayable baseline and compact inventory artifact without changing repo behavior.

## Changelog

- v0.1 (2026-04-03): Recorded the baseline default-load estimate, replay command, and compact surface inventory for Task 1.
