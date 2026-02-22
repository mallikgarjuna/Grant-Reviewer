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
- A) Only after the user clicks "Submit", handled as a validation error returned from the backend.
- B) Real-time on the frontend as the user types/pastes into the input fields, before submission.
- C) As a distinct intermediate step after submission but before calling the LLM.
> Recommendation: **B** — Real-time validation provides the best user experience, preventing unnecessary backend roundtrips and aligning with the expectation to surface compliance before submission. (Alternative A is a poor UX. Alternative C adds unnecessary friction steps).
> **Selected: B**

**Q4: How should we strictly handle draft reviews (idempotent drafts) to prevent accidental duplicate submissions?**
- A) Rely solely on backend logic; the frontend just sends requests.
- B) The frontend should generate and store a deterministic `logical_id` (or draft ID) for the review, pass it to the backend, and lock the UI while processing.
- C) The frontend doesn't need to worry about duplicate submissions for the MVP.
> Recommendation: **B** — The frontend needs to participate by generating or managing a stable ID (like a draft session) and locking the UI to prevent double-clicks, perfectly complementing backend idempotency. (Alternative A leads to race conditions. Alternative C wastes expensive LLM calls.)
> **Selected: B**

**Q5: What is the scope of styling and layout changes for this feature?**
- A) A complete redesign of the submission page using entirely new components.
- B) Reusing existing forms and UI components but adjusting them to accommodate three inputs and inline compliance warnings.
- C) No styling changes; just raw HTML inputs to get it working.
> Recommendation: **B** — Reusing existing components (buttons, textareas, alerts) maintains consistency and speeds up development, adhering to the "smallest functional slice" constraint. (Alternative A is out of scope. Alternative C looks broken.)
> **Selected: B**

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

The primary actor is a researcher who has an existing proposal draft and wants actionable, criteria-driven feedback. They will predominantly copy-paste their draft into the UI. The application is strictly a review tool, not a co-writer; it evaluates against funding criteria but does not rewrite text for the user. Text extraction from complex formats (images/tables) is a known friction point to be addressed in future document-parsing work (P2 #15).

**Brainstorming Q&A:**

**Q1: For this specific structural update (WF-6), who is the primary target persona?**
- A) A first-time user who is completely unfamiliar with the NWO Veni call and needs heavy guidance.
- B) A researcher who already has a draft proposal (often constructed offline in Word) and wants to evaluate it against the rubric.
- C) A grant office administrator submitting on behalf of a researcher.
> Recommendation: **B** — The core use-case we've observed is researchers pasting in existing drafts to get feedback. (Alternative A requires too much heavy inline hand-holding for an MVP. Alternative C is a secondary persona that behaves identically to B for the purposes of pasting text).
> **Selected: B**
> *User Comment*: "but what if the text also has images/tables? how do we handle them? We need to consider/brainstorm solution to these."
> *System Note*: In the MVP (copy-paste textareas), images and rich tables will be lost as plain text. This validates the importance of the parked P2 #15 item (document upload via MarkItDown), which can extract markdown tables and image alt-text/captions. For this WF-6 MVP, we must rely on the user pasting plain text and accept that visual context is lost until P2 #15 is implemented.

**Q2: How does the target user typically interact with the input fields?**
- A) They type their proposal from scratch directly into our UI.
- B) They copy-paste large chunks of text from an external document into the text areas.
- C) They upload a file and expect it to automatically populate.
> Recommendation: **B** — Copy-pasting is the dominant behavior based on the current architecture. (Alternative A is rare for 1500+ word grants. Alternative C is highly desirable but was already explicitly parked as P2 #15 for future development).
> **Selected: B**

**Q3: When the user sees a compliance warning (e.g., "Word count exceeded: 450/400"), what is their expected reaction?**
- A) They will immediately edit the text within our UI to fix the issue before submitting.
- B) They will ignore it and submit anyway, expecting the AI to help them cut down the text.
- C) They will go back to their Word document, fix it there, and re-paste it.
> Recommendation: **A & B** — Based on your previous choice for "Soft enforce", users will likely do a mix of A and B.
> **Selected: A & B (with a critical correction)**
> *User Context/Constraint*: "but we are not helping them to rewrite their proposal, right? Our goal is to review their proposal as per the evaluation/assessment/review criteria of the funding call. But not to write the proposal. Let's reconsider this."
> *Correction*: You are absolutely correct. The tool evaluates; it does not rewrite or compress. Therefore, if a user submits an over-length proposal, the AI review should note the compliance violation in its evaluation, but the tool is *not* an active editing assistant. The frontend compliance warning exists purely to alert them that their draft breaks the rules *before* they ask for a review.

