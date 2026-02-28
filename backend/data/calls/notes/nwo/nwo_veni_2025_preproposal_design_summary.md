# NWO Veni 2025 – Pre-proposal

## PeerLens Call Definition Design Summary

**Chat Context Export from ChatGPT → VSCode/Codex**

---

# 1. Scope of This Conversation

This document summarizes the full architectural design of the YAML definition for:

- Funding Agency: NWO
- Call: NWO Talent Programme – Veni 2025
- Stage: Pre-proposal
- Year-specific modeling
- Rich YAML (evaluation + compliance + guidance)
- Structured input + optional assisted extraction
- Alignment cross-node logic

---

# 2. High-Level Decisions

## 2.1 Versioning Strategy

- One YAML per year per stage.
- Example filename: calls/nwo/veni/2025/nwo_veni_2025_preproposal.yaml
- IDs should remain stable across years if semantics remain stable.

---

## 2.2 Stage Modeling

We model **Pre-proposal only** in this YAML.

Full proposal will be a separate YAML.

---

# 3. Proposal Structure (Gate 2 Outcome)

We model only narrative, evaluable sections.

Excluded:

- Administrative metadata sections
- Portal instructions

### Final Node Tree (Flat Structure)

- academic_profile (Form section 2a)
- key_outputs (Form section 2b)
- research_idea (Form section 3)

Depth = 1
No nested children.

---

# 4. Evaluation Criteria (Gate 3 Outcome)

Pre-proposal has one criterion:

- Quality of the researcher (100%)

We refined into 8 atomic evaluation elements:

1. elem_target_group_fit_and_growth
2. elem_peer_exceeding_quality
3. elem_key_output_quality_impact_evidence
4. elem_positioning_in_themes
5. elem_network_collaboration_visibility
6. elem_innovative_ideas_capability
7. elem_cv_idea_alignment
8. elem_alignment_plan_credibility

Alignment is evaluated using research_idea + academic_profile.

---

# 5. Node ↔ Evaluation Mapping (Gate 4 Outcome)

## academic_profile

MANDATORY:

- target_group_fit_and_growth
- peer_exceeding_quality

IMPORTANT:

- positioning_in_themes
- network_collaboration_visibility
- innovative_ideas_capability

---

## key_outputs

MANDATORY:

- key_output_quality_impact_evidence

IMPORTANT:

- peer_exceeding_quality

---

## research_idea

MANDATORY:

- cv_idea_alignment

IMPORTANT:

- alignment_plan_credibility

OPTIONAL:

- innovative_ideas_capability

---

# 6. Compliance & Guidance Layer (Gate 2b Outcome)

Compliance is separate from evaluation.

Severity levels:

- ERROR → hard violation
- WARNING → structural weakness
- INFO → advisory (not used yet)

---

## academic_profile (2a)

Word limit:

- Min 400
- Max 700

Compliance:

- Word limit (ERROR)
- No h-index / JIF (ERROR)
- Must address independence stage (WARNING)

---

## key_outputs (2b)

Constraints:

- Max 10 outputs
- 400–700 words total
- No JIF
- No h-index
- No bibliometric shortcuts
- Each output must be explained

All above = ERROR

---

## research_idea (3)

Word limit:

- Default: 100 words
- ENW pilot (Science): 500 words

Compliance:

- Word limit (ERROR)
- No methodological overload (WARNING)
- Should indicate alignment with CV (WARNING)

---

# 7. Runtime Behavior Design

## 7.1 Structured Section Input (Primary Mode)

Users input sections separately:

- academic_profile
- key_outputs
- research_idea

Advantages:

- Deterministic compliance checking
- Clean evaluation mapping
- Reduced hallucination risk

---

## 7.2 Assisted Extraction (Optional)

Supports:

- Paste text
- .docx
- .pdf

Flow:

1. Extract section based on dropdown selection.
2. Show extracted snippet preview.
3. Show extraction confidence.
4. Require user confirmation.
5. Only then run evaluation.

Never silently evaluate extracted content.

---

## 7.3 Alignment Logic

If academic_profile missing:

- Mark alignment elements as: NOT_ASSESSABLE
- Offer optional:
  “Paste 5–10 bullet summary of academic profile”

Never fabricate alignment.

---

# 8. YAML Characteristics

The YAML is "Rich":

Includes:

- funding_agency
- funding_call
- evaluation_criteria
- evaluation_elements
- proposal_nodes
- guidance_text
- compliance_rules
- content_constraints
- node_expectations
- runtime_notes

Not included:

- Portal upload mechanics
- Submission platform instructions
- Administrative metadata

---

# 9. Architectural Principles Established

1. Do not mix compliance and scoring.
2. Do not score what is not assessable.
3. Always require extraction confirmation.
4. Version YAML per year and per stage.
5. Keep evaluation elements atomic.
6. Use expectation_strength conservatively.
7. Preserve original form section numbers as metadata only.

---

# 10. Next Logical Development Paths

Possible next steps in VSCode:

A) JSON Schema validator for YAML
B) Evaluation engine runtime implementation
C) Compliance detection module
D) Assisted extraction module
E) Alignment cross-node evaluation logic
F) Admin ingestion CLI

---

# 11. Minimal TL;DR

We designed a robust, stage-specific, year-specific YAML for:
NWO Veni 2025 Pre-proposal.

It models:

- 3 narrative nodes
- 8 refined evaluation elements
- Strict compliance layer
- Alignment cross-node logic
- Structured input primary mode
- Assisted extraction secondary mode

System is defensible, scalable, and MVP-safe.

---

END OF EXPORT
