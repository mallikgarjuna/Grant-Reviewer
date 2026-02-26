# WF-0035 — Universal Form: Dynamic UI renderer

Artifact: brainstorm
Version: v0.4
Status: Draft
Last Updated: 2026-02-26

---

## Preflight Intake (Interactive)

Initial decisions to anchor the brainstorm:

- Primary actor: Researchers submitting proposal content.
- Current pain: UI is hardcoded to a single call/program so newly ingested calls cannot be submitted.
- Dynamic renderer input: backend-provided UI schema/DTO.
- MVP scope: flat fields + simple sections only (no nested/recursive structures).
- "Done" acceptance: any ingested call renders without code changes, user can submit, backend receives structurally valid payload.

**Brainstorming Q&A:**

**Q1: Who is the primary actor for this “universal form” MVP?**
- A) Applicants (researchers) submitting proposal content.
- B) Internal admins configuring calls/forms.
- C) Both equally.
> Recommendation: A — This is the launch-critical UX implied by P1 #1 (unblocks end-user submissions for multiple calls). B/C expand scope into admin tooling.
> **Selected: A**

**Q2: What is the current “call-specific” behavior you want to remove (most painful symptom)?**
- A) UI is hardcoded to a single call/program (field list + labels), so new ingested calls cannot be submitted.
- B) UI can render fields, but routing/mapping to backend payload is hardcoded per call.
- C) UI and backend both assume one call; multiple calls break selection/loading.
> Recommendation: A — This is the clearest falsifiable problem statement and directly connects to launch readiness. B/C may still be true but are second-order.
> **Selected: A**

**Q3: What should the dynamic renderer take as its input “form definition” (source of truth)?**
- A) Backend-provided UI schema/DTO (already shaped for the frontend).
- B) Raw call definition structure (frontend interprets the call schema directly).
- C) A hybrid: backend provides structure, frontend enriches (labels/help/order).
> Recommendation: A — Keeps frontend simpler and avoids parsing raw canonical JSON; aligns with existing backend DTO direction (e.g., metadata endpoints).
> **Selected: A**

**Q4: What is the MVP rendering scope for WF-0035 (leave recursion for P1 #2 unless overridden)?**
- A) Flat fields + simple sections only (no nested/recursive structures).
- B) Flat + one level of grouping (accordions/sections), but no arbitrary-depth recursion.
- C) Full nested recursion (trees/arrays/objects) in this WF.
> Recommendation: A — Matches the current launch blocker and defers recursion risk into P1 #2 as intended.
> **Selected: A**

**Q5: What does “done” look like for this WF (single acceptance scenario)?**
- A) Pick any ingested call in UI, the form renders without code changes, user can submit, and backend receives a structurally valid payload.
- B) Form renders dynamically, but submission can still be blocked/manual.
- C) Rendering parity only (looks right), payload correctness can come later.
> Recommendation: A — Rendering without submit is a demo, not a product; this WF should close the loop to a valid backend payload.
> **Selected: A**

---

## Repo Reality Snapshot (Read-Only) (2026-02-26)

- Frontend submit UI is currently call-specific: `VeniSubmitForm` hardcodes `VENI_CALL_CODE = "nwo_veni_2025_preproposal"` and 3 fixed node logical IDs (`academic_profile`, `key_outputs`, `research_idea`).
- The submit page currently filters `/api/bff/calls` to only show Veni calls, then submits to `/api/bff/check-compliance` and `/api/bff/structured-review`.
- Backend already exposes call-aware primitives needed by a universal renderer:
  - `GET /calls` (active calls)
  - `GET /api/public/calls/{call_logical_id}/config` (mode gating + `expected_nodes`)
  - `GET /calls/{call_id}/nodes?view=tree` (flat/tree)
  - `GET /api/public/calls/{call_logical_id}/nodes/metadata` (UI-oriented metadata by `logical_id`)
- The repo has explicit prior decisions to fail-fast on nested nodes for MVP universal rendering, rather than rendering broken UI (see decisions log).
- There are already frontend tests asserting the current behavior is a “hardcoded Veni structured form shell”.

Open questions suggested by the snapshot:

