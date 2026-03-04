# WF-0048 — Agency/Call Variability Policy Contract

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
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

## 2. Desired Outcome

Primary success signal: the engine rejects unknown fields and malformed variability with deterministic contract-failure semantics (stable code + field-path details) at the `call_config_snapshot` boundary.

Outcomes this enables (not necessarily fully implemented in this WF):

- Frontend/BFF stops guessing API shapes and can rely on a versioned, strict activated snapshot contract.
- Core pipeline remains call-agnostic (no identity branching); variability is expressed only through declared config/activation surfaces.
- Deterministic behavior: identical payloads yield identical serialized pipeline results (including telemetry policy as defined in contract tests).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 2)

Contract Notes / Non-obvious constraints (Section 2):

- Strict-by-default stance: reject unknown fields everywhere; introduce new fields only via version bump / explicit contract evolution.
- Determinism scope: guarantee `PipelineResult.to_dict()` determinism for the same payload (not “content-only”).
- Harden the `ReviewRequestV1` boundary first (snapshot + proposal_nodes + digest); keep broader API DTO changes out of the initial tracer-bullet slice.
- Phase 0 “good enough”: contract surfaces + error semantics + testable invariants; avoid architecture/implementation plan bloat.

## 2.1 Contract — Activated Call Config Snapshot (Boundary Schema Sketch)

Goal: the core pipeline consumes a single strict, versioned activated snapshot contract so it remains 100% call-agnostic (no call identity branching) while still allowing per-call variability via declared surfaces.

Proposed contract (v1 sketch; strict-by-default):

- Top-level request payload:
  - `request_id: str` (required)
  - `mode: "DIAGNOSTIC"|"STRICT"` (required)
  - `stage_ref: str` (required; validated)
  - `call_config_snapshot: ActivatedCallConfigSnapshotV1` (required; strict; unknown fields rejected)
  - `call_config_digest: "sha256:<hex>"` (required; must match canonical JSON of validated snapshot)
  - `proposal_nodes: dict[str, str]` (required)
  - Unknown top-level fields: rejected

- `ActivatedCallConfigSnapshotV1`:
  - `schema_version: "v1"` (required; enables explicit evolution)
  - `expectations: list[ActivatedExpectationV1]` (required)
  - Allowed extension points (all optional; strict sub-models; unknown fields rejected):
    - `stage_gating`
    - `hierarchy` / `nesting`
    - `evaluation_criteria` / `evaluation_elements`
    - `compliance_rules`
    - `reviewer_policy`
    - `prompt_knobs`
  - Unknown fields: rejected everywhere

Why this enforces “no identity branching”:

- The activated snapshot contains no agency/call identity inputs; variability is only expressed through declared config/activation surfaces inside the snapshot.

## 2.2 Contract — Deterministic Failure Semantics (WF-0045 compatible)

All boundary violations map to deterministic contract failures with stable codes and stable field-path details. Minimum required semantics:

- `CALL_CONFIG_DIGEST_MISMATCH`: digest does not match the canonical JSON of the validated snapshot.
- `MALFORMED_REVIEW_REQUEST`: schema violations (including unknown fields) with:
  - `details.field_errors: list[{path, kind, message}]` (stable ordering by path)

Additional required clarifications:

- Field path format: use JSON Pointer paths (e.g., `/call_config_snapshot/expectations/0/check_id`).
- Field error ordering: stable sort ascending by `path`, then by `kind`, then by `message`.
- Validation ordering / precedence:
  1) Parse + strict schema validation (including unknown-field rejection) for the top-level payload and the activated snapshot.
  2) Only if (1) succeeds, validate `call_config_digest` against canonical JSON of the validated snapshot.
  - Implication: schema violations always return `MALFORMED_REVIEW_REQUEST` even if the digest also would have mismatched.
- Minimum `kind` vocabulary (stable): `unknown_field`, `missing_field`, `type_error`, `value_error`.

## 2.3 Contract — Deterministic Success Semantics

The same validated payload yields identical serialized results:

- Determinism target: `PipelineResult.to_dict()` canonical JSON (sorted keys, stable list ordering).
- No nondeterministic data (timestamps, random IDs) may enter the serialized result contract (including telemetry).

## 3. Target User / Actor

Primary contract consumer we optimize for: Frontend BFF route handlers.

First “shape guessing” to eliminate: snapshot/request payload shape guessing (before expanding to results/telemetry).

Activated snapshot producer responsibility: backend service layer assembles the activated snapshot from call-definition/config + stage_ref + submitted nodes; the engine only consumes the strict snapshot (no DB lookups and no call identity branching in core execution).

