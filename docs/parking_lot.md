<!-- docs/parking_lot.md -->
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
- **Traceability**: include a `Ref:` to the origin artifact/chat/commit (e.g., `Ref: WF-0035 brainstorm`, `Ref: docs/...`, `Ref: branch ...; commit ...`) when applicable.
- **Date**: when parked (YYYY-MM-DD).

### Chat Hygiene (Meta Rules)

- When suggesting next actions in chat, include a recommendation and a brief rationale so the user can choose quickly.
- If continuing work would benefit from a fresh chat (context bloat, switching WFs/branches, or a runner expecting a clean session), stop and explicitly tell the user to start a new chat and provide an exact copy-paste prompt.

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

### WF Log Rule (Mandatory)

Maintain a single sequential WF log table in this file (all `WF-xxxx` IDs known to the project), and mark origin for each row as:
- `promoted` (from P0/P1/P2 with reference), or
- `started-directly` (not promoted from parking lot).

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
| 1 | Universal Form: nested/hierarchical submit support | product | Merge the still-open nested-call gap into one item: remove the current nested-node block in universal submit, render hierarchical parent/child sections safely, and stop preserving a duplicate “recursive UI” placeholder plus an ERC symptom-only duplicate. (Ref: WF-0035 Phase 0.2 risk audit Q1; user report 2026-03-02; current unsupported state in `UniversalSubmitForm`.) | 2026-02-22 |
| 2 | Cross-call contract hardening for base review semantics | tech-debt | Extend deterministic cross-call coverage beyond the current proof set and add explicit `QUOTA_EXCEEDED` / `REVIEWS_DISABLED` assertions so universal review behavior is proven before broader onboarding. Keep this focused on real contract gaps, not another planning-only hardening pass. (Ref: `next move` follow-up after WF-0038/0039/0040/0041/0043, 2026-03-02.) | 2026-03-02 |
| 3 | Expand coverage to the remaining promised call gap | product | Real call coverage now exists for NWO, ERC, and MSCA. Rewrite the old “ingest real call data” placeholder into the real remaining gap: add at least one credible ZonMw or equivalent missing promised-program call only after P1 #1-#2 are handled or explicitly bundled. (Ref: WF-0037, WF-0044, WF-0061, WF-0062, backlog audit 2026-03-08.) | 2026-02-16 |
| 4 | Add Terms of Service + upgrade Privacy | legal | Add `/terms` page; expand `/privacy` beyond 3 bullets; add inline retention reminder near submit button. | 2026-02-16 |
| 5 | NWO Veni 2025 preproposal — WF-7: Assisted extraction (paste-only) preview+confidence+confirm | product | Optional extraction UX that requires explicit confirmation before evaluation; avoid silent misrouting. (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 6 | Add node hierarchy selector | product | Implement only after P1 #1-#3 so selector behavior sits on dynamic/call-aware foundations rather than one-off UI logic. | 2026-02-16 |
| 7 | Assisted extraction: add `.docx`/`.pdf` support | idea | Defer file parsing to a dedicated WF (new deps + file handling/security considerations). (Ref: `docs/reference/nwo_veni_2025_preproposal_north_star.md`) | 2026-02-21 |
| 8 | Design optional competitive-analysis extension boundary (out-of-core) | tech-debt | Define extension contract for optional competitive analysis as a separate module with no dependency edge into base review pipeline v1.0 core stages. (Ref: WF-0045 non-goals/deferred, 2026-03-03.) | 2026-03-03 |

### P1 Rationale Snapshot (2026-03-08)

- Current launch blocker is still the mismatch between promised multi-program coverage and incomplete truly universal submit behavior.
- The nested/hierarchical submit gap is the main unresolved product bottleneck; do not hide it behind duplicate backlog rows or more call-authoring churn.
- Cross-call hardening stays ahead of broader onboarding so new calls land on a contract surface that is actually proven across failure modes.
- Broad content expansion should now target the remaining promised-program gap, not re-park already completed ERC/MSCA authoring work.
- Assisted extraction remains valuable but non-blocking for launch baseline; `.docx`/`.pdf` remains deferred due dependency/security scope.

Promotion dependency note:
- If promoting P1 #4, first verify WF-0035 and P1 #1-#3 are done, or bundle them in the same WF with explicit dependency sequencing.
- If promoting P1 #6, first verify WF-0035 and P1 #1-#2 are done (or included in that same WF).

---

## 🟢 P2 — Must-fix before scaling

| # | Task | Type | Recommendation | Date |
|---|------|------|----------------|------|
| 1 | Multi-step Evaluation Gating (ERC Step 1 vs Step 2) | product | The ERC StG evaluates B1 in Step 1, and both B1+B2+Resources in Step 2. We authored the full schema combined. We must build a UX/Execution routing rule engine to conditionally trigger subsets of node evaluations based on the chosen Step. (Ref: WF-0032 Brainstorm Section 3) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-25 |
| 2 | Review prompt revision for V2 expectations structure | product | Revise `build_review_prompt()` to optimally reference V2 `EvaluationCriterion` / `EvaluationElement` fields from updated YAML ingestion. Current prompt functions but isn't tuned for V2. (Ref: WF-0029 brainstorm S4 Q2 note) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 3 | Structured review: `requires_context_from` dependency engine | product | Add `requires_context_from: list[str]` field to YAML `node_expectations` + V2 schema + `NodeExpectation` model + ingestion pipeline. Replaces hardcoded NWO Veni rules with generalized cross-node context resolution. (Ref: WF-0029 brainstorm §9.4, deferred in PRD v0.3) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-22 |
| 4 | Add error monitoring (Sentry) | ops | Zero error tracking in production; blind to LLM timeouts, BFF failures, and client crashes with real users. ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-16 |
| 5 | E2E: Critical Negative Scenarios | ops | Run automated E2E tests for missing mandatory nodes, wrong stages, and policy-blocking content to prove operational readiness. (Ref: Architect Feedback Step 6) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-26 |
| 6 | E2E: Happy-path ERC Sample | ops | Run a full happy-path E2E with a sample ERC proposal text (submit -> process -> cards shown correctly). (Ref: Architect Feedback Step 6) ([Conv: 8c803359-d2c1-4594-aaf6-78da7fd6d305](vscode://cortex-app.antigravity/conversation?id=8c803359-d2c1-4594-aaf6-78da7fd6d305)) | 2026-02-26 |
| 7 | Prompt quality tuning | product | Test AI output quality with real ERC/NWO proposals; tune `PromptTemplate` for actionable, criteria-specific feedback. | 2026-02-16 |
| 8 | Production hardening | ops | Lock CORS, verify rate limiting beyond daily quota, add custom 404 page, tune Vercel/Render timeout alignment. | 2026-02-16 |
| 9 | Structured review: single mega-prompt optimization | product | Replace per-node sequential LLM calls with a single mega-prompt for all nodes — fewer API calls, lower latency. Directly mitigates the 3x latency risk (15-45s) identified in WF-0029 brainstorm S6 Q4. Requires new prompt template + parser. (Ref: WF-0029 brainstorm Q4.2 option B) | 2026-02-22 |
| 10 | Structured review: LLM-generated overall summary | product | After per-node reviews, add an additional LLM call to synthesize a holistic cross-node summary (alignment, strengths, gaps). (Ref: WF-0029 brainstorm Q4.4 option A) | 2026-02-22 |
| 11 | Structured review: parallel per-node LLM calls | product | Fire LLM calls concurrently instead of sequentially — faster wall-clock time but adds rate-limiting and error-handling complexity. May be unnecessary if mega-prompt (P2 #9) is adopted instead. (Ref: WF-0029 brainstorm S4 Q2 option C, S8 Q5) | 2026-02-22 |
| 12 | Structured review: batch submission of multiple proposals | product | Allow submitting multiple proposals or revisions in one request. May not be needed depending on app evolution. (Ref: WF-0029 brainstorm S8 Q5) | 2026-02-22 |
| 13 | Backend async review execution beyond existing detail polling | product | Review detail already polls; the deferred gap is backend async job orchestration and terminal-status handling beyond the current synchronous create path. Keep this framed as backend/runtime work, not as if polling were still missing. (Ref: WF-0029 PRD v0.3 deferral; WF-0017 bounded polling already done.) | 2026-02-22 |
| 14 | Structured review: `StructuredSubmission` aggregate table | tech-debt | Replace JSONB `structured_payload` on Review with a proper normalized aggregate table linking multiple `ProposalSnippet` rows to one Review. Enables per-node audit history and replay. (Ref: WF-0029 brainstorm §9.1 option A, deferred in PRD v0.3) | 2026-02-22 |
| 15 | Structured review: per-node grouped detail endpoint | product | New `/reviews/{id}/structured` endpoint returning `nodes[].cards[]` grouped response. Current MVP uses flat `cards[]` from existing detail endpoint. (Ref: WF-0029 PRD v0.3 deferral) | 2026-02-22 |
| 16 | Assisted extraction via document upload (.docx / .pdf) | product | Use a service like MarkItDown or an MCP tool to parse uploaded documents and auto-populate the structured UI inputs (reducing copy-paste friction with tables/images). (Ref: WF-0030 S1 Q2) | 2026-02-22 |
| 17 | Machine validation of page-based constraints (`max_pages`) | product | `max_pages` is currently authored merely as a UI signaling field. Since the MVP uses plain text strings rather than PDF uploads, we cannot physically count pages. Add a rough heuristic (e.g., 1 page = 4000 chars) or PDF parsing to strictly enforce this in the backend. (Ref: WF-0032 Brainstorm Section 6) | 2026-02-25 |
| 18 | Deprecate `POST /reviews` (migrate to structured-only create flow) | tech-debt | Follow-on WF: make `POST /api/structured-review` support single-node UX cleanly (idempotency + persistence + errors), migrate frontend/BFF, then deprecate `POST /reviews` with a compatibility window. (Ref: WF-0034 Phase 0.1 chat: [WF-0034-phase-0-1](chats/wf/WF-0034-phase-0-1.md), 2026-02-26; branch `wf/WF-0034-unify-review-execution-core`; commit `a53843a`.) | 2026-02-26 |
| 19 | Universal Form: Markdown / rich-text inputs per node | idea | MVP is plain text only. Follow-on: support Markdown or rich text per node (copy-paste with basic formatting) without breaking compliance counting and backend normalization. (Ref: WF-0035 brainstorm Q3 in Target User / Actor.) | 2026-02-26 |
| 20 | Universal Form: Unify legacy single-snippet mode | idea | Follow-on: fold `legacy_single_snippet` calls into the same universal submit experience (selection + UX) without breaking current behavior; keep structured-node and legacy semantics explicit. (Ref: WF-0035 brainstorm MVP Definition Q5.) | 2026-02-26 |
| 21 | Call onboarding: DB/API preflight for new call YAMLs | ops | Standardize a smoke-test checklist after ingesting a new call into DB (`/calls`, `/calls/{id}/nodes`, `/public config`, `/nodes/metadata`) to catch mapping/shape issues before frontend work. (Ref: WF-0037 brainstorm v0.1, Q1.) | 2026-02-27 |
| 22 | Call YAML: domain/pilot variants scaffolding | idea | Don’t invent `domain_id` branching unless the official call defines it; follow-on: define a universal pattern for when/how to introduce domain selection and per-domain constraints. (Ref: WF-0037 brainstorm v0.2 Section 3 Q3.) | 2026-02-27 |
| 23 | Compliance UX: “informational-only constraints” mode | idea | Add a way to surface constraints (fonts/margins/page layout etc.) in compliance check output as informational guidance without pretending they’re enforceable/deterministic. (Ref: WF-0037 brainstorm v0.3 Section 4 Q5; user request in chat.) | 2026-02-27 |
| 24 | Call YAML schema: separate evaluable vs non-evaluable guidance fields | idea | Add explicit fields to keep “evaluation-tied guidance” separate from “helpful but non-evaluable explanatory notes”, so prompts can stay honest while still helping applicants. (Ref: WF-0037 brainstorm v0.4 Section 5 Q2; user request in chat.) | 2026-02-27 |
| 25 | Universal Form: add backend structured-calls listing/filter endpoint | tech-debt | Replace frontend N+1 config gating with one backend-filtered list (e.g., `ui_mode=structured_nodes`) only after WF-0035 ships; keeps current WF scoped to existing APIs while reducing latency/failure fanout later. (Ref: WF-0035 brainstorm “Post-WF-0032..WF-0037 Reality Check” Q3 selected A; WF-0035 PRD v0.2 FR16/C1.) | 2026-02-28 |
| 26 | Universal Form: canonical domain-options contract for UI | product | Remove interim per-call frontend domain-options mapping by adding source-grounded domain options to the canonical call-definition/public metadata/config contract. (Ref: WF-0035 brainstorm “Post-WF-0032..WF-0037 Reality Check” Q1 selected A; AD 35.4 in `docs/logs/decisions.md`.) | 2026-02-28 |
| 27 | Universal Form: large-form navigation for >10 nodes | product | Add section navigation/stepper/TOC patterns for larger flat calls once MVP universality is stable; avoid bundling this UX expansion into WF-0035’s 3-10 node target. (Ref: WF-0035 brainstorm “Target User / Actor” Q5 selected A; PRD v0.2 Target scope.) | 2026-02-28 |
| 28 | Universal Submit: split orchestration into dedicated hooks/modules | tech-debt | Defer large `UniversalSubmitForm` decomposition into focused hooks (`gating`, `render-model`, `submit orchestration`, `draft persistence`) to a new WF to reduce regression risk post-WF-0035 ship gate. (Ref: WF-0035 adversarial audit follow-up, branch `wf/WF-0035-universal-form-dynamic-ui-renderer`.) | 2026-02-28 |
| 29 | Surface `DiagnosticFinding v1` directly in UI/API (deprecate `ReviewCard` adapter) | idea | Follow-on to WF-0038: make `DiagnosticFinding v1` the externally consumed contract (UI/API/analytics) and retire `DiagnosticFinding v1 -> ReviewCard` compatibility mapping after a transition window. (Ref: WF-0038 PRD v0.2 + AD 38.15.) | 2026-02-28 |
| 30 | Universal review: explicit supporting-context contract beyond WF-0063 MVP | product | Do not promote for launch-baseline work. Promote only after the split contract is proven beyond the MSCA proof call and after cross-call hardening is complete, because this changes semantics, not just visibility. WF should explicitly define: which supporting nodes may influence primary review, whether context is opt-in or automatic, request/persistence boundaries, fail-closed validation, prompt/runtime behavior, and review-detail/user-facing labels proving when supporting content was visible vs primary-reviewed vs context-used. Trigger to promote: once current launch-critical submit/review contract work is done and we have a concrete product answer to “what exactly may supporting content influence?” If that answer is still vague, keep parked. (Ref: `docs/brainstorms/brainstorm-WF-0063-universal-node-visibility-reviewability.md` §9, `docs/prds/prd-WF-0063-universal-node-visibility-reviewability.md` DS1/DS3/FR9/FR11/FR12, WF-0063 closure clarification chat 2026-03-08.) | 2026-03-08 |

## Rejected / Ignored

| Task | Status | Rationale | Date |
|---|---|---|---|
| Adopt Ralph-style fresh-context execution | Ignored | User rejected this because forcing manual chat/window swapping and repeated copy-paste prompts adds overhead and breaks flow. Keep out of the active numbered backlog. (Ref: WF-0046 deferral.) | 2026-03-04 |

---

## WF Initiative Log (All WF IDs)

Note: `Backlog Ref At Promotion` is a historical snapshot of the parking-lot slot used when that WF was promoted. It is provenance only, not a promise that the same numbered slot still exists or means the same thing today.

| Seq | WF ID | Slug / Initiative | Origin | Backlog Ref At Promotion | Date |
|---|---|---|---|---|---|
| 1 | WF-0009 | peerlens-landing-page | started-directly | - | unknown |
| 2 | WF-0010 | peerlens-landing-design-refresh | started-directly | - | unknown |
| 3 | WF-0011 | local-postgres-dev-db | started-directly | - | unknown |
| 4 | WF-0012 | alembic-migration-baseline | started-directly | - | unknown |
| 5 | WF-0013 | app-shell-signout | promoted | P0 #1 (historical) | 2026-02-16 |
| 6 | WF-0014 | review-history | promoted | P0 #2 (historical) | 2026-02-16 |
| 7 | WF-0015 | practices-upgrade | promoted | P1 #3 (historical) | 2026-02-17 |
| 8 | WF-0016 | review-results-ux | promoted | P0 #4 (historical) | 2026-02-17 |
| 9 | WF-0017 | auto-polling-processing-reviews | promoted | P0 #5 (historical) | 2026-02-18 |
| 10 | WF-0018 | harden-submit-flow-ux | promoted | P0 #6 (historical) | 2026-02-18 |
| 11 | WF-0019 | add-loading-empty-states | promoted | P1 #7 (historical) | 2026-02-18 |
| 12 | WF-0020 | nwo-veni-2025-preproposal-wf1 | promoted | P1 #8 (historical) | 2026-02-21 |
| 13 | WF-0021 | nwo-veni-2025-preproposal-wf2 | promoted | P1 #9 (historical) | 2026-02-21 |
| 14 | WF-0023 | tier2-phase4 | started-directly | - | unknown |
| 15 | WF-0024 | tier3-refactor | started-directly | - | unknown |
| 16 | WF-0025 | archiving-convention | started-directly | - | unknown |
| 17 | WF-0026 | sdlc-4-phase-refactor | started-directly | - | unknown |
| 18 | WF-0027 | nwo-veni-2025-preproposal-wf3 | promoted | P1 #10 (historical) | 2026-02-21 |
| 19 | WF-0028 | compliance-engine | promoted | P1 #11 (historical) | 2026-02-22 |
| 20 | WF-0029 | nwo-veni-2025-preproposal-wf5-structured-review | promoted | P1 #12 (historical) | 2026-02-22 |
| 21 | WF-0030 | nwo-veni-2025-preproposal-wf6-frontend-structured-form | promoted | P1 #13 (historical) | 2026-02-22 |
| 22 | WF-0031 | accessibility-pass | promoted | P1 #14 (historical) | 2026-02-25 |
| 23 | WF-0032 | erc-2026-stg | started-directly | - | 2026-02-26 |
| 24 | WF-0033 | data-contract-foundation | promoted | P2 #15 (historical) | 2026-02-26 |
| 25 | WF-0034 | unify-review-execution-core | promoted | P2 #16 (historical) | 2026-02-26 |
| 26 | WF-0035 | universal-form-dynamic-ui-renderer | promoted | P1 #1 (historical) | 2026-02-26 |
| 27 | WF-0036 | nwo-veni-2025-preproposal-yaml-reauthor | promoted | P1 #9 (historical) | 2026-02-26 |
| 28 | WF-0037 | nwo-vidi-2025-full-proposal-yaml-reauthor | started-directly | - | 2026-02-27 |
| 29 | WF-0038 | peerlens-review-engine-pipeline-v1 | started-directly | - | 2026-02-28 |
| 30 | WF-0039 | structured-pipeline-v1-rollout | started-directly | - | 2026-03-01 |
| 31 | WF-0040 | structured-pipeline-v1-legacy-retirement | promoted | P1 #10 (historical) | 2026-03-01 |
| 32 | WF-0041 | nwo-veni-2025-preproposal-single-call-mvp | promoted | P0 #1 (historical) | 2026-03-01 |
| 33 | WF-0042 | agent-memory-system | started-directly | - | 2026-03-01 |
| 34 | WF-0043 | nwo-veni-2025-preproposal-single-call-mvp-harden | promoted | P0 #1 (historical) | 2026-03-01 |
| 35 | WF-0045 | base-review-pipeline-v1-call-agnostic | promoted | P1 #15 (historical same-day park/pick; numbering later reused) | 2026-03-03 |
| 36 | WF-0046 | agent-instruction-optimization | started-directly | - | 2026-03-04 |
| 37 | WF-0047 | git-hooks-rule-enforcement | promoted | P2 #31 (historical) | 2026-03-04 |
| 38 | WF-0048 | agency-call-variability-policy | promoted | P1 #15 (historical) | 2026-03-04 |
| 39 | WF-0057 | ops-evidence-debt-closure | promoted | P1 #10 (historical) | 2026-03-06 |
| 40 | WF-0062 | erc-cog-2026-contract-model-correction | started-directly | - | 2026-03-07 |

---

## Revision History

Note: backlog slot references inside revision-history entries (for example `P1 #10`) describe the numbering that existed at the time of that edit. They are historical snapshots, not guaranteed matches to the current active tables.

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
- **v1.6** (2026-02-26): Promoted P2 #1 (Unify review service execution core) to WF-0034. Renumbered P2.
- **v1.7** (2026-02-26): Parked follow-on item to eventually deprecate `POST /reviews` after migrating to structured-only create flow. (Ref: WF-0034.)
- **v1.8** (2026-02-26): Reordered priorities for safer launch sequencing after WF-0032/0033/0034: pulled frontend call-agnostic prerequisites + ERC CoG source re-authoring into P1 ahead of broad data ingestion; renumbered P2 accordingly.
- **v1.9** (2026-02-26): Replaced `Promoted Items` with a unified WF initiative log table (all known WF IDs), explicitly marking each as `promoted` or `started-directly`; added missing WF-0032 as started-directly.
- **v2.0** (2026-02-28): Parked WF-0035 scope-creep follow-ons: backend structured-call filter endpoint, canonical domain-options contract, and large-form navigation UX.
- **v2.1** (2026-02-28): Parked deferred WF-0035 follow-up for `UniversalSubmitForm` structural decomposition into dedicated hooks/modules.
- **v2.2** (2026-02-28): Parked explicit follow-up to migrate `backend/data/calls/legacy/erc/erc_cog_2026_full_official.yaml` from legacy v1 shape to v2 WF-0038-native call-definition format.
- **v3.4** (2026-03-08): Parked WF-0063 scope-creep follow-up for an explicit supporting-context contract beyond the proof-call MVP, with traceability back to the brainstorm/PRD and architect recommendation.
- **v2.3** (2026-03-01): Added P1 #10 for legacy structured-review engine retirement after pipeline-v1 rollout and backfilled WF initiative log with WF-0037/WF-0038 plus new WF-0039.
- **v2.4** (2026-03-01): Promoted P1 #10 to WF-0040 (`structured-pipeline-v1-legacy-retirement`) and removed it from active P1 backlog.
- **v2.5** (2026-03-01): Added P1 #10 follow-up to backfill WF-0040 runtime evidence after waiver-based closure.
- **v2.6** (2026-03-01): Promoted P0 #1 to WF-0043 (`nwo-veni-2025-preproposal-single-call-mvp-harden`) and removed it from active P0 backlog.
- **v2.7** (2026-03-02): Added P1 #11 for cross-call deterministic contract hardening of pipeline-v1 (`QUOTA_EXCEEDED`/`REVIEWS_DISABLED` included).
- **v2.8** (2026-03-02): Added P1 #12 for source-grounded, per-call upload-gated re-authoring of `erc_cog_2026_full`, `nwo_vidi_2025_full_proposal`, and `erc_stg_2026_full`.
- **v2.9** (2026-03-02): Refined P1 #12 to explicitly encode primary target + validation baseline + mandatory per-call source upload gates; added P1 #13 for separately parked optional non-NWO expansion (MSCA first, ZonMw follow-up).
- **v3.0** (2026-03-03): Parked then immediately promoted a new P1 item to `WF-0045` — “Base Review Pipeline v1.0 (call-agnostic): structural validation, compliance gate, expectation-level evaluation, cross-node alignment, risk audit, output aggregation; optional competitive analysis kept out of core.”
- **v3.1** (2026-03-03): Parked two critical deferred follow-ups from WF-0045 Phase 0.1: agency/call-specific variability policy definition and optional competitive-analysis extension boundary design.
- **v3.2** (2026-03-03): Clarified WF-0045 initiative-log backlog reference as historical to avoid confusion with later reused active P1 numbering.
- **v3.3** (2026-03-04): Appended deferred improvements from WF-0046 brainstorm to P2 tracking (hooks-based rule enforcement and Ralph-style zero-context loops).
- **v3.5** (2026-03-08): Backlog audit cleanup removed already-implemented items (Alembic baseline, review-detail hardcoded mapping, completed ERC CoG/MSCA expansion placeholders), merged duplicate nested-submit items, rewrote stale coverage/async entries to match current repo reality, and moved the rejected fresh-context idea out of the active priority table.
- **v3.6** (2026-03-08): Second-pass WF initiative log wording audit renamed the backlog-reference column to historical promotion provenance, added an explicit note, and normalized promoted rows to mark backlog refs as historical snapshots rather than live active-slot references.
- **v3.7** (2026-03-08): Strengthened P2 #30 with explicit promotion timing and gating: treat supporting-context semantics as post-launch-baseline work only, after multi-call proof and cross-call hardening, and only when product semantics are concrete enough to specify influence boundaries honestly.
