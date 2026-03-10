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
