# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-01

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- Any contract changes must preserve:
  - API error semantics/idempotency (notably `IDEMPOTENCY_PAYLOAD_MISMATCH` and existing 4xx/5xx mappings)
  - `/app/reviews` persistence behavior (review record creation + status transitions)

---

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- Backend create endpoints: `POST /api/structured-review` (structured multi-node) and `POST /reviews` (single-snippet).
- Both endpoints enforce `Idempotency-Key` + payload hash (`request_payload_sha256`); mismatch returns `IDEMPOTENCY_PAYLOAD_MISMATCH`.
- Reviews are persisted early (review row created before engine work); execution failures appear as `review.status=FAILED` with an `overall_summary` message rather than an API error for many runtime/LLM/policy failure modes.
- Reviewer-policy enforcement is in `backend/app/services/review_execution_core.py`:
  - `POST_CHECK` + `BLOCKING` run deterministic forbidden-term scans on LLM feedback text
  - `BLOCKING` triggers up to 2 attempts, then fails with `POLICY_BLOCKING`
- Existing tests already cover many related seams (`backend/tests/test_api.py`, `backend/tests/test_review_execution_core.py`, `backend/tests/test_structured_reviewer_service.py`), but the “hardening target” (trust + regression bundle) is not yet captured as a single explicit contract suite.

## Open Questions / Deferred (Phase 0.1)

- Which single flow is the hardening target for this WF: `POST /api/structured-review`, `POST /reviews`, or both?
- What *exactly* is the `/app/reviews` persistence contract for execution failures (timeout, policy blocking, response validation failure)?
- What is the “deterministic verification bundle” artifact: documented checklist, pytest subset, fixture matrix, or a combination?
- What are the top 3 regressions we’re guarding against (invariants, not just “trust”)?

---

## 1. Problem Statement

Hardening needed for the single-call MVP for `nwo_veni_2025_preproposal`:
- Preserve API error semantics + idempotency invariants.
- Preserve review persistence + failure-state semantics used by `/app/reviews`.
- Add confidence that reviewer-policy enforcement (blocking/post-check/prompt-only) cannot silently regress.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 1)
