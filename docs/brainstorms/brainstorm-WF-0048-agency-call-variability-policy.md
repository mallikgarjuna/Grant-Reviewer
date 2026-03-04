# WF-0048 — Agency/Call Variability Policy Contract

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.

---

## Repo Reality Snapshot (Read-Only) — 2026-03-04

- `call_config_snapshot` is produced in `backend/app/services/structured_reviewer_service.py` as a loose `dict`.
- `backend/app/engine/review_request_validator.py` validates minimal shape + digest, but does not strictly reject unknown fields.
- Engine boundary uses `backend/app/engine/contracts.py:ReviewRequestV1.call_config_snapshot: dict` (untyped boundary).
- Core pipeline reads snapshot dict directly (`backend/app/engine/pipeline_v1.py`) with no strict snapshot model.
- There are already engine utilities that expect richer config surfaces (e.g., stage gating; evaluation criteria/elements), but they are not enforced at the snapshot boundary.

## 1. Problem Statement

Problem: `call_config_snapshot` is an untyped boundary, so variability can leak in as ad-hoc fields and consumers (frontend/BFF) end up guessing API shapes; core pipeline risks silent drift across calls.

Who is harmed: Frontend/BFF developers integrating review submission and rendering results across multiple calls.

Why now: WF-0045 established a call-agnostic base pipeline; the deferred follow-up is to lock variability behind a strict, declared contract so the core remains 100% call-agnostic and external layers stop inferring/guessing shapes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 1)

Contract Notes / Non-obvious constraints (Section 1):

- Canonical term is **evaluation criteria/elements** (not “rubric”) at researcher-facing boundaries.
- Hard requirement: core execution has **no call identity branching** (no `if agency == ...`, no call-code branching); all variability must be expressed via declared config/activation surfaces.
- Contract boundary requirement: strict typed input/output models (Pydantic strict) that reject unknown fields; violations map to deterministic contract-failure semantics (compatible with WF-0045).
- Activated snapshot must include explicit allowed extension points: stage gating, hierarchy/nesting, evaluation criteria/elements, compliance rules, reviewer-policy, prompt knobs.

## Open Questions / Deferred

- What is the versioning strategy for the activated snapshot contract (e.g., `schema_version`)?
- Which fields are required vs optional for v1 (minimum viable strictness without blocking current calls)?
- Exact error taxonomy/details format for contract failures (stable field-paths; stable codes) to keep compatibility guarantees.