- Should WF-0035 replace `VeniSubmitForm` with a universal form component (retire Veni-only route), or keep Veni as a “legacy special-case” behind gating?
- Which backend DTO is the renderer’s primary contract: `nodes?view=tree` vs `public nodes/metadata`, and what minimum UI schema must be assembled client-side?
- What should be the failure UX when a selected call is structured but has nested nodes (explicit unsupported blocking state vs silent flattening)?
- How should call selection work for non-Veni calls (dropdown of all calls vs only “structured_nodes” calls)?

## Contract Notes (Implementation Guardrails)

- `GET /api/bff/calls` returns `{ id, code, name, ... }` where:
  - `id` is the UUID used for `GET /calls/{call_id}/nodes` and for submitting reviews.
  - `code` is the `call_logical_id` used for `GET /api/public/calls/{call_logical_id}/config` and `GET /api/public/calls/{call_logical_id}/nodes/metadata`.
- **Ordering SSOT**: `GET /calls/{call_id}/nodes?view=flat` (DB `order_index`).
- **Label/constraints SSOT**: `GET /api/public/calls/{call_logical_id}/nodes/metadata`.
- **Submission SSOT**: use `node_logical_id` from metadata (do not infer from titles).

---

## 1. Problem Statement

Researchers cannot submit non-Veni structured calls because the submit UI is hardcoded to Veni's 3 fields. WF-0035 targets the smallest universal renderer that supports any *structured* call with a flat (non-nested) node list: render N textareas, allow partial submission (at least one filled node), and fail-fast with a clear blocking message for nested calls (recursive rendering deferred to P1 #1).

**Brainstorming Q&A:**

**Q1: What is the concrete user-visible failure today?**
- A) Non-Veni calls cannot be submitted because the form only renders Veni’s 3 fields.
- B) Non-Veni calls appear, but submitting fails (API mismatch/errors).
- C) Calls load inconsistently; user can’t reliably select a call.
> Recommendation: A — This is the top-level product failure described in P1 #1 and is directly falsifiable in the UI.
> **Selected: A**

**Q2: What is the “minimal universality” we’re targeting in WF-0035?**
- A) Any structured call with a flat node list (no nesting) renders N textareas.
- B) Only 2–3 known calls (Veni + 1–2 more) render dynamically.
- C) Any call at all (including legacy single-snippet) renders via one universal component.
> Recommendation: A — Keeps scope tightly aligned to the launch blocker while avoiding legacy-mode entanglement; recursion is explicitly deferred.
> **Selected: A**

**Q3: What should the form do with nodes that are “expected” but the user leaves empty?**
- A) Allow partial submission (at least one node), and only evaluate submitted nodes.
- B) Hard-require all expected nodes before submit.
- C) Make it configurable per call (more complex).
> Recommendation: A — Matches current UX behavior and reduces the risk of blocking users when some sections are legitimately not applicable.
> **Selected: A**

**Q4: What’s the MVP behavior for nested nodes (since recursion is deferred)?**
- A) Fail-fast with a clear blocking message: “This call isn’t supported yet (nested sections)”.
- B) Flatten nested nodes into a single list anyway.
- C) Hide nested nodes and allow partial rendering.
> Recommendation: A — Prevents silent data loss or misleading UI; recursive rendering is already tracked as a separate backlog item (P1 #1).
> **Selected: A**

**Q5: What is the success metric for Phase 0 clarity (not implementation)?**
- A) We can write an unambiguous MVP statement + explicit non-goals that prevent scope creep.
- B) We can list every component we’ll build.
- C) We have UI mockups.
> Recommendation: A — Phase 0 should be decision-tight, not architecture-heavy.
> **Selected: A**

## 2. Desired Outcome

WF-0035 ships a single universal submit experience: user selects any structured call (flat nodes only), the UI dynamically renders N textareas, performs minimal client-side validation (at least one section + word counters), relies on backend compliance checks for enforceable rules, and hard-blocks unsupported nested calls with a clear message. Recursive rendering is explicitly deferred to the parked backlog item: `P1 #1 Universal Form: Recursive UI components for nested schemas`.

**Brainstorming Q&A:**

**Q1: What’s the primary “ship outcome” for WF-0035?**
- A) A single submit route renders dynamic N-node textareas for any flat structured call and can submit successfully.
- B) Backend adds a new UI-schema endpoint; frontend stays mostly the same.
- C) Only refactor Veni form internals; no multi-call support yet.
> Recommendation: A — This closes the user loop and removes call-specific UI, which is the core P1 #1 (promoted) launch blocker.
> **Selected: A**

