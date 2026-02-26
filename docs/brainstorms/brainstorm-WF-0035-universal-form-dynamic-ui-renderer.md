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

(Interactive; fill via Q&A below.)

## 2. Desired Outcome

(Interactive; fill via Q&A below.)

## 3. Target User / Actor

(Interactive; fill via Q&A below.)

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
