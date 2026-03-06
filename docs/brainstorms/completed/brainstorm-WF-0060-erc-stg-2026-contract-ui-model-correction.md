<!-- docs/brainstorms/brainstorm-WF-0060-erc-stg-2026-contract-ui-model-correction.md -->
# WF-0060 — ERC StG 2026 Contract/UI Model Correction

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-06

Type: feature

## Preflight Checklist

### Step 1 — Long-Form Problem Intake

- The current ERC StG 2026 call model appears to conflate structural grouping nodes with applicant-entered proposal surfaces.
- That distortion leaks upward into submit UX, persisted submitted-node coverage, review-detail ordering, and test fixtures introduced in WF-0059.
- The corrective goal is source-first: re-anchor the contract in the official ERC 2026 Starting Grant application form and work programme, then plan the narrowest safe propagation through ingestion, backend behavior, frontend rendering, submission, persisted submitted-node coverage, and review-detail semantics.
- This workflow does not start implementation yet. Phase 0 closes only when the corrected semantics and migration boundary are explicit enough to replace WF-0059 assumptions safely.

## Repo Reality Snapshot (Read-Only) (2026-03-06)

- [backend/data/calls/canonical/erc/erc_stg_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_stg_2026_full.yaml) currently models `b1` and `b2` as expectation-bearing nodes and leaves `resources_time_commitment` as a top-level section.
- That current shape is convenient for the WF-0059 tracer path, but it is not a defensible source-truth if `b1`/`b2` are merely document containers and Section C Resources belongs under Part A / Budget.
- [docs/walkthroughs/completed/walkthrough-WF-0059-multi-call-ux-unblocker.md](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/walkthroughs/completed/walkthrough-WF-0059-multi-call-ux-unblocker.md) proves runtime support for the old ERC proof-call shape; it must not be treated as semantic authority for ERC StG 2026.
- The safe corrective strategy is therefore contract-first with explicit compatibility treatment for legacy WF-0059 review records and tests.

## Source Grounding

Primary sources used for this Phase 0 artifact:

- [backend/data/calls/canonical/erc/erc_cog_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_cog_2026_full.yaml) as the internal reference pattern to critique, not as ERC StG truth.
- `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-StG-2026/af_he-erc-stg_en.pdf`
- `/home/mgurram/Projects/Non-Github/PeerLens_proj/ERC-StG-2026/wp_horizon-erc-2026_en.pdf`

Source-backed facts for correction:

- The application form places `Section C. Resources (Maximum 8000 characters allowed)` under `Part A -> 3 - Budget`, not under `Part B2`.
- The application form presents `Part B1` as a container for `Proposal summary`, `Part I of the Scientific Proposal`, and `Curriculum vitae and Track Record`.
- The application form presents `Part B2` as a container for `Part II of the Scientific Proposal`.
- The work programme states that `Part I and Part II of the Scientific Proposal, Curriculum Vitae and Track Record, Resources and Time Commitment` are collectively the `Research Proposal`.
- The work programme states that Step 1 assesses `Part I of the Scientific Proposal` plus `CV and Track Record`, while Step 2 assesses the complete `Research Proposal`.
- The application form states that the abstract / `Proposal summary` "will be used ... in the evaluation process", which supports modeling it as a real reviewable surface rather than dropping it as metadata.

## Corrected Hierarchy Proposal

Canonical top-level call:

```text
erc_stg_2026_full
- part_a
  - budget
    - resources_time_commitment
- part_b
  - b1
    - proposal_summary
    - b1_part1_scientific_proposal
    - b1_cv_track_record
  - b2
    - b2_part2_scientific_proposal
```

Proposed semantic rules:

- `part_a`, `budget`, `part_b`, `b1`, and `b2` are structural containers only.
- They should not be applicant-editable text surfaces.
- They should not carry direct node expectations unless later source evidence proves a container itself is reviewed independently from its child content.
- The reviewable/input-bearing units should be the actual content-bearing leaf nodes shown in the official form.
- `Part I` and `Part II` should each be modeled as one applicant-entered node, not split into inferred internal subsections, because the source forms define them as single uploaded narrative sections.

## Node Semantics

