---
title: "Spec: Call Authoring Workflow"
version: "1.1"
status: "Living Specification"
updated: "2026-02-28"
applies_to: "All funding agencies (NWO, ERC, MSCA, Horizon Europe, etc.)"
---

# Spec: Call Authoring Workflow

## PeerLens - Funding Call YAML Design Methodology

---

# 1. Purpose

This document defines the standardized workflow for converting a funding call into a PeerLens YAML definition.

It ensures:

- Structural consistency
- Legal defensibility
- Evaluation alignment with funder criteria
- Separation of compliance and scoring
- Year-specific versioning
- Safe runtime behavior
- Scope focus on evaluable proposal structure, evaluation criteria/elements, and enforceable content constraints only

This spec must be followed for all new call onboardings.

---

# 2. Core Principles

## 2.1 One YAML Per Year Per Stage

Each funding call is versioned by:

- Funding agency
- Call
- Year
- Stage (pre-proposal, full proposal, etc.)

Example: calls/nwo/veni/2025/nwo_veni_2025_preproposal.yaml

IDs should remain stable across years unless semantics change.

---

## 2.2 Separate Evaluation From Compliance

Never mix:

- Evaluation elements (scoring logic)
- Compliance rules (formatting, prohibited content)

Evaluation findings must not silently absorb compliance violations.

Outputs must separate:

- Evaluation Findings
- Compliance Findings
- Structural Warnings

---

## 2.3 Conservative Node ↔ Element Mapping

Only map evaluation elements to nodes when clearly justified by funder documentation.

Avoid over-mapping.

---

## 2.4 Alignment Requires Context

If an evaluation element requires cross-node context (e.g., CV ↔ Research Idea alignment):

- If required node is missing → mark element as `NOT_ASSESSABLE`
- Never fabricate alignment
- Optionally request minimal summary input to enable alignment checks

---

## 2.5 Structured Input First

Primary input mode:

- Structured by proposal section (node-based input)

Optional:

- Assisted extraction from full document
- Must include:
  - Extracted snippet preview
  - Extraction confidence
  - Explicit user confirmation
- Never evaluate silently extracted content

---

## 2.6 Model Only Evaluable Narrative Content

Do NOT create proposal_nodes for:

- Administrative portal fields
- Submission mechanics
- Contact details
- Budget upload mechanics

Model only narrative content that reviewers assess.

---

## 2.7 Preserve Source Metadata Without Coupling IDs

- Logical node IDs must be stable (e.g., `academic_profile`)
- Preserve original form section numbering as metadata (e.g., `source_section: "2a"`)

Never encode brittle numbering into logical IDs.

---

# 3. Required Inputs Per Call

Minimum required documents:

1. Proposal narrative structure source
   (Application form template; may be PDF/DOCX/MD/TXT/etc.)

2. Evaluation criteria source
   (Guide for reviewers or criteria section of call; may be PDF/MD/TXT/etc.)

Optional but useful:

- Reviewer guide
- Annexes affecting compliance
- Pilot modifications

Without both structure and evaluation sources, YAML must not be finalized.

---

# 4. Gated Authoring Workflow

## Gate 1 – Source Confirmation

- Identify structure source
- Identify evaluation logic source
- Confirm stage
- Confirm year
- Flag ambiguities

Stop for approval.

---

## Gate 2 – Proposal Node Tree Draft

- Extract narrative sections
- Exclude administrative-only sections
- Ensure depth ≤ 5
- Use stable semantic IDs
- Preserve form numbering as metadata

Stop for approval.

---

## Gate 3 – Evaluation Elements Extraction

- Extract criteria from official evaluation section
- Break into atomic evaluation elements
- Ensure elements are:
  - Independently evaluable
  - Promptable
  - Non-overlapping
- IDs must be globally unique within YAML

Stop for approval.

---

## Gate 4 – Node ↔ Element Mapping

For each proposal node:

- Map relevant evaluation elements
- Assign:
  - `expectation_strength` (MANDATORY / IMPORTANT / OPTIONAL)
  - `evaluation_intent` (QUALITY / STRATEGIC_FIT / RISK / COMPLIANCE)

Use conservative mapping.

Stop for approval.

---

## Gate 2b – Guidance & Compliance Layer

For each node:

Add:

- `guidance_text` (condensed, reviewer-relevant instructions)
- `content_constraints` (word limits, item limits)
- `compliance_rules` with severity:
  - ERROR
  - WARNING
  - INFO (optional)

Only encode rules that:

- Influence review interpretation
- Create compliance risk
- Affect allowed vs prohibited content

Do NOT paste full explanatory notes verbatim.

Stop for approval.

---

## Gate 5 – YAML Generation

Generate rich YAML including:

- funding_agency
- funding_call
- evaluation_criteria
- evaluation_elements
- proposal_nodes
- guidance_text
- compliance_rules
- content_constraints
- node_expectations
- runtime_notes (if needed)

Run validation before ingestion.

---

# 5. Runtime Evaluation Contract

When reviewing a proposal section:

1. Structural check
2. Compliance check
3. Evaluation mapping
4. Cross-node checks (if applicable)

If required context missing:

- Mark element as NOT_ASSESSABLE
- Explain clearly

Never hallucinate missing information.

---

# 6. Output Contract

Review outputs must clearly separate:

## Evaluation Findings

Mapped to evaluation elements.

## Compliance Findings

Mapped to compliance rules.

## Structural Warnings

Missing sections, extraction issues, etc.

---

# 7. Assisted Extraction Rules

If full document upload is supported:

- Extract candidate section
- Show preview
- Show extraction confidence
- Require explicit confirmation
- Evaluate only confirmed snippet

Never auto-evaluate silently extracted content.

---

# 8. Validation Requirements

Before ingestion:

- Every evaluation_element_id referenced must exist.
- Every proposal_node must have at least one expectation.
- All word limits must be machine-enforceable.
- No duplicate IDs.
- All severities valid.

---

# 9. Logging Requirements

When onboarding a new call:

- Record architectural decisions in `docs/logs/decisions.md`
- Record clarifications in `docs/logs/qa_history.md`
- Record prompt changes in `docs/logs/prompt_history.md`

---

# 10. Living Specification Rule

This document must be updated whenever:

- A new modeling pattern is introduced
- A new compliance pattern appears
- A new extraction behavior is added
- Runtime behavior changes
- A failure mode is discovered

---

# 11. WF-0038 Readiness Gate (Required Before Rollout)

Before enabling a new call on pipeline v1, complete all checks below.

## 11.1 Authoring Baseline

- Start from `backend/data/calls/templates/call_definition_v2_template.yaml`
- Keep structure aligned with `backend/app/schemas/call_definitions_v2.py`
- Use official source documents only (structure + evaluation criteria/elements)

## 11.2 Validation and Ingestion

- Dry-run must pass:
  - `cd backend && uv run python scripts/ingest_call.py data/calls/<agency>/<file>.yaml --dry-run`
- Ingest must succeed into the target environment DB.
- Dry-run summary must show expected node and evaluation-element counts.

## 11.3 Runtime Smoke for Structured Review

- Ensure runtime is on the current v1-only structured-review path (`POST /api/structured-review` no longer uses call-level engine allowlist toggles).
- Submit at least one `POST /api/structured-review` request for the target call.
- Request must succeed without malformed-request errors caused by call config / expectation mapping.

## 11.4 Ship Decision

Mark the call as WF-0038-ready only when Sections 11.1, 11.2, and 11.3 all pass.

PeerLens call definitions must always follow this workflow.

END OF SPEC
