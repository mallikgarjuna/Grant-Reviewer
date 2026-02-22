# WF-0030 — NWO Veni 2025 Preproposal Structured AI Review (WF-6 Phase) Brainstorm

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

---

## 1. Problem Statement

The single text area submission input does not align with the strict 3-node structure of the NWO Veni pre-proposal. Additionally, users lack real-time visibility into their compliance with word and output limits prior to submission, leading to potential frustration and backend validation errors.

**Brainstorming Q&A:**

**Q1: What is the primary user-facing problem we are solving with this frontend update?**
- A) The current input is a single text box, which doesn't match the required 3-node structure of the NWO Veni pre-proposal.
- B) Users don't know if their proposal is compliant with word limits and output counts until they submit.
- C) Both A and B—the UI needs to capture the structured nodes and surface compliance errors preventatively.
> Recommendation: **C** — We need to capture the distinct data shapes and provide immediate compliance feedback prior to submission as defined in the north star. (Alternative A misses the compliance requirement. Alternative B misses the basic data geometry requirement.)
> **Selected: C**
> *User Comment*: "Currently, for NWO-Veni, we are working to address 3-node input structure. What if another funding call has different number of nodes (say 5)? Shouldn't we make it flexible? If yes, when/where are we doing this?"
> *Follow-up Action*: Parked as P2 #14 (Dynamic frontend forms based on Call schema) to keep the MVP scope strictly to the Veni 3-node structure while acknowledging the future need for N-node flexibility.

**Q2: How should the frontend handle the 3-node input structure?**
- A) Three distinct text areas stacked on one page, clearly labeled as academic profile, key outputs, and research idea.
- B) A single text area where users must paste everything, and we try to parse it automatically on the frontend.
- C) A multi-step wizard where users fill out one node per screen.
> Recommendation: **A** — Three distinct text areas are simple, clear, and ensure the user explicitly provides the required discrete nodes, eliminating parsing complexity and misrouting. (Alternative B is error-prone and requires complex parsing logic. Alternative C is too heavy for the MVP and slows down power-pasters.)
> **Selected: A**
> *User Comment*: "Is it feasible to let the researcher upload separate documents (.docx or .pdf) per each node, and we parse it to markdown using a service like MarkItDown... and display the parsed markdown on UI in 3 distinct text areas? How complicated to implement this in MVP? I beleive this reduces some friction for researchers"
> *Follow-up Action*: Parked as P2 #15 (Assisted extraction via document upload) as this introduces new backend dependencies and parsing/security considerations that extend beyond the immediate strict-MVP slice, but is a great UX improvement for the backlog.

**Q3: When should the compliance UI (word limits, max outputs) be calculated and displayed to the user?**
> **Selected: B** — Real-time on the frontend as the user types/pastes.

**Q4: How should we strictly handle draft reviews (idempotent drafts) to prevent accidental duplicate submissions?**
> **Selected: B** — The frontend generates a deterministic `logical_id` (draft ID), passes it to the backend, and locks the UI.

**Q5: What is the scope of styling and layout changes for this feature?**
> **Selected: B** — Reusing existing forms/components but adjusting them for three inputs and inline warnings.

---

## 2. Desired Outcome

The desired outcome is to capture 100% compliant structured inputs (preventing wasted LLM tokens) while maintaining a frictionless user experience via real-time warnings, durable local drafts with recovery toasts, and clear visual transitions to a processing state.

**Brainstorming Q&A:**

**Q1: What measurable change defines success for this specific frontend update (WF-6)?**
- A) A 100% reduction in invalid or non-compliant submissions reaching the backend LLM.
- B) A faster average time to submit a proposal for a user.
- C) The visual presence of the word-count indicators, regardless of whether they actively block submission.
> Recommendation: **A** — This strongly aligns with the core goal of the compliance engine (WF-4/WF-5) which is to prevent wasted LLM tokens and ensure high-quality, pre-validated inputs. (Alternative B is hard to measure. Alternative C is too weak).
> **Selected: A**

