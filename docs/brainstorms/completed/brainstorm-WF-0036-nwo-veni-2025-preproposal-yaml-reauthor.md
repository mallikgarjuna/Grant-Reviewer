# WF-0036 — Re-author NWO Veni 2025 preproposal YAML (official sources)

Artifact: brainstorm
Version: v1.0
Status: Done
Last Updated: 2026-02-26

---

## Preflight Intake (Interactive)

Decisions:

- Archive approach: keep both old and new YAML (`*_legacy.yaml` + new canonical filename).
- Updated conventions: add a source manifest (SHA256 + mapping) and standardize reviewer policy rules.
- Max outputs: keep `max_items=10` as informational only (WARNING), not deterministically enforced in compliance engine MVP.
- Prohibited metrics: enforce via `reviewer_policy` forbidden terms with blocking/ post-check semantics.
- ENW/Science pilot: keep domain key `science_enw`.

**Brainstorming Q&A:**

**Q1: Should the re-authored YAML overwrite `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`, or be a new file?**
- A) Overwrite in-place (keeps call code stable for runtime).
- B) New file (keep old as-is; update ingestion/docs to point to new).
- C) Keep both: move old to `*_legacy.yaml`, write new to canonical name.
> Recommendation: C — Explicit archive preserves diffability while keeping runtime paths stable.
> **Selected: C**

**Q2: What is the “must-fix” definition of “updated ERC-StG-2026 conventions” for this YAML?**
- A) Source manifest with SHA256 + “used for” mapping (like `backend/data/calls/sources/erc_stg_2026_full.sources.md`).
- B) Add/standardize `reviewer_policy` rules and stages where applicable.
- C) Strictly match ERC YAML structure even if Veni is flatter (risk: forcing irrelevant fields).
> Recommendation: A+B — Keep the YAML V2 schema, add source manifest traceability and enforceable reviewer-policy where appropriate; do not force irrelevant ERC-only structures.
> **Selected: A+B**

**Q3: How should we encode “max 10 outputs” given MVP constraints (plain text, no robust parsing)?**
- A) Keep as `content_constraints.max_items=10` + compliance rule as `WARNING` (informational), not an enforced `ERROR`.
- B) Make it an enforced `ERROR` anyway (likely unenforceable deterministically).
- C) Drop it entirely from YAML.
> Recommendation: A — Preserve the constraint as guidance without pretending to enforce it deterministically on plain text.
> **Selected: A**

**Q4: Prohibited metrics (JIF, h-index): how should we enforce?**
- A) Encode as `reviewer_policy` forbidden terms with `POST_CHECK` (or `BLOCKING`) to prevent the model from using them in feedback.
- B) Keep as `compliance_rules` only (won’t actually be enforced by current compliance engine).
- C) Omit for now.
> Recommendation: A — The runtime has deterministic post-check enforcement; BLOCKING is viable because policy blocking currently fails the node execution if violated.
> **Selected: A**

**Q5: ENW/Science pilot: what’s the exact domain key we standardize on in YAML + UI?**
- A) `science_enw` (matches current frontend/backend usage).
- B) Rename to something else.
> Recommendation: A — Preserve compatibility with existing code while encoding the domain-specific limit explicitly.
> **Selected: A**

---

## Part B: Risk Audit (2026-02-26)

- Scope creep risk: treating “call YAML re-authoring” like a product feature. Mitigation: keep WF-0036 as “call-definition maintenance”; no API/UI work.
- Source integrity risk: authoring without official docs or unclear mapping. Mitigation: add a source manifest (SHA256 + mapping) and keep legacy YAML archived for diffing.
- Enforcement mismatch risk: encoding constraints the runtime cannot deterministically enforce. Mitigation: keep `max_items` guidance-only; enforce prohibited metrics via `reviewer_policy` where deterministic post-check exists.
- Review quality risk: reviewers accidentally use bibliometrics / venue prestige language. Mitigation: add `reviewer_policy` BLOCKING/POST_CHECK rules for forbidden terms and PROMPT_ONLY guidance for DORA/merits/bias avoidance.

## Part C: Revise (What Changed) (2026-02-26)

- Re-authored YAML from official sources and kept runtime path stable:
  - Canonical: `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`
  - Archived legacy: `backend/data/calls/nwo/nwo_veni_2025_preproposal_legacy.yaml`
- Added traceability manifest: `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`
- Added/standardized `reviewer_policy` to align with call guidance (bibliometrics ban, venue-prestige language, DORA/merits principle, bias avoidance).
- Verified via dry-run ingest (no DB required): `cd backend && PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run`

## Repo Reality Snapshot (Read-Only) (2026-02-26)

- Current V2 schema supports `reviewer_policy` with deterministic forbidden-term enforcement; `BLOCKING` causes node execution to fail if any forbidden term appears in LLM feedback.
- Compliance engine currently enforces word limits (including `word_limit_by_domain`) but does not deterministically enforce `max_items` (so `max_items=10` should be guidance-only for now).
- Existing Veni YAML at `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml` already models the ENW/Science pilot as `domain_id: science_enw`.
