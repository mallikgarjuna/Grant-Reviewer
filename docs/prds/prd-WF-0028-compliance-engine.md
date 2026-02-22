# WF-0028 — NWO Veni 2025 preproposal Compliance Engine PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-22

## 1. In Scope

- A deterministic backend Python service/endpoint (`/api/check-compliance`) that validates proposed grant text against canonical rule definitions.
- Sourcing compliance rules exclusively from the canonical `CallDefinition` JSON via `CallDefinitionService.get_hydrated_nodes()`.
- Evaluating deterministic node-level rules:
  - Text presence (Mandatory fields).
  - Minimum and maximum word limits, dependent on the user's `domain` selection (e.g., specific rules for ENW vs. SGW).
  - Maximum items (if the input format supports itemization).
- Returning a structured JSON payload defining explicit errors and warnings with fields: `node_logical_id`, `rule_id`, `severity`, `actual`, `expected`, `message`, and `is_blocking`.

## 2. Out of Scope

- Parent-child aggregate word counting (as the V2 ingestion currently flattens nodes with `parent_node_id=None`).
- Parsing or enforcing complex natural-language `compliance_rules` and `guidance_text` deterministically (these are surfaced read-only to the UI if needed, but not evaluated by the engine).
- Auto-fixing or truncating text automatically.
- Evaluating subjective guidelines using an LLM (e.g., "Is the tone appropriate?"). This is deferred to the AI Review workflow (WF-5).
- Building the UI form that consumes and displays these errors (WF-6).
- Persisting a multi-node "Draft" aggregate to the database.

## 3. User / System Flow

- **Happy Path:**
  1. The researcher clicks "Check Compliance" in the frontend UI.
  2. The frontend POSTs a payload containing the `call_id`, the selected `domain`, and a flat list of `draft_nodes` (Node ID + Snippet Text).
  3. The backend hydrates the canonical rules for the `call_id`.
  4. The engine evaluates each `draft_node` against its specific constraints (`word_limit_by_domain`, mandatory presence).
  5. The backend returns HTTP 200 with an empty lists of errors and warnings.
  6. The UI displays "All Checks Passed" and enables the AI Review submission button.

- **Failure Path 1 (Word Limit Exceeded):**
  1. The researcher clicks "Check Compliance".
  2. The engine detects that the "Academic Profile" node exceeds the domain-specific word limit.
  3. The backend returns HTTP 200 with a structured Error (`is_blocking=True`) detailing the `logical_id`, `expected` count, `actual` count, and a clear `message`.

- **Failure Path 2 (Missing Domain):**
  1. The frontend POSTs the payload but omits the `domain` field for a domain-dependent call.
  2. The backend returns HTTP 422 Unprocessable Entity, requiring precisely which payload field is missing.

## 4. Functional Requirements

- **F1 (Hydration):** The engine MUST load constraints using `CallDefinitionService.get_hydrated_nodes(call_id)`.
- **F2 (Word Counting):** The engine MUST implement a standard, predictable word-counting algorithm (e.g., splitting by whitespace after stripping basic markdown/HTML) to compare against limits. Note: The UI must display a disclaimer that counts are approximate.
- **F3 (Domain-Awareness):** The engine MUST accept a `domain` string to correctly resolve `word_limit_by_domain` constraints found in the NWO Veni `content_constraints` JSON block.
- **F4 (Mandatory Evaluation):** The engine MUST determine "mandatory" status deterministically. *(Note: The PRD Needs to explicitly define the source of 'mandatory' since V2 schema relies on Expectation Strength. We will define a node as mandatory if it has ANY constraints or expectations defined, OR if we explicitly add a 'mandatory: true' flag to the JSON config).*
- **F5 (Decoupled Logic):** The core compliance evaluation MUST be a pure Python function (`def evaluate_compliance(payload) -> ComplianceReport`) decoupled from the FastAPI transport layer to enable exhaustive unit testing without HTTP overhead.

## 5. Data & API Contracts

**Request Payload (`POST /api/check-compliance`):**
```json
{
  "call_id": "uuid",
  "domain": "ENW",
  "draft_nodes": [
    {
      "node_id": "uuid",
      "text": "The quick brown fox..."
    }
  ]
}
```

**Response Payload (`HTTP 200 OK`):**
```json
{
  "is_compliant": false,
  "errors": [
    {
      "node_logical_id": "academic_profile",
      "rule_id": "word_limit_max",
      "severity": "ERROR",
      "actual": "1250",
      "expected": "1200",
      "message": "Word limit exceeded by 50 words.",
      "is_blocking": true
    }
  ],
  "warnings": [
    {
      "node_logical_id": "key_output_1",
      "rule_id": "mandatory_presence",
      "severity": "WARNING",
      "actual": "Missing",
      "expected": "Present",
      "message": "This section is highly recommended.",
      "is_blocking": false
    }
  ]
}
```

## 6. Components / Modules

- **`app.schemas.compliance`**: Pydantic models for the request and response contracts defined above.
- **`app.services.compliance_engine`**: The pure Python service containing `evaluate_compliance()`. It handles word counting, domain resolution, and rule evaluation.
- **`app.api.routes.compliance`**: FastAPI router exposing `POST /api/check-compliance`, injecting the `CallDefinitionService` and delegating to the `compliance_engine`.

## 7. Edge Cases

- **Empty Text:** A user sends `{"text": "   \n  "}`. The engine must strip whitespace and treat it as empty/missing for mandatory checks.
- **Missing Constraints:** A node is submitted that has no defined `content_constraints` in the canonical JSON. The engine should pass it by default (return no errors).
- **Word Counting Artifacts:** LaTeX equations or Markdown syntax (`**bold**`) artificially inflating word counts. The engine should ideally strip non-visible markdown before counting, or at least document its exact naive splitting behavior.

## 8. Telemetry (Minimal)

- Log a standard warning if `evaluate_compliance` takes longer than 500ms (it should be <50ms).
- Track the ratio of `is_compliant: true` vs `false` to understand how often users are blocked (optional MVP, can just use standard API access logs).

## Deferred / Not in MVP

- Hierarchical aggregate word counting.
- Evaluation of qualitative `compliance_rules` strings.

## Open Questions

- **Mandatory Source:** How exactly do we determine if a node is mandatory given the V2 schema lacks an explicit boolean? (Recommendation: We assume a node is mandatory if it has a `content_constraints.word_limit` defined, or we must update the YAML ingestion to include an explicit `mandatory: true` flag in `content_constraints`).

## Changelog

- v0.1 (2026-02-22): Initial PRD generated directly from Brainstorm v0.1.
