# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
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

### Decisions (Section 2)

Q1 (canonical storage “done” criteria): **A** — Store validated JSONB + `schema_version` + `checksum` + `source_path` (optional `raw_yaml`) per call; re-ingest updates the stored doc only if checksum changes.

Q2 (projection re-ingest behavior): **A** — Idempotent upsert by `logical_id`; update mutable fields (`name`/`description`/`guidance_text`/`order_index`) and replace expectations deterministically.

Q3 (minimum projection for robust review): **A** — Project nodes/criteria/elements/expectations + `guidance_text`; keep constraints/rules/notes in JSONB and access by `logical_id` when needed.

Q4 (runtime read path for prompt-building): **A** — Add an internal service that loads the projection and hydrates per-node config from JSONB via `(call_code, node_logical_id)`.

Q5 (verification definition): **A** — Add targeted commands/tests proving: V2 ingests to DB, re-ingest is idempotent (`logical_id` => stable UUID), V1 ingest still works, and JSONB doc is stored with `schema_version` + checksum.

### Summary

After WF-0021, call definitions are stored canonically as versioned/validated JSONB for robustness against schema evolution, while the stable relational projection enables efficient querying and traceability for reviews. Verification must include a real DB round-trip and an idempotent re-ingest check.

### Critical Clarifications (from architectural review)

- **Semantic checksum**: compute `checksum` over the validated, canonicalized JSON representation (stable key ordering; ignore YAML comments/whitespace), not raw YAML text.
- **Single-read hydration**: the internal read service must fetch the canonical JSONB document once per call and hydrate node configs in-memory (avoid N+1 JSON parsing/lookup per node).

---

## 3. Target User / Actor

### Questions (Section 3)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: Who is the primary actor for WF-0021 work?
- A (Recommended): internal dev/admin running ingestion and maintaining call definitions
- B: researcher using the UI
- C: both

Q2: Who is the secondary actor (affected indirectly)?
- A (Recommended): backend product developer building review/compliance features on top of stored call definitions
- B: data analyst / ops
- C: researcher

Q3: What is the actor’s primary “job to be done”?
- A (Recommended): reliably ingest evolving call definitions with idempotent updates and stable traceability keys
- B: manually patch DB records to match YAML
- C: keep YAML static to avoid changes

Q4: What pain are we removing?
- A (Recommended): schema drift forces frequent DB migrations and breaks re-ingest traceability and downstream logic
- B: YAML parsing errors only
- C: UI confusion (frontend scope)

Q5: What outcome matters most to this actor?
- A (Recommended): ingestion + runtime access are stable even as YAML evolves (minimal future churn)
- B: fastest possible ingest execution time
- C: perfect DB normalization of every YAML field

### Decisions (Section 3)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

WF-0021 is primarily a developer-facing robustness upgrade: make call-definition ingestion and runtime access stable under schema evolution, enabling later review/compliance work without repeated backend/frontend rewrites.

---

## 4. Rough Idea (Unstructured Thinking)

### Questions (Section 4)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: What is the simplest robust architecture to accommodate evolving YAML?
- A (Recommended): persist validated call-definition JSONB as canonical store + maintain relational projection for core review graph
- B: fully normalize every field into relational tables immediately
- C: keep YAML-only and parse on every request

Q2: How do we connect canonical JSON to projection rows?
- A (Recommended): stable `logical_id` fields on projected entities; hydrate extras from JSONB by `(call_id/code, logical_id)`
- B: match by names/titles only
- C: match by UUIDs generated on first ingest with no mapping

Q3: How should ingestion be structured?
- A (Recommended): two-phase: validate+store document; then upsert projection by `logical_id`
- B: projection-only ingest; no canonical document storage
- C: document-only ingest; no projection

Q4: How do we handle multi-version schemas?
- A (Recommended): explicit `schema_version` per stored document; strict validation per version; multiple versions can coexist
- B: “best effort” parse with unknown fields ignored
- C: enforce single immutable schema forever

Q5: How do we keep future API/frontend diffs minimal?
- A (Recommended): define one internal call-config read service now; endpoints later just expose it
- B: embed YAML parsing logic into each endpoint/feature as needed
- C: duplicate logic across services and refactor later

### Decisions (Section 4)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

Implement canonical JSONB storage plus `logical_id`-keyed projection. Ingest is two-phase and version-aware. Runtime reads use a single internal service that can hydrate node config (constraints/rules/notes) from canonical JSONB while continuing to use the projection for joins and ordering.

### Critical Clarifications (from architectural review)

- **Transaction boundary**: canonical document write + projection upserts must run in a single DB transaction (no intermediate state if the process crashes mid-ingest).
- **Orphan handling**: projection ingestion must define what happens when YAML removes entities:
  - Default: **soft-delete/archive** missing `logical_id`s in the projection (do not hard-delete rows that might be referenced by reviews/snippets).

---

## 5. Constraints

### Questions (Section 5)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: Scope boundary relative to planned WFs?
- A (Recommended): only WF-0021 scope (canonical JSONB + logical_id + V2 DB ingest + keep V1 compatibility)
- B: include WF-3 structured-config endpoint
- C: include WF-4 compliance engine

Q2: Frontend changes?
- A (Recommended): none
- B: minimal UI toggle
- C: full structured form

Q3: Migration posture?
- A (Recommended): minimal DB schema changes required for robustness (new doc table + `logical_id` columns + constraints); avoid drive-by refactors
- B: large refactor to redesign the entire domain model
- C: no DB schema changes at all

Q4: Backward compatibility requirement?
- A (Recommended): preserve existing V1 ingestion behavior and existing call fixtures; add V1 doc storage if feasible
- B: break V1
- C: stop supporting V1 ingest

