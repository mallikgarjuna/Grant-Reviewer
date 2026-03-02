# WF-0044 — P1 #12: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-02

Q&A transcript (archived): docs/brainstorms/qna/brainstorm-QnA-WF-0044-call-yaml-source-gated-migration.md

---

## Changelog

- v0.1 (2026-03-02): Capture scope lock + gating rules + runtime utilization matrix; add explicit requirement to wire `reviewer_policy` into structured pipeline v1.
- v0.2 (2026-03-02): Resolve Phase 0.2 blockers: define “minimal-change re-authoring”, add planned verification commands, and lock applicability tagging approach.

## Repo Reality Snapshot (Read-Only) (2026-03-02)

- Call YAML authoring workflow is codified in `docs/call-yaml/authoring-workflow.md`, including explicit source gates (structure + evaluation sources required) and conservative node↔element mapping.
- Canonical v2 call YAMLs already exist for the required baseline calls:
  - `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
  - `backend/data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml`
  - `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
- Each existing canonical YAML references a traceability manifest in `backend/data/calls/sources/*.sources.md`.
- Ingestion path supports both v1 and v2 schemas; v1/v2 detection is based on `funding_agency.short_name` (v1) vs `funding_agency.id` (v2). Mixing keys is a hard error (see `backend/scripts/ingest_call.py`).
- Existing `erc_cog_2026_full_official.yaml` lives under `backend/data/calls/legacy/erc/` and is v1-shaped; this WF’s primary target is a new canonical v2 `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml` plus upload-gated re-authoring/traceability updates.

Key open questions raised by repo reality:

- Should `erc_cog_2026_full_official` remain v1-shaped forever as a legacy mirror (recommended per your Q1:A), or should we also add an explicit “legacy mirror policy” note in the new traceability manifest?
- Where should uploaded PDFs/DOCX live: keep external absolute paths in `.sources.md` like prior WFs did, or move/copy into a repo-controlled folder for portability?
- What exactly constitutes the “validation baseline/preflight”: schema validate only, `ingest_call.py --dry-run` only, or also full DB ingest + selected pytest?
- For NWO Vidi: confirm we treat official `.docx` as acceptable application-form source (you answered Q2:A) and record it in traceability.
- For ERC calls: do we require both Work Programme PDF and Reviewer Guide PDF as “assessment-criteria sources”, or is one sufficient if it contains criteria/elements?

---

## 1. Problem Statement

This WF needs a source-grounded, upload-gated workflow to migrate and (re-)author call YAML definitions so they are defensible, ingestable, and consistent with canonical v2 schema.

Contract notes / non-obvious constraints:
- **Upload gate is hard**: before authoring each call YAML, stop and request that call’s official application-form document(s) and assessment-criteria PDF(s) separately; do not proceed without traceability references.
- **Scope lock**: primary target is legacy `erc_cog_2026_full_official` -> canonical v2 `erc_cog_2026_full`, with required validation baseline calls: `nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`.
- **Legacy mirror preserved**: `erc_cog_2026_full_official` remains a legacy mirror file; it is re-authored from official sources for traceability parity, not converted into v2.
- **Source storage policy (hybrid)**: for each official source file, keep external/original path context when available, and also store a copy under `backend/data/calls/source_files/WF-0044/<call_code>/...`; manifests reference both paths + SHA256. (See Q&A Section 1 Q1.)
- **Baseline validation is strong**: for the required baseline calls, run both `--dry-run` and a real DB ingest into a non-prod local DB. (See Q&A Section 1 Q2.)
- **ERC criteria sources are dual**: for ERC calls, require both Work Programme PDF and Reviewer Guide PDF as assessment-criteria sources. (See Q&A Section 1 Q3.)
- **One traceability manifest per call**: keep a single `backend/data/calls/sources/<call>.sources.md` covering both application-form + criteria sources. (See Q&A Section 1 Q4.)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0044-call-yaml-source-gated-migration.md` (Preflight — Intake; Section 1)
Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0044-call-yaml-source-gated-migration.md` (Section 2)

## 2. Desired Outcome

