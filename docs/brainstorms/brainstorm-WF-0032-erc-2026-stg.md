# WF-0032 — ERC Starting Grant 2026

Artifact: brainstorm
Version: v0.0
Status: Not started
Last Updated: 2026-02-25

## Repo Reality Snapshot (Read-Only)
*Date: 2026-02-25*
- **Current Data State**: We have `erc_cog_2026_full_official.yaml` but no `ERC-2026-STG` formal V2 YAML yet.
- **Architectural Motivation**: The ingestion and `/app/reviews/[id]` UX currently assumes flat proposal structures (fitted to the existing Veni preproposal). We need an ERC STG (with deep `Part B1` / `Part B2` nesting) to force generalizations.
- **Authoring Process**: Must explicitly adhere to `docs/workflow/call-yaml-authoring-workflow.md` (separation of compliance vs. evaluation, conservative Node↔Element mapping).
- **Frontend Impact**: This workflow (WF-0032) focuses on authoring and ingesting the call definition to stress-test the backend, setting the stage for the universal Dynamic UI renderer in the next workflow.

## Preflight Checklist
**Step 1 — Long-Form Problem Intake**
User provided the following pain points & constraints:
- **Concrete examples**: The ERC 2026 StG has deep nesting (Parts B1, B2, CV, Track Record), cross-part contextual logic, and word limits defined per-part/subsection (sometimes pages instead of words). Evaluation is two-step: Step 1 evaluates B1 only; Step 2 evaluates both B1 and B2.
- **Constraints & Non-goals**: Exclude purely administrative fields, budget upload, Appendix (Current/On-going grants), Commitment Letters.
- **Quirks**: B1 = Summary (2000 chars) + Part I (5 pages) + CV/Track Record (4 pages). B2 = Part II (7 pages). Admin form "Section C. Resources" (8000 chars) is evaluated during Step 2.

### Section 1 — Problem Statement

**Decisions:**
- The primary problem is breaking the backend's flat-list assumption to expose missing relational validation/storage rules.
- We will model a single YAML containing the full structure, mapping elements unconditionally, deferring step-gating to backend execution logic.
- We will add machine-enforceable constraints like `max_pages` or `max_chars` to `content_constraints`.
- The deepest nesting boundary is cross-part (B1/B2/CV/Track Record/Resources), meaning complexity is in breadth and conditional context, not just depth.
- We will strictly follow conservative Node↔Element mapping justified by funder documentation.

**Brainstorming Q&A:**

**Q1: What is the primary problem we are solving by ingesting the ERC 2026 StG call?**
- A) Providing users to immediately generate ERC reviews on the frontend.
- B) Breaking our backend's current assumption that all proposal structures are flat lists, exposing missing relational validation/storage rules.
- C) Making sure our system knows about pages vs word counts.
> Recommendation: B — While A and C are true, the mandate from the architectural overview specifically states that the pain of deep nodes breaking our backend is the forcing function for the upcoming recursive UI changes.
> **Selected: B**

**Q2: How should our MVP address the Two-Step Evaluation (Step 1 = B1 only; Step 2 = B1+B2+Resources)?**
- A) Model two separate Call Definition YAMLs: one for `erc-2026-stg-step1` and one for `erc-2026-stg-step2`.
- B) Model one YAML containing the full structure, but add metadata tags to elements noting which step they belong to.
- C) Model one YAML containing the full structure, mapping elements unconditionally, and handle the evaluation gating logic later in backend evaluation execution workflows.
> Recommendation: C — Keeping it contained in a single YAML without introducing bespoke evaluation lifecycle metadata allows us to focus entirely on structural/nesting complexities right now, deferring the business logic of multi-step evaluation routing until necessary.
> **Selected: C**

**Q3: How should we represent "Page Limits" vs "Word/Character Limits" in our `content_constraints` modeling?**
- A) Convert page limits roughly to words (e.g., 5 pages = ~2000 words) using existing `max_words`.
- B) Introduce a new machine-enforceable constraint like `max_pages` or `max_chars`.
- C) Add it solely as a `guidance_text` warning and rely on the UI/user to enforce it for MVP, stick to existing constraints schema if strictly necessary.
> Recommendation: B — The workflow spec says all limits must be machine-enforceable. Adding `max_pages` or `max_chars` explicitly forces the schema to evolve logically rather than hacking word counts into existence.
> **Selected: B**