Q5: External side effects constraints?
- A (Recommended): avoid OpenAI API calls; ingestion work should be deterministic and testable locally
- B: ok to run paid LLM calls during verification
- C: depend on external services during ingest

### Decisions (Section 5)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

WF-0021 stays tightly scoped: DB robustness foundation (canonical JSONB + stable projection) and V2 ingest into DB while keeping V1 compatibility. No frontend, no new endpoints, no compliance engine, no external/paid side effects.

---

## 6. Risks / Unknowns

### Questions (Section 6)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: Primary implementation risk?
- A (Recommended): getting idempotent upsert semantics right (uniqueness constraints + correct matching keys) without breaking existing flows
- B: YAML parse errors
- C: frontend regressions

Q2: Data model evolution risk?
- A (Recommended): choosing the wrong “stable projection” boundaries; mitigate by keeping canonical JSONB and projecting only high-value stable fields
- B: over-optimizing tables early
- C: not storing enough data to run reviews

Q3: Migration/backfill risk?
- A (Recommended): existing DB rows lack `logical_id`; mitigation: allow nullable for existing rows, backfill on first re-ingest, and enforce uniqueness only when present (or provide a one-time backfill script)
- B: drop and recreate DB
- C: ignore existing data

Q4: Operational risk?
- A (Recommended): ingest script currently supports V2 dry-run only; adding V2 DB ingest must preserve V1 and remain deterministic with clear failure modes
- B: performance
- C: concurrency at scale (premature)

Q5: Test/verification risk?
- A (Recommended): lack of DB round-trip tests for idempotency; must add targeted tests and a small repro harness
- B: too many tests slow down iteration
- C: manual-only verification is sufficient

### Decisions (Section 6)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

Big risks are correctness and compatibility: idempotent upsert by `logical_id`, safe migrations/backfill, and preserving V1 while enabling V2 DB ingest. Mitigation is canonical JSONB storage + narrow projections + targeted DB tests.

### Critical Clarifications (from architectural review)

- **Deletion/orphans**: define a projection deletion strategy that preserves referential integrity:
  - Prefer soft-delete (`is_active` / `archived_at`) for nodes/criteria/elements when missing from a re-ingest.
  - Node expectations can be replaced deterministically because they are “derived links”.
- **Backfill robustness**: consider a one-off migration/backfill that assigns deterministic `logical_id`s to legacy V1 projection rows (e.g., slugified titles/names, stable within call), so new code can safely treat `logical_id` as always-present going forward.

---

## 7. MVP Definition

### Questions (Section 7)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: Must-have deliverable in WF-0021?
- A (Recommended): canonical call-definition document storage (validated JSONB + schema_version + checksum) + stable projection ingestion for V2 into DB
- B: only `logical_id` columns
- C: only V2 DB ingest with no canonical storage

Q2: Must-have traceability keys?
- A (Recommended): `logical_id` on nodes/criteria/elements with uniqueness constraints scoped to the call; re-ingest matches by these keys
- B: rely on names/titles
- C: rely on generated UUIDs without stable mapping

Q3: Minimum runtime access capability (no API yet)?
- A (Recommended): an internal read service that can hydrate per-node config from JSONB via `logical_id`
- B: ad-hoc SQL queries in prompt builder
- C: no runtime access until WF-3

Q4: Minimum V1 compatibility requirement?
- A (Recommended): V1 ingest still works; V1 docs can also be stored canonically (preferred)
- B: V1 ingest only; no doc storage
- C: break V1

Q5: Proof of done?
- A (Recommended): DB round-trip verification + idempotent re-ingest test + V1 regression + JSONB doc storage check
- B: manual CLI only
- C: only schema validation

### Decisions (Section 7)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

MVP is a robustness foundation: canonical call-definition doc storage and stable relational projection ingestion keyed by `logical_id`, with V2 DB ingest enabled and V1 preserved. Runtime code can fetch and hydrate evolving fields from the canonical document without needing immediate API/frontend changes.

---

## 8. Explicit Non-Goals

### Questions (Section 8)

User pre-approved: **use recommended options for all questions** unless explicitly overridden later.

Q1: Are we building the structured-config endpoint now?
- A (Recommended): no (WF-3)
- B: yes
- C: partially

Q2: Are we changing the frontend to structured input now?
- A (Recommended): no (future WF)
- B: minimal
- C: yes

Q3: Are we implementing the compliance engine now?
- A (Recommended): no (WF-4)
- B: partial
- C: yes

Q4: Are we normalizing all constraints/rules into relational tables now?
- A (Recommended): no; keep them in canonical JSONB and hydrate at runtime via `logical_id`
- B: yes, fully normalize now
- C: partially normalize a subset now

Q5: Are we widening scope to other funders beyond ensuring the architecture supports evolution?
- A (Recommended): no; implement architecture generically but only ingest the NWO V2 fixture(s) and preserve V1 behavior
- B: yes; add multiple new funder schemas now
- C: yes; redesign all call ingestion

### Decisions (Section 8)

Q1: **A**. Q2: **A**. Q3: **A**. Q4: **A**. Q5: **A**.

### Summary

WF-0021 explicitly excludes WF-3+ items (endpoints, frontend, compliance engine) and avoids premature normalization of every evolving YAML field. It focuses on canonical storage + stable projection + traceability.

---

## Changelog

- v0.2 (2026-02-21): Incorporated critical architectural review clarifications (orphan strategy, transactional ingest, N+1 hydration avoidance, semantic checksum, and legacy `logical_id` backfill posture).
