# WF-0044 — P1 #12: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration

Artifact: brainstorm
Version: v0.0
Status: Not started
Last Updated: 2026-03-02

Q&A transcript (archived): docs/brainstorms/qna/brainstorm-QnA-WF-0044-call-yaml-source-gated-migration.md

---

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
- **Baseline calls: minimal-change policy**: for `nwo_veni_2025_preproposal`, `nwo_vidi_2025_full_proposal`, `erc_stg_2026_full`, only change YAML to fix schema/ingest breakage and preserve compatibility with the universal structured review engine outputs/contracts. (See Q&A Section 2 Q2.)
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

## 5. Constraints

- No expansion to P1 #13 (MSCA/ZonMw) unless explicitly pulled in.
- Keep changes narrowly scoped to call definitions, ingestion/validation, and traceability.

## Open Questions / Deferred

- Whether to commit `backend/data/calls/source_files/WF-0044/...` into git or keep it gitignored while still hashing and referencing the local copy path.
- Whether baseline validation additionally requires targeted pytest selectors (vs ingest-only).
Note: current baseline decision is dry-run + local DB ingest; pytest is optional unless needed for engine-compat confidence.

## 7. MVP Definition

- Implement the per-call upload gating + traceability update loop for the 3 calls in scope.
- Deliver canonical v2 migration for ERC CoG with no v1/v2 schema ambiguity.

## 8. Explicit Non-Goals

- Any new non-NWO call expansion (P1 #13) stays parked.
- Generalized assisted document extraction is out of scope.
