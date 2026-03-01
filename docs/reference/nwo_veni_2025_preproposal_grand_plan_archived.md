# NWO Veni 2025 Pre-proposal — Archived Grand Plan (Reference Only)

**Status**: Archived reference.

This document is a *north-star* plan captured during design. It is **not** an active workflow (WF) artifact and must **not** be used as an implementation checklist.

Execution should be done via the parking-lot chunk items:
- `docs/parking_lot.md` (P1 #5–#12)
- Chunk boilerplate: `docs/reference/nwo_veni_2025_preproposal_north_star.md`

**Important**:
- Do **not** reuse any placeholder WF ID mentioned in older drafts. Always mint the next WF ID from `docs/index.md`.
- Keep each chunk strictly scoped to its own WF (small, incremental, shippable).

## Summary (what this delivers)

Implement end-to-end PeerLens support for `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml` as a **structured-input** experience:

- **3 nodes**: `academic_profile`, `key_outputs`, `research_idea` (with domain-specific word limit for ENW pilot).
- **Evaluation**: single evaluation criterion with **8 evaluation elements**, producing ReviewCards.
- **Compliance**: deterministic rule checks **separate from evaluation** (ERROR/WARNING), displayed in the UI.
- **Alignment**: requires `academic_profile + research_idea`; when missing, create cards as **NOT_ASSESSABLE** (never fabricate).
- **Assisted extraction (paste-only)**: “extract → preview + confidence + confirm → fill field”; **.docx/.pdf deferred to parking lot**.
- **Persistence**: structured reviews are stored in Postgres and appear in review history (same `/reviews/*` UX).

---

## Workflow execution note (how to actually run this now)

Do not attempt to execute this plan as one WF. Instead, promote and execute one chunk at a time from `docs/parking_lot.md`:

- `pick P1 #5` (WF-1: YAML parse + V2 loader; dry-run only)
- then proceed through `pick P1 #6` … `pick P1 #12` as independent WFs

---

## Decisions (lock now; implement exactly)

Record these in `docs/logs/decisions.md` under the WF ID that actually implements the relevant change (each chunk is its own WF):

1. **Full-stack scope**: backend + frontend + persistence.
2. **Persistence model**: structured submissions stored in normalized tables; `Review` can target either a snippet or a structured submission (exactly one).
3. **Compliance** is deterministic, stored, and returned alongside evaluation results; it does **not** block evaluation execution.
4. **NOT_ASSESSABLE** is a first-class card state (typed) and never LLM-generated.
5. **Assisted extraction**: paste-text only for the initial extraction chunk; docx/pdf deferred.

---

## Backend changes (implementation details)

### A) Fix the NWO Veni YAML so it is parseable

File: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`

- Convert the invalid inline `:contentReference[...]` fragments into comments (at least the two `source_section` lines for `key_outputs` and `research_idea`).
- Do **not** change semantics/IDs/limits.

Acceptance check (non-DB): `cd backend && uv run python scripts/ingest_call.py ... --dry-run` should at least parse YAML after fix (even if schema mismatch remains).

### B) Add “Call Definition V2” schema + loader (supports rich YAML)

New module:

- `backend/app/schemas/call_definitions_v2.py` (Pydantic models) supporting:
  - `funding_agency.{id,name,country}`
  - `funding_call.{id,code,title,year,stage,language,deadlines,domain_notes}`
  - `evaluation_criteria[].{id,name,stage,weight_percent,evaluation_elements[]}`
  - `proposal_nodes[].{id,label,node_type,source_section,content_constraints,guidance_text,compliance_rules,node_expectations}`
  - `runtime_notes[]`
- Validation:
  - all `evaluation_element_id` refs exist
  - all IDs unique within their namespace (`crit_*`, `elem_*`, `comp_*`, `node ids`)
  - node count expected = 3 for this call (strict, because UI is specialized)

Loader:

- `backend/app/services/call_definition_loader.py`
  - `load_call_definition_from_yaml(path) -> CallDefinitionV1 | CallDefinitionV2`
  - version detection:
    - if `funding_agency.short_name` exists ⇒ V1 (`app/schemas/call_definitions.py`)
    - elif `funding_agency.id` exists ⇒ V2
  - loader is used by:
    - ingestion
    - structured-input config endpoint
    - compliance engine

### C) DB schema extensions (Alembic migration)

Modify SQLModel domain + add migration (new revision) to support:

1. **Stable logical IDs** (for traceability back to YAML):
   - `proposal_nodes.logical_id` (nullable string; unique per `(funding_call_id, logical_id)`)
   - `evaluation_criteria.logical_id` (nullable string; unique per `(funding_call_id, logical_id)`)
   - `evaluation_elements.logical_id` (nullable string; unique per `(evaluation_criterion_id, logical_id)` or `(funding_call_id, logical_id)` via join strategy)
2. **Structured submissions** (persist the 3-node structured input):
   - `structured_submissions`:
     - `id` (UUID PK)
     - `user_id` (FK users)
     - `funding_call_id` (FK funding_calls)
     - `domain_id` (nullable string; values like `science_enw` or null)
     - `created_at`
   - `structured_submission_sections`:
     - `id` (UUID PK)
     - `structured_submission_id` (FK)
     - `proposal_node_id` (FK proposal_nodes)
     - `text` (non-null)
     - unique `(structured_submission_id, proposal_node_id)`
   - `structured_key_outputs`:
     - `id` (UUID PK)
     - `structured_submission_id` (FK)
     - `order_index` (int)
     - `reference_text` (text, can be empty)
     - `explanation_text` (text, required)
3. **Review targets**:
   - Make `reviews.proposal_snippet_id` nullable
   - Add `reviews.structured_submission_id` nullable FK
   - Add DB check constraint: exactly one of the two is non-null
4. **Compliance findings persistence**:
   - new enum `ComplianceSeverity = ERROR | WARNING | INFO`
   - `compliance_findings`:
     - `id` UUID PK
     - `review_id` FK reviews
     - `proposal_node_id` nullable FK proposal_nodes (nullable for global findings)
     - `rule_id` string (e.g., `comp_max_10_outputs`)
     - `severity` enum
     - `message` string
     - `details_json` text (JSON string; optional)
     - `order_index` int

### D) Ingestion: support V2 YAML without breaking V1

Update `backend/scripts/ingest_call.py` to:

- load via `call_definition_loader` and ingest either V1 (existing behavior) or V2.
- V2 ingestion mapping rules (exact):
  - FundingAgency:
    - `short_name = funding_agency.id.upper()` (e.g., `NWO`)
    - `name = funding_agency.name`
  - FundingCall:
    - `code = funding_call.code` (e.g., `nwo_veni_2025_preproposal`)
    - `name = funding_call.title`
    - `call_year = funding_call.year`
    - `is_active = True`
  - EvaluationCriterion / Element:
    - persist `logical_id` from YAML `id`
    - persist name/description
  - ProposalNode:
    - `logical_id = node.id` (e.g., `academic_profile`)
    - `title = node.label`
    - set `node_type = SECTION` (flat list; no hierarchy)
    - keep `guidance_text`
  - NodeExpectations:
    - unchanged persistence model; just map `evaluation_element_id` via logical ids

### E) Compliance engine (deterministic; no LLM)

New module: `backend/app/services/compliance_engine.py`

- Inputs:
  - call code (or call_id) + domain_id
  - structured payload (`academic_profile` text, `research_idea` text, `key_outputs[]`)
  - call definition V2 (for constraints + rule metadata)
- Output: ordered list of `ComplianceFinding` records (maps 1:1 to DB model + API schema)
- Implement required rules:
  - Academic profile:
    - word count 400–700 ⇒ ERROR
    - prohibited metrics: `h-index`, `h index`, `journal impact factor`, `JIF` (case-insensitive) ⇒ ERROR
    - independence/target-group mention heuristic (keyword-based) ⇒ WARNING
  - Key outputs:
    - max items ≤ 10 ⇒ ERROR
    - each output has non-empty explanation ⇒ ERROR
    - total explanation word count 400–700 ⇒ ERROR
    - prohibited metrics (same patterns) in reference or explanation ⇒ ERROR
  - Research idea:
    - max words = 100 default; 500 if `domain_id == "science_enw"` ⇒ ERROR
    - methodological overload heuristic ⇒ WARNING
    - alignment reference present heuristic ⇒ WARNING

### F) Structured review service (LLM + NOT_ASSESSABLE)

New module: `backend/app/services/structured_reviewer_service.py`

- Responsibilities (in order):
  1. Persist structured submission (sections + outputs) under the authenticated user.
  2. Run compliance engine and persist compliance findings.
  3. Build the evaluation “expectation set”:
     - fetch all node expectations for the 3 nodes
     - compute assessability:
       - for `elem_cv_idea_alignment` and `elem_alignment_plan_credibility`, require both `academic_profile` and `research_idea`
       - if missing, mark those expectations **NOT_ASSESSABLE** (no LLM call for them)
  4. Build a single prompt containing:
     - per-node guidance + user content
     - key outputs rendered as numbered items (reference + explanation)
     - expectation list only for assessable expectations
     - strict JSON-only response format identical to current
  5. Call LLM (same client), validate cardinality for assessable expectation IDs only.
  6. Create Review + ReviewCards:
     - add `assessment_status` on ReviewCard: `ASSESSED | NOT_ASSESSABLE`
     - `NOT_ASSESSABLE` cards: deterministic feedback, e.g., “Not assessable: missing academic_profile text required for alignment.”
- Update prompt builder strategy:
  - new `backend/app/services/structured_prompt_builder.py` (do not overload `prompt_builder.py`)

### G) Backend API surface (FastAPI)

Add/extend endpoints in `backend/main.py` + schemas in `backend/app/schemas/api.py`:

1. `GET /calls/{call_id}/structured-config`
   - Only for calls backed by V2 structured UX (currently NWO Veni 2025 preproposal)
   - Returns:
     - node logical ids + labels + guidance
     - constraints (word limits, max outputs)
     - supported domains (include `science_enw` + default)
2. `POST /structured-extraction/preview`
   - Body: `{ call_id, target_node_logical_id, raw_text }`
   - Response: `{ extracted_text, confidence, reasons[], preview }`
   - Implement call-specific heading heuristics for 2a/2b/3 markers; confidence scoring is deterministic.
3. `POST /structured-reviews`
   - Body contains:
     - `call_id`
     - `domain_id` optional
     - `academic_profile_text` (optional but recommended)
     - `research_idea_text` (optional)
     - `key_outputs[]` list (each `{ reference_text, explanation_text }`)
   - Apply idempotency/quota logic identical to `/reviews`.
4. Extend `GET /reviews/{review_id}` response:
   - add optional `compliance_findings: ComplianceFinding[]`
   - ensure existing clients remain compatible (field optional)
5. Extend `GET /reviews` list:
   - if structured submission: `node_title` becomes `"Pre-proposal (structured)"` (or derived from call stage)
6. Extend `DELETE /reviews/{review_id}`:
   - delete compliance findings + structured submission graph when present

---

## Frontend changes (Next.js)

### A) Call-aware submit UI (specialized for NWO Veni)

Modify `frontend/src/app/app/page.tsx`:

- Detect selected call by `call.code === "nwo_veni_2025_preproposal"`.
- Swap from “single snippet” form to “structured pre-proposal” form:
  - domain selector (default / ENW Science pilot)
  - academic profile textarea + live word count + limit indicators
  - key outputs editor:
    - add/remove items up to 10
    - each item has:
      - reference input
      - explanation textarea
    - show total word count of explanations
  - research idea textarea + live word count and dynamic max (100/500)

### B) Assisted extraction UI (paste-only)

- Add per-section “Assist extraction” action that opens a modal:
  - paste raw full text
  - choose target section
  - call BFF `POST /structured-extraction/preview`
  - show preview + confidence + reasons
  - require explicit “Use this text” confirmation to fill the section field

### C) BFF wiring

Update:

- `frontend/src/lib/bff/types.ts`: add request/response types for:
  - structured config
  - extraction preview
  - structured review create
  - compliance findings on review detail
- `frontend/src/lib/bff/adapter.ts`: add functions mirroring backend endpoints.
- Add Next route handlers under `frontend/src/app/api/bff/…` for:
  - `structured-config`
  - `structured-extraction`
  - `structured-reviews`

### D) Review detail UI: show compliance separately

Modify `frontend/src/app/app/reviews/[reviewId]/page.tsx`:

- If `compliance_findings` present:
  - render a “Compliance” section above review cards
  - group by severity (ERROR first, then WARNING)
  - optionally group by node label (academic profile / key outputs / research idea)
- For NOT_ASSESSABLE cards:
  - display a distinct visual state (neutral styling) and the deterministic message

### E) Local “review attempt” storage + retry

Update `frontend/src/lib/review-attempt` logic to support a second draft shape:

- `kind: "snippet" | "structured_preproposal"`
- Ensure retry on the review detail page replays the correct create call and payload hash logic.

---

## Testing & verification (must be concrete)

Backend (`cd backend`):

1. Unit tests for compliance engine:
   - word count boundary cases (399/400/700/701)
   - prohibited metric detection variants (`h index`, `H-Index`, `JIF`, `Journal Impact Factor`)
   - key outputs:
     - 11 items triggers ERROR
     - missing explanation triggers ERROR
     - word count excludes reference fields by construction (explanations only)
   - research idea domain max 100 vs 500
2. API tests (extend `backend/tests/test_api.py`):
   - `POST /structured-reviews` creates a review with:
     - compliance findings persisted and returned
     - cards created for all expectations; alignment expectations become NOT_ASSESSABLE when `academic_profile_text` missing
   - `GET /reviews/{id}` includes compliance list when present
   - list reviews includes a sensible `node_title` for structured reviews
3. Manual smoke (stub mode):
   - set `LLM_MODE=stub` and hit structured create once; ensure idempotency works.

Frontend (`cd frontend`):

- Manual: confirm the structured form renders only for the Veni call; submit flows to the new endpoint; review page shows compliance + cards.

---

## Acceptance criteria (definition of done)

1. Ingesting NWO Veni YAML succeeds and registers:
   - 1 criterion, 8 evaluation elements, 3 nodes with logical IDs.
2. Structured submit supports:
   - academic profile text
   - key outputs list editor (≤10)
   - research idea text
   - domain selector toggling 100/500 max words
3. Compliance findings render separately from evaluation cards and persist with the review.
4. Alignment elements are **NOT_ASSESSABLE** if either `academic_profile` or `research_idea` is missing; the system never asks the LLM to “guess” alignment.
5. Assisted extraction (paste-only) works with preview + confidence + explicit confirmation before inserting extracted text.
6. Review history includes structured reviews and they can be opened and deleted.

---

## Explicit assumptions (fixed)

- Word counting uses a deterministic tokenization (`\\b\\w+\\b`) and is applied exactly as described in the compliance engine section.
- Key outputs word limit is enforced on **explanation_text only** (because references/URLs/types/indicators are excluded).
- “No h-index/JIF” detection is regex-based and errs on the side of flagging (better false positive than missed compliance).
- Structured reviews use the same quota and idempotency mechanism as snippet reviews.
