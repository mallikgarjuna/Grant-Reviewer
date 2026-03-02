# YAML Definitions

- **Naming context:** Call YAML naming: `{agency}_{program}_{year}_{stage}.yaml`.
- **Source gating:** Author call YAML only from official funder documents provided in-workflow; if missing, stop and request them.
- **2026-03-02 — Per-call upload gate:** For re-authoring `erc_cog_2026_full`, `nwo_vidi_2025_full_proposal`, and `erc_stg_2026_full`, stop before each call and request that call's application-form + assessment-criteria PDFs separately (do not batch-author without uploads).
- **Scoping limits:** Encode only evaluable proposal structure, evaluation criteria/elements, and enforceable content constraints.
- **2026-03-02 — Runtime utilization reminder:** Call-specific `reviewer_policy` rules from v2 call YAML are currently applied in the single-snippet reviewer flow (prompt injection + deterministic forbidden-term post-checks). The structured pipeline_v1 path is primarily driven by DB expectations and does not automatically enforce reviewer_policy unless explicitly wired into the engine pipeline.