- Canonical v2 `erc_cog_2026_full` exists, validates, and is ingestable.
- Baseline/preflight validation passes for `nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`.
- `erc_cog_2026_full_official` (legacy mirror), `nwo_vidi_2025_full_proposal`, and `erc_stg_2026_full` are re-authored from official sources with updated traceability manifests.

Contract notes / non-obvious constraints:
- **Acceptance is staged for primary target**: for canonical v2 `erc_cog_2026_full`, require (1) `--dry-run` passes, (2) real local DB ingest succeeds, and (3) at least one structured review request can run end-to-end locally using that call code. (See Q&A Section 2 Q1.)
- **Baseline calls: minimal-change re-authoring**: for `nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`, re-authoring means (1) refresh traceability from official sources, and (2) apply targeted corrections only when sources clearly contradict the current YAML, while preserving `proposal_nodes[*].id` and universal structured review engine contracts. Any behavior-affecting change requires explicit notes + verification. (See Q&A Part B Clarifications Q1.)
- **Baseline node ID stability**: keep existing `proposal_nodes[*].id` stable unless clearly wrong. (See Q&A Section 2 Q3.)
- **Traceability minimum**: each `.sources.md` includes `Path`, `SHA256`, `Used for`, plus official URL/source page (if available) and downloaded/provided date. (See Q&A Section 2 Q4.)
- **Do not commit PDFs/DOCX**: keep local copied sources gitignored; still record SHA256 + local path(s) in manifests. (See Q&A Section 2 Q5.)

## 3. Target User / Actor

- Primary actor: internal developer/operator maintaining call definitions as code and needing legally-defensible traceability.