**Q4: How should we treat a user who attempts to bypass the compliance warnings?**
- A) Force them to type an explicit confirmation word (e.g., "IGNORE") before the submit button unlocks.
- B) Show a simple, dismissible confirmation modal ("Your draft exceeds official limits. Proceed?").
- C) We don't need a modal; if the button is active and they click it despite the red text, just let it through.
> Recommendation: **B** — A simple confirmation modal adds exactly one intentional click, confirming they saw the warning without creating excessive friction. (Alternative A is too punishing. Alternative C is too passive and might lead to accidental submissions of malformed pastes).
> **Selected: B**

**Q5: What level of UI density does this user expect?**
- A) High density: lots of small text, tight margins, showing all rules simultaneously (Academic style).
- B) Medium density: clean, modern forms with clear distinct sections and inline validation.
- C) Low density: massive text areas taking up the whole screen, hiding all instructions behind tooltips.
> Recommendation: **B** — Clean, modern, distinct sections match the PeerLens brand guidelines while keeping the interface focused on the content. (Alternative A is overwhelming. Alternative C hides too much crucial context).
> **Selected: B**

---

## 4. Rough Idea Exploration

The MVP approach is a single form containing three distinct `<textarea>` fields representing the Veni nodes. Word counts are calculated client-side in real-time to provide immediate compliance feedback without network overhead. The form includes an ENW/Science pilot toggle to dynamically adjust the research idea word limit (100 vs 500). Draft idempotency is guaranteed by a frontend-generated UUID. If a user bypasses the soft-warning for an oversized (or missing) node, they must confirm via a modal popup.

**Brainstorming Q&A:**

**Q1: How should we technically capture the 3 structured nodes from the user?**
- A) A single `<form>` element containing 3 distinct `<textarea>` fields, submitted as a single JSON payload.
- B) Three separate forms that the user must submit one by one.
- C) A complex rich-text editor (like Quill or TipTap) that forces the user to use specific headers for each node.
> Recommendation: **A** — Delivering a single form with 3 `<textarea>` fields is the simplest, most reliable way to map directly to the `VeniPreproposalParams` schema expected by the backend. (Alternative B creates unnecessary friction and state-management issues. Alternative C is drastically over-engineered for plain text ingestion).
> **Selected: A**
> *User Comment*: "are we considering into account when the researcher does not fill all nodes/textareas before submission? We should."
> *System Note*: Yes, this is a critical flow. The frontend must allow submission of partial drafts (e.g., if a user only wants to review their Academic Profile). If a node is completely empty, it will not trigger a word-count maximum error, but the backend AI evaluation will cleanly mark alignment criteria dependent on that missing node as `NOT_ASSESSABLE` (as implemented in WF-0029). The frontend validation must not strictly require all three fields to be populated to submit.

**Q2: How should the live compliance engine (word counts) be implemented on the frontend?**
- A) Send a debounce API request to the backend `/compliance` endpoint on every keystroke to get the exact counts.
- B) Implement a lightweight Javascript utility on the frontend that mimics the backend's word count logic for real-time feedback.
- C) Don't show real-time counts; only count when they click a "Check Compliance" button.
> Recommendation: **B** — A local JS utility provides zero-latency feedback without hammering the backend, keeping the UI highly responsive. Since word counts are deterministic (split by whitespace), maintaining parity between frontend JS and backend Python is trivial. (Alternative A wastes network requests. Alternative C is a poor user experience).
> **Selected: B**

