---
title: "Funding Call YAML Files"
version: "1.2"
status: "Active"
updated: "2026-03-02"
---

# Funding Call YAML Files

This directory contains YAML call definitions for ingestion into the Grant Reviewer database.

Guidelines for authoring call YAML that validates/ingests correctly:
- `docs/call-yaml/guidelines.md`
- `backend/data/calls/templates/call_definition_v2_template.yaml` (starter template)

## Filename Convention

```
{agency}_{program}_{year}_{stage}.yaml
```

| Component | Format | Examples |
|-----------|--------|----------|
| `agency` | lowercase acronym | `erc`, `nwo`, `msca`, `nsf` |
| `program` | lowercase code | `cog`, `stg`, `vici`, `vidi`, `pf`, `career` |
| `year` | 4 digits | `2026`, `2025` |
| `stage` | lowercase slug | `preproposal`, `full_proposal` |

**Examples:**
- `canonical/erc/erc_stg_2026_full.yaml` - ERC Starting Grant 2026, full proposal
- `canonical/nwo/nwo_veni_2025_preproposal.yaml` - NWO Veni 2025, pre-proposal
- `canonical/nwo/nwo_vidi_2025_full_proposal.yaml` - NWO Vidi 2025, full proposal
- `canonical/msca/msca_pf_2026_full.yaml` - MSCA Postdoctoral Fellowship 2026, full
- `canonical/nsf/nsf_career_2026_full.yaml` - NSF CAREER Award 2026, full

## Suggested Layout

- Agency-specific canonical call YAMLs under `canonical/<agency>/`
- Legacy/superseded YAMLs under `legacy/`
- Design/authoring notes under `notes/`
- Source traceability manifests under `sources/`
- WF-scoped copied source artifacts under `source_files/WF-<id>/`
- Reusable starter templates under `templates/`

## Source Retention Lifecycle (WF-0044)

When source files are copied locally for source-gated authoring:
- Keep copied files through WF implementation and technical review gates.
- Verify manifest metadata (`Path`, `SHA256`, `Used for`, provenance/date) before closeout.
- After WF completion, move retained copies to secure long-term storage or purge local copies that are not required in-repo.
- Keep manifests committed even when copied binaries are not retained in git.

## Test Files

These files are for testing validation logic and are not real funding calls:
- `invalid_ref.yaml` - Contains broken references (for testing error handling)
- `edge_case_call.yaml` - Tests edge cases (section-only nodes, multiple expectations)

## Usage

```bash
# Validate a call definition (dry run)
uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml
```
