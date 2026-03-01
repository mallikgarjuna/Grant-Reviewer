# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-01

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for decisions/contracts (what we will implement).
- The Q&A transcript is rationale only; it must not introduce new contracts.
- Any contract discovered during implementation must be promoted into this brainstorm (do not let “truth” live only in code or in Q&A).

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 1)

Primary actor: applicant / researcher end-user.

What’s broken today:
- The app does not yet deliver a trustworthy “one real call works” end-to-end flow for `nwo_veni_2025_preproposal` using the universal engine: pick call → fill call-driven sections → deterministic compliance blocking → run structured review → see results tied to proposal sections and evaluation criteria/elements.

Why now:
- Without one fully working call, product claims remain speculative; trust and demo credibility are blocked.

Contract notes / non-obvious constraints:
- “Done” requires results to be traceable to both proposal sections and evaluation criteria/elements (not generic feedback).
- Scope stays single-call; avoid multi-agency abstractions.
- Universal engine only (no call-specific pipelines beyond what the existing engine already supports).
- Avoid call-specific hardcoding (e.g., Veni-only label/order mappings); implement call-driven behavior even in the single-call MVP.

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- Call YAML is already authored in canonical v2 shape, including proposal nodes, evaluation criteria/elements, node expectations, reviewer policy, and domain-limited word limits: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Ingestion exists via DB upsert: `backend/scripts/ingest_call.py`.
- Universal submit UI exists and is call-driven for structured calls: `frontend/src/components/submit/UniversalSubmitForm.tsx`.
- Deterministic compliance exists and can block on mandatory presence and word limits: `backend/app/services/compliance_engine.py` + `POST /api/check-compliance`.
- Structured review execution exists and can policy-block based on forbidden terms in LLM output: `POST /api/structured-review` + `backend/app/services/review_execution_core.py`.

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 2)

MVP success (demoable repeatedly):
- User can complete full happy-path in UI: select call → fill all required nodes (arbitrary count) → compliance blocks/clears → submit → review detail shows per-card proposal section + evaluation element traceability.

Measurable outcomes:
- No per-call hardcoding in frontend for node label/order or domain options; submit and review-detail experiences are driven by canonical call definition + DB/API metadata/config.
- Compliance is honest + enforceable: mandatory presence + min/max word limits (domain-aware for Veni pilot) block submission; warnings are visible but do not block.
- Results UX surfaces explicit evaluation element names for each card/finding and ties each to a proposal section label.

Contract notes / non-obvious constraints:
- “Arbitrary count” means: do not assume 3 nodes; support any number of call-defined proposal nodes without code changes.
- Domain UX must be call-specific and call-driven; do not assume a “domain” concept for other calls (e.g., ERC/MSCA) unless their call definition introduces it.

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 3)

Primary persona (MVP): early-career researcher applying to Veni (self-serve).

Primary job-to-be-done (MVP): criteria/elements-grounded feedback to revise (not “compliance-only”).

Usage pattern (MVP): single-pass UX (paste once → submit → results). Multiple runs may exist, but we do not optimize for iterative loop UX in WF-0041.

Trust posture copy: “Structured feedback aligned to evaluation criteria/elements; still use judgement.”

Contract notes / non-obvious constraints:
- Each submission should still create/persist a Review that appears in `/app/reviews` (current behavior); follow-up improvements to review history UX are allowed later, but do not break persistence/listing.

## 4. Rough Idea (Unstructured Thinking)

TBD.

## 5. Constraints (Initial)

- Scope: **single-call MVP only** for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Implementation: use the **universal engine** end-to-end; avoid multi-agency abstractions.
- Success definition: happy-path “one call is fully usable” (ingest+activate call, call-driven submit UI, compliance blocking, run review, call-aware results).
- No call-specific hardcoding: avoid “Veni-only” mappings in UI/API; behavior should be driven by canonical call definition + DB metadata (even though this WF ships only one call).
- Domain options must not be hardcoded client-side; domain selection UX must be sourced from call metadata/config.

## 6. Risks / Unknowns

TBD.

## Open Questions / Deferred

TBD.

## 7. MVP Definition

TBD.

## 8. Explicit Non-Goals

TBD.
