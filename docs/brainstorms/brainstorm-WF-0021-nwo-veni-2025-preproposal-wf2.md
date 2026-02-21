# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-02-21

---

## 1. Problem Statement

### Decisions (Section 1)

Q1 (core problem): **A** — YAML will evolve; we need canonical storage + stable projection so changes don’t force frequent DB migrations or API/frontend rewrites.

Q2 (canonical source of truth): **A** — Persist a validated JSON document (JSONB) per call definition (`schema_version` + checksum).

Q3 (stable relational projection in WF-0021): **A** — Proposal nodes + evaluation criteria + evaluation elements + node expectations + `guidance_text`, all keyed by stable `logical_id` for idempotent re-ingest and traceability.

Q4 (schema evolution compatibility posture): **A** — Strict validation per `schema_version`; allow multiple schema versions to coexist; fail fast on unknown fields unless the schema version explicitly models them.

Q5 (V1 compatibility posture): **A** — Keep V1 ingest working; also persist a canonical JSON document for V1 for consistency (preferred).

### Summary

WF-0021 must make call-definition persistence robust to schema evolution by introducing a canonical call-definition document store (JSONB) while maintaining a stable relational projection for review/query flows and traceability via stable `logical_id`s.

---

## 2. Desired Outcome

TBD (Phase 0.1 Section 2)

---

## 3. Target User / Actor

TBD (Phase 0.1 Section 3)

---

## 4. Rough Idea (Unstructured Thinking)

TBD (Phase 0.1 Section 4)

---

## 5. Constraints

TBD (Phase 0.1 Section 5)

---

## 6. Risks / Unknowns

TBD (Phase 0.1 Section 6)

---

## 7. MVP Definition

TBD (Phase 0.1 Section 7)

---

## 8. Explicit Non-Goals

TBD (Phase 0.1 Section 8)
