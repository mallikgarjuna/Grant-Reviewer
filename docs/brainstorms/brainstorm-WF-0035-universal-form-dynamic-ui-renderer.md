# WF-0035 — Universal Form: Dynamic UI renderer

Artifact: brainstorm
Version: v0.1
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

(Interactive; fill via Q&A below.)

## 5. Constraints

(Interactive; fill via Q&A below.)

## 6. Risks / Unknowns

(Interactive; fill via Q&A below.)

## 7. MVP Definition

(Interactive; fill via Q&A below.)

## 8. Explicit Non-Goals

(Interactive; fill via Q&A below.)