**Q4: Which piece of the proposal serves as the absolute deepest nesting boundary we must survive for this authoring?**
- A) `Part B1` -> `Section 1a`
- B) `Part B2` -> `State of the Art` -> `Methodology`
- C) `Part B1` / `Part B2` / `CV` / `Track Record` / `Resources` — the complexity is breadth and conditional context, not just depth.
> Recommendation: C — As you stated, cross-part logic is significant. The structure needs to support linking across distinct main components, not just deep subsections.
> **Selected: C**

**Q5: What is the strictly enforced boundary for mapping Evaluation Elements to Nodes in this ERC YAML?**
- A) We map every rubric criteria broadly to every section to be safe.
- B) We only map evaluation elements to nodes when clearly justified by funder documentation, using conservative Node↔Element mapping.
- C) We combine compliance rules into the evaluation elements.
> Recommendation: B — This is a direct rule from `call-yaml-authoring-workflow.md` (2.3).
> **Selected: B**

### Section 2 — Desired Outcome

**Decisions:**
- Success is defined purely backend and data-driven: The ingestion script must successfully parse the deep ERC 2026 StG YAML, gracefully updating the database schema if necessary, and populating the DB without errors.
- We expect the backend data model to explicitly add official support for hierarchical `proposal_nodes` (e.g., `parent_id` foreign key) and new machine-enforceable constraints (`max_pages`).
- MVP is achieved when the complete ERC 2026 StG call (B1, B2, CV, up to Resources) is authored per spec, ingested successfully, and the `GET /calls/{id}/nodes` endpoint returns the tree structure correctly.
- Pre-WF-0033 validation demands an automated backend integration test to prove the hierarchical data structural integrity in both ingestion and API retrieval.
- Backward compatibility is strictly required: the changes must not break the existing flat NWO Veni YAML ingestion.

**Brainstorming Q&A:**

**Q1: What measurable change defines success for this workflow (WF-0032)?**
- A) The frontend form can dynamically render the ERC call structure.
- B) The ingestion script successfully parses the deep ERC 2026 StG YAML, gracefully updating the database schema if necessary, and populates the DB without errors.
- C) A new evaluation endpoint is added to the API.
> Recommendation: B — We are completely deferring the dynamic frontend renderer to the next workflow (WF-0033). Success here is a pure data and backend capability milestone.
> **Selected: B**

**Q2: What behavior change do we expect from the backend's data model?**
- A) The backend adds official support for hierarchical `proposal_nodes` (e.g., via a `parent_id` self-referential foreign key) and new `max_pages`/`max_chars` constraints.
- B) The backend flattens all nested children during ingestion to keep the DB simple.
- C) The backend ignores nested children to avoid breaking the frontend.
> Recommendation: A — We explicitly want to break the flat-list assumption. Supporting a true recursive node hierarchy requires updating SQLModel tables properly.
> **Selected: A**

**Q3: What would make this “good enough” for an MVP finish?**
- A) The YAML is authored perfectly and we can manually insert the rows into Postgres.
- B) A partial ERC call (just Part B1) is fully authored, ingested, and queryable.
- C) The complete ERC 2026 StG call (B1, B2, CV, up to Resources) is authored per spec, the ingestion script handles it, and `GET /calls/{id}/nodes` returns the tree correctly.
> Recommendation: C — To actually stress test the frontend later, we need the complete disjointed structure present in the API response.
> **Selected: C**

**Q4: How do we validate success before moving to the next workflow (WF-0033)?**
- A) We write a React component to test the API response.
- B) We run automated backend integration tests to ensure the complex data structure (nodes and evaluation mappings) is preserved exactly as authored during ingestion and retrieval.
- C) We just trust the ingestion script output logs.
> Recommendation: B — A robust automated test confirming that `GET /calls/{id}/nodes` faithfully reproduces the nested hierarchy establishes our confidence boundary before we touch frontend code.
> **Selected: B**

**Q5: What happens to the existing NWO Veni YAML ingestion during this workflow?**
- A) We delete it, focusing entirely on ERC.
- B) We ensure that the schema upgrades required for the ERC call remain backward-compatible, so the NWO Veni flat structure still ingests and serves perfectly.
- C) We refactor the NWO Veni YAML to force it into a nested hierarchy too.
> Recommendation: B — Backward compatibility is essential. The new schema must support both flat (NWO) and deep (ERC) structures simultaneously.
> **Selected: B**

