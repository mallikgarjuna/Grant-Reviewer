---
title: "Call YAML Migration Notes"
version: "1.0"
status: "Active"
updated: "2026-02-28"
---

# Call YAML Migration Notes

## V1 to V2 Migration Summary

Legacy V1 shape (examples):
- `funding_agency.short_name`
- Recursive `proposal_nodes[].children`
- Uppercase node types (`SECTION`, `SUBSECTION`)

Current V2 shape:
- `funding_agency.id`
- Flat `proposal_nodes[]` with `parent_logical_id`
- Lowercase node types used in current call artifacts (`section`, `subsection`, `narrative`)
- Optional `reviewer_policy` and `runtime_notes`

## Directory Conventions

- Active canonical calls: `backend/data/calls/canonical/<agency>/`
- Legacy or archived calls: `backend/data/calls/legacy/<agency>/`
- Source manifests: `backend/data/calls/sources/`
- Authoring notes: `backend/data/calls/notes/`
- Starter templates: `backend/data/calls/templates/`

## Compatibility Rules

- Treat old V1 files as legacy unless explicitly needed for backward-compat tests.
- Prefer V2 canonical files for ingestion and runtime smoke tests.
- Keep links and runbook commands updated whenever paths move.