Contract notes / non-obvious constraints:
- Official sources are supplied by user upload per call; no authoring proceeds without the upload + traceability reference. (See Q&A Section 3 Q2.)
- “Real DB ingest” validation targets local Postgres dev DB. (See Q&A Section 3 Q3.)
- “E2E structured review” acceptance means calling the FastAPI endpoint locally with `call_code=erc_cog_2026_full` (API-level contract). (See Q&A Section 3 Q4.)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0044-call-yaml-source-gated-migration.md` (Section 3)

## 4. Rough Idea (Unstructured Thinking)

- Use the existing call-yaml SSOT docs to drive a gated, per-call upload workflow:
  - `docs/call-yaml/authoring-workflow.md` (living authoring spec)
  - `docs/call-yaml/guidelines.md` (v2 schema/ingest rules + common mistakes)
  - `backend/data/calls/templates/call_definition_v2_template.yaml` (starter template)
  - Schema SSOT: `backend/app/schemas/call_definitions_v2.py`
- Encode the per-call upload gate as a checklist section inside this brainstorm (no extra gate files).
- Author canonical CoG at `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml` with `funding_call.id/code = erc_cog_2026_full`.
- Keep `backend/data/calls/legacy/erc/erc_cog_2026_full_official.yaml` as a v1-shaped legacy mirror, but re-author its content from official sources and maintain a traceability manifest.
- Universal structured review engine compatibility:
  - Treat existing runtime tests (service + API) as the primary contract surface.
  - When sources reveal missing/critical universal-engine details (policy constraints, stage gating, compliance semantics), capture them as explicit “engine-impact notes” and implement them only when they do not destabilize baseline call IDs/contracts.

## Runtime Utilization Matrix (Current vs Target)

Purpose: ensure call- and agency-specific rules encoded in YAML are actually applied during review generation and output.

Legend:
- `Yes` = enforced/used today
- `Partial` = present but not enforced end-to-end
- `Target` = required outcome for WF-0044

| Surface | Evaluation criteria/elements + expectations | `reviewer_policy` prompt injection | `reviewer_policy` deterministic post-check | Node `content_constraints` / `compliance_rules` |
| --- | --- | --- | --- | --- |
| Single-snippet review (`ReviewerService.generate_review`) | Yes (DB expectations) | Yes (call definition JSON -> prompt) | Yes (POST_CHECK/BLOCKING via forbidden_terms) | Partial (prompt guidance from DB node only; constraints mostly UI-driven) |
| Structured pipeline v1 (`StructuredReviewerService.generate_structured_review_pipeline_v1`) | Yes (DB expectations -> engine snapshot) | Partial (not wired from call definition today) | Partial (not wired from call definition today) | Partial (context/constraints not currently part of engine snapshot) |
| UI/node metadata (`CallDefinitionService.get_hydrated_nodes`) | N/A | N/A | N/A | Yes (hydrated from call definition JSON by node logical id) |

Target requirement (WF-0044):
- Wire call-definition `reviewer_policy` into structured pipeline v1 so call/agency-specific reviewer constraints are honored during structured review output (prompt-level + deterministic enforcement where applicable), without breaking existing runtime contracts.

Acceptance tests (planned; implement in Phase 3):

- **PROMPT_ONLY is injected:** For a call with `reviewer_policy.enforcement_mode=PROMPT_ONLY`, structured review execution must include a “Reviewer Policy” block in the prompt content sent to the LLM (or an equivalent engine-input field) for the applicable node/stage, and the review must complete successfully.
- **POST_CHECK warns:** For a call with `reviewer_policy.enforcement_mode=POST_CHECK` + `forbidden_terms=["<term>"]`, if the returned feedback contains `<term>`, the structured review must still complete but record a deterministic warning signal (either in review summary and/or card metadata) that a reviewer-policy warning violation occurred.
- **BLOCKING blocks deterministically:** For a call with `reviewer_policy.enforcement_mode=BLOCKING` + `forbidden_terms=["<term>"]`, if the returned feedback contains `<term>`, structured review must fail with a stable, contract-safe error summary/category (no partial cards) after bounded retry attempts.
- **Stage + node scoping respected:** `applies_to_stage` and `applies_to_node_ids` must filter which rules apply per node review within the same structured request.
- **No regression:** Existing structured endpoint contract tests (WF-0043 surfaces) must still pass for `nwo_veni_2025_preproposal`.

## 5. Constraints

- No expansion to P1 #13 (MSCA/ZonMw) unless explicitly pulled in.
- Keep changes narrowly scoped to call definitions, ingestion/validation, and traceability.

Contract notes / non-obvious constraints:
- Engine-critical discoveries from sources must be recorded in `docs/logs/decisions.md` (WF-linked) and in `docs/memory/` when generalizable/recurring.
- Upload gate accepts official documents in any file type as needed (PDF/DOCX/MD/TXT/etc.); require completeness of content (criteria/elements + enforceable reviewer-policy constraints), not a specific file extension.
- We may update `docs/call-yaml/authoring-workflow.md` / `docs/call-yaml/guidelines.md` with small surgical changes when we learn a generalizable pattern, explicitly noting applicability limits (not all patterns apply to all calls/agencies).
- “STOP for uploads” allows creating skeleton YAML placeholders/TODOs, but forbids substantive authoring derived from sources until those sources are uploaded and traced.

## Open Questions / Deferred

- Whether to commit `backend/data/calls/source_files/WF-0044/...` into git or keep it gitignored while still hashing and referencing the local copy path.
- Whether baseline validation additionally requires targeted pytest selectors (vs ingest-only).
Note: current baseline decision is dry-run + local DB ingest; pytest is optional unless needed for engine-compat confidence.

- How we represent “pattern applicability” in `docs/call-yaml/` (e.g., agency-scoped notes, or explicitly labeled “ERC-only”, “NWO-only”, “general” patterns) to avoid over-generalizing from a single call.

---

## Verification Commands (Planned; Local)

Baseline (all 3 must pass):

- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run`

Baseline (real DB ingest into local Postgres dev DB):

- Set `DATABASE_URL` to local Postgres dev DB URL (project standard).
- Run the same three calls without `--dry-run`.

Primary target acceptance (erc_cog_2026_full):

- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run`
- Ingest into local Postgres dev DB (no Docker).
- One structured-review API request (minimal node payload) returns review cards for `call_code=erc_cog_2026_full`.

## 7. MVP Definition

- Implement the per-call upload gating + traceability update loop for the 3 calls in scope.
- Deliver canonical v2 migration for ERC CoG with no v1/v2 schema ambiguity.

## 8. Explicit Non-Goals

- Any new non-NWO call expansion (P1 #13) stays parked.
- Generalized assisted document extraction is out of scope.
