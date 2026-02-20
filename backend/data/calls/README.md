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
- `erc_cog_2026_full.yaml` - ERC Consolidator Grant 2026, full proposal
- `nwo_vici_2026_pre.yaml` - NWO Vici 2026, pre-proposal
- `msca_pf_2026_full.yaml` - MSCA Postdoctoral Fellowship 2026, full
- `nsf_career_2026_full.yaml` - NSF CAREER Award 2026, full

## Test Files

These files are for testing validation logic and are not real funding calls:
- `invalid_ref.yaml` - Contains broken references (for testing error handling)
- `edge_case_call.yaml` - Tests edge cases (section-only nodes, multiple expectations)

## Usage

```bash
# Validate a call definition (dry run)
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```
