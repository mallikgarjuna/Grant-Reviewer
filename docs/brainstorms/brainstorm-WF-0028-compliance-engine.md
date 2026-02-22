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
