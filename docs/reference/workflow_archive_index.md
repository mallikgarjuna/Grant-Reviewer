<!-- docs/reference/workflow_archive_index.md -->
# Workflow Archive Index

This file is the historical archive route previously embedded inline in `docs/index.md`.

Use it for:

- legacy task lookup,
- completed workflow lookup,
- and path recovery for older artifacts.

## Legacy Task Registry (pre-WF)

| Task ID | Component | PRD | Task File | Walkthrough | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0.0 | Phase 0 | - | [task-0-brainstorming.md](../tasks/completed/task-0-brainstorming.md) | - | [x] |
| 1.0 | Phase 1 | - | [task-1-domain-model.md](../tasks/completed/task-1-domain-model.md) | - | [x] |
| 2.0 | Phase 2 | - | [task-2-sample-data.md](../tasks/completed/task-2-sample-data.md) | - | [x] |
| 3.0 | Phase 3 | - | [task-3-core-logic.md](../tasks/completed/task-3-core-logic.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_3_core_logic.md) | [x] |
| 4.0 | Phase 4 | - | - | [walkthrough](../walkthroughs/completed/walkthrough_task_4_interface_readiness.md) | [x] |
| 5.0 | Admin Ingestion | [prd-5.0](../prds/completed/prd-5.0-admin-ingest.md) | [task-5.0](../tasks/completed/task-5.0-admin-ingest.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_5.0_admin_ingest.md) | [x] |
| 6.0 | LLM Integration | [prd-6.0](../prds/completed/prd-6.0-llm-integration.md) | [task-6.0](../tasks/completed/task-6.0-llm-integration.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_6.0_llm_integration.md) | [x] |
| 7.0 | FastAPI MVP | [prd-7.0](../prds/completed/prd-7.0-fastapi-mvp.md) | [task-7.0](../tasks/completed/task-7.0-fastapi-mvp.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_7.0_fastapi_mvp.md) | [x] |
| 8.0B | Frontend Contracts | [prd-8.0B](../prds/completed/prd-8.0B-bff-contracts.md) | [task-8.0B](../tasks/completed/task-8.0B-bff-contracts.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_8.0B_bff_contracts.md) | [x] |
| 8.0A | Frontend UI Slice | [prd-8.0A](../prds/completed/prd-8.0A-frontend-ui.md) | [task-8.0A](../tasks/completed/task-8.0A-frontend-ui.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_8.0A_frontend_ui.md) | [x] |
| 8.0C | Deployment Wiring | [prd-8.0C](../prds/completed/prd-8.0C-deployment-wiring.md) | [task-8.0C](../tasks/completed/task-8.0C-deployment-wiring.md) | [walkthrough](../walkthroughs/completed/walkthrough_task_8.0C_deployment_wiring.md) | [x] |
| 8.1 | Lint Baseline Cleanup | [prd-8.1](../prds/completed/prd-8.1-lint-baseline-cleanup.md) | [task-8.1](../tasks/completed/task-8.1-lint-baseline-cleanup.md) | - | [x] |

## Completed Workflow Lookup

The completed WF archive is intentionally compact here to avoid recreating the old `docs/index.md` bloat in a new default surface.

- Legacy-with-spec completed workflows:
  - Use `rg --files docs/brainstorms/completed docs/prds/completed docs/tasks/completed docs/walkthroughs/completed | rg 'WF-00(09|10|11|12|13|14|15|16|17|18|19|21|23|24|25|44)'`
- Active-standard completed workflows:
  - Use `rg --files docs/brainstorms/completed docs/prds/completed docs/tasks/completed docs/walkthroughs/completed | rg 'WF-00(26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|45|46|47|48|49|50|51|52|53|54|55|56|57|58|59|60|61|62|63|64|65|66|67|68|69|70|71|72|73|74|75|76|77|78|80|81)'`

## Still-Active / Non-Archived WF References

These rows remain in the active dashboard because they are not fully archived yet:

| WF ID | Slug / Feature | Key Artifact | Status |
| :--- | :--- | :--- | :--- |
| WF-0079 | researcher-visible-carry-through-mvp | [Tasks](../tasks/task-WF-0079-researcher-visible-carry-through-mvp.md) | Completed |
| WF-0082 | codex-usage-optimization | [Tasks](../tasks/task-WF-0082-codex-usage-optimization.md) | Phase 2 (Ready) |

## Notes

- Historical artifact paths still follow the standard naming convention: `<artifact>-WF-XXXX-<slug>.md`.
- If you know the WF ID or slug, `rg --files docs | rg 'WF-XXXX|slug-fragment'` is the fastest recovery path.
