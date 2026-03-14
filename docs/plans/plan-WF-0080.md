<!-- docs/plans/plan-WF-0080.md -->
# Plan — WF-0080 Atomic Finding Model for Structured Review Output

Status: Draft helper plan
WF ID assumption: `WF-0080` is the next available WF after `WF-0079`
Purpose: reusable reference for future Phase 0/1/2 runners

## Important Usage Note

This file is a planning helper, not a workflow artifact substitute.
Use it to seed the next WF, then create the canonical brainstorm/PRD/task/walkthrough artifacts under `docs/` per the workflow system.

Suggested future-chat prompt:

```text
Use @docs/plans/plan-WF-0080.md
Start WF-0080 using the standard phase runners.
Treat the plan as intent/reference only.
Generate the canonical WF artifacts from it.
```

## Intent

Move the structured-review output from the current coarse card model to an atomic finding model.
Each visible finding should be traceable to:

- one `proposal_node`
- one `evaluation_element`
- one `subordinate_prompt`

Each finding should carry its own structured feedback fields instead of collapsing everything into one `feedback_text` blob plus an optional additive companion paragraph.

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
- `subordinate_prompt` traceability is not first-class in the output
- OpenAI synthesis is additive wording only, not atomic finding generation

## Outcome Definition

The new sufficient output unit is:

```text
review
  -> reviewed_node[]
     -> finding[]
```

Each finding must be a first-class object with explicit traceability and structured feedback parts.

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
- subordinate_prompt_id_snapshot
- subordinate_prompt_text_snapshot
- finding_status
- severity
- assessment_status
- evidence_basis_text
- issue_summary_text
- deterministic_guidance_text
- llm_guidance_text nullable
- source_mode ("deterministic" | "llm_additive" | "hybrid")
- created_at
```

Why this is sufficient:

- `ReviewCard` is too coarse for the required traceability
- snapshots preserve historical renderability even if call YAML changes later
- separate deterministic vs additive LLM fields keep truthfulness explicit

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
- subordinate_prompt
- severity
- assessment_status
- evidence_basis
- issue_summary
- deterministic_guidance
- llm_guidance nullable
- source_mode
```

### 4. Sufficient UI changes

Replace the current “one large card body” reading flow with:

```text
Reviewed section
  -> Finding list
     -> one bordered finding item per subordinate prompt finding
        -> issue summary
        -> evidence basis
        -> deterministic guidance
        -> additive llm guidance (if present)
        -> traceability chips/labels
```

Minimum visible traceability labels:

- `Reviewed section`
- `Evaluation criterion`
- `Evaluation element`
- `Subordinate prompt`
- `Deterministic guidance`
- `Additive LLM guidance` when present

## Sufficient Prompt Contract

The prompt must stop asking for one merged feedback blob.
It must ask for atomic findings keyed to node + evaluation element + subordinate prompt.

### Prompt shape

System intent:

```text
You are generating structured review findings for grant proposal text.
Return atomic findings only.
Each finding must map to exactly one proposal node, one evaluation element, and one subordinate prompt.
Do not merge multiple subordinate prompts into one finding.
Do not return free-form prose outside the JSON schema.
Keep deterministic traceability fields unchanged when provided.
LLM guidance must be additive and must not replace deterministic guidance.
If evidence is insufficient, return no finding or mark assessment_status accordingly; do not hallucinate evidence.
```

User payload skeleton:

```text
CALL CONTEXT
- call_code: <call_code>
- review_stage: <stage>

NODE UNDER REVIEW
- proposal_node_logical_id: <node_id>
- proposal_node_title: <title>
- submitted_text: <proposal text>

TRACEABLE EVALUATION TARGETS
- evaluation_criterion_logical_id
- evaluation_criterion_name
- evaluation_element_logical_id
- evaluation_element_name
- subordinate_prompt_id
- subordinate_prompt_text
- deterministic_guidance_text

TASK
For each subordinate prompt target, decide whether there is a reviewer-visible finding.
Return zero or more atomic findings.
Each finding must:
- reference the exact proposal node, evaluation element, and subordinate prompt
- explain the issue in a short issue_summary
- cite grounded evidence from the submitted text in evidence_basis
- preserve deterministic guidance as provided
- optionally add concise llm_guidance that helps revision
```