### Section 3 — Target User / Actor

**Decisions:**
- The primary consumer of this specific workflow's output is our own backend infrastructure (database schema, API, and validation logic), proving it can handle complex nodes.
- Future YAMLs will be authored by AI Agents (like this one) guided by strictly structured specifications and workflow runners.
- The two-step evaluation logic of the ERC StG does NOT need to be exposed to the end-user in this MVP. We author the full structure now; the UX implications of how B1 vs B2 is evaluated is deferred.
- Funder-specific compliance rules (like strict page limits) will be treated as warnings (`severity: WARNING`) to flag issues without aggressively blocking the user from receiving feedback.
- Ingestion does not require a new admin panel; it remains a developer tool (CLI script).

**Brainstorming Q&A:**

**Q1: Who is the primary consumer of this specific workflow's output?**
- A) End-users (researchers) interacting with the frontend.
- B) Backend systems (database schema, API, and validation logic) preparing for the universal form.
- C) Funders reviewing how we model their calls.
> Recommendation: B — We are explicitly not building the frontend yet. The target consumer of this ERC authoring pass is our own backend infrastructure, proving it can handle complex nodes.
> **Selected: B**

**Q2: Who will be authoring future YAMLs using the updated rules we discover here?**
- A) Non-technical administrative staff via a UI.
- B) AI Agents (like me) guided by strictly structured specifications and workflow runners.
- C) Senior developers directly writing Python code.
> Recommendation: B — We are relying on declarative YAMLs specifically so LLMs and standard workflow runners can scale our call coverage without writing new application code.
> **Selected: B**

**Q3: Does the two-step evaluation logic of the ERC StG need to be exposed to the end-user in this MVP?**
- A) Yes, the user must explicitly choose "Step 1" or "Step 2" when submitting.
- B) No, we just author the full structure. The user experience of how B1 vs B2 is evaluated is a concern for the later Review Execution phase/frontend workflows.
- C) Yes, we should refuse to accept B2 text if they are only in Step 1.
> Recommendation: B — Keep the scope tight. Author the data structure now; handle the UX implications of that structure later.
> **Selected: B**

**Q4: How should we treat funder-specific compliance rules (like the ERC's strict page limits) for the end-user?**
- A) As hard errors (`severity: ERROR`) that block parsing/submission.
- B) As warnings (`severity: WARNING`) that flag the issue in the Review results but don't prevent the AI from giving quality feedback.
- C) Ignore compliance rules; focus only on the rubric.
> Recommendation: B — As established in earlier workflows, PeerLens is an advisory tool, not a gatekeeper. We flag compliance issues, but we don't aggressively block a user from getting feedback on a slightly-too-long draft.
> **Selected: B**

**Q5: Is there any specific administrative persona (e.g., an "Approver") required to ingest this call?**
- A) Yes, we need to build an admin approval endpoint.
- B) No, ingestion remains a developer tool (CLI script) for this workflow.
> Recommendation: B — We are building infrastructure, not an admin panel. The CLI script (`scripts/ingest_call.py`) remains the ingestion mechanism.
> **Selected: B**

### Section 4 — Rough Idea Exploration

**Decisions:**
- We will support the new `max_pages` constraint by adding it to `ContentConstraintsDefinitionV2` and updating the JSONB constraints in the `proposal_node` table, keeping rules machine-enforceable.
- The hierarchical node structure will be represented relationally using a `parent_id` self-referential foreign key in the backend `CallDefinitionV2` schema and the `proposal_node` database table.
- We will defer the frontend/UX gating of Step 1 (B1 only) vs Step 2 (B1 + B2 + CV + Track Record + Resources) and simply map the relevant evaluation elements accurately to their respective nodes in the full YAML structure.
- We will strictly preserve backward compatibility: the NWO Veni YAML will remain a flat list (`parent_id: None`), proving the schema supports both flat and deep topologies transparently.
- We must implement a recursive check (e.g., in the Pydantic `model_validator` or ingest script) to explicitly reject circular references in the `parent_id` chains.

**Brainstorming Q&A:**

