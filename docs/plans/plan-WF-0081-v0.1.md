<!-- docs/plans/plan-WF-0081-v0.1.md -->
# Plan — WF-0081 Atomic Finding Model for Structured Review Output

Status: Draft helper plan
WF ID assumption: `WF-0081` is the next available WF after `WF-0080`
Purpose: reusable reference for future Phase 0/1/2 runners

## Important Usage Note

This file is a planning helper, not a workflow artifact substitute.
Use it to seed the next WF, then create the canonical brainstorm/PRD/task/walkthrough artifacts under `docs/` per the workflow system.

Suggested future-chat prompt:

```text
Use @docs/plans/plan-WF-0081-v0.1.md
Start WF-0081 using the standard phase runners.
Treat the plan as intent/reference only.
Generate the canonical WF artifacts from it.
```

## Intent

Move the structured-review output from the current coarse card model to an atomic finding model at the **Evaluation Element** level.
Each visible finding should be traceable to:

- one `proposal_node`
- one `evaluation_element`

**Note on Scope (MVP pragmatism):** While subordinate prompts represent the deepest level of granularity, forcing a 1:1 finding mapping per subordinate prompt risks fragmenting the researcher's reading experience and increases LLM hallucination risk. Subordinate prompts will act as grounding context for the LLM to write a cohesive, element-level finding.

Each finding should carry explicit structured feedback parts (summary, evidence, and synthesized guidance) instead of collapsing everything into one `feedback_text` blob.

## Repo Reality Anchor

Current researcher-visible flow:

```text
/app
  -> /api/bff/structured-review
  -> backend /api/structured-review
  -> StructuredReviewerService
  -> pipeline_v1 deterministic cards
  -> optional additive companion text
  -> /app/reviews/[reviewId]
```

Current output unit:

```text
review -> cards[]
```

Current user-visible limitation:

- one visible card compresses too much structure
- OpenAI synthesis is additive wording only, decoupled from the core finding generation
- No obvious positive reinforcement ("Requirements Met") if a section is good

## Outcome Definition

The new sufficient output unit is:

```text
review
  -> reviewed_node[]
     -> finding[]
```

Each finding must be a first-class object anchored to an `evaluation_element`. The UI will display a synthesized, actionable narrative that weaves deterministic policy with LLM suggestions to minimize cognitive load.

## Sufficient Contract Changes

### 1. Persist atomic findings

Add a new persisted finding-level contract instead of overloading `ReviewCard`.

Sufficient stored unit:

```text
ReviewFinding
- id
- review_id
- proposal_node_id
- proposal_node_logical_id_snapshot
- evaluation_criterion_logical_id_snapshot
- evaluation_criterion_name_snapshot
- evaluation_element_logical_id_snapshot
- evaluation_element_name_snapshot
- severity ("critical" | "warning" | "note" | "success")
- assessment_status ("ASSESSED" | "NOT_ASSESSABLE" | "REQUIREMENTS_MET")
- evidence_basis_text
- issue_summary_text
- actionable_feedback_text
- created_at
```

Why this is sufficient:
- `ReviewCard` is too coarse for the required traceability.
- Snapshots preserve historical renderability even if call YAML changes later.
- `actionable_feedback_text` combines the "why" (deterministic policy) and "how to fix" (LLM advice) into one seamless read.
- `assessment_status` now natively supports a "pass" condition (`REQUIREMENTS_MET`).

### 2. Keep backward compatibility

Do not break existing review-detail readers immediately.

Sufficient compatibility strategy:

- preserve `ReviewCard` reads for legacy reviews
- add new `findings`-based review-detail shape for new atomic-flow reviews
- allow the UI to render either:
  - legacy cards
  - atomic findings grouped under reviewed nodes

### 3. New review-detail response shape

Target response:

```text
ReviewDetailResponse
- review
- reviewed_nodes[]

ReviewedNode
- proposal_node_logical_id
- proposal_node_title
- node_role
- findings[]

AtomicFinding
- finding_id
- evaluation_criterion
- evaluation_element
- severity
- assessment_status
- evidence_basis
- issue_summary
- actionable_feedback
```

### 4. Sufficient UI changes