**Q2: How should the system enforce the deterministic compliance rules (Word Count, Max Outputs)?**
- A) Hard enforce: The submit button is completely disabled if any node violates an `ERROR` level compliance rule (e.g., word count > limit).
- B) Soft enforce: The submit button is active, but clicking it shows a warning modal that the user can choose to bypass.
- C) The frontend just shows red text, but the backend rejects the request and returns a 400 error.
> Recommendation: **A** — Hard enforcement via a disabled submit button is the clearest UX. (Alternative B violates the strict compliance rules defined in the NWO Veni call. Alternative C relies too heavily on backend roundtrips.)
> **Selected: B**
> *User Rationale / Constraint*: "I'd say B instead of A, because they are looking for reviewing their proposal to improve it. A warning is sufficient to alert them."
> *System Note*: This requires a deviation from the backend's strict compliance rejection (which currently returns 400 Bad Request on ERRORs). We must either downgrade backend ERRORs to WARNINGs for this endpoint, or pass a `force=true` flag to bypass the backend compliance gate.

**Q3: When the user is drafting their submission and taking a break, what is the expected behavior?**
- A) The user must keep the browser tab open; if they refresh, the text is lost.
- B) The frontend automatically saves the draft text to `localStorage` so it survives a page refresh.
- C) The frontend automatically saves the draft continuously to the backend database.
> Recommendation: **B** — `localStorage` is extremely cheap to implement for the MVP and significantly improves UX (preventing accidental data loss) without requiring complex backend draft-state management. (Alternative A is a hostile UX. Alternative C is over-engineered.)
> **Selected: B**
> *User Comment*: "and the page regresh should show warning alert pop up with a proper message?"
> *Follow-up Action*: Yes, added requirement: when restoring from `localStorage` on page load, display a dismissible warning/toast informing the user that their previous draft was restored.

**Q4: What should happen immediately *after* a successful, compliant submission?**
- A) The user stays on the form page, but the fields are cleared and a "Success" toast appears.
- B) The frontend routes the user to a "Processing" or "Results" page where they can wait for the AI review to complete via polling/WebSocket.
- C) The UI is replaced seamlessly with the returned review cards on the exact same page.
> Recommendation: **B** — Transitioning the user to a dedicated processing/results view clearly communicates that the state has changed from "Drafting" to "Evaluating," which is crucial since the structured review might take 30-90 seconds.
> **Selected: B**

**Q5: What makes this feature "good enough" to ship as the MVP?**
- A) The 3 NWO Veni nodes are hardcoded text areas, real-time word/item counts are visible, the submit button is disabled if `ERROR` thresholds are breached, and duplicate submissions are prevented via a draft ID lockout.
- B) The form is fully dynamic (loads fields from the DB), handles all validation, and supports document uploads.
- C) The form looks beautiful and has animations, even if the validation relies entirely on the backend 400 errors.
> Recommendation: **A** — This is the strict definition of the North Star requirements scoped to the absolute minimal functional slice. It correctly hardcodes the Veni structure for now while fulfilling all compliance and safety requirements.
> **Selected: A**
> *System Note*: Since the user selected Q2:B (Soft enforce), the MVP criteria here must be adjusted: The submit button is *not* disabled on ERROR thresholds, but instead triggers a soft-warning modal that the user can bypass.

---

## 3. Target User / Actor

*(To be filled during Phase 0.1 brainstorm)*

---

## 4. Rough Idea (Unstructured Thinking)

*(To be filled during Phase 0.1 brainstorm)*

---

## 5. Constraints

*(To be filled during Phase 0.1 brainstorm)*

---

## 6. Risks / Unknowns

*(To be filled during Phase 0.1 brainstorm)*

---

## 7. MVP Definition

*(To be filled during Phase 0.1 brainstorm)*

---

## 8. Explicit Non-Goals

*(To be filled during Phase 0.1 brainstorm)*
