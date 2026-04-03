<!-- docs/walkthroughs/completed/walkthrough-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization

Artifact: walkthrough
Version: v0.5
Status: Completed
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
- Task 2 converted `docs/index.md` from a heavy inline registry into a compact active dashboard and moved historical lookup behind `docs/reference/workflow_archive_index.md`.

## Task 2 Verification Snapshot

| Surface | Chars | Estimated tokens |
| :--- | ---: | ---: |
| `docs/index.md` | 1611 | 403 |
| `docs/reference/workflow_archive_index.md` | 3979 | 995 |

Task 2 outcome:

- `docs/index.md` dropped from `31734` chars / `7934` estimated tokens to `1611` chars / `403` estimated tokens.
- The active dashboard still exposes `WF-0082`, `Mission`, `Parking lot`, and the archive route.
- Historical lookup now routes through `docs/reference/workflow_archive_index.md` instead of staying inline in the default dashboard.

## Task 3 Verification Snapshot

- `AGENTS.md` now routes `docs/index.md` through workflow/task tracking only instead of any work request.
- The rest of the high-signal AGENTS rules remain unchanged.
- File length remains within the repo's tiny-file guardrail.

## Final Before / After Comparison

Method:

- Same deterministic estimate as the baseline: `round(char_count / 4)` over the likely repo-local default-load path `AGENTS.md` + `docs/index.md` + `docs/memory/index.md`.

| Surface | Before chars | Before est. tokens | After chars | After est. tokens |
| :--- | ---: | ---: | ---: | ---: |
| `AGENTS.md` | 2939 | 735 | 2950 | 738 |
| `docs/index.md` | 31734 | 7934 | 1611 | 403 |
| `docs/memory/index.md` | 994 | 248 | 1243 | 311 |
| Combined | 35667 | 8917 | 5804 | 1451 |

Result:

- Combined estimated default-load path reduced from `8917` to `1451`.
- Estimated reduction: `7466` tokens, about `83.7%`.
- The main win came from converting `docs/index.md` into a compact active dashboard and narrowing the `AGENTS.md` trigger.

## Durable Operating Rule

- `always_on`: only tiny, high-signal entry surfaces that the repo intentionally wants near every session start, such as `AGENTS.md`.
- `on_demand`: router or reference surfaces that are useful when a task explicitly calls for them, such as `docs/memory/index.md` and selected memory leaves.
- `archival`: history-heavy surfaces that preserve traceability and lookup value but should not be default prompt payload, such as workflow/task registries now routed through `docs/reference/workflow_archive_index.md`.
- New instruction surfaces should default to `on_demand` unless there is a strong reason they must be `always_on`.
- Large historical material should be compacted behind active routers instead of living inline in default dashboards.

## Safety / Traceability / Terminology Checks

- Workflow safety preserved: active workflow routing remains visible from `docs/index.md`, and detailed workflow docs remain available on demand.
- Traceability preserved: historical workflow/task lookup still routes through `docs/reference/workflow_archive_index.md`, and file provenance headers remain intact.
- Researcher-facing terminology preserved: `AGENTS.md` still explicitly requires `evaluation criteria/elements` and still forbids `rubric` in researcher-facing text.

## Phase 3.3 Closure Notes

- Part C1 fixed the Phase 3.2 status-drift finding by aligning the task, walkthrough, dashboard, and archive surfaces on one terminal workflow state.
- Part C2 added and ran a deterministic cross-artifact status-alignment verification command so future handoffs fail closed on stale WF metadata.
- Part C3 moves the active WF artifacts into `completed/` directories and updates the live routes to point at the completed paths.

## Changelog

- v0.1 (2026-04-03): Recorded the baseline default-load estimate, replay command, and compact surface inventory for Task 1.
- v0.2 (2026-04-03): Recorded the Task 2 dashboard compaction result and the post-split verification snapshot for `docs/index.md`.
- v0.3 (2026-04-03): Recorded the narrowed `AGENTS.md` trigger and confirmed the file stayed within the tiny-file guardrail for Task 3.
- v0.4 (2026-04-03): Recorded the final before/after default-load comparison, the durable operating rule, and the closing safety/traceability/terminology checks for Task 5.
- v0.5 (2026-04-03): Closed the walkthrough as `Completed`, recorded the Phase 3.2 review fix, and added the Phase 3.3 closure notes.
