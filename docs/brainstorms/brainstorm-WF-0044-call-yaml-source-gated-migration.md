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
