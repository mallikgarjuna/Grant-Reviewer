# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
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

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 4)

Direction (MVP):
- Remove all call-specific hardcoding in the applicant experience by making submit + review-detail UI entirely call-driven from backend call metadata/config.

Concrete targets (repo-grounded):
- Review detail page currently hardcodes Veni node labels/order (`VENI_NODE_LABELS` / `VENI_NODE_ORDER`) and must be made call-aware.
- Backend already returns `node_title`, `criterion`, and `evaluation_element_name` per card in `GET /reviews/{review_id}`; UI should use these fields directly (and only add stable IDs as an optional “info” affordance).
- Submit UI already renders nodes from APIs; ensure it supports arbitrary node counts without per-call assumptions.
- Domain options are currently hardcoded client-side; domain selector must be driven by backend metadata/config and only appear when the selected call declares domain-limited constraints.

Open questions / gaps to resolve:
- Review detail ordering requires call-driven ordering metadata; today the review detail payload does not include `call_id`, so the page cannot fetch `/calls/{call_id}/nodes` without a contract change.
- Current review detail page uses a Veni-only coverage summary (`submitted_nodes` query param + hardcoded Veni labels/order); this must be replaced by call-driven coverage derived from stored structured payload + call nodes metadata.

## 5. Constraints (Initial)

- Scope: **single-call MVP only** for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Implementation: use the **universal engine** end-to-end; avoid multi-agency abstractions.
- Success definition: happy-path “one call is fully usable” (ingest+activate call, call-driven submit UI, compliance blocking, run review, call-aware results).
- No call-specific hardcoding: avoid “Veni-only” mappings in UI/API; behavior must be driven by canonical call definition + DB/API metadata/config (even though this WF ships only one call).
- Domain options must not be hardcoded client-side; domain selection UX must be sourced from backend call metadata/config.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 5)

Hard constraints (MVP):
- We may extend/add **generic** contracts/metadata so UI is fully call-driven; validate primarily with Veni, but ship nothing Veni-specific.
- Hardcoding is forbidden in both backend and frontend (no per-call maps/branches/constants for labels/order/domain options).
- Domain selection is optional and call-specific: frontend shows a selector only when backend exposes domain options for the selected call.
- Each submit persists a Review and appears in `/app/reviews`; do not break review history.
- Review detail ordering/grouping must be call-driven (use DB node ordering); if current review-detail contracts lack what’s needed, extend them generically.

Required generic contract changes (allowed in WF-0041):
- Review detail response must include `call_id` (and `call_code`) so the UI can fetch call nodes and order/group sections deterministically by `order_index`.
- Call metadata/config must expose `domain_options[]` (may be empty) when domain applies; frontend renders a selector only if non-empty.

Contract safety / invariants (must preserve):
- Preserve API error semantics and idempotency behavior (e.g., `DOMAIN_REQUIRED`, `DOMAIN_INVALID`, `UNKNOWN_NODE_ID`, `IDEMPOTENCY_PAYLOAD_MISMATCH`, `QUOTA_EXCEEDED`).
- Preserve persistence side effects: each submit persists a Review and it appears in `/app/reviews`.

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0041-nwo-veni-2025-preproposal-single-call-mvp.md` (Section 6)

Key risks:
- Review detail ordering can’t be truly call-driven without call identification/ordering metadata available to the page; may require a generic API contract extension (e.g., include `call_id` and/or ordered node list in review detail response).
- Domain options are currently frontend-hardcoded; removing hardcoding requires backend-exposed domain options metadata that is present only for calls that define domain-limited constraints.
- Reviewer-policy blocking can fail reviews if the LLM output contains forbidden terms; we need a single server-side retry seam to keep the happy path resilient without weakening policy enforcement.
- “Arbitrary node count” can regress silently if we only test Veni; we need at least one additional structured call shape for test coverage (tests-only, not product scope expansion).

Compliance honesty risk:
- Some YAML constraints are non-enforceable deterministically in plain text (e.g., `max_items`); for MVP we will surface these as informational guidance to the researcher, not blocking enforcement.

## Open Questions / Deferred

Deferred (explicitly not in WF-0041):
- Iterative “revise/resubmit loop” UX improvements (beyond current persisted review history).
- Assisted extraction UX (paste-only preview/confirm) and `.docx`/`.pdf` ingestion.
- Multi-step evaluation gating (ERC Step 1 vs Step 2) and any ERC/MSCA-specific domain concepts.
- Heuristic/approximate enforcement for non-enforceable constraints (e.g., parsing `max_items` from plain text).

Open questions (must be resolved in planning before implementation):
- Exact DTO additions for review detail (`call_id`, `call_code`, and whether to include ordered node list vs fetch nodes separately).
- How to surface stable IDs as an “info” affordance per card (e.g., `evaluation_element_id`, `node_expectation_id`) without harming UX.
- How to compute coverage summary deterministically from stored structured payload and call nodes (no query-param hacks).

## 7. MVP Definition

MVP checklist (WF-0041 “done”):
- Ingest+activate `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml` via standard ingestion (no manual per-call wiring).
- Universal submit UI renders all call-defined nodes (arbitrary count) using backend nodes + metadata, with no per-call branching.
- Domain selector appears only if backend exposes `domain_options[]`; domain affects only domain-limited constraints for calls that define it.
- Deterministic compliance blocks on enforceable constraints (presence + word limits + domain-limited word limits); non-enforceable constraints are informational only.
- Structured review runs via universal engine and produces cards that show proposal section + evaluation element + criterion (criteria/elements grounding).
- Review detail page is fully call-driven (no Veni hardcoding): deterministic section grouping and ordering based on call nodes metadata (`order_index`), with optional “info” affordance for stable IDs.

## 8. Explicit Non-Goals

Non-goals (WF-0041):
- No multi-agency abstractions or “framework” work beyond generic contract/metadata needed to remove hardcoding.
- No new calls added as product scope; use existing canonical calls only for tests to validate “arbitrary node count.”
- No changes to evaluation logic beyond what’s required for universal call-driven execution and presentation.
