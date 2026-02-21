# NWO Veni 2025 Pre-proposal — “North Star” (Workflow Chunk Boilerplate)

Use this short boilerplate at the top of each dedicated workflow chat when executing the NWO Veni 2025 pre-proposal work in small chunks (multiple WFs).

## Copy/paste prompt header

```text
North star: NWO Veni 2025 pre-proposal structured review.

Target structure (3 nodes):
- academic_profile (400–700 words)
- key_outputs (≤10 items; 400–700 words total explanations)
- research_idea (max 100 words default; max 500 words for ENW/Science pilot)

Evaluation:
- Single evaluation criterion (“Quality of the researcher”) refined into 8 evaluation elements.
- Alignment evaluation requires both academic_profile + research_idea.
- Missing context => mark alignment-related evaluation as NOT_ASSESSABLE (never fabricate).

Compliance:
- Deterministic compliance checks are separate from scoring.
- Enforce ERROR/WARNING rules (word limits, max outputs, no h-index/JIF, explanation per output).

Runtime:
- Primary: structured input.
- Optional: assisted extraction (paste-only) must show preview + confidence + require confirmation.

This chat is Chunk WF-[X] only.
In-scope: <exact scope for this chunk>
Out-of-scope: <explicit exclusions (e.g., no DB schema changes, no frontend changes, etc.)>
```

## Notes

- Do **not** reuse any placeholder WF ID from planning. Always mint the next WF ID from `docs/index.md`.
- Keep each chunk strictly incremental and shippable (small diff, scoped verification, docs updated).