**Q2: What is the minimal call selection behavior?**
- A) Dropdown lists all calls with `ui_mode="structured_nodes"` (from `GET /api/public/calls/{code}/config`), not just Veni.
- B) Dropdown lists all calls (including legacy), but legacy routes elsewhere.
- C) Keep Veni-only dropdown; add a hidden query-param for other calls.
> Recommendation: A — Keeps selection aligned to structured-mode calls and avoids legacy-path complexity in this WF.
> **Selected: A**

**Q3: What is the minimal “schema/DTO” the frontend uses to render the form?**
- A) `GET /calls/{call_id}/nodes?view=flat` for node list + `GET /api/public/calls/{code}/nodes/metadata` for labels/constraints.
- B) A new single “form schema” endpoint purpose-built for UI.
- C) Only `nodes/metadata` (ignore DB nodes list).
> Recommendation: A — Uses existing endpoints and keeps contract changes out of this WF’s MVP ideation.
> **Selected: A**

**Q4: What is the MVP validation UX (client-side) before submit?**
- A) Only “at least one section required” + basic per-field word counters; rely on `/api/bff/check-compliance` for real enforcement.
- B) Enforce “expected nodes must be filled” client-side.
- C) No validation at all; submit and show backend errors.
> Recommendation: A — Avoids duplicating enforceable rules on the client; keeps client UX helpful but not authoritative.
> **Selected: A**

**Q5: What is “good enough” error handling for unsupported calls?**
- A) Clear blocking banner: “This call has nested sections and is not supported yet” + link to tracked deferred work.
- B) Try to flatten and warn.
- C) Hide the call from selection entirely.
> Recommendation: A — Transparent and safe; avoids silent corruption and preserves user trust.
> **Selected: A**

## 3. Target User / Actor

Primary user is a researcher actively preparing a submission and iterating over multiple sessions. The dominant behavior is copy-pasting text blocks from an existing document into multiple node fields. MVP supports plain text only (no tables/images), optimized for speed of pasting and minimal friction. Expected flat-structured calls are roughly 3–10 nodes; larger call navigation is out of scope for this WF.

**Brainstorming Q&A:**

**Q1: What stage is the primary user in when they hit this form?**
- A) Actively preparing a submission, iterating multiple times.
- B) One-shot “paste and run” to sanity-check quickly.
- C) Admin/ops verifying ingestion correctness.
> Recommendation: A — This aligns with the need for draft persistence and repeated edits; it also matches the current localStorage draft pattern in the repo.
> **Selected: A**

**Q2: What is the dominant user behavior for filling nodes?**
- A) Copy-paste text blocks from an existing document into multiple fields.
- B) Type directly into the UI as their primary editor.
- C) A mix, but mostly typing.
> Recommendation: A — Optimizing for paste-first reduces friction and maps to the current “plain text paste” disclaimer UX.
> **Selected: A**

**Q3: What is the minimum supported content type per node for MVP?**
- A) Plain text only (no tables/images), with explicit upfront disclaimer.
- B) Markdown allowed (basic formatting).
- C) Rich text editor (WYSIWYG).
> Recommendation: A — Keeps compliance counting and backend normalization deterministic. Defer Markdown/rich text to a parked follow-on item to avoid silent mismatches.
> **Selected: A**

**Q4: What should the UI optimize for: speed vs guidance?**
- A) Speed: fast paste, clear labels, minimal friction.
- B) Guidance: lots of inline instructions, constraints, and helper text.
- C) Balanced.
> Recommendation: A — This is the lowest-risk MVP for launch-readiness; deeper guidance can be layered in later via metadata DTOs.
> **Selected: A**

**Q5: What is the expected number of nodes for “flat structured calls” we must handle in MVP?**
- A) 3–10 nodes (typical).
- B) 10–30 nodes (needs heavier navigation).
- C) 30+ nodes (needs wizard/steps).
> Recommendation: A — Fits a single-page form without introducing navigational architecture; larger calls will be blocked until recursion/navigation work exists.
> **Selected: A**

## 4. Rough Idea (Unstructured Thinking)

Replace the hardcoded Veni form with a universal submit form used by the existing submit route. The universal form builds a list of eligible calls by gating on `ui_mode="structured_nodes"`, then builds a flat render model from existing backend endpoints (`nodes?view=flat` + public `nodes/metadata`). Draft persistence is isolated per selected call. Compliance UX remains unchanged (local counters + backend check-compliance + warning bypass modal).