**Q1: What is the simplest implementation direction to support the new `max_pages` constraint?**
- A) Add `max_pages: int | None = None` to `ContentConstraintsDefinitionV2`, alongside a migration to add this column to the `proposal_node` table's JSONB constraints object.
- B) Calculate `max_pages * 400` locally and just write `max_words: 2000` into the YAML, pretending page limits don't exist.
- C) Create a whole new `PageConstraintDefinition` schema parallel to `TotalWordLimitDefinition`.
> Recommendation: A — Modifying the existing `ContentConstraintsDefinitionV2` is the most direct and least disruptive path that still gives us machine-enforceable rules specifically for pages.
> **Selected: A**

**Q2: How should we represent the nested Node hierarchy in the backend's `CallDefinitionV2` python schema?**
- A) Change `proposal_nodes: list[ProposalNodeDefinitionV2]` to a nested tree structure (e.g., `children: list[ProposalNodeDefinitionV2]`).
- B) Keep `list[ProposalNodeDefinitionV2]` flat in the YAML and schema, but add a `parent_id: str | None = None` field to each node to establish the relationships relationally.
- C) Create a separate grouping schema (e.g., `NodeGroupDefinition`) that points to flat nodes.
> Recommendation: B — A self-referential `parent_id` foreign key is the standard SQL/relational way to represent hierarchies. It keeps the ingestion payload simple (a flat list of nodes where some point to others) while allowing recursive queries in the database and API.
> **Selected: B**

**Q3: How do we handle the "Step 1" vs "Step 2" evaluation logic for this MVP?**
- A) We write a complex rule engine into the backend now.
- B) We defer evaluating Step 1 vs Step 2 entirely. We just map elements correctly (B1 elements to B1 nodes, Step 2 extra elements to B2/B1/Resources) and assume the UI/Execution phase will handle what gets shown when.
- C) We add a `stage: Literal["STEP_1", "STEP_2"]` to each node in the schema.
> Recommendation: B — Following the "simplest implementation" rule, simply associating the correct elements to their respective node targets is sufficient for the data layer. (User emphasis: Step 2 evaluates BOTH B1 and B2, so correct data modeling is crucial, but UX gating happens later).
> **Selected: B**

**Q4: Should we refactor the existing `nwo_veni` YAML right now to use `parent_id`?**
- A) Yes, rewrite the old YAML to match the new hierarchical structure exactly so everything is identical.
- B) No. Let `parent_id` default to `None`. The NWO YAML stays flat (as it naturally is), proving our new schema handles both topologies gracefully.
- C) Yes, but do it in a separate workflow.
> Recommendation: B — The whole point of backward compatibility is that a feature like nesting should be strictly opt-in based on the data.
> **Selected: B**

**Q5: What is the external dependency constraint for this workflow?**
- A) We depend on the NWO giving us their API schema.
- B) We depend *only* on the official ERC StG 2026 funder PDFs (Application Forms + Guide for Peer Reviewers) to define our structural and evaluation truth.
- C) We depend on the frontend being ready.
> Recommendation: B — Funder documentation is our single source of truth. We must not hallucinate structure or criteria.
> **Selected: B**

### Section 6 — Risks / Unknowns

**Decisions:**
- The biggest technical risk is that the ingestion script's YAML parser (Pydantic) might throw massive, unreadable validation errors on deep nesting, making debugging painful.
- Validating the actual `parent_id` foreign key constraint in the `proposal_node` table during SQLite/Postgres creation is the foundational risk and must be tested early.
- Immediate rework could be caused if we discover an ERC evaluation criterion applies to weird slices of multiple nodes, breaking our conservative mapping strategy.
- We will explicitly mitigate the `parent_id` circular reference risk by writing unit tests for `CallDefinitionV2` that catch loops during Pydantic validation.
- We cannot physically enforce `max_pages` limits via text extraction alone. We will treat `max_pages` purely as a schema field intended for UI guidance, and explicitly defer "rough heuristic conversion to machine-enforceable character limits" to a future task/parking lot item.

**Brainstorming Q&A:**

**Q1: What assumption is most fragile about ingesting the ERC 2026 StG call?**
- A) That an `erc_cog_2026_full_official.yaml` demo file already loosely exists, meaning the official ERC rubric is straightforward to extract.
- B) That the funder's PDF structure perfectly aligns with non-overlapping `evaluation_elements`.
- C) That the ingestion script's YAML parser can handle deep nesting without Pydantic throwing massive, unreadable validation errors.
> Recommendation: C — Pydantic errors on deeply nested structures can be famously opaque. If we get the schema slightly wrong in `call_definitions_v2.py`, debugging the ingestion failure will be painful.
> **Selected: C**

