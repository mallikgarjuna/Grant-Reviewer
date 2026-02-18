# Project Dashboard

Quick links:
- Parking lot / backlog: `docs/parking_lot.md`

## Legacy Task Registry (pre-WF)

| Task ID | Component | PRD | Task File | Walkthrough | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0.0 | Phase 0 | - | [task-0-brainstorming.md](tasks/task-0-brainstorming.md) | - | [x] |
| 1.0 | Phase 1 | - | [task-1-domain-model.md](tasks/task-1-domain-model.md) | - | [x] |
| 2.0 | Phase 2 | - | [task-2-sample-data.md](tasks/task-2-sample-data.md) | - | [x] |
| 3.0 | Phase 3 | - | [task-3-core-logic.md](tasks/task-3-core-logic.md) | [walkthrough](walkthroughs/walkthrough_task_3_core_logic.md) | [x] |
| 4.0 | Phase 4 | - | - | [walkthrough](walkthroughs/walkthrough_task_4_interface_readiness.md) | [x] |
| 5.0 | Admin Ingestion | [prd-5.0](prds/prd-5.0-admin-ingest.md) | [task-5.0](tasks/task-5.0-admin-ingest.md) | [walkthrough](walkthroughs/walkthrough_task_5.0_admin_ingest.md) | [x] |
| 6.0 | LLM Integration | [prd-6.0](prds/prd-6.0-llm-integration.md) | [task-6.0](tasks/task-6.0-llm-integration.md) | [walkthrough](walkthroughs/walkthrough_task_6.0_llm_integration.md) | [x] |
| 7.0 | FastAPI MVP | [prd-7.0](prds/prd-7.0-fastapi-mvp.md) | [task-7.0](tasks/task-7.0-fastapi-mvp.md) | [walkthrough](walkthroughs/walkthrough_task_7.0_fastapi_mvp.md) | [x] |
| 8.0B | Frontend Contracts | [prd-8.0B](prds/prd-8.0B-bff-contracts.md) | [task-8.0B](tasks/task-8.0B-bff-contracts.md) | [walkthrough](walkthroughs/walkthrough_task_8.0B_bff_contracts.md) | [x] |
| 8.0A | Frontend UI Slice | [prd-8.0A](prds/prd-8.0A-frontend-ui.md) | [task-8.0A](tasks/task-8.0A-frontend-ui.md) | [walkthrough](walkthroughs/walkthrough_task_8.0A_frontend_ui.md) | [x] |
| 8.0C | Deployment Wiring | [prd-8.0C](prds/prd-8.0C-deployment-wiring.md) | [task-8.0C](tasks/task-8.0C-deployment-wiring.md) | [walkthrough](walkthroughs/walkthrough_task_8.0C_deployment_wiring.md) | [x] |
| 8.1 | Lint Baseline Cleanup | [prd-8.1](prds/prd-8.1-lint-baseline-cleanup.md) | [task-8.1](tasks/task-8.1-lint-baseline-cleanup.md) | - | [x] |

## WF Registry (new work)

This table tracks new WF-based initiatives. Legacy task-ID artifacts remain above during migration.
WF IDs start after the legacy Task IDs (first WF is `WF-0009`).

