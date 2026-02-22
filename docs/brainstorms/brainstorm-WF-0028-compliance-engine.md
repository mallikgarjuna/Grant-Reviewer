# WF-0028 — NWO Veni 2025 preproposal Compliance Engine (WF-4 Phase)

Artifact: brainstorm
Version: v0.0
Status: Not started
Last Updated: 2026-02-22

---

## 1. Problem Statement

**Summary:**
The compliance engine provides immediate, deterministic feedback to researchers about strict rule violations (e.g., word count, missing mandatory sections) prior to LLM evaluation. The researcher is the primary beneficiary. The check runs when explicitly requested ("Check Compliance"). Failures are categorized into Errors (blocking) and Warnings (non-blocking). We build the backend engine first (before the frontend form) to establish the API contract for validation errors so the frontend knows exactly what shape of error data to natively display.

**Brainstorming Q&A:**
- **Q1:** What is the primary problem the compliance engine solves?
  - **A:** Giving immediate feedback to researchers about strict rule violations (e.g., word count, missing sections) without waiting for a full AI review.
- **Q2:** Who is the primary beneficiary of this deterministic compliance check?
  - **A:** The Researcher (gets instant feedback on hard constraints).
- **Q3:** When should this compliance evaluation run?
  - **A:** Only when the researcher explicitly clicks "Check Compliance" or "Submit for AI Review".
- **Q4:** How should compliance failures be categorized?
  - **A:** Differentiate between warnings (e.g. "close to word limit") and errors (e.g. "missing mandatory field").
- **Q5:** Why is it critical to build the backend compliance engine now, before the frontend form (WF-6)?
  - **A:** To establish the API contract for validation errors so the frontend form knows exactly what shape of error data to display per field.

---

## 2. Desired Outcome

**Summary / Decisions:**
A successful compliance engine MVP blocks 100% of malformed submissions from reaching the LLM evaluation step, saving API costs and improving feedback quality. We expect researchers to fix formatting and structural issues locally before seeing AI feedback. For the MVP, it's sufficient to deterministically validate basic word counts, section presence, and data types, while leaving subjective rules (like tone) exclusively for the LLM evaluation phase. Once a proposal passes all compliance checks, the UI should return a clean "All Checks Passed" payload and wait for the researcher to explicitly click "Submit for AI Review".

**Brainstorming Q&A:**
- **Q1:** What measurable change defines success for the compliance engine MVP?
  - **A:** 0% malformed submissions reach the LLM evaluation step, saving API costs and avoiding bad feedback.
- **Q2:** What is the specific behavior change we expect from the user?
  - **A:** Users fix their formatting and structural issues locally before they ever see AI feedback.
- **Q3:** What would make this "good enough" for MVP?
  - **A:** Validating basic word counts, section presence (non-empty fields), and data types (e.g. valid selections).
- **Q4:** How should the engine handle rules that cannot be deterministically evaluated (e.g., "Is the tone appropriate")?
  - **A:** Skip them entirely in this deterministic pass and leave them exclusively for the LLM evaluation phase.
- **Q5:** What happens in the UI when a proposal is 100% compliant?
  - **A:** It returns a clean "All Checks Passed" payload and WAITS for the researcher to explicitly click "Submit for AI Review".

---

## 3. Target User / Actor

**Summary / Decisions:**
The primary user interacting with the compliance engine is the **Researcher**. The engine acts as a bridge enforcing rules defined by **Admins** via YAML. The engine must interact directly with the researcher, providing a structured error response that maps exactly to UI fields (e.g., "Section B is over the 400-word limit by 12 words"). This solves the twofold frustration of waiting for a slow AI review only to get formatting feedback, and AI hallucinating structural feedback instead of focusing on the science.

**Brainstorming Q&A:**
- **Q1:** Is the compliance engine interacting directly with the researcher, or running invisibly?
  - **A:** Directly with the researcher (provides a clear list of pass/fails in the UI before they can submit).
- **Q2:** How does the researcher discover the constraints they are violating?
  - **A:** The compliance engine generates a structured error response that maps exactly to the fields in the UI, pointing out what to fix (e.g., "Section B is over the 400-word limit by 12 words").