**Q3: We need to implement the "Soft enforce" bypass you requested in Section 2. How should this flow work?**
- A) If there is an `ERROR`, the "Submit" button turns yellow and says "Submit with Warnings". Clicking it immediately submits with a `force=true` flag.
- B) If there is an `ERROR`, the "Submit" button remains active. Clicking it opens a modal showing the exact errors and requiring a second "Confirm Submission" click.
- C) The frontend quietly changes all `ERROR` severity levels to `WARNING` severity levels so the backend accepts them natively.
> Recommendation: **B** — A modal with a second confirmation click ensures the user explicitly acknowledges the rule violations before wasting LLM tokens. It serves as an intentional friction point. (Alternative A is too easy to click accidentally. Alternative C requires altering the backend's strict NWO logic, which weakens the integrity of the compliance engine).
> **Selected: B**

**Q4: How should the frontend handle the `logical_id` (draft ID) to ensure idempotency?**
- A) The frontend generates a UUID (v4) when the page loads to uniquely identify the draft session.
- B) The frontend hashes the content of the three text areas. If the content hasn't changed, it doesn't allow a second submission.
- C) The backend handles it entirely; the frontend just disables the submit button while the request is in-flight.
> Recommendation: **A** — Generating a UUID on page load (or upon first text entry) is the standard, safest way to ensure a unique operational token for the draft session, perfectly matching the backend's `logical_id` design. (Alternative B is overly complex. Alternative C doesn't protect against network retries or fast double-clicks before the JS disables the button).
> **Selected: A**

**Q5: For the NWO Veni "Research Idea" node, there is a special case: default is max 100 words, but the ENW/Science pilot allows 500 words. How should the frontend handle this?**
- A) Add a checkbox: `[ ] Applying for ENW/Science pilot`. If checked, the UI word limit indicator changes from 100 to 500.
- B) Always show 500 words as the limit to be safe.
- C) Always show 100 words as the limit and let ENW users figure out the warning bypass themselves.
> Recommendation: **A** — A simple toggle checkbox perfectly models the domain requirement without confusing standard applicants, and maps cleanly to the backend compliance engine rules. (Alternative B encourages non-ENW applicants to write too much. Alternative C creates a frustrating experience for valid ENW applicants).
> **Selected: A**

---

## 5. Constraints

The primary constraint is that the frontend must be built within the existing Next.js React application, interfacing with the backend FastAPI endpoints. The real-time word count logic must perfectly mirror the Python backend's custom whitespace-splitting rule. The draft ID (`logical_id`) for idempotency must be stored transiently on the client (e.g. `localStorage` or session state) since there is no server-side user mapping. Finally, the strict compliance engine on the backend must be accommodated with a `force=true` (or equivalent) bypass flag to allow soft-enforced submissions.

**Brainstorming Q&A:**

**Q1: To achieve a universal, schema-driven form, how should the frontend fetch the required node structure?**
- A) When the user selects a funding call from the dropdown, the frontend Next.js client fetches the full Call definition from the backend, parses the `proposal_structure` nodes, and dynamically renders the corresponding textareas on the fly.
- B) The backend should serve a pre-rendered HTML form for each call so the frontend doesn't need to parse schemas.
- C) We should hardcode a giant map of every known funding call's structure directly in the frontend Next.js codebase.
> Recommendation: **A** — Fetching the schema dynamically as JSON is the standard SPA approach. The Next.js frontend simply maps over the `proposal_structure` array returned by the API to render the `<textarea>` components. This keeps the frontend entirely agnostic to specific funders. (Alternative B violates the strict API/SPA separation. Alternative C requires a frontend release every time a new YAML is ingested, completely defeating the purpose of the data-driven architecture).
> **Selected: A**

**Q2: What is the primary technical limitation for the real-time word count utility?**
- A) It must perfectly match the exact hidden tokenization logic of OpenAI's models.
- B) It only needs to match the Python backend's custom whitespace-splitting logic (as defined in `utils.compliance`).
- C) It must parse HTML and Markdown tags perfectly to exclude them from the count.
> Recommendation: **B** — The backend compliance engine uses a very specific RegEx/whitespace splitting logic to count "words". The frontend JS must simply mirror this logic exactly so they never disagree. (Alternative A is impossible as we count words, not tokens, for NWO compliance. Alternative C complicates the MVP for an edge case, especially since users are pasting plain text).
> **Selected: B**

**Q3: We need to store the `logical_id` (draft ID) securely to ensure idempotency. What is the constraint here?**
- A) It must be stored in a secure HttpOnly cookie.
- B) It must be stored in the database immediately upon page load.
- C) It is a transient session token; it can live in the JS memory/DOM or `localStorage` just long enough to prevent double-clicks or accidental resubmissions of the exact same draft state.
> Recommendation: **C** — The draft `logical_id` exists purely to deduplicate submissions on the backend during the 90-second wait. Storing it in an HTML hidden input or `localStorage` during the session is completely sufficient and doesn't require complex session cryptography. (Alternative A is overkill for an MVP without full user auth. Alternative B wastes database writes for drafts that might be abandoned immediately).
> **Selected: C**

