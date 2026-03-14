// frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ReviewDetailResponse } from "@/lib/bff/types";

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
        visible_not_reviewed_node_logical_ids: ["research_idea"],
        no_generated_cards_node_logical_ids: ["academic_profile"],
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
      visible_not_reviewed_node_logical_ids: string[];
      no_generated_cards_node_logical_ids: string[];
    };

    expect(response.status).toBe(200);
    expect(body.cards[0].source_basis_label).toBe(
      "Call for Proposals (Veni 2025) §4.3.1",
    );
    expect(body.cards[0].source_basis_state).toBe("available");
    expect(body.cards[1].source_basis_label).toBeNull();
    expect(body.cards[1].source_basis_state).toBe("unavailable");
    expect(body.supporting_context_node_logical_ids).toEqual([]);
    expect(body.visible_not_reviewed_node_logical_ids).toEqual(["research_idea"]);
    expect(body.no_generated_cards_node_logical_ids).toEqual(["academic_profile"]);
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
        visible_not_reviewed_node_logical_ids: [],
        no_generated_cards_node_logical_ids: [],
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
      visible_not_reviewed_node_logical_ids: string[];
      no_generated_cards_node_logical_ids: string[];
    };

    expect(response.status).toBe(200);
    expect(body.detail_state).toBe("legacy_fallback");
    expect(body.cards).toHaveLength(1);
    expect(body.cards[0].source_basis_label).toBeNull();
    expect(body.cards[0].source_basis_state).toBe("legacy_fallback");
    expect(body.supporting_context_node_logical_ids).toEqual([]);
    expect(body.visible_not_reviewed_node_logical_ids).toEqual([]);
    expect(body.no_generated_cards_node_logical_ids).toEqual([]);
  });

  it("wf0067_bff_review_detail_preserves_backend_detail_state_verbatim", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    getReviewMock.mockResolvedValue({
      ok: true,
      data: {
        call_id: "call-erc",
        call_code: "erc_stg_2026_full",
        detail_state: "proof_path_unmapped",
        ordering_source: "call_nodes",
        submitted_node_logical_ids: ["node-1"],
        submitted_leaf_ids: ["node-1"],
        primary_evaluated_node_logical_ids: ["node-1"],
        supporting_context_node_logical_ids: [],
        visible_not_reviewed_node_logical_ids: [],
        no_generated_cards_node_logical_ids: [],
        unmapped_node_logical_ids: [],
        review: {
          id: "review-proof-path",
          status: "COMPLETED",
          overall_rating: "NOTE",
          overall_summary: "Summary",
        },
        cards: [],
      },
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ reviewId: "review-proof-path" }),
    });
    const body = (await response.json()) as {
      detail_state: string;
      unmapped_node_logical_ids: string[];
    };

    expect(response.status).toBe(200);
    expect(body.detail_state).toBe("proof_path_unmapped");
    expect(body.unmapped_node_logical_ids).toEqual([]);
  });

  it.each([
    "nwo_veni_2025_preproposal",
    "erc_stg_2026_full",
    "MSCA-PF-2025",
  ])(
    "wf0067_bff_review_detail_representative_calls_preserve_trust_fields_%s",
    async (callCode) => {
      authMock.mockResolvedValue({ userId: "user-1" });
      getReviewMock.mockResolvedValue({
        ok: true,
        data: {
          call_id: `call-${callCode}`,
          call_code: callCode,
          ordering_source: "call_nodes",
          submitted_node_logical_ids: ["node-1"],
          submitted_leaf_ids: ["node-1"],
          primary_evaluated_node_logical_ids: ["node-1"],
          supporting_context_node_logical_ids: [],
          visible_not_reviewed_node_logical_ids: [],
          no_generated_cards_node_logical_ids: [],
          review: {
            id: `review-${callCode}`,
            status: "COMPLETED",
            overall_rating: "SUCCESS",
            overall_summary: "Summary",
          },
          cards: [
            {
              id: "card-1",
              node_expectation_id: "expectation-1",
              node_logical_id: "node-1",
              node_title: "Node 1",
              criterion: "Quality",
              criterion_description: "Quality criterion",
              evaluation_element_name: "Element 1",
              expectation_guidance_note: null,
              rating: "SUCCESS",
              feedback_text: "Feedback",
              source_basis_label: "Official source",
              source_basis_state: "available",
            },
          ],
        },
      });

      const { GET } = await import("./route");
      const response = await GET(new Request("http://localhost"), {
        params: Promise.resolve({ reviewId: `review-${callCode}` }),
      });
      const body = (await response.json()) as {
        call_code: string;
        cards: Array<{ source_basis_state: string; source_basis_label: string | null }>;
        supporting_context_node_logical_ids: string[];
      };

      expect(response.status).toBe(200);
      expect(body.call_code).toBe(callCode);
      expect(body.cards[0].source_basis_state).toBe("available");
      expect(body.cards[0].source_basis_label).toBe("Official source");
      expect(body.supporting_context_node_logical_ids).toEqual([]);
    },
  );

  it("wf0079_bff_review_detail_preserves_optional_companion_text", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    const backendPayload: ReviewDetailResponse = {
      call_id: "call-erc-poc",
      call_code: "ERC-2026-PoC",
      detail_state: "call_linked",
      ordering_source: "call_nodes",
      submitted_node_logical_ids: ["poc_idea_innovation", "poc_pi_strategic_leadership"],
      submitted_leaf_ids: ["poc_idea_innovation", "poc_pi_strategic_leadership"],
      primary_evaluated_node_logical_ids: [
        "poc_idea_innovation",
        "poc_pi_strategic_leadership",
      ],
      supporting_context_node_logical_ids: [],
      visible_not_reviewed_node_logical_ids: [],
      no_generated_cards_node_logical_ids: [],
      review: {
        id: "review-wf0079",
        status: "COMPLETED",
        overall_rating: "NOTE",
        overall_summary: "Summary",
      },
      cards: [
        {
          id: "card-1",
          node_expectation_id: "expectation-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Excellence criterion",
          evaluation_element_name: "Breakthrough innovation potential",
          expectation_guidance_note: null,
          rating: "NOTE",
          feedback_text: "Deterministic innovation feedback.",
          synthesized_companion_text: "Additive innovation companion guidance.",
          assessment_status: "ASSESSED",
          not_assessable_reason: null,
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
        {
          id: "card-2",
          node_expectation_id: "expectation-2",
          node_logical_id: "poc_pi_strategic_leadership",
          node_title: "PI strategic leadership",
          criterion: "Excellence",
          criterion_description: "Excellence criterion",
          evaluation_element_name: "Leadership",
          expectation_guidance_note: null,
          rating: "NOTE",
          feedback_text: "Deterministic leadership feedback.",
          synthesized_companion_text: null,
          assessment_status: "ASSESSED",
          not_assessable_reason: null,
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
    };
    getReviewMock.mockResolvedValue({
      ok: true,
      data: backendPayload,
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ reviewId: "review-wf0079" }),
    });
    const body = (await response.json()) as ReviewDetailResponse;

    expect(response.status).toBe(200);
    expect(body.cards[0].synthesized_companion_text).toBe(
      "Additive innovation companion guidance.",
    );
    expect(body.cards[1].synthesized_companion_text).toBeNull();
  });

  it("wf0080_bff_review_detail_preserves_backend_projection", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    const backendPayload: ReviewDetailResponse = {
      call_id: "call-erc-poc",
      call_code: "ERC-2026-PoC",
      detail_state: "call_linked",
      ordering_source: "call_nodes",
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "action_required",
        ordered_card_ids: ["card-2", "card-1", "card-3"],
        top_action_card_ids: ["card-2", "card-1", "card-3"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
      submitted_node_logical_ids: ["poc_idea_innovation"],
      submitted_leaf_ids: ["poc_idea_innovation"],
      primary_evaluated_node_logical_ids: ["poc_idea_innovation"],
      supporting_context_node_logical_ids: [],
      visible_not_reviewed_node_logical_ids: [],
      no_generated_cards_node_logical_ids: [],
      review: {
        id: "review-wf0080",
        status: "COMPLETED",
        overall_rating: "WARNING",
        overall_summary: "Summary",
      },
      cards: [],
    };
    getReviewMock.mockResolvedValue({
      ok: true,
      data: backendPayload,
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ reviewId: "review-wf0080" }),
    });
    const body = (await response.json()) as ReviewDetailResponse;

    expect(response.status).toBe(200);
    expect(body.detail_projection).toEqual(backendPayload.detail_projection);
  });
});