| WF ID | Slug / Feature | Brainstorm | Spec | PRD | Task File | Walkthrough | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| WF-0009 | peerlens-landing-page | [Brainstorm](brainstorms/brainstorm-WF-0009-peerlens-landing-page.md) | [Spec](specs/pages/spec-WF-0009-peerlens-landing-page.md) | [PRD](prds/prd-WF-0009-peerlens-landing-page.md) | [Tasks](tasks/task-WF-0009-peerlens-landing-page.md) | [Walkthrough](walkthroughs/walkthrough-WF-0009-peerlens-landing-page.md) | Done |
| WF-0010 | peerlens-landing-design-refresh | [Brainstorm](brainstorms/brainstorm-WF-0010-peerlens-landing-design-refresh.md) | [Spec](specs/pages/spec-WF-0010-peerlens-landing-design-refresh.md) | [PRD](prds/prd-WF-0010-peerlens-landing-design-refresh.md) | [Tasks](tasks/task-WF-0010-peerlens-landing-design-refresh.md) | [Walkthrough](walkthroughs/walkthrough-WF-0010-peerlens-landing-design-refresh.md) | Done |
| WF-0011 | local-postgres-dev-db | [Brainstorm](brainstorms/brainstorm-WF-0011-local-postgres-dev-db.md) | [Spec](specs/features/spec-WF-0011-local-postgres-dev-db.md) | [PRD](prds/prd-WF-0011-local-postgres-dev-db.md) | [Tasks](tasks/task-WF-0011-local-postgres-dev-db.md) | [Walkthrough](walkthroughs/walkthrough-WF-0011-local-postgres-dev-db.md) | Done |
| WF-0012 | alembic-migration-baseline | [Brainstorm](brainstorms/brainstorm-WF-0012-alembic-migration-baseline.md) | [Spec](specs/features/spec-WF-0012-alembic-migration-baseline.md) | [PRD](prds/prd-WF-0012-alembic-migration-baseline.md) | [Tasks](tasks/task-WF-0012-alembic-migration-baseline.md) | [Walkthrough](walkthroughs/walkthrough-WF-0012-alembic-migration-baseline.md) | Done |
| WF-0013 | app-shell-signout | [Brainstorm](brainstorms/brainstorm-WF-0013-app-shell-signout.md) | [Spec](specs/features/spec-WF-0013-app-shell-signout.md) | [PRD](prds/prd-WF-0013-app-shell-signout.md) | [Tasks](tasks/task-WF-0013-app-shell-signout.md) | [Walkthrough](walkthroughs/walkthrough-WF-0013-app-shell-signout.md) | Done |
| WF-0014 | review-history | [Brainstorm](brainstorms/brainstorm-WF-0014-review-history.md) | [Spec](specs/features/spec-WF-0014-review-history.md) | [PRD](prds/prd-WF-0014-review-history.md) | [Tasks](tasks/task-WF-0014-review-history.md) | [Walkthrough](walkthroughs/walkthrough-WF-0014-review-history.md) | Done |
| WF-0015 | practices-upgrade | [Brainstorm](brainstorms/brainstorm-WF-0015-practices-upgrade.md) | [Spec](specs/features/spec-WF-0015-practices-upgrade.md) | [PRD](prds/prd-WF-0015-practices-upgrade.md) | [Tasks](tasks/task-WF-0015-practices-upgrade.md) | [Walkthrough](walkthroughs/walkthrough-WF-0015-practices-upgrade.md) | Done |
| WF-0016 | review-results-ux | [Brainstorm](brainstorms/brainstorm-WF-0016-review-results-ux.md) | [Spec](specs/features/spec-WF-0016-review-results-ux.md) | [PRD](prds/prd-WF-0016-review-results-ux.md) | [Tasks](tasks/task-WF-0016-review-results-ux.md) | [Walkthrough](walkthroughs/walkthrough-WF-0016-review-results-ux.md) | Done |
| WF-0017 | auto-polling-processing-reviews | [Brainstorm](brainstorms/brainstorm-WF-0017-auto-polling-processing-reviews.md) | [Spec](specs/features/spec-WF-0017-auto-polling-processing-reviews.md) | [PRD](prds/prd-WF-0017-auto-polling-processing-reviews.md) | [Tasks](tasks/task-WF-0017-auto-polling-processing-reviews.md) | [Walkthrough](walkthroughs/walkthrough-WF-0017-auto-polling-processing-reviews.md) | Done |
---

## Research & Market Analysis

- **Competitor Research (2026-02-14)**: [Walkthrough](walkthroughs/walkthrough-competitor-research.md) — Analyzed 8 competitors (Grantease, Grantable, Paperpal, Writefull, SciSpace, Elicit, Overleaf, Grammarly).
- **Landing Page Blueprints**: [Strategy Reference](reference/landing_page_blueprint.md) — 9-section frameworks (Product-Led vs. Sales-Led).
- **Brand Guidelines**: [Visual & Voice](reference/brand_guidelines.md) — PeerLens atomic design tokens and academic tone.
