# WF-0028 — NWO Veni 2025 preproposal Compliance Engine PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-22

## 1. In Scope

- A deterministic backend Python service/endpoint (`/api/check-compliance`) that validates proposed grant text against canonical rule definitions.
- Sourcing compliance rules exclusively from the canonical `CallDefinition` JSON via `CallDefinitionService.get_hydrated_nodes()`.
- Evaluating deterministic node-level rules:
  - Text presence (Mandatory fields).
  - Minimum and maximum word limits (`total_word_limit.min_words`/`max_words`), and domain-specific overrides (`word_limit_by_domain.science_enw_max_words`).
- Returning a structured JSON payload defining explicit errors and warnings with fields: `node_logical_id`, `rule_id`, `severity`, `actual`, `expected`, `message`, and `is_blocking`.

## 2. Out of Scope

- Parent-child aggregate word counting (as the V2 ingestion currently flattens nodes with `parent_node_id=None`).
- Parsing or enforcing complex natural-language `compliance_rules` and `guidance_text` deterministically (these are surfaced read-only to the UI if needed, but not evaluated by the engine).
- Validating `max_items` constraints (this requires a structured itemized input format, which is explicitly removed from MVP to keep the text-only payload simple).
- Auto-fixing or truncating text automatically.
- Evaluating subjective guidelines using an LLM (e.g., "Is the tone appropriate?"). This is deferred to the AI Review workflow (WF-5).
- Building the UI form that consumes and displays these errors (WF-6).
- Persisting a multi-node "Draft" aggregate to the database.

## 3. User / System Flow

- **Happy Path:**
  1. The researcher clicks "Check Compliance" in the frontend UI.
  2. The frontend POSTs a payload containing the `call_id`, the optional `domain` selection, and a flat list of `draft_nodes` (Node Logical ID + Snippet Text).
  3. The backend hydrates the canonical rules for the `call_id`.
  4. The engine evaluates each `draft_node` against its specific constraints (`total_word_limit`, optional `word_limit_by_domain`, and mandatory presence).
  5. The backend returns HTTP 200 with empty lists mapping `errors` and `warnings` to `node_logical_id`.
  6. The UI displays "All Checks Passed" and enables the AI Review submission button.

- **Failure Path 1 (Word Limit Exceeded):**
  1. The researcher clicks "Check Compliance".
  2. The engine detects that the "Academic Profile" node exceeds the domain-specific word limit.
  3. The backend returns HTTP 200 with a structured Error (`is_blocking=True`) detailing the `logical_id`, `expected` count, `actual` count, and a clear `message`.

- **Failure Path 2 (Schema/Validation Error):**
  1. The frontend POSTs a payload with a `node_logical_id` that does not exist in the hydrated `CallDefinition` for that `call_id`, OR it omits the `domain` field when a call requires a domain-specific check.
  2. The backend returns HTTP 422 Unprocessable Entity, requiring precisely which payload field/ID is invalid or missing.

## 4. Functional Requirements

- **F1 (Hydration):** The engine MUST load constraints using `CallDefinitionService.get_hydrated_nodes(call_id)`.
- **F2 (Word Counting):** The engine MUST implement a standard, predictable word-counting algorithm (e.g., splitting by whitespace after stripping basic markdown/HTML) to compare against limits. Note: Semantic exclusions (e.g., "excludes references") are ignored in MVP; we use a single native tokenization strategy and note this limitation in the UI.
- **F3 (Domain-Awareness):** The engine accepts an *optional* `domain` string (using canonical lowercase IDs like `science_enw`). It evaluates `word_limit_by_domain` only if provided. If a domain-specific limit exists, it takes precedence over `total_word_limit.default_max_words`. If a call requires a domain limit and the field is missing, it returns a 422.
- **F4 (Mandatory Evaluation):** The engine MUST determine "mandatory" status deterministically. A node is considered mandatory if its `content_constraints` specifies `total_word_limit.min_words` (or a domain-specific minimum) > 0, OR if `node_expectations` contains an element designated as `MANDATORY` by the call policy. If a node is mandatory but omitted from the payload or is empty, it fails validation. (The engine must NOT look for `word_limit` or `mandatory: true` flat fields as they are not in the V2 schema).
- **F5 (Decoupled Logic):** The core compliance evaluation MUST be a pure Python function (`def evaluate_compliance(payload, hydrated_nodes) -> ComplianceReport`) decoupled from the FastAPI transport layer to enable exhaustive unit testing without HTTP overhead.

## 5. Data & API Contracts

**Request Payload (`POST /api/check-compliance`):**
```json
{
  "call_id": "uuid",
  "domain": "science_enw",
  "draft_nodes": [
    {
      "node_logical_id": "academic_profile",
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
- **`main.py` (or `app.api.routes.compliance`)**: The FastAPI router defining `POST /api/check-compliance`. (Implementation should follow the existing centralized routing pattern or explicitly extract to a `routes/` module if refactoring).

## 7. Edge Cases

- **Missing Expected Nodes:** If the `CallDefinition` declares a node as mandatory, but the frontend omits its `node_logical_id` from the `draft_nodes` array entirely, it must be flagged identically to submitting empty text (Blocking Error).
- **Unknown Node IDs:** If the frontend submits a `node_logical_id` not present in the call configuration, return a 422 Unprocessable Entity immediately to fail fast.
- **Precedence of Limits:** If both `total_word_limit` and `word_limit_by_domain` exist on a node, the domain-specific limit strictly overrides the default total.
- **Auth Contract:** The compliance endpoint does NOT persist `User` review history, but it SHOULD inherit the same API authentication dependencies (`X-GR-User-Id` BFF boundaries) as the rest of the application to prevent unauthenticated scraping.
- **Word Counting Artifacts:** LaTeX equations or Markdown syntax (`**bold**`) artificially inflating word counts. The engine will use a single standard tokenization strategy and ignore complex semantic exclusions (e.g. "excludes references") for MVP.

## 8. Telemetry (Minimal)

- Log a standard warning if `evaluate_compliance` takes longer than 500ms (it should be <50ms).
- Track the ratio of `is_compliant: true` vs `false` to understand how often users are blocked (optional MVP, can just use standard API access logs).

## Deferred / Not in MVP

- Hierarchical aggregate word counting.
- Evaluation of qualitative `compliance_rules` strings.

## Open Questions

- None. (Resolved: Mandatory source defined by expectation strength or min_words constraint).

## Changelog

- v0.1 (2026-02-22): Initial PRD generated directly from Brainstorm v0.1.
- v0.3 (2026-02-22): Addressed Phase 1.2 risk audit: switched to `node_logical_id`, dropped `max_items` MVP scope, defined mandatory heuristics, added 422 edge cases, clarified domain overriding.