**Brainstorming Q&A:**

**Q1: What is the simplest frontend shape for the universal form?**
- A) Replace `VeniSubmitForm` with a `UniversalSubmitForm` used by `/app/app/page.tsx`.
- B) Keep `VeniSubmitForm` and add a separate `/app/universal` route.
- C) Keep Veni as default, add universal form only when non-Veni selected.
> Recommendation: A — Eliminates call-specific UI at the root and prevents a long-lived parallel “universal” route that will drift.
> **Selected: A**

**Q2: How should the form build the list of eligible calls?**
- A) Fetch all calls (`/api/bff/calls`), then for each call code check `/api/public/calls/{code}/config` and include only `ui_mode="structured_nodes"`.
- B) Backend adds a “structured_only” filter to `/calls` to avoid N+1 calls.
- C) Hardcode a list of supported call codes in frontend.
> Recommendation: A — Correctness first for MVP ideation; contract optimization (B) can be tackled later if N+1 becomes problematic.
> **Selected: A**

**Q3: How should the form build the render model for flat nodes?**
- A) `GET /calls/{call_id}/nodes?view=flat` for node IDs + `GET /api/public/calls/{code}/nodes/metadata` for labels/constraints; render in the returned ordering.
- B) Only call `nodes?view=tree` and flatten client-side.
- C) Only call metadata and ignore DB nodes list.
> Recommendation: A — Uses existing contracts and keeps the UI aligned with DB node identity while pulling UI text/constraints from metadata DTOs.
> **Selected: A**

**Q4: What should draft persistence key off of?**
- A) Key drafts by `call_id` (UUID) so switching calls never overwrites drafts.
- B) Key drafts by `call code` (logical id) for portability across environments.
- C) One shared draft across all calls.
> Recommendation: A — Safest for in-app UX; prevents accidental cross-call draft collisions.
> **Selected: A**

**Q5: What should happen to compliance checking UX in the universal form?**
- A) Keep the existing flow: local word counters + `/api/bff/check-compliance` before submit + bypass modal for warnings.
- B) Remove client-side counters; backend-only.
- C) Skip compliance check for MVP; submit directly.
> Recommendation: A — Preserves current UX and the backend enforcement model; avoids surprising regressions during universalization.
> **Selected: A**

## 5. Constraints

Implementation timebox is 2–3 days for a tight MVP. Prefer no new backend endpoints (use existing contracts); frontend should keep UX close to the current submit page, but minor improvements are acceptable if they reduce confusion or support call selection. Call coverage is explicitly limited to structured calls with flat nodes; nested calls must hard-block. Draft persistence remains localStorage per call; no server-side drafts.

**Brainstorming Q&A:**

**Q1: What is the time constraint for WF-0035 implementation (once we leave ideation)?**
- A) 2–3 days (tight MVP).
- B) 1 week.
- C) Open-ended.
> Recommendation: A — Matches the urgency of the P1 launch blocker and forces aggressive scope discipline.
> **Selected: A**

**Q2: What is the hard backend constraint for this WF?**
- A) No new backend endpoints; use existing contracts only.
- B) Small backend tweaks allowed if they reduce frontend complexity.
- C) Backend refactor is allowed.
> Recommendation: A — Keeps this WF focused on frontend universalization; the repo already has usable endpoints for nodes/config/metadata.
> **Selected: A**

**Q3: What is the hard frontend constraint?**
- A) Keep UX similar to current submit page; avoid redesign.
- B) Redesign is acceptable if it speeds universalization.
- C) Any UI is fine; correctness only.
> Recommendation: A — Minimizes regression risk. Allow small, targeted UX tweaks (e.g., call selection and clearer unsupported-call messaging) without a full redesign.
> **Selected: A (with small, targeted UX tweaks allowed)**

**Q4: What is the constraint on call coverage for MVP?**
- A) Only structured calls with flat nodes; nested calls must hard-block.
- B) Must include at least one nested call (partial support).
- C) Must include legacy single-snippet calls too.
> Recommendation: A — Preserves the explicit deferral boundary; nested support is a separate parked initiative.
> **Selected: A**

