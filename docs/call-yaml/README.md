---
path: "docs/call-yaml/README.md"
title: "Call YAML Docs Hub"
version: "1.0"
status: "Active"
updated: "2026-03-08"
---

# Call YAML Docs Hub

This directory is the single docs entrypoint for call-definition authoring.

## What This Is (SSOT Map)

When authoring or updating a funding-call YAML, treat these as the “single sources of truth” for different concerns:

- **Schema SSOT (what fields/enums exist; what validates):**
  - `backend/app/schemas/call_definitions_v2.py`
- **Ingestion SSOT (what ingests; what breaks at runtime):**
  - `backend/scripts/ingest_call.py`
- **Living authoring SSOT (how we convert official documents to YAML, with gates):**
  - `docs/call-yaml/authoring-workflow.md`
- **Authoring checklist SSOT (critical rules + common mistakes for v2 YAML):**
  - `docs/call-yaml/guidelines.md`
- **Starter template SSOT (new call scaffolding):**
  - `backend/data/calls/templates/call_definition_v2_template.yaml`

Call-specific truth lives in:

- The call YAML itself: `backend/data/calls/canonical/<agency>/...` (or `legacy/...`)
- Its traceability manifest: `backend/data/calls/sources/<call_code>.sources.md`

## Primary docs

- Authoring workflow: `docs/call-yaml/authoring-workflow.md`
- Authoring guidelines: `docs/call-yaml/guidelines.md`
- Onboarding checklist: `docs/call-yaml/onboarding-checklist.md`

## WF-0063 Policy Snapshot

- Runtime split behavior is opt-in only through `runtime_config.split_visibility_reviewability_enabled`.
- `proposal_nodes[*].node_role` is authoritative for primary-vs-supporting intent.
- Proof-call-first policy applies: do not enable split mode for additional calls without explicit approval and parity verification.

## Runtime/data artifacts

- Canonical call YAML files: `backend/data/calls/canonical/`
- Legacy/superseded call YAML files: `backend/data/calls/legacy/`
- Authoring/design notes: `backend/data/calls/notes/`
- Starter templates: `backend/data/calls/templates/`
- Source traceability manifests: `backend/data/calls/sources/`

## When We Use These Docs

Use `docs/call-yaml/` whenever we:

- Onboard a new funding call from official sources (PDF/DOCX/MD/TXT/etc.).
- Migrate a legacy YAML into canonical v2 shape.
- Re-author an existing canonical YAML from updated/official sources (source-grounded refresh).

## When Sources Reveal New Info We Missed Originally

If official sources reveal something new that is critical/useful for the universal structured review engine:

- First, decide if it is **call-specific** or a **generalizable pattern**.
- Call-specific:
  - encode it in that call’s YAML (only if it doesn’t break existing contracts) and trace it in that call’s `.sources.md`.
- Generalizable pattern:
  - make a small, surgical update to `docs/call-yaml/authoring-workflow.md` and/or `docs/call-yaml/guidelines.md`.
- Always record the discovery:
  - `docs/logs/decisions.md` (searchable, WF-linked),
  - and `docs/memory/` if it’s a recurring gotcha/rule.

Important: not all patterns apply to all agencies/calls; treat these docs as guidance + gates, not as a claim that every call has the same structure/criteria semantics.

## When To Update Schema/Template SSOTs

Sometimes a “universal pattern” requires changes beyond call YAML authoring:

- Update `backend/app/schemas/call_definitions_v2.py` (schema SSOT) only if:
  - the pattern cannot be represented cleanly with existing fields/enums, and
  - it is truly cross-call (not agency-specific), and
  - we are willing to treat it as a versioned contract change (ingestion + validation + tests).
- Update `backend/data/calls/templates/call_definition_v2_template.yaml` (starter template) if:
  - the pattern is broadly applicable and will prevent repeated authoring mistakes, and
  - it can be expressed with the current schema without encoding agency-specific assumptions.

## Compatibility note

Legacy doc paths remain as pointer files:

- `docs/call-yaml/authoring-workflow.md`
- `docs/call-yaml/guidelines.md`
