export type ReviewStatus = "PENDING" | "COMPLETED" | "FAILED";
export type ReviewRating = "CRITICAL" | "WARNING" | "SUCCESS" | "NOTE";

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
  parent_node_id: string | null;
  title: string;
  node_type: "SECTION" | "SUBSECTION";
  order_index: number;
  has_expectations: boolean;
};

export type NodesResponse = {
  nodes: NodeSummary[];
};

export type CreateReviewRequest = {
  call_id: string;
  node_id: string;
  snippet_text: string;
};

export type CreateReviewResponse = {
  review_id: string;
  status: ReviewStatus;
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
  criterion: string;
  rating: ReviewRating;
  feedback_text: string;
};

export type ReviewDetailResponse = {
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
