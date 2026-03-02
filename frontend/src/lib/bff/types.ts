export type ReviewStatus = "PENDING" | "COMPLETED" | "FAILED";
export type ReviewRating = "CRITICAL" | "WARNING" | "SUCCESS" | "NOTE";
export type ReviewStage = "STEP_1" | "STEP_2";

export type ApiError = {
  code: string;
  message: string;
  details: Record<string, unknown>;
  status: number;
};

export type Result<T> =
  | { ok: true; data: T }
  | { ok: false; error: ApiError };

export type BffRequestContext = {
  externalUserId: string;
};

export type CreateReviewAttempt = {
  idempotencyKey: string;
  payloadSha256: string;
  createdAtMs: number;
};

export type CallSummary = {
  id: string;
  code: string;
  name: string;
  year: number;
  agency_short_name: string;
};

export type CallsResponse = {
  calls: CallSummary[];
};

export type NodeSummary = {
  id: string;
  logical_id?: string | null;
  parent_node_id: string | null;
  title: string;
  node_type: "SECTION" | "SUBSECTION";
  order_index: number;
  has_expectations: boolean;
};

export type NodesResponse = {
  nodes: NodeSummary[];
};

export type CallConfigResponse = {
  call_logical_id: string;
  config_version: string;
  ui_mode: "legacy_single_snippet" | "structured_nodes";
  expected_nodes?: string[];
  domain_options?: Array<{
    value: string;
    label: string;
    order_index: number;
  }>;
};

export type CallNodeMetadataDto = {
  logical_id: string;
  title: string | null;
  parent_logical_id: string | null;
  source_section?: string | null;
  word_limit_min: number | null;
  word_limit_max: number | null;
};

export type CallNodesMetadataResponse = {
  call_logical_id: string;
  nodes: CallNodeMetadataDto[];
  unknown_node_logical_ids: string[] | null;
};

export type CreateReviewRequest = {
  review_stage: ReviewStage;
  call_id: string;
  node_id: string;
  snippet_text: string;
};

export type CreateReviewResponse = {
  review_id: string;
  status: ReviewStatus;
};

export type StructuredReviewNodeInput = {
  node_logical_id: string;
  text: string;
};

export type StructuredReviewRequest = {
  review_stage: ReviewStage;
  call_id: string;
  nodes: StructuredReviewNodeInput[];
};

export type ComplianceCheckRequest = {
  call_id: string;
  domain?: string | null;
  draft_nodes: StructuredReviewNodeInput[];
};

export type ViolationSeverity = "ERROR" | "WARNING";

export type ComplianceViolation = {
  node_logical_id: string;
  rule_id: string;
  severity: ViolationSeverity;
  actual: string;
  expected: string;
  message: string;
  is_blocking: boolean;
};

export type ComplianceCheckResponse = {
  is_compliant: boolean;
  errors: ComplianceViolation[];
  warnings: ComplianceViolation[];
};

export type ReviewSummary = {
  id: string;
  status: ReviewStatus;
  overall_rating: ReviewRating | null;
  overall_summary: string | null;
};

export type ReviewCardSummary = {
  id: string;
  node_expectation_id: string;
  node_logical_id?: string | null;
  node_title: string;
  criterion: string;
  criterion_description?: string | null;
  evaluation_element_name: string;
  expectation_guidance_note?: string | null;
  rating: ReviewRating;
  feedback_text: string;
  assessment_status?: "ASSESSED" | "NOT_ASSESSABLE" | null;
  not_assessable_reason?: string | null;
};

export type ReviewDetailResponse = {
  call_id?: string | null;
  call_code?: string | null;
  ordering_source?: "call_nodes" | "review_payload_fallback";
  unmapped_node_logical_ids?: string[];
  review: ReviewSummary;
  cards: ReviewCardSummary[];
};

export type DeleteReviewResponse = {
  ok: boolean;
};

export type ReviewListItem = {
  id: string;
  status: ReviewStatus;
  overall_rating: ReviewRating | null;
  created_at: string;
  call_name: string;
  node_title: string;
};

export type ReviewsListResponse = {
  reviews: ReviewListItem[];
};