**Q4: Regarding the "Soft enforce" warning bypass, what is the backend constraint?**
- A) The backend currently rejects any compliance `ERROR` with a 400 Bad Request immediately. Therefore, the frontend MUST pass a specific flag (e.g., `?force_bypass=true`) when submitting if the user bypassed the warning, and the backend must be updated to accept this flag.
- B) The backend already accepts everything; we don't need to change anything.
- C) We should just remove the strict compliance checks from the backend entirely.
> Recommendation: **A** — Because the backend was built to strictly reject errors (WF-0028/29), we must introduce a "force" flag in the frontend payload and make a tiny update to the backend endpoint to downgrade ERRORs to WARNINGs when this flag is present. (Alternative B is factually incorrect based on the current codebase. Alternative C ruins the core value proposition of the compliance engine).
> **Selected: A**

**Q5: What is our primary time/effort constraint for this specific chunk?**
- A) We have months to build a perfect drafting experience.
- B) We are keeping this scoped to the absolute minimal functional slice to close the loop between the user and the newly built V2 data models / AI evaluation backend.
- C) We must finish this in exactly 2 hours, no matter what corners we cut.
> Recommendation: **B** — The goal is to rapidly ship the frontend that "unlocks" all the backend work completed in WFs 2-5, proving the end-to-end value of the structured AI review. (Alternative A invites scope-creep. Alternative C sacrifices quality and test coverage).
> **Selected: B**

---

## 6. Risks / Unknowns

The primary UX risk is rendering a complex, deeply nested YAML structure elegantly as flat HTML textareas. Additionally, bypassing warnings (`force=true`) risks degrading LLM output quality due to excessive token ingestion. A key usability gap currently is the inability to process rich text/tables during a copy-paste action, which must be clearly communicated to users via an upfront disclaimer.

**Brainstorming Q&A:**

**Q1: What is the biggest UX risk of moving to a dynamic, schema-driven multi-node form?**
- A) The UI logic becomes too complex and brittle, making it hard to maintain.
- B) We fail to render complex nested YAML structures beautifully, resulting in a confusing or ugly layout for the researcher.
- C) The user gets overwhelmed by seeing too many input boxes at once and abandons the form.
> Recommendation: **B** — The backend `proposal_structure` can theoretically define deeply nested nodes, but rendering them elegantly as flat or minimally-nested HTML `<textarea>` components requires careful spacing, typography, and clear labeling (the "Ink+Parchment" aesthetic). (Alternative A is a standard React challenge, not unique here. Alternative C is unlikely if the grouping is clear).
> **Selected: B**

**Q2: How should the frontend handle the specific `message` strings returned by the backend compliance engine (e.g., "Word count exceeded: 450/400")?**
- A) Just show a generic red glow. The user will figure it out.
- B) Directly render the exact `message` string returned by the backend (or mirrored by the local JS) beneath the relevant textarea in red text.
- C) Ignore the backend message and write our own custom error strings in the frontend codebase.
> Recommendation: **B** — Directly rendering the deterministic strings from the compliance engine ensures total consistency between what the user sees and what the system actually evaluates. (Alternative A is terrible UX. Alternative C creates a frustrating split-brain where the UI says one thing, and the evaluation cards say another).
> **Selected: B**

**Q3: What happens if a funding call YAML definition is updated on the backend *after* a user has saved a draft in `localStorage`?**
- A) The frontend crashes trying to map old keys to new schema inputs.
- B) The frontend silently ignores the `localStorage` and loads the new schema completely empty.
- C) The frontend attempts a "best-effort" mapping based on the node IDs (e.g., `academic_profile`), restoring what it can and dropping the rest.
> Recommendation: **C** — Since the `localStorage` draft will be keyed by the stable `id` of each `ProposalNode`, a best-effort mapping ensures the user retains most of their work, even if the schema evolved slightly. (Alternative A is unacceptable. Alternative B destroys user data unnecessarily).
> **Selected: C**

