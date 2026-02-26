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

### Promotion Gate (Mandatory Before `pick`)

Before promoting any item, verify against the latest rationale snapshot in this file:
1. Confirm the item still matches current architecture and isn't superseded.
2. Confirm dependency items are either already done or included in the same WF.
3. Confirm launch-critical ordering is preserved unless the user explicitly overrides it.

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
| 1 | Ingest real call data | product | Only 2 YAMLs exist (ERC + partial NWO); landing promises NWO, ZonMw, ERC, MSCA — deliver at least 1 complete call per program. | 2026-02-16 |
| 2 | Add Terms of Service + upgrade Privacy | legal | Add `/terms` page; expand `/privacy` beyond 3 bullets; add inline retention reminder near submit button. | 2026-02-16 |
| 3 | NWO Veni 2025 preproposal — WF-7: Assisted extraction (paste-only) preview+confidence+confirm | product | Optional extraction UX that requires explicit confirmation before evaluation; avoid silent misrouting. (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 4 | Add node hierarchy selector | product | Defer until universal form architecture is active; implement as part of dynamic renderer UX (depends on P2 #15/#16/#18) to avoid one-off UI debt. | 2026-02-16 |
| 5 | Assisted extraction: add `.docx`/`.pdf` support | idea | Defer file parsing to a dedicated WF (new deps + file handling/security considerations). (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |

### P1 Rationale Snapshot (2026-02-24)

- Launch risk is currently dominated by content coverage, accessibility, and legal readiness; these are ordered first.
- Assisted extraction (paste-only) is high-value but not a launch blocker, so it follows launch-readiness essentials.
- Node hierarchy selector is intentionally deprioritized until dynamic universal forms are implemented; doing it now would optimize a UX path the current hardcoded Veni form does not use.
- `.docx`/`.pdf` extraction remains explicitly deferred due additional dependency/security complexity.

Promotion dependency note:
- If promoting P1 #5, first verify status of P2 #15, P2 #16, and P2 #18, or bundle required dependency work into the same WF.

---

## 🟢 P2 — Must-fix before scaling

| # | Task | Type | Recommendation | Date |
|---|------|------|----------------|------|
| 1 | Unify review service execution core | tech-debt | Keep separate endpoints (`/reviews` single-node and `/api/structured-review` multi-node), but extract shared execution pipeline (policy injection, LLM call, response validation, policy post-checks) into a common internal component to reduce drift and duplicate fixes. ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-26 |
| 2 | Multi-step Evaluation Gating (ERC Step 1 vs Step 2) | product | The ERC StG evaluates B1 in Step 1, and both B1+B2+Resources in Step 2. We authored the full schema combined. We must build a UX/Execution routing rule engine to conditionally trigger subsets of node evaluations based on the chosen Step. (Ref: WF-0032 Brainstorm Section 3) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-25 |
| 3 | Review prompt revision for V2 expectations structure | product | Revise `build_review_prompt()` to optimally reference V2 `EvaluationCriterion` / `EvaluationElement` fields from updated YAML ingestion. Current prompt functions but isn't tuned for V2. (Ref: WF-0029 brainstorm S4 Q2 note) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 4 | Structured review: `requires_context_from` dependency engine | product | Add `requires_context_from: list[str]` field to YAML `node_expectations` + V2 schema + `NodeExpectation` model + ingestion pipeline. Replaces hardcoded NWO Veni rules with generalized cross-node context resolution. (Ref: WF-0029 brainstorm §9.4, deferred in PRD v0.3) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 5 | Universal Form: Dynamic UI renderer | product | The frontend submission form is currently hardcoded for NWO Veni. Build a dynamic UI renderer that consumes flattened backend schemas to support diverse program intakes without new frontend code. (Ref: WF-0030 PRD v0.4 deferral) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 6 | Universal Form: Recursive UI components for nested schemas | product | Some funding calls (e.g., ERC) contain nested `ProposalNode` structures. To support complex calls, the dynamic frontend requires recursive component rendering and the backend must serve deep structures. (Ref: WF-0030 S13 Q7 / Codex Audit) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 7 | Review detail page: remove hardcoded Veni node mapping | tech-debt | `/app/reviews/[reviewId]` currently uses hardcoded Veni labels/order. Refactor to call-aware node metadata so section headings/grouping remain correct for future funding calls. ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-23 |
| 8 | Add error monitoring (Sentry) | ops | Zero error tracking in production; blind to LLM timeouts, BFF failures, and client crashes with real users. ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-16 |
| 9 | E2E: Critical Negative Scenarios | ops | Run automated E2E tests for missing mandatory nodes, wrong stages, and policy-blocking content to prove operational readiness. (Ref: Architect Feedback Step 6) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-26 |
| 10 | E2E: Happy-path ERC Sample | ops | Run a full happy-path E2E with a sample ERC proposal text (submit -> process -> cards shown correctly). (Ref: Architect Feedback Step 6) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-26 |
| 11 | Re-author ERC CoG YAML from official sources | product | Rebuild `erc_cog_2026` call YAML with the same source-grounded standard used for ERC StG (evaluable proposal structure + evaluation criteria/elements + enforceable reviewer-policy), plus source manifest traceability. Start immediately after WF-0032 closure. | 2026-02-26 |
| 12 | Set up Alembic migration baseline | tech-debt | Neon Postgres is live with `create_all()` — one schema change will silently break prod; create baseline migration. | 2026-02-16 |
| 13 | Prompt quality tuning | product | Test AI output quality with real ERC/NWO proposals; tune `PromptTemplate` for actionable, criteria-specific feedback. | 2026-02-16 |
| 14 | Production hardening | ops | Lock CORS, verify rate limiting beyond daily quota, add custom 404 page, tune Vercel/Render timeout alignment. | 2026-02-16 |
| 15 | Structured review: single mega-prompt optimization | product | Replace per-node sequential LLM calls with a single mega-prompt for all nodes — fewer API calls, lower latency. Directly mitigates the 3× latency risk (15–45s) identified in WF-0029 brainstorm S6 Q4. Requires new prompt template + parser. (Ref: WF-0029 brainstorm Q4.2 option B) | 2026-02-22 |
| 16 | Structured review: LLM-generated overall summary | product | After per-node reviews, add an additional LLM call to synthesize a holistic cross-node summary (alignment, strengths, gaps). (Ref: WF-0029 brainstorm Q4.4 option A) | 2026-02-22 |
| 17 | Structured review: parallel per-node LLM calls | product | Fire LLM calls concurrently instead of sequentially — faster wall-clock time but adds rate-limiting and error-handling complexity. May be unnecessary if mega-prompt (P2 #5) is adopted instead. (Ref: WF-0029 brainstorm S4 Q2 option C, S8 Q5) | 2026-02-22 |
| 18 | Structured review: batch submission of multiple proposals | product | Allow submitting multiple proposals or revisions in one request. May not be needed depending on app evolution. (Ref: WF-0029 brainstorm S8 Q5) | 2026-02-22 |
| 19 | Structured review: async processing / polling | product | Synchronous MVP may hit 90s worst-case latency. Async would POST → return review_id → poll for completion. Adds WebSocket/polling complexity. (Ref: WF-0029 PRD v0.3 deferral) | 2026-02-22 |
| 20 | Structured review: `StructuredSubmission` aggregate table | tech-debt | Replace JSONB `structured_payload` on Review with a proper normalized aggregate table linking multiple `ProposalSnippet` rows to one Review. Enables per-node audit history and replay. (Ref: WF-0029 brainstorm §9.1 option A, deferred in PRD v0.3) | 2026-02-22 |
| 21 | Structured review: per-node grouped detail endpoint | product | New `/reviews/{id}/structured` endpoint returning `nodes[].cards[]` grouped response. Current MVP uses flat `cards[]` from existing detail endpoint. (Ref: WF-0029 PRD v0.3 deferral) | 2026-02-22 |
| 22 | Assisted extraction via document upload (.docx / .pdf) | product | Use a service like MarkItDown or an MCP tool to parse uploaded documents and auto-populate the structured UI inputs (reducing copy-paste friction with tables/images). (Ref: WF-0030 S1 Q2) | 2026-02-22 |
| 23 | Machine validation of page-based constraints (`max_pages`) | product | `max_pages` is currently authored merely as a UI signaling field. Since the MVP uses plain text strings rather than PDF uploads, we cannot physically count pages. Add a rough heuristic (e.g., 1 page = 4000 chars) or PDF parsing to strictly enforce this in the backend. (Ref: WF-0032 Brainstorm Section 6) | 2026-02-25 |

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
| 11 | P1 | NWO Veni 2025 preproposal — WF-4: Implement compliance engine + persist findings | [WF-0028](tasks/task-WF-0028-compliance-engine.md) | 2026-02-22 |
| 12 | P1 | NWO Veni 2025 preproposal — WF-5: Add structured reviews API + NOT_ASSESSABLE alignment | [WF-0029](tasks/task-WF-0029-nwo-veni-2025-preproposal-wf5-structured-review.md) | 2026-02-22 |
| 13 | P1 | NWO Veni 2025 preproposal — WF-6: Build frontend structured form + compliance UI + idempotent drafts | [WF-0030](tasks/task-WF-0030-nwo-veni-2025-preproposal-wf6-frontend-structured-form.md) | 2026-02-22 |
| 14 | P1 | Accessibility pass (forms + results) | [WF-0031](tasks/task-WF-0031-accessibility-pass.md) | 2026-02-25 |
| 15 | P2 | Data Contract Foundation (Tree Nodes + Metadata DTO) | [WF-0033](tasks/task-WF-0033-data-contract-foundation.md) | 2026-02-26 |

---

## Revision History

- **v0.1** (2026-02-13): Created as a dedicated parking place for snapshot + priorities + non-urgent TODOs.
- **v0.2** (2026-02-16): Restructured into P0/P1/P2 priority tables with independent numbering, code phrase (`park this`), and promotion mechanics. Pre-populated 15 MVP readiness items from deep frontend + infra audit.
- **v0.3** (2026-02-22): Promoted WF-4 (compliance engine) to `WF-0028`, moved it to Promoted Items, and renumbered remaining P1 items.
- **v0.4** (2026-02-22): Promoted WF-5 (structured reviews API) to `WF-0029`, moved it to Promoted Items, and renumbered remaining P1 items.
- **v0.5** (2026-02-22): Added P2 #5 (mega-prompt), P2 #6 (overall summary), P2 #7 (prompt revision for V2) from WF-0029 brainstorm.
- **v0.6** (2026-02-22): Promoted WF-6 (frontend structured form) to `WF-0030`, moved it to Promoted Items, and renumbered remaining P1 items.
- **v0.7** (2026-02-22): Promoted P2 #14 (Dynamic frontend forms) into scope for WF-0030 based on Senior Architectural mandate. Renumbered P2.
- **v0.8** (2026-02-22): Added P2 #15 (Recursive UI components) from WF-0030 post-Codex adversarial review.
- **v0.9** (2026-02-23): Added P2 #18 to track review-detail node label/order refactor beyond hardcoded Veni mappings.
- **v1.0** (2026-02-24): Reordered P1 for launch-readiness sequencing, added mandatory promotion gate, and recorded dependency-aware rationale snapshot.
- **v1.1** (2026-02-25): Promoted P1 #2 (Accessibility pass) to WF-0031 and renumbered remaining P1 items.
- **v1.2** (2026-02-26): Added P2 #22 to track shared-core refactor for single-node and structured review services while preserving separate API contracts.
- **v1.3** (2026-02-26): Added P2 #23 to track source-grounded re-authoring of ERC CoG YAML after ERC StG workflow completion.
- **v1.4** (2026-02-26): Reordered P2 priorities to map exactly to the Architect's 7-step Execution Pipeline (Contracts -> Runtime -> App Alignment -> E2E). Added 2 new explicit ops items for E2E validation scenarios.
- **v1.5** (2026-02-26): Promoted P2 #1 (Tree API) and P2 #2 (Metadata DTO) to WF-0033. Renumbered P2.
