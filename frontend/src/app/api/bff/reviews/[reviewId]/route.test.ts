// frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

const authMock = vi.fn();
const getReviewMock = vi.fn();

vi.mock("@clerk/nextjs/server", () => ({
  auth: authMock,
}));

vi.mock("@/lib/bff/adapter", () => ({
  getReview: getReviewMock,
  deleteReview: vi.fn(),
}));

describe("GET /api/bff/reviews/[reviewId]", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.unstubAllEnvs();
  });

  it("wf0067_bff_review_detail_preserves_backend_trust_fields", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    getReviewMock.mockResolvedValue({
      ok: true,
      data: {
        call_id: "call-1",
        call_code: "nwo_veni_2025_preproposal",
        ordering_source: "call_nodes",
        submitted_node_logical_ids: ["key_outputs"],
        submitted_leaf_ids: ["key_outputs"],
        primary_evaluated_node_logical_ids: ["key_outputs"],
        supporting_context_node_logical_ids: [],
        review: {
          id: "review-1",
          status: "COMPLETED",
          overall_rating: "SUCCESS",
          overall_summary: "Summary",
        },
        cards: [
          {
            id: "card-1",
            node_expectation_id: "expectation-1",
            node_logical_id: "key_outputs",
            node_title: "Key outputs",
            criterion: "Quality",
            criterion_description: "Quality criterion",
            evaluation_element_name: "Peer-exceeding quality",
            expectation_guidance_note: null,
            rating: "SUCCESS",
            feedback_text: "Feedback",
            assessment_status: "ASSESSED",
            not_assessable_reason: null,
            source_basis_label: "Call for Proposals (Veni 2025) §4.3.1",
            source_basis_state: "available",
          },
          {
            id: "card-2",
            node_expectation_id: "expectation-2",
            node_logical_id: "research_idea",
            node_title: "Research idea",
            criterion: "Quality",
            criterion_description: "Quality criterion",
            evaluation_element_name: "CV-idea alignment",
            expectation_guidance_note: null,
            rating: "NOTE",
            feedback_text: "Feedback",
            assessment_status: "NOT_ASSESSABLE",
            not_assessable_reason: "insufficient_evidence",
            source_basis_label: null,
            source_basis_state: "unavailable",
          },
        ],
      },
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ reviewId: "review-1" }),
    });
    const body = (await response.json()) as {
      cards: Array<{
        source_basis_label: string | null;
        source_basis_state: string;
      }>;
      supporting_context_node_logical_ids: string[];
    };

    expect(response.status).toBe(200);
    expect(body.cards[0].source_basis_label).toBe(
      "Call for Proposals (Veni 2025) §4.3.1",
    );
    expect(body.cards[0].source_basis_state).toBe("available");
    expect(body.cards[1].source_basis_label).toBeNull();
    expect(body.cards[1].source_basis_state).toBe("unavailable");
    expect(body.supporting_context_node_logical_ids).toEqual([]);
  });

  it("wf0067_bff_review_detail_unavailable_source_basis_preserved", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    getReviewMock.mockResolvedValue({
      ok: true,
      data: {
        call_id: null,
        call_code: null,
        ordering_source: "review_payload_fallback",
        submitted_node_logical_ids: ["legacy_section"],
        submitted_leaf_ids: [],
        primary_evaluated_node_logical_ids: [],
        supporting_context_node_logical_ids: [],
        review: {
          id: "review-legacy-1",
          status: "COMPLETED",
          overall_rating: "NOTE",
          overall_summary: "Legacy summary",
        },
        cards: [
          {
            id: "legacy-card-1",
            node_expectation_id: "expectation-legacy",
            node_logical_id: null,
            node_title: "Legacy section",
            criterion: "Excellence",
            criterion_description: "Excellence criterion",
            evaluation_element_name: "Legacy element",
            expectation_guidance_note: null,
            rating: "NOTE",
            feedback_text: "Legacy feedback",
            assessment_status: "ASSESSED",
            not_assessable_reason: null,
            source_basis_label: null,
            source_basis_state: "legacy_fallback",
          },
        ],
      },
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ reviewId: "review-legacy-1" }),
    });
    const body = (await response.json()) as {
      cards: Array<{
        source_basis_label: string | null;
        source_basis_state: string;
      }>;
      detail_state: string;
      supporting_context_node_logical_ids: string[];
    };

    expect(response.status).toBe(200);
    expect(body.detail_state).toBe("legacy_fallback");
    expect(body.cards).toHaveLength(1);
    expect(body.cards[0].source_basis_label).toBeNull();
    expect(body.cards[0].source_basis_state).toBe("legacy_fallback");
    expect(body.supporting_context_node_logical_ids).toEqual([]);
  });
});