| Node | Role | Input-bearing | Reviewable | Stage | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `part_a` | structural only | no | no | n/a | top-level admin container |
| `budget` | structural only | no | no | n/a | form grouping for Part A Section 3 |
| `resources_time_commitment` | input-bearing | yes | yes | STEP_2 | Part A Section C text field; belongs under budget |
| `part_b` | structural only | no | no | n/a | top-level narrative container |
| `b1` | structural only | no | no | n/a | Part B1 document container |
| `proposal_summary` | input-bearing | yes | yes | BOTH | applicant-entered summary inside Part B1; AF says it is used in the evaluation process |
| `b1_part1_scientific_proposal` | input-bearing | yes | yes | BOTH | Part I narrative surface |
| `b1_cv_track_record` | input-bearing | yes | yes | BOTH | CV + Track Record narrative surface |
| `b2` | structural only | no | no | n/a | Part B2 document container |
| `b2_part2_scientific_proposal` | input-bearing | yes | yes | STEP_2 | Part II narrative surface |

Context-only nodes:

- None in the current correction proposal. Every non-structural node above represents real applicant-entered proposal content.

## Critical Semantics To Preserve

- `proposal_summary` must not disappear just because the work programme's step text foregrounds Part I and CV/Track Record; the application form explicitly says the summary is used in the evaluation process, which supports keeping it reviewable in Step 1 and Step 2.
- `resources_time_commitment` must move under `Part A / Budget` in the contract, while still remaining reviewable only at Step 2.
- `b1` and `b2` should stop carrying expectations. Expectations belong on the leaf nodes actually containing applicant text.
- `Part I` and `Part II` should remain whole-node surfaces unless and until official ERC source text justifies a finer-grained applicant-facing contract.

## Minimal Safe Migration Path

1. Correct the canonical YAML first.
   Replace container-as-surface semantics in [backend/data/calls/canonical/erc/erc_stg_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_stg_2026_full.yaml) while keeping stable logical IDs where semantics remain valid.
2. Add container-awareness to ingestion/runtime.
   Introduce explicit container semantics so structural nodes render as grouping only and are excluded from editable/reviewable leaf submission sets.
3. Preserve legacy review-detail compatibility.
   Old WF-0059 reviews that persisted `submitted_node_logical_ids = ["b1", ...]` or `["b2", ...]` need compatibility expansion for display and coverage accounting rather than hard failure.
4. Migrate submit/frontend behavior to leaf-node submission.
   The submit model should collect text only for `proposal_summary`, `b1_part1_scientific_proposal`, `b1_cv_track_record`, `b2_part2_scientific_proposal`, and `resources_time_commitment`.
5. Re-baseline review-detail semantics.
   Persisted submitted-node coverage, reviewed/not-reviewed grouping, and zero-card coverage must operate on leaf nodes, not containers.

Compatibility rule for existing WF-0059-era records:

- Legacy container submissions should not be optimistically expanded into reviewed leaf coverage by default.
- Legacy `b1` and `b2` references should be treated as ambiguous container-era evidence unless companion payload data proves which leaf nodes were actually submitted.
- Legacy review detail may render a compatibility note that coverage originated from deprecated container semantics rather than leaf-node semantics.
- Legacy top-level `resources_time_commitment` references should resolve to the moved node under `part_a -> budget` without changing the logical leaf ID.

## Risks To WF-0059 Assumptions And Tests

These WF-0059 assumptions should be treated as invalid once the contract is corrected:

- Tests or fixtures that submit `b1` or `b2` as if they were editable text nodes.
- Assertions that container nodes emit review cards or reviewed-node coverage directly.
- Expectations that `resources_time_commitment` is a top-level sibling of `b1` and `b2`.
- Review-detail ordering/coverage snapshots that encode the old proof-call shape instead of deriving from the corrected leaf-node hierarchy.
- Any node-expectation mapping on `b1` or `b2` themselves.
- Compatibility assumptions that expand legacy container submissions into optimistic leaf-node reviewed coverage without proof.

Required replacement direction:

- Replace container-node submission tests with leaf-node submission tests.
- Replace container-node review-detail assertions with leaf-coverage assertions plus structural grouping assertions.
- Rebuild proof artifacts against the corrected ERC StG hierarchy after implementation.

## MVP Boundary For This Corrective WF

- In scope: source-grounded ERC StG 2026 contract correction and the minimum downstream changes required to make the corrected hierarchy the source of truth across ingestion, submit UX, persisted coverage, and review detail.
- Out of scope for Phase 0: implementation, broad universal-call redesign, and any re-authoring of other calls unless needed as compatibility controls.

## Approval Target

This brainstorm is ready for review if the user agrees on:

- the corrected hierarchy above
- the classification of structural-only vs input-bearing vs reviewable nodes
- the compatibility treatment for legacy WF-0059 records
- the rule that container nodes must stop carrying expectations and direct review surfaces
