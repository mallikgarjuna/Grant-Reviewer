# Architectural Decisions (Domain)

- **Hierarchy Structure**: All hierarchical levels of a grant proposal are stored in a single `ProposalNode` table with a reflexive `parent_node_id` foreign key. The universal renderer binds state by `logical_id` (V2 YAML) but the DB persists by UUID.

- **V2 YAML vs V1 YAML**: Detect V2 schema via `funding_agency.id`. V1 schema uses `funding_agency.short_name`. If building/expanding universal rendering, fail-fast on unsupported recursive arrays/nested nodes until full P2 implementation is ready.

- **Review Output**: The SSOT output for the peer review engine is `DiagnosticFinding v1`. `ReviewCard` is a compatibility surface for the UI and persistence that aggregates grouped findings deterministically.

- **Trace-First Schema**: Findings MUST include required traceability fields (`criterion_ref`, `element_ref`, `primary_expectation_ref`, `check_id`, `subject_ref`). Anchors (`TEXT_SPAN`, `STRUCTURAL_LOCATOR`) are mandatory.

- **Pipeline Structure**: The pipeline model is two-pass. Pass 1 produces normalized `Observation v1`. Pass 2 maps observations to `DiagnosticFinding v1`.

- **Versioning Discipline**: Treat `Call Definition V2` and engine contracts like `ReviewRequest v1`, `Observation v1`, and `DiagnosticFinding v1` as real compatibility versions. Treat the current review engine as `current` or `base` unless/until a real successor exists; avoid implying a live product-line split with casual `pipeline v1` shorthand.

- **Review Stage Strictness**: `review_stage` (`STEP_1`/`STEP_2`) is explicit API input. Critical reviewer constraints like "Excellence-only" at Step 1 are `BLOCKING` rather than warning-only.

- **Error Semantics vs Execution Failures**: Contract failures (e.g. malformed inputs) reject the entire request with NO partial findings. Execution failures (e.g. LLM timeout) indicate the engine failed.

- **Idempotency**: Client-side idempotency via UUID v4 session identifier passed as `Idempotency-Key` header on submission. Bounded polling every 3 seconds with a 90-second cap is used for tracking backend review process.

- **Review Detail Contract State**: When `ReviewDetailResponse` adds state fields such as `detail_state`, set them in `backend/main.py` `/reviews/{id}` assembly. Do not make BFF inference the only source of truth.

- **Review Runtime Split (2026-03-08)**: `POST /reviews` runs through `ReviewerService.generate_review`; `POST /api/structured-review` runs through `StructuredReviewerService.generate_structured_review_pipeline_v1` and `pipeline_v1`. `QUOTA_EXCEEDED` / `REVIEWS_DISABLED` are API-boundary gates in `backend/main.py`, so planning/tests must prove downstream non-invocation instead of inventing a service-entry gate.

- **ERC Stage Truth Drift (2026-03-09)**: Current ERC StG canonical data mixes `BOTH` and `STEP_2` elements on `b2_part2_scientific_proposal`, so node metadata derives `BOTH` while official process says B2 is Step 2 only. BFF currently coerces invalid `review_stage` to `STEP_1`, and structured runtime does not call `activate_expectations_for_stage()`. Treat ERC stage truth as unresolved until one authoritative source drives metadata, validation, execution, and review evidence together.

- **Structured Snapshot Reality (2026-03-11)**: `backend/app/engine/contracts.py` allows optional `evaluation_criteria` / `evaluation_elements` in `ActivatedCallConfigSnapshotV1`, but `backend/app/services/structured_reviewer_service.py` currently sends an expectations-only `call_config_snapshot` into runtime validation/execution. Do not treat contract type surface alone as proof that richer canonical call fidelity reaches runtime behavior.

- **WF-0076 Runtime Lookup Seam (2026-03-12)**: For ERC PoC runtime subordinate-prompt carriage, map by existing identity `NodeExpectation.element.logical_id -> canonical_json.evaluation_criteria[*].evaluation_elements[*].id` and project onto expectation-level `subordinate_prompts`. Why: keeps the seam additive and sourced from active `CallDefinition.canonical_json` without new persistence.

- **WF-0076 Runtime Consumption Signal (2026-03-12)**: `evaluate_expectations` now emits deterministic reason suffix `subordinate_prompt_ids=<id1,id2,...>` when expectation-level subordinate prompts are carried. Why: provides an active-path runtime proof surface consumed by both findings and compatibility review-card feedback.

- **WF-0076 Presentation Seam (2026-03-12)**: Researcher-facing rendering for machine feedback `content_evaluated;subordinate_prompt_ids=...` is now scoped to `StructuredReviewerService._resolve_feedback_text_for_card` for `ERC-2026-PoC` only, mapping IDs to canonical subordinate prompt text with deterministic order and unresolved-ID fallback. Why: improves readability without mutating engine-level raw `reason` traceability or widening cross-call behavior.

- **WF-0077 Guidance Seam (2026-03-13)**: For deterministic researcher-facing guidance improvements on the structured path, prefer `StructuredReviewerService._resolve_feedback_text_for_card` over evaluator, compatibility mapper, or frontend-only transforms. Why: evaluator/mapper must preserve machine-oriented cross-call traceability semantics, while the service already owns bounded user-facing rewrites with seam-specific regression tests.

- **WF-0077 Raw Reason Reality (2026-03-13)**: Current persisted/API `ReviewCard` surfaces expose `feedback_text` and `not_assessable_reason`, not engine card `reason`. Why: a backend-only `StructuredReviewerService` slice can honestly prove only that the mocked machine reason/source string remains unchanged while guidance is derived into `feedback_text`; proving a new persisted audit field would require a wider seam.

- **WF-0078 Planned Synthesis Seam (2026-03-13)**: For structured-review LLM synthesis, keep `pipeline_v1` as deterministic SSOT and add per-card synthesis downstream in `StructuredReviewerService` with an additive synthesis surface, explicit input exclusions (no raw machine `reason`, no full proposal/call-definition prompting), and per-card fail-closed fallback to WF-0077 deterministic guidance. Why: preserves auditability and avoids turning synthesis availability into whole-review availability.

- **WF-0078 Carry-Through Constraint (2026-03-13)**: Current structured-review persistence/API/detail/export paths still center on persisted `ReviewCard.feedback_text` and `ReviewCardSummary.feedback_text`. Why: a new synthesized companion/provenance field can be proven backend-only at the service seam, but any ship-ready researcher-facing rollout needs an explicit persistence/API/frontend carry-through decision and verification rather than assuming the additive field will surface automatically.

- **WF-0078 Seam Proof Surface (2026-03-13)**: `StructuredReviewerService` now keeps additive synthesis evidence only in-memory via typed `last_synthesis_requests` / `last_synthesis_results`, backed by `StructuredReviewSynthesisService`. Why: gives service-test-visible proof of accepted/rejected per-card synthesis without mutating persisted `ReviewCard.feedback_text` or widening API/storage contracts.

- **WF-0078 Synthesis Entry Gate (2026-03-13)**: ERC PoC additive synthesis must only run when the card already has approved WF-0077 deterministic guidance (`Revise ...`), canonical same-element subordinate-prompt context, and same-card node title context in the typed request. Why: otherwise the backend seam drifts beyond the approved prompt boundary and can synthesize off weak/raw machine surfaces.
