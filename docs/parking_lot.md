# Parking Lot / Backlog

**Purpose**: The prioritized backlog for "not now" items. When you're ready to work on one, promote it into the WF workflow system.

## Guidelines

### Priority Tiers

- **🔴 P0** — Must-fix before any real user touches the app.
- **🟡 P1** — Must-fix before public launch.
- **🟢 P2** — Must-fix before scaling / ongoing traffic.

> **All code phrases** (including `park this`, `pick`, and others): see [docs/reference/code_phrases.md](reference/code_phrases.md).

Each table has **independent numbering** (1, 2, 3…) so items are easy to reference (e.g., "P0 #2").

### Adding Items (Code Phrase: `park this`)

Say **"park this"** followed by a description and the agent will:
1. Add the item to the appropriate P0/P1/P2 table.
2. Assign the next `#` within that table.
3. Confirm: "Parked as P[x] #[n]: [title]".

You can also add items manually. Each row should have:
- **#**: sequential within the table.
- **Task**: short, verb-first title.
- **Type**: `product` / `tech-debt` / `ops` / `legal` / `idea`.
- **Recommendation**: one-line why and what.
- **Date**: when parked (YYYY-MM-DD).

### Picking Items (Code Phrase: `pick P[x] #[n]`)

Say **`pick P0 #1`** (or any P[x] #[n] reference) and the agent will promote that item into a new WF.

### Promoting Items (What Happens When Picked)

When you pick an item to start work:
1. **Assign the next WF ID** from the WF Registry in `docs/index.md`.
2. **Move the row** from the priority table to the **Promoted Items** section below.
3. Mark it: `→ Promoted to WF-xxxx` with links to artifacts as they're created.
4. **Renumber** remaining items in that priority tier so `#1` is always the top item.
5. **Add the WF row** to `docs/index.md` WF Registry.
6. Follow the standard WF phase workflow from there.

### Maintenance

- Prefer fewer, higher-signal items; merge duplicates.
- Re-prioritize periodically — items can move between P0/P1/P2.
- Where to park: **minor opportunistic fixes** → `docs/maintenance.md`; **everything else** → here.

---

## 🔴 P0 — Must-fix before real users

| # | Task | Type | Recommendation | Date |
|---|------|------|----------------|------|

---

## 🟡 P1 — Must-fix before public launch

| # | Task | Type | Recommendation | Date |
|---|------|------|----------------|------|
| 1 | Add node hierarchy selector | product | Group flat node `<select>` by parent sections (cascade or grouped optgroups) — current flat list is confusing for 10+ nodes. | 2026-02-16 |
| 2 | Add Terms of Service + upgrade Privacy | legal | Add `/terms` page; expand `/privacy` beyond 3 bullets; add inline retention reminder near submit button. | 2026-02-16 |
| 3 | Accessibility pass (forms + results) | product | Ensure errors are announced (`aria-live`), focus lands on first invalid field, buttons/alerts are keyboard + screen-reader friendly. | 2026-02-16 |
| 4 | Ingest real call data | product | Only 2 YAMLs exist (ERC + partial NWO); landing promises NWO, ZonMw, ERC, MSCA — deliver at least 1 complete call per program. | 2026-02-16 |
| 5 | NWO Veni 2025 preproposal — WF-4: Implement compliance engine + persist findings | product | Add deterministic ERROR/WARNING findings separate from scoring; expose in review detail. (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 6 | NWO Veni 2025 preproposal — WF-5: Add structured reviews API + NOT_ASSESSABLE alignment | product | Persist structured submission and enforce “missing context → NOT_ASSESSABLE” (never fabricate alignment). (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 7 | NWO Veni 2025 preproposal — WF-6: Build frontend structured form + compliance UI + idempotent drafts | product | Replace single snippet textarea with 3-node structured input for this call; render compliance separately. (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 8 | NWO Veni 2025 preproposal — WF-7: Assisted extraction (paste-only) preview+confidence+confirm | product | Optional extraction UX that requires explicit confirmation before evaluation; avoid silent misrouting. (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 9 | Assisted extraction: add `.docx`/`.pdf` support | idea | Defer file parsing to a dedicated WF (new deps + file handling/security considerations). (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |

---

## 🟢 P2 — Must-fix before scaling

| # | Task | Type | Recommendation | Date |
|---|------|------|----------------|------|
| 1 | Set up Alembic migration baseline | tech-debt | Neon Postgres is live with `create_all()` — one schema change will silently break prod; create baseline migration. | 2026-02-16 |
| 2 | Add error monitoring (Sentry) | ops | Zero error tracking in production; blind to LLM timeouts, BFF failures, and client crashes with real users. | 2026-02-16 |
| 3 | Prompt quality tuning | product | Test AI output quality with real ERC/NWO proposals; tune `PromptTemplate` for actionable, criteria-specific feedback. | 2026-02-16 |
| 4 | Production hardening | ops | Lock CORS, verify rate limiting beyond daily quota, add custom 404 page, tune Vercel/Render timeout alignment. | 2026-02-16 |

---

## Promoted Items

| # | Original P-tier | Task | WF ID | Date Promoted |
|---|---|---|---|---|
| 1 | P0 | Add app shell + sign-out | [WF-0013](tasks/task-WF-0013-app-shell-signout.md) | 2026-02-16 |
| 2 | P0 | Add review history ("My Reviews") | [WF-0014](tasks/task-WF-0014-review-history.md) | 2026-02-16 |
| 3 | P1 | Practices Upgrade (CI/CD) | [WF-0015](tasks/task-WF-0015-practices-upgrade.md) | 2026-02-17 |
| 4 | P0 | Upgrade review results UX | [WF-0016](tasks/task-WF-0016-review-results-ux.md) | 2026-02-17 |
| 5 | P0 | Add auto-polling for processing reviews | [WF-0017](tasks/task-WF-0017-auto-polling-processing-reviews.md) | 2026-02-18 |
| 6 | P0 | Harden submit flow UX | [WF-0018](tasks/task-WF-0018-harden-submit-flow-ux.md) | 2026-02-18 |
| 7 | P1 | Add loading & empty states | [WF-0019](tasks/task-WF-0019-add-loading-empty-states.md) | 2026-02-18 |
| 8 | P1 | NWO Veni 2025 preproposal — WF-1: Fix YAML parse + add CallDefinition V2 loader (dry-run only) | WF-0020 | 2026-02-21 |
| 9 | P1 | NWO Veni 2025 preproposal — WF-2: Add `logical_id` columns + ingest V2 YAML into DB | [WF-0021](tasks/task-WF-0021-nwo-veni-2025-preproposal-wf2.md) | 2026-02-21 |
| 10 | P1 | NWO Veni 2025 preproposal — WF-3: Add `structured-config` endpoint + frontend mode gating | [WF-0027](tasks/task-WF-0027-nwo-veni-2025-preproposal-wf3.md) | 2026-02-21 |

---

## Revision History

- **v0.1** (2026-02-13): Created as a dedicated parking place for snapshot + priorities + non-urgent TODOs.
- **v0.2** (2026-02-16): Restructured into P0/P1/P2 priority tables with independent numbering, code phrase (`park this`), and promotion mechanics. Pre-populated 15 MVP readiness items from deep frontend + infra audit.