**Q4: The `force=true` bypass allows users to submit non-compliant drafts. What is the primary downstream risk of this?**
- A) The LLM might aggressively hallucinate or truncate the review if the text is massively over length.
- B) The database will become corrupted.
- C) The cost per evaluation will increase exponentially without limits.
> Recommendation: **A** — If a user pastes 5,000 words into a 100-word box and forces it through, the LLM context window might stretch or the model might lose focus, resulting in a poor quality evaluation. (Alternative B is false; text is just text. Alternative C is a risk, but capped by the model's max tokens).
> **Selected: A**

**Q5: Since we parked document upload parsing (P2 #15), researchers pasting highly formatted tables into a plain `<textarea>` will destroy their formatting. How do we mitigate this UX risk for the MVP?**
- A) We must build a complex WYSIWYG editor anyway, violating MVP scope.
- B) Add a clear, dismissible UI disclaimer above the form: "Please paste plain text. Complex formatting like tables/images are not currently supported."
- C) Let the user figure it out when the evaluation comes back garbled.
> Recommendation: **B** — A clear, upfront disclaimer manages expectations perfectly without requiring complex engineering. (Alternative A destroys the timeline. Alternative C damages trust in the AI's capability).
> **Selected: B**

---

## 7. MVP Definition

The frontend MVP for WF-0030 is a universal, dynamically rendered submission form at a single route (e.g., `/app/submit`). The frontend fetches the schema for the user-selected funding call from the backend API, iterates over the `proposal_structure` definition, and dynamically renders the appropriate number of `<textarea>` fields (3 nodes for Veni, 5 for ERC, etc.). It implements a purely local JavaScript equivalent of the backend's word-counting logic to provide zero-latency compliance UI. It generates a deterministic UUID `logical_id` to ensure idempotency. It includes a frontend-only soft-bypass mechanism via a confirmation modal, which appends a `force=true` (or equivalent) parameter to the backend request.

**Brainstorming Q&A:**

**Q1: Based on our discussions, which of the following best defines the strict frontend MVP for WF-0030?**
- A) A single page at `/app/submit` that dynamically fetches the selected `FundingCall` schema, renders `<textarea>` fields for each `ProposalNode`, provides real-time word-count feedback using local JS, manages idempotency via a UUID `logical_id`, and includes a modal to allow users to bypass compliance warnings (`force=true`). Document parsing and WYSIWYG formatting are explicitly excluded.
- B) A set of hardcoded pages for each funding call (e.g., `/app/submit/nwo-veni`, `/app/submit/erc-cog`) with real-time validation and document upload capabilities.
- C) A wizard-style interface that guides the user through the nodes one by one, saving to the database at every step.
> Recommendation: **A** — This perfectly encapsulates the "universal form" constraint, the UX safety mechanisms (idempotency, warnings), and the agreed-upon deferrals (no doc parsing). It represents the smallest slice of value that unlocks the V2 backend. (Alternative B violates the dynamic schema architecture. Alternative C is drastically over-engineered for the MVP).
> **Selected: A**

---

## 8. Explicit Non-Goals

The following features will explicitly *not* be built during WF-0030 to protect the delivery timeline of the MVP slice.

**Brainstorming Q&A:**

**Q1: To strictly fence the scope of this frontend work, which of the following is an explicit NON-goal for WF-0030?**
- A) Real-time word counting.
- B) Extracting tables, images, or semantic formatting from uploaded `.docx` or `.pdf` files.
- C) Generating a UUID for idempotency.
> Recommendation: **B** — Document parsing (MarkItDown/MCP) is highly valuable but was explicitly parked as P2 #15. We must actively avoid building any file-upload or rich-text parsing logic in this chunk to ensure rapid delivery. (Alternatives A and C are explicit requirements, not non-goals).
> **Selected: B**

---

## 9. Parked / Non-Scoped Items

The following items arose during brainstorming but were explicitly parked to keep the MVP scope constrained. They are logged in `docs/parking_lot.md` for future prioritization:

1.  **Assisted Extraction via Document Upload (P2 #14)**: Building a backend service (e.g., using MarkItDown) to parse uploaded `.docx` or `.pdf` files and automatically populate the structured `<textarea>` inputs on the frontend, gracefully handling or stripping images/tables to reduce copy-paste friction.
2.  **Rich Text / WYSIWYG Editor Support**: Permitting markdown/HTML pasting to preserve lists, bolds, and italics natively within the text areas (Currently deferred to maintain strict plain-text token counting parity).
3.  **Cross-Node Context Dependency Engine (P1 #12)**: While the backend handles `NOT_ASSESSABLE`, the frontend MVP will not attempt to visualize complex cross-node dependencies.

---
