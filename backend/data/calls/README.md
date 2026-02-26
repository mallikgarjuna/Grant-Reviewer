# Funding Call YAML Files

This directory contains YAML call definitions for ingestion into the Grant Reviewer database.

Guidelines for authoring call YAML that validates/ingests correctly:
- `docs/reference/call_yaml_guidelines.md`

## Filename Convention

```
{agency}_{program}_{year}_{stage}.yaml
```

| Component | Format | Examples |
|-----------|--------|----------|
| `agency` | lowercase acronym | `erc`, `nwo`, `msca`, `nsf` |
| `program` | lowercase code | `cog`, `stg`, `vici`, `vidi`, `pf`, `career` |
| `year` | 4 digits | `2026`, `2025` |
| `stage` | `pre` or `full` | `pre` (pre-proposal), `full` (full proposal) |

**Examples:**
- `erc/erc_stg_2026_full.yaml` - ERC Starting Grant 2026, full proposal
- `nwo/nwo_veni_2025_preproposal.yaml` - NWO Veni 2025, pre-proposal
- `msca_pf_2026_full.yaml` - MSCA Postdoctoral Fellowship 2026, full
- `nsf_career_2026_full.yaml` - NSF CAREER Award 2026, full

## Suggested Layout

- Agency-specific call YAMLs under subfolders (for example `erc/`, `nwo/`)
- Source traceability manifests under `sources/`

## Test Files

These files are for testing validation logic and are not real funding calls:
- `invalid_ref.yaml` - Contains broken references (for testing error handling)
- `edge_case_call.yaml` - Tests edge cases (section-only nodes, multiple expectations)

## Usage

```bash
# Validate a call definition (dry run)
uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml
```