Replace the current “one large card body” reading flow with:

```text
Reviewed section
  -> Finding list
     -> one bordered finding item per evaluation element finding
        -> evaluation element name (header)
        -> issue summary
        -> evidence basis
        -> actionable feedback
```

If a section fully meets requirements, explicitly show a "Requirements Met" or "Green Check" state to build researcher confidence.

## Sufficient Prompt Contract

The prompt must ask for findings keyed to the node and evaluation element. It must not ask the LLM to echo back static IDs, which wastes tokens.

### Prompt shape

System intent:

```text
You are generating structured review findings for grant proposal text.
Evaluate the submitted text against the provided Evaluation Element and its context prompts.
If the text satisfies the requirements, return an empty findings array.
If there are issues, return one or more findings.
Do not echo back the node or element IDs in the JSON; they are injected by the system.
Provide a short issue_summary, cite grounded evidence from the submitted text in evidence_basis, and provide cohesive actionable_feedback that advises the researcher on how to satisfy the requirements.
```

User payload skeleton:

```text
CALL CONTEXT
- call_code: <call_code>
- review_stage: <stage>

NODE UNDER REVIEW
- submitted_text: <proposal text>

EVALUATION TARGET
- evaluation_element_name
- rubric_context (including subordinate prompts for context)
- deterministic_guidance_text

TASK
Evaluate the text. If requirements are met, return `{ "findings": [] }`.
Otherwise, return findings specifying `issue_summary`, `evidence_basis`, `actionable_feedback`, and `severity`.
```

## Sufficient JSON Schema Sketch

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["findings"],
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "severity",
          "evidence_basis",
          "issue_summary",
          "actionable_feedback"
        ],
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["critical", "warning", "note"]
          },
          "evidence_basis": {
            "type": "string",
            "minLength": 1
          },
          "issue_summary": {
            "type": "string",
            "minLength": 1
          },
          "actionable_feedback": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    }
  }
}
```

*Note: The backend orchestrator will attach the `finding_id`, `proposal_node_logical_id`, and `evaluation_element_logical_id` to the returned objects.*

## Minimal WF Slice Plan

### Phase 0 target

Lock the problem framing:

- the current card model is insufficient
- the new output unit is `finding` at the `evaluation_element` scale
- UX must be cohesive: one actionable feedback field rather than split deterministic/LLM chunks
- empty findings signify explicitly met requirements

### Phase 1 target

Lock the product contract:

- atomic finding persistence
- review-detail API shape
- grouped node/finding UI
- slimmed prompt/schema contract for purely creative LLM output
- backward compatibility for legacy reviews

### Phase 2 target

Split into minimal tasks.

Recommended implementation order:

1. Storage contract for persisted atomic findings
2. Slim prompt/schema contract and parser tests
3. Service write path from structured-review runtime into finding persistence (attaching IDs)
4. Backend detail API carry-through
5. BFF/types carry-through
6. Review-detail UI rendering redesign
7. Walkthrough closeout with browser validation

## Suggested Task Boundaries

Keep tasks atomic and under the repo’s file-touch limits.

Recommended first three tasks:

1. Add finding storage contract and migration
2. Add slim prompt/schema contract and parser tests
3. Persist atomic element-level findings for one representative `ERC-2026-PoC` node path

## Must-Have Verification

- failing regression that proves the current card-only detail contract cannot represent element-level atomic findings
- parser/schema tests for the LLM finding JSON
- backend detail contract test proving grouped node + findings response
- frontend test proving the UI shows element-level finding items and elegant "Requirements Met" empty states
- browser validation proving the researcher can read a cohesive, single `actionable_feedback` block

## Explicit Non-Goals for the Next WF

- redesign review history/list surfaces beyond what is needed for truthful labels
- multi-call rollout beyond a narrow representative wedge unless Phase 0/1 explicitly approves it
- forcing 1:1 mapping of findings to subordinate prompts

## Ship Bar

The next WF is only complete when a researcher can open `/app/reviews/<review-id>` and see:

- reviewed nodes grouped clearly
- atomic findings listed separately by evaluation element
- a unified `actionable_feedback` narrative per finding
- a clear success state for sections that meet all element requirements