**Q2: What must be validated earliest in the implementation phase?**
- A) That the backend API (`GET /calls/{id}/nodes`) returns the data fast enough.
- B) The actual `parent_id` foreign key constraint in the `proposal_node` table, ensuring SQLModel creates it correctly without dropping existing data.
- C) That the LLM prompt still works.
> Recommendation: B — The database migration/schema update is the foundational risk. If the table doesn't build correctly, nothing else matters.
> **Selected: B**

**Q3: What could cause immediate rework?**
- A) The frontend team deciding they don't like `parent_id` and want a nested JSON array instead.
- B) Discovering that an ERC evaluation criterion applies to *half* of a node, rather than the whole node, forcing us to break the nodes down further than the PDF defines.
- C) Finding out another funding agency uses a completely different way of nesting.
> Recommendation: B — The "conservative Node↔Element mapping" principle is strict. If the ERC rubric assesses "impact" across a weird slice of B1 and B2, we might have to redesign where the nodes break.
> **Selected: B**

**Q4: How do we mitigate the risk of the `parent_id` circular reference loop?**
- A) Wait for it to crash in production and fix the data.
- B) Write a unit test for `CallDefinitionV2` that explicitly passes a circular YAML and expects a `ValueError`.
- C) Rely on Postgres foreign key constraints.
> Recommendation: B — Test-Driven Development (TDD) for the Pydantic schema validation is the cheapest and most reliable mitigation.
> **Selected: B**

**Q5: Is there a risk regarding "max_pages" vs character limits?**
- A) Yes, `max_pages` is inherently subjective (font size, margins) whereas characters are absolute, meaning our backend validation of `max_pages` is physically impossible until we parse the PDF.
- B) No, pages are easy to count.
- C) We should enforce `max_chars` instead.
> Recommendation: A — This is a critical unknown. If we only have raw text pasted from a UI (which is how the MVP works), we *cannot* count pages. We can only store the constraint for the UI to display as guidance, or we must introduce a rough conversion heuristic (e.g., 1 page = 4000 chars) for the backend to enforce.
> **Selected: A and B** — Defer the "rough heuristic text conversion" to a Parked/Deferred item. `max_pages` remains purely a schema transfer artifact for frontend UI display.

### Section 7 & 8 — MVP Definition and Non-Goals

**Decisions:**
- MVP requires a newly authored `erc_stg_2026_full.yaml` with the exact ERC B1/B2/Resources structure, correctly mapped criteria, successful ingestion, and automated API tests proving querying capability.
- Existing features, explicitly the dynamic frontend rendering and the backend multi-step evaluation engine mapping, will be untouched.
- We will definitely NOT include PDF parsing or specialized Step 1 vs Step 2 data endpoints.

**Brainstorming Q&A:**

**Q1: If we had to finish this workflow today, what absolute minimum must exist?**
- A) The `CallDefinitionV2` Pydantic models must have `parent_id` and `max_pages`, the database table must be updated, and `erc_cog_2026_full_official.yaml` must ingest without crashing.
- B) A newly authored `erc_stg_2026_full.yaml` with the exact ERC B1/B2/Resources structure and its criteria mapped, successfully ingested, with automated tests proving it can be queried via API.
- C) Both the ERC and NWO YAMLs ingested successfully via the CLI tool.
> Recommendation: B (with C implied) — Authoring the *real* ERC StG 2026 structure (not the old demo COG one) and proving it ingested correctly via tests is the exact MVP definition. Since backward compatibility is a constraint, C happens naturally.
> **Selected: B (and C)**

**Q2: What feature can explicitly wait until the next workflows?**
- A) Modifying the frontend application to render the tiered node groupings (B1/B2).
- B) Modifying the backend evaluation engine to group the LLM calls by Step 1 or Step 2.
- C) Both A and B.
> Recommendation: C — Leave the execution engine and the UI completely alone. We are building the data track.
> **Selected: C**

**Q3: What must NOT be included in this workflow?**
- A) A new endpoint specifically for fetching Step 1 vs Step 2 data.
- B) PDF Parsing logic for users to upload their grants instead of pasting text.
- C) Both A and B.
> Recommendation: C — Again, scope control. We are just defining data boundaries.
> **Selected: C**

---

### Out-of-Scope / Deferred to Parking Lot

The following items were explicitly identified during brainstorm as scope-creep or future requirements, and have been transferred to `docs/parking_lot.md`:

