# WF-0036 — Re-author NWO Veni 2025 preproposal YAML (official sources)

Artifact: task
Version: v1.0
Status: Done
Last Updated: 2026-02-26

---

## Checklist (Done)

- [x] Gate on official sources provided in-workflow (DOCX + PDF).
- [x] Re-author canonical call YAML: `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`.
- [x] Archive legacy YAML for diffing: `backend/data/calls/legacy/nwo/nwo_veni_2025_preproposal_legacy.yaml`.
- [x] Add traceability manifest (SHA256 + “used for” mapping): `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`.
- [x] Encode constraints only where evaluable/enforceable; keep `max_items` guidance-only.
- [x] Add/standardize `reviewer_policy` rules:
  - [x] BLOCKING forbidden bibliometrics terms (e.g., h-index/JIF).
  - [x] POST_CHECK forbidden “top-tier/prestigious” venue language.
  - [x] PROMPT_ONLY DORA/merits principle reminder.
  - [x] PROMPT_ONLY bias/personal-attributes avoidance reminder.
- [x] Verify via dry-run ingest (no DB): see walkthrough.
