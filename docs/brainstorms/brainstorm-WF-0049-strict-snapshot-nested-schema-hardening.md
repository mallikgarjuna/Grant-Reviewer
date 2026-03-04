# WF-0049 — Strict Snapshot Nested Schema Hardening

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-04

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0049-strict-snapshot-nested-schema-hardening.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions.
- The Q&A transcript is rationale only.
- WF-0049 scope is contract hardening at the request boundary; no pipeline-mode product expansion.

## 1. Problem Statement

`ActivatedCallConfigSnapshotV1` now enforces strict top-level boundary behavior, but several declared extension surfaces are still loosely typed (`dict[str, object]` / `list[dict[str, object]]`).
That leaves drift risk: payloads can pass boundary validation while still carrying ambiguous nested shapes that are not contract-governed.

## 2. Desired Outcome

- Nested snapshot extension surfaces become strict, versioned models with unknown-field rejection at every level.
- Existing producer payloads either validate deterministically or fail with actionable deterministic `field_errors`.
- Digest behavior remains deterministic across omitted/default nested fields.

## 3. Target User / Actor

- Backend engine maintainers preserving request-contract integrity.
- Producer/BFF integrators who need stable schema feedback.
- Workflow owners managing multi-call variability without introducing call-identity branching.

## 4. Rough Idea (Unstructured Thinking)

Create explicit Pydantic nested models for currently loose extension points and wire them into `ActivatedCallConfigSnapshotV1`.
Add a producer-compatibility fixture matrix for current payload sources and lock digest semantics using schema-validated projection rules.

Contract notes:
- No `extensions: dict` escape hatch in v1.
- No changes to `PipelineResult` public contract in this WF.

## 5. Constraints

- Keep behavior deterministic and backward-compatible where contract allows.
- Avoid touching unrelated UI/API products.
- Preserve no-identity-branching policy.
- Keep implementation slices to <=3 files per task.

## 6. Risks / Unknowns

- Producer payload drift: some existing snapshots may contain undeclared nested keys.
- Over-hardening risk: too-strict nested schemas may block legitimate near-term payload evolution.
- Digest regressions if canonicalization includes synthesized defaults inconsistently.

## Open Questions / Deferred

- Should some nested surfaces remain intentionally permissive in v1 (with strict shape only for currently active fields)?
- Should we introduce `schema_version: "v1.1"` immediately or keep WF-0049 inside current `v1` with additive strictness?
- Deferred: broader DTO/API redesign and frontend policy UX.

## 7. MVP Definition

Smallest functional slice:
- Strict nested schemas for active extension surfaces currently used by producer paths.
- Deterministic validation errors and digest compatibility tests for those surfaces.
- CI-selectable contract tests for nested-shape invariants.

## 8. Explicit Non-Goals

- New business features in review pipeline stages.
- Any call-identity-specific logic paths.
- Performance optimization unrelated to contract correctness.