1.  **Dynamic UI Renderer (P2 #15 / #17)**: Building the frontend to actually ingest and display the new recursive ERC YAML created in this workflow.
2.  **`max_pages` text-to-page heuristic conversion**: Because we only extract plain text from the UI, we cannot effectively validate page counts blindly. We are ignoring formatting semantics (font, margins) during ingestion, and leaving `max_pages` strictly as a UI informational field. Heuristic constraint checking (e.g. 1 page = 4000 characters) is deferred.
3.  **Two-Step Evaluation Execution/UX gating**: We are authoring the full ERC structure conceptually encompassing both B1 and B2, mapping evaluation elements correctly. However, building the frontend UX or backend LLM-routing engine to conditionally execute "Step 1" vs "Step 2" is deferred to future evaluation features.
4.  **PDF Uploads / Parsing**: We will not build a PDF ingestor to enforce constraints automatically; we continue relying on User-guided snippet pasting.

### Section 5 — Constraints

**Decisions:**
- We strictly limit this workflow to authoring the YAML and proving backend ingestion/API handling, deferring all UI work.
- We will rely on SQLModel dev behavior (or local DB reset) for schema changes since Alembic is not yet wired up.
- To protect against infinite loops, we will enforce a reasonable maximum depth during ingestion validation along with strict acyclic checks on the `parent_id` foreign key.
- We will completely ignore formatting constraints (fonts, margins) and not even codify them in guidance; we aim exclusively to enforce boundaries (words/pages/chars) to evaluate textual content and avoid cluttering the database.
- We depend only on the official ERC StG 2026 funder PDFs (Application Forms + Guide for Peer Reviewers) to define structural and evaluation truth.

**Brainstorming Q&A:**

**Q1: What is our primary time/scope constraint for this workflow?**
- A) We must build the full frontend to prove it works before closing WF-0032.
- B) We must limit this workflow strictly to authoring the YAML and proving the backend ingestion/API can handle it, deferring all UI work.
- C) We need to ingest this call into production immediately.
> Recommendation: B — As established, keeping this slice thin (backend only) minimizes risk before we tackle the dynamic UI.
> **Selected: B**

**Q2: What is our primary technical constraint regarding database migrations (Alembic)?**
- A) We must write a full Alembic migration for the new `parent_id` and `max_pages` columns.
- B) Since Parking Lot P2 #1 (Set up Alembic migration baseline) is not yet done, we are still relying on SQLModel `create_all()`. We will drop/recreate local tables or ensure the new columns are nullable/have defaults so SQLModel can handle them in development safely.
- C) We shouldn't change the database schema at all.
> Recommendation: B — We don't have Alembic wired up yet. Assuming we are testing locally, relying on SQLModel's dev behavior (or a local DB reset) is our current technical constraint for schema changes.
> **Selected: B**

**Q3: What constraint MUST we apply to the `parent_id` foreign key relationships?**
- A) Nodes can be nested infinitely deep.
- B) To protect against runaway recursive queries (CTEs) or infinite loops, we must enforce a reasonable maximum depth (e.g., max 5 levels) during ingestion validation, alongside strict acyclic checks.
- C) Nodes can only have one level of nesting (a parent and a child).
> Recommendation: B — Bounded recursion protects the backend from both malicious payloads and simple authoring mistakes.
> **Selected: B**

**Q4: How do we handle `content_constraints` that we *cannot* easily machine-enforce (like "font size 11pt, 1.5 spacing, 2cm margins")?**
- A) We build a PDF parser into the backend to check margins and fonts.
- B) We ignore them completely.
- C) We encode them strictly as `guidance_text` on the node so the user is aware, but we do not attempt to machine-validate them in the `content_constraints` block.
> Recommendation: C — Separation of concerns: the backend only enforces what it has the data to enforce.
> **Selected: B** — (User override: Ignore formatting constraints entirely so as not to clutter the backend; PeerLens focuses on textual content evaluation).

**Q5: What is the external dependency constraint for this workflow?**
- A) We depend on the NWO giving us their API schema.
- B) We depend *only* on the official ERC StG 2026 funder PDFs (Application Forms + Guide for Peer Reviewers) to define our structural and evaluation truth.
- C) We depend on the frontend being ready.
> Recommendation: B — Funder documentation is our single source of truth. We must not hallucinate structure or criteria.
> **Selected: B**