**Q5: What is the constraint on persistence/drafts?**
- A) localStorage draft per call is sufficient; no server drafts.
- B) Must persist drafts server-side.
- C) No drafts needed.
> Recommendation: A — Matches current behavior and is sufficient for MVP paste/iterate workflows.
> **Selected: A**

## Flat-Only Definition (MVP Guardrail)

For WF-0035, a call is **flat-supported** iff **every** node returned by `GET /calls/{call_id}/nodes` has `parent_node_id == null`.

If any node has `parent_node_id != null`, the UI must hard-block the call with an explicit message:

> Nested calls are not supported yet (recursive rendering deferred).

Rationale: prevents shipping partial/incorrect nested rendering and keeps recursion work isolated.

## 6. Risks / Unknowns

Primary risks are contract ambiguity (which DTOs/fields are truly required for reliable labels/constraints), and silent corruption (a form that renders but submits structurally wrong payloads). Mitigation is to render with safe fallbacks when metadata is missing (label defaults to `logical_id`, hide constraints, show warning banner) and to validate a non-Veni structured call round-trip early before frontend work expands.

**Brainstorming Q&A:**

**Q1: What is the riskiest unknown for WF-0035?**
- A) Frontend contract ambiguity: what exact DTOs/fields are required to render labels/constraints reliably.
- B) Performance: N+1 call gating (`config` per call) becomes slow.
- C) Compliance UX drift: counters/checks differ between client and server.
> Recommendation: A — If the UI can’t trust labels/constraints, we’ll either hardcode (defeating universality) or ship confusing UX.
> **Selected: A**

**Q2: What is the biggest failure mode we must prevent?**
- A) Rendering a form that looks valid but submits a structurally wrong payload (silent corruption).
- B) The form fails to load sometimes.
- C) The form is ugly.
> Recommendation: A — Silent wrong submissions waste LLM tokens and erode trust; load/visual issues are visible and easier to catch.
> **Selected: A**

**Q3: What should we do if metadata is missing/incomplete for a node?**
- A) Render with safe fallbacks (label = logical_id, constraints hidden) and show a warning banner.
- B) Hard-block the call as unsupported.
- C) Hide the node.
> Recommendation: A — Keeps the app usable while making the missing-data issue explicit; avoids data loss (C) and over-blocking (B).
> **Selected: A**

**Q4: What’s the biggest scope-creep temptation to explicitly guard against?**
- A) “Just add recursion/navigation” for ERC-like calls inside WF-0035.
- B) “Just support Markdown/rich text now.”
- C) “Just redesign the whole submit UX.”
> Recommendation: A — Recursion is the highest-risk expansion and is already tracked as a separate launch prerequisite item (P1 #1).
> **Selected: A**

**Q5: What must we validate early to avoid rework?**
- A) One non-Veni flat structured call exists in DB and can round-trip submit with expected node IDs.
- B) UI polish.
- C) Performance tuning.
> Recommendation: A — Validates the true end-to-end premise (schema-driven rendering + submission) before investing in UI layering.
> **Selected: A**

## 7. MVP Definition

MVP is a universal, schema-driven submit form that supports any structured call with a flat node list (no nesting): dynamically render N plain-text inputs, run the existing compliance-check flow, and submit successfully end-to-end. Minimum supported node types are simple text inputs grouped by section/subsection semantics; unknown/unsupported types must fail visibly. “MVP complete” requires demonstrating Veni plus at least one additional flat structured call.

**Brainstorming Q&A:**

**Q1: What is the smallest functional slice (frontend) we must ship?**
- A) Universal dynamic renderer for flat structured calls + submit works end-to-end.
- B) Universal renderer only (no submit).
- C) Only multi-call dropdown (still Veni-only form).
> Recommendation: A — Rendering without submit does not remove the launch blocker; end-to-end payload correctness is the point of the universal form.
> **Selected: A**

**Q2: What is the minimum backend dependency for the universal renderer?**
- A) Use existing endpoints only; accept any small UX gaps (fallback labels).
- B) Add one small backend endpoint to return a single “form schema” payload.
- C) Freeze universal work until backend exposes perfect UI schema.
> Recommendation: A — Matches the explicit constraint: no new backend endpoints in this WF.
> **Selected: A**

**Q3: What is the minimum supported node types in the renderer?**
- A) `section/subsection/textarea` as plain text inputs only; anything else is “unsupported”.
- B) Support file upload nodes too.
- C) Support rich widgets (tables, list builders).
> Recommendation: A — Minimizes scope and avoids content-type drift that would break compliance counting and backend normalization.
> **Selected: A**