Allowed “call variability input” to the producer: call-definition config + stage_ref + submitted nodes only (no agency/call_code hints and no ad-hoc runtime switches).

Minimum documentation target (Phase 1): a single strict schema doc for `ActivatedCallConfigSnapshotV1` with examples + rejection cases.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 3)

Contract Notes / Non-obvious constraints (Section 3):

- “Frontend/BFF first-class consumer” means: examples and tests are written from BFF integration perspective (what must be sent; what gets rejected; how errors are surfaced).
- Snapshot contract precedes result-contract cleanups; do not broaden v1 into review-result DTO changes.

## 4. Rough Idea (Unstructured Thinking)

High-level direction: define a strict, versioned `ActivatedCallConfigSnapshotV1` contract and enforce it at the engine boundary (request validator). The engine consumes only the typed snapshot object; core stages remain call-agnostic and interpret variability only through declared config/activation surfaces.

Design principles (non-architectural, contract-first):

- Declare explicit extension points (stage gating, hierarchy/nesting, evaluation criteria/elements, compliance rules, reviewer-policy, prompt knobs) rather than accepting ad-hoc fields.
- Reject unknown fields deterministically; evolve the contract via explicit version bumps.
- Preserve digest semantics: digest is computed from canonical JSON serialization of the validated snapshot.
- Determinism is a first-class requirement: the same validated payload yields identical serialized results (`PipelineResult.to_dict()`).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 4)

Contract Notes / Non-obvious constraints (Section 4):

- No “escape hatches” (`extensions: dict`) in v1; if flexibility is needed, add it explicitly and version it.
- Engine must not infer behavior from call identity; only from the snapshot’s declared surfaces.

## 5. Constraints

- Hard requirement: no `if agency == ...` / call-code branching in core execution; all variability is config/activation-driven.
- Strict contracts at boundaries (Pydantic strict models; reject unknown fields).
- Deterministic contract-failure semantics compatible with WF-0045.
- Keep implementation changes within the 3-file limit per task slice; if it needs more, split.
- For behavior changes, use TDD (RED/GREEN) with deterministic contract tests.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 5)

## 6. Risks / Unknowns

- Risk: “Strict-by-default” breaks existing internal producers that currently send extra fields; mitigation is incremental adoption via explicit contract evolution and targeted tests.
- Risk: Determinism fails due to nondeterministic IDs or ordering; mitigation is tests asserting stable `PipelineResult.to_dict()` output for identical payloads.
- Unknown: exact error taxonomy/details format for contract failures expected by downstream consumers (must stay WF-0045-compatible).
- Unknown: snapshot versioning strategy (`schema_version` vs implicit versioned model selection).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 6)

## Open Questions / Deferred

- What is the versioning strategy for the activated snapshot contract (e.g., `schema_version`)?
- Which fields are required vs optional for v1 (minimum viable strictness without blocking current calls)?
- Exact error taxonomy/details format for contract failures (stable field-paths; stable codes) to keep compatibility guarantees.

## 7. MVP Definition

If shipping in 2–3 days (MVP slice):

- Introduce a strict, typed `ActivatedCallConfigSnapshotV1` model (Pydantic strict, `extra="forbid"` or equivalent) as the sole engine-consumed snapshot boundary (no loose dict).
- Enforce validation in `validate_review_request_payload()` with deterministic contract-failure semantics:
  - unknown fields rejected
  - malformed variability rejected
  - errors include stable codes and stable field-path details
- Add deterministic contract tests proving:
  - unknown fields are rejected
  - no call-identity branching is required
  - identical payload yields identical serialized results

Explicitly excluded from MVP:

- Refactoring frontend/BFF consumers (beyond relying on the now-strict boundary).
- Reworking broader API DTOs for review results beyond what is needed to keep determinism tests stable.
- Hardening call-definition ingestion pipelines (separate follow-up once snapshot contract is proven).

## 7.1 Migration / Rollout Notes (Incremental + Reversible)

- Land the strict activated snapshot parsing in the request validator behind deterministic tests first (no functional expansion of variability).
- Ensure existing internal producers are updated to emit the new required `schema_version` and to remove any unknown fields before flipping strict rejection in prod.
- If a break is discovered, revert by rolling back the strict validator change (tests remain as the safety net for re-landing).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 7)

## 8. Explicit Non-Goals

- No agency/call identity branching inside the core engine (this is a prohibition, not a deliverable).
- No new competitive-analysis features inside the core pipeline (keep any such work out-of-core / separate WF).
- No broad redesign of the review UI or cross-endpoint API harmonization in this WF’s first tracer-bullet slice.
- No “forward-compat via unknown fields” mechanism; contract evolution is explicit and versioned.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0048-agency-call-variability-policy.md` (Section 8)