- **Q3:** Are there different types of target users for this feature?
  - **A:** Yes, researchers (fixing their drafts) and admins (defining the rules in the YAML).
- **Q4:** What is the researcher's core frustration with the current state that this solves?
  - **A:** Both: Waiting for a full AI review only to be told "You forgot the word count in section C", and the AI hallucinating feedback on missing sections instead of focusing on the science.

---

## 4. Rough Idea (Unstructured Thinking)

**Summary / Decisions:**
The simplest implementation direction is to read the compliance rules directly from the V2 database model (specifically looking at constraints like `word_limit`, `mandatory`, `compliance_rules`, and `guidance_text` on `EvaluationElement`). The frontend will save the draft to the database first, then call a `/check-compliance/{draft_id}` API endpoint. This endpoint will return an HTTP 200 with a structured JSON payload containing lists of `errors` and `warnings`, including the specific underlying reason/rule that failed so the UI can display *why* it failed. The engine will be strictly read-only and will *not* auto-fix answers (leaving scientific nuance to the researcher). The biggest technical risk is standardizing accurate word counting between the frontend editor and backend validator, so the UI must include a clear disclaimer about word count approximations.

**Brainstorming Q&A:**
- **Q1:** Where does the "source of truth" for compliance rules live?
  - **A:** In the database, populated from the funding call YAML definitions (including `word_limit`, `mandatory`, `compliance_rules`, and `guidance_text`).
- **Q2:** What should the compliance engine API endpoint return?
  - **A:** HTTP 200 with a detailed JSON object containing lists of `errors` and `warnings` and the specific reasons/rules that failed, allowing the frontend to display exactly *why* an error was flagged.
- **Q3:** How is the proposal data passed to the compliance engine for checking?
  - **A:** The frontend first saves the draft to the database, then calls a `/check-compliance/{draft_id}` endpoint.
- **Q4:** Should the compliance engine support "auto-fixing" issues?
  - **A:** No, it should strictly be read-only and return feedback. It is up to the researcher to fix it.
- **Q5:** What is the highest technical risk for this rough idea?
  - **A:** Word counting accurately (e.g., handling markdown, HTML, or LaTeX rendering artifacts). We must include a disclaimer on the UI about word counts.

---

## 5. Constraints

**Summary / Decisions:**
The system must be built as a purely data-driven, local backend Python service with no hardcoded AI calls or third-party dependencies, relying exclusively on the PostgreSQL `EvaluationElement` definitions. Because this is a blocking necessity for the upcoming frontend work (WF-6), the time constraint is strict: it must be shipped immediately.

**Brainstorming Q&A:**
- **Q1:** What is the primary technical constraint for the compliance engine?
  - **A:** It must rely exclusively on the `EvaluationElement` definitions in the PostgreSQL database, meaning no hardcoded rules per funding call in the code.
- **Q2:** What is the time constraint for building this MVP?
  - **A:** Must be fully shipped today/tomorrow so we can unblock WF-6 (the complex frontend form).
- **Q3:** Are there any external dependencies to worry about?
  - **A:** No, this should be a purely deterministic, local backend operation using only the database and standard Python string manipulation.

---

## 6. Risks / Unknowns

**Summary / Decisions:**
The most fragile assumption is that the drafted `ProposalNode` tree structure perfectly aligns with the `EvaluationElement` tree; if they drift, the compliance traversal will break or return false positives. Another major risk is aggregate constraints (e.g., a word limit on a parent section spanning multiple child subsections), which must be handled explicitly. To prevent future rework, the core validation logic must be built as a decoupled, purely testable Python function (`def evaluate_compliance(draft_id)`) separate from the FastAPI transport layer.

**Brainstorming Q&A:**
- **Q1:** What is the most fragile assumption we are making?
  - **A:** That the `ProposalNode` tree structure in the database exactly matches the expected shape defined by the `EvaluationElement` tree for every call.
- **Q2:** What edge case needs validation early?
  - **A:** What happens if a constraint applies to a parent section but the drafted text is split among 5 child subsections? (e.g., aggregate word counts).
- **Q3:** What could cause the most rework later?
  - **A:** Tying the validation logic too tightly to the API transport layer instead of keeping it as a pure, testable internal Python service/function.