**Q4: What calls must be demonstrated for “MVP complete”?**
- A) Veni + 1 additional flat structured call.
- B) Veni only.
- C) Veni + ERC (nested).
> Recommendation: A — Demonstrating at least one additional call proves universality and prevents overfitting to Veni.
> **Selected: A**

**Q5: What is explicitly excluded from this MVP?**
- A) Recursive/nested rendering, Markdown/rich text, legacy single-snippet unification, server-side drafts.
- B) Only recursive/nested rendering excluded.
- C) Nothing excluded.
> Recommendation: A — These exclusions protect the 2–3 day MVP timebox and preserve the pre-parked follow-on items.
> **Selected: A**

---

## Phase 0 Risk Audit Notes (Summary)

- Kept WF-0035 scope flat-only and fail-fast for nested calls; ERC-StG-2026 remains explicitly blocked until recursive rendering work ships.
- Clarified call selection behavior: structured-node calls only; exclude calls that fail config/metadata fetch and show a non-blocking warning banner.
- Clarified nested detection: if any node has a non-null `parent_node_id`, hard-block as unsupported for WF-0035.
- Clarified rendering order: use `/calls/{call_id}/nodes?view=flat` ordering as source-of-truth; metadata only enriches.
- Frontend typing should tolerate future `NodeSummary` expansion (e.g., `logical_id` presence/nullable; `node_type` may expand beyond `SECTION|SUBSECTION`).
- Preflight before frontend implementation: ingest the 2nd call into DB and smoke-test:
  - `GET /calls`
  - `GET /calls/{call_id}/nodes` (ensure flat-only guardrail: `parent_node_id` all null)
  - `GET /api/public/calls/{code}/config` (`ui_mode="structured_nodes"`)
  - `GET /api/public/calls/{code}/nodes/metadata` (ensure expected logical IDs exist)

### Remaining Blocker

- Identify and ingest at least one additional *official, flat-supported structured call* (non-Veni) using the updated authoring conventions (no legacy YAML structure).
- Selected target for the 2nd call proof: **NWO Vidi 2025 full proposal** (deadline: **2026-04-09 14:00 CEST**).
- Source gate: official funder docs must be provided in-workflow before authoring the YAML; once provided, ingest into DB and validate flat-only guardrail (`parent_node_id` all null).

## 8. Explicit Non-Goals

Non-goals are explicit to prevent scope creep: no recursive rendering (nested calls hard-block), no Markdown/rich text (plain text only), no legacy single-snippet unification, no server-side drafts, and no major UX redesign beyond minimal tweaks needed for call selection and unsupported-call messaging.

**Brainstorming Q&A:**

**Q1: What is the clearest non-goal about nested structures for WF-0035?**
- A) No recursive rendering; any nested call hard-blocks with an explicit unsupported message.
- B) Flatten nested nodes silently.
- C) Partially render only top-level nodes.
> Recommendation: A — Prevents silent corruption and preserves the explicit deferral boundary to recursive rendering work.
> **Selected: A**

**Q2: What is the non-goal about content types?**
- A) No Markdown/rich text; plain text only.
- B) Markdown allowed but no rich text.
- C) Full rich text editor.
> Recommendation: A — Keeps compliance counting and backend normalization deterministic; Markdown/rich text is already tracked as a follow-on.
> **Selected: A**

**Q3: What is the non-goal about call modes?**
- A) Do not unify legacy single-snippet calls into this universal form in WF-0035.
- B) Unify legacy + structured now.
- C) Remove legacy mode entirely.
> Recommendation: A — Keeps this WF tightly scoped; legacy unification is parked as a separate follow-on.
> **Selected: A**

**Q4: What is the non-goal about drafts/persistence?**
- A) No server-side drafts; localStorage only.
- B) Add server drafts now.
- C) Remove drafts entirely.
> Recommendation: A — Sufficient for MVP and consistent with current behavior.
> **Selected: A**

**Q5: What is the non-goal about UX scope?**
- A) No major redesign; only minimal UI tweaks needed for call selection and unsupported-call messaging.
- B) Full redesign is in scope.
- C) No UI tweaks allowed at all.
> Recommendation: A — Minimizes regression risk while allowing the small changes required by universalization.
> **Selected: A**
