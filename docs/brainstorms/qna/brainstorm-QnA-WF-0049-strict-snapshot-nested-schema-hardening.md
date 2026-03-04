# WF-0049 — Strict Snapshot Nested Schema Hardening

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-04

## Section 1 — Scope and Boundary

**Q1: Should WF-0049 include pipeline behavior changes beyond schema hardening?**
- A) No; contract boundary hardening only.
- B) Yes; include pipeline-stage behavior improvements.
- C) Include minor opportunistic behavior fixes.
> Recommendation: A — keeps WF atomic and auditable. B/C increase regression risk and blur acceptance criteria.
> **Selected: A**

**Q2: How strict should nested extension surfaces be?**
- A) Strict models for all declared surfaces in one pass.
- B) Strict models for active/used surfaces first; expand later.
- C) Keep loose dicts with docs only.
> Recommendation: B — fastest risk reduction with manageable compatibility impact; C is insufficient.
> **Selected: B**

## Section 2 — Compatibility and Determinism

**Q3: How should digest be validated after nested schema hardening?**
- A) Against raw input payload.
- B) Against schema-validated projection excluding unset fields.
- C) Against fully normalized payload including defaults.
> Recommendation: B — deterministic and producer-compatible for omitted defaults; C previously caused false mismatches.
> **Selected: B**

**Q4: How should producer compatibility be enforced?**
- A) Add fixture matrix for known producer payload classes.
- B) Rely on ad hoc manual payload tests.
- C) Delay compatibility checks to post-merge.
> Recommendation: A — catches boundary regressions before merge with deterministic evidence.
> **Selected: A**

## Section 3 — Versioning and Rollout

**Q5: Versioning strategy for WF-0049 changes?**
- A) Keep within `schema_version: "v1"` and tighten nested contracts additively.
- B) Introduce `schema_version: "v1.1"` immediately.
- C) Defer decision; implement first.
> Recommendation: A — avoids unnecessary producer migration unless additive strictness proves incompatible.
> **Selected: A**
