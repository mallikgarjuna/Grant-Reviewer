# Brainstorming Log: Admin Workflow (Phase 0)

**Date**: 2026-02-07
**Objective**: Define how an Admin efficiently populates the backend with new Funding Calls, specific Proposal Hierarchies, and mapped Evaluation Rubrics.

## 1. The Problem
The domain model is highly relational and specific. A single "Funding Call" requires:
1.  **Agency & Call Metadata**: Simple row creation.
2.  **Rubric Definition**: Creating ~5-10 `EvaluationCriteria`, each with ~3-5 `EvaluationElements`.
3.  **Proposal Structure**: Creating reliable `ProposalNode` trees (Sections, Subsections).
4.  **The Mapping (Expectations)**: The most complex part. Linking specific `ProposalNode` IDs to specific `EvaluationElement` IDs with a `strength`, `intent`, and `guidance_note`.

**Pain Point**: Doing this via raw SQL or a generic "Admin UI" (like Django Admin) is error-prone and tedious. The relationships are too dense to manage without a dedicated view.

## 2. Who is the Admin?
- **Role**: "Research Engineer" or "Grant Officer".
- **Skill Level**: Technical enough to edit config files or run scripts, but needs a structured process.
- **Goal**: rapid iteration on the *content* (prompts/guidance) without fighting the *database*.

## 3. Proposed Solution: "Call Definition as Code" (YAML)
We treat a Funding Call definition as a code artifact (YAML file). This file is the single source of truth and is "compiled" (ingested) into the database.

### Why YAML?
- **Hierarchical**: Matches the Proposal Node structure naturally.
- **Readable**: Admins can write multi-line strings for `guidance_text` and `guidance_note`.
- **Version Control**: The definitions can be committed to the repo.
- **Copy-Paste**: Easy to scaffold a new call from an existing one.

### Proposed Schema Structure

```yaml
# call_definition.yaml
meta:
  agency: "ERC"
  call_code: "COG-2026"
  call_name: "Consolidator Grant 2026"
  year: 2026

rubric:
  - id: "excellence" # Local reference ID
    name: "Excellence"
    description: "Groundbreaking nature and ambition"
    elements:
      - id: "obj_clarity"
        name: "Clarity of Objectives"
        description: "Are objectives measurable and verifiable?"
      - id: "method_soundness"
        name: "Soundness of Methodology"

structure:
  - title: "1. Excellence"
    type: "SECTION"
    children:
      - title: "1.1 Objectives"
        type: "SUBSECTION"
        guidance: "Describe the state of the art..."
        expectations:
          - element_ref: "obj_clarity" # Links to rubric.elements.id
            strength: "MANDATORY"
            intent: "QUALITY"
            guidance_note: "Check if objectives are specific (SMART)."
          - element_ref: "method_soundness"
            strength: "IMPORTANT"
            intent: "RISK"
```

## 4. The Workflow
1.  **Draft**: Admin creates `data/definitions/2026_erg_cog.yaml`.
2.  **Validate**: Run `python scripts/validate_call.py` (checks schema/refs).
3.  **Ingest**: Run `python scripts/ingest_call.py` (idempotent upsert).
4.  **Verify**: Use the Researcher UI to see the populated structure.

## 5. Alternative: Interactive CLI
- A script asking: "Add a section? (y/n)", "Add expectation? (select from list)".
- **Pros**: Good for non-technical users.
- **Cons**: Hard to edit/review later. Hard to visualize the whole tree.

## 6. Decision
**Proceed with YAML-based ingestion.** It aligns with the "Developer-First" stage and allows us to build a library of test calls easily.
