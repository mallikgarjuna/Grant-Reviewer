# WF-0036 — Re-author NWO Veni 2025 preproposal YAML (official sources)

Artifact: prd
Version: v1.0
Status: Done
Last Updated: 2026-02-26

---

## Goal

Re-author the NWO Veni 2025 pre-proposal call definition YAML from official sources, using the updated authoring conventions (traceable sources + reviewer policy), without changing product behavior beyond call-definition content.

## Scope

- Rewrite the call YAML from the provided official documents, preserving call code stability.
- Preserve diffability by archiving the legacy YAML.
- Add a source manifest (SHA256 + mapping) for traceability.
- Encode evaluable structure, evaluation criteria/elements, and enforceable constraints only.
- Add reviewer policy rules for prohibited bibliometrics and prestige language.

## Out Of Scope

- Any UI work, API work, or database changes.
- Deterministic enforcement of “max outputs” on free-text nodes (MVP limitation).

## Shipped Artifacts

- Canonical: `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`
- Archived legacy: `backend/data/calls/nwo/nwo_veni_2025_preproposal_legacy.yaml`
- Source manifest: `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`

## Acceptance / Verification

- `CallDefinitionV2` schema validates for the canonical YAML.
- Dry-run ingest passes:
  - `cd backend && PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
