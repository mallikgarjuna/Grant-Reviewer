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

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- Call YAML is already authored in canonical v2 shape, including proposal nodes, evaluation criteria/elements, node expectations, reviewer policy, and domain-limited word limits: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Ingestion exists via DB upsert: `backend/scripts/ingest_call.py`.
- Universal submit UI exists and is call-driven for structured calls: `frontend/src/components/submit/UniversalSubmitForm.tsx`.
- Deterministic compliance exists and can block on mandatory presence and word limits: `backend/app/services/compliance_engine.py` + `POST /api/check-compliance`.
- Structured review execution exists and can policy-block based on forbidden terms in LLM output: `POST /api/structured-review` + `backend/app/services/review_execution_core.py`.

## 2. Desired Outcome

TBD.

## 3. Target User / Actor

TBD.

## 4. Rough Idea (Unstructured Thinking)

TBD.

## 5. Constraints (Initial)

- Scope: **single-call MVP only** for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Implementation: use the **universal engine** end-to-end; avoid multi-agency abstractions.
- Success definition: happy-path “one call is fully usable” (ingest+activate call, call-driven submit UI, compliance blocking, run review, call-aware results).

## 6. Risks / Unknowns

TBD.

## Open Questions / Deferred

TBD.

## 7. MVP Definition

TBD.

## 8. Explicit Non-Goals

TBD.
