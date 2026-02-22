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