## Sufficient JSON Schema Sketch

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["proposal_node_logical_id", "findings"],
  "properties": {
    "proposal_node_logical_id": {
      "type": "string",
      "minLength": 1
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "finding_id",
          "proposal_node_logical_id",
          "evaluation_criterion_logical_id",
          "evaluation_criterion_name",
          "evaluation_element_logical_id",
          "evaluation_element_name",
          "subordinate_prompt_id",
          "subordinate_prompt_text",
          "severity",
          "assessment_status",
          "evidence_basis",
          "issue_summary",
          "deterministic_guidance",
          "llm_guidance",
          "source_mode"
        ],
        "properties": {
          "finding_id": {
            "type": "string",
            "minLength": 1
          },
          "proposal_node_logical_id": {
            "type": "string",
            "minLength": 1
          },
          "evaluation_criterion_logical_id": {
            "type": "string",
            "minLength": 1
          },
          "evaluation_criterion_name": {
            "type": "string",
            "minLength": 1
          },
          "evaluation_element_logical_id": {
            "type": "string",
            "minLength": 1
          },
          "evaluation_element_name": {
            "type": "string",
            "minLength": 1
          },
          "subordinate_prompt_id": {
            "type": "string",
            "minLength": 1
          },
          "subordinate_prompt_text": {
            "type": "string",
            "minLength": 1
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "warning", "note", "success"]
          },
          "assessment_status": {
            "type": "string",
            "enum": ["ASSESSED", "NOT_ASSESSABLE"]
          },
          "evidence_basis": {
            "type": "string",
            "minLength": 1
          },
          "issue_summary": {
            "type": "string",
            "minLength": 1
          },
          "deterministic_guidance": {
            "type": "string",
            "minLength": 1
          },
          "llm_guidance": {
            "type": ["string", "null"]
          },
          "source_mode": {
            "type": "string",
            "enum": ["deterministic", "llm_additive", "hybrid"]
          }
        }
      }
    }
  }
}
```

## Minimal WF Slice Plan

### Phase 0 target

Lock the problem framing:

- the current card model is insufficient
- the new output unit is `finding`
- traceability must include `proposal_node`, `evaluation_element`, and `subordinate_prompt`
- additive LLM text must stay visibly separate from deterministic guidance

### Phase 1 target

Lock the product contract:

- atomic finding persistence
- review-detail API shape
- grouped node/finding UI
- prompt/schema contract for OpenAI generation
- backward compatibility for legacy reviews

### Phase 2 target

Split into minimal tasks.

Recommended implementation order:

1. Storage contract for persisted atomic findings
2. Prompt/schema contract for atomic finding generation
3. Service write path from structured-review runtime into finding persistence
4. Backend detail API carry-through
5. BFF/types carry-through
6. Review-detail UI rendering redesign
7. Copy/export truthfulness review
8. Walkthrough closeout with browser validation

## Suggested Task Boundaries

Keep tasks atomic and under the repo’s file-touch limits.

Recommended first three tasks:

1. Add finding storage contract and migration
2. Add prompt/schema contract and parser tests
3. Persist atomic findings for one representative `ERC-2026-PoC` node path

## Must-Have Verification

- failing regression that proves the current card-only detail contract cannot represent subordinate-prompt atomic findings
- parser/schema tests for the LLM finding JSON
- persistence test proving one finding per subordinate prompt
- backend detail contract test proving grouped node + findings response
- frontend test proving the UI shows one finding item per subordinate prompt
- browser validation proving the researcher can distinguish deterministic guidance from additive LLM guidance

## Explicit Non-Goals for the Next WF

- redesign review history/list surfaces beyond what is needed for truthful labels
- multi-call rollout beyond a narrow representative wedge unless Phase 0/1 explicitly approves it
- replacing deterministic guidance with LLM-only guidance
- free-form markdown dumping as the primary output unit

## Ship Bar

The next WF is only complete when a researcher can open `/app/reviews/<review-id>` and see:

- reviewed nodes grouped clearly
- atomic findings listed separately
- each finding traceable to one evaluation element and one subordinate prompt
- deterministic guidance clearly separated from additive LLM guidance
- no ambiguity about which part came from the deterministic engine vs the LLM
