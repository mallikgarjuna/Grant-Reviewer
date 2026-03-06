import "@testing-library/jest-dom/vitest";
import fs from "node:fs";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ReviewDetailPage from "./page";

let submittedNodesParam = "academic_profile,key_outputs";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useParams: () => ({ reviewId: "review-1" }),
  useSearchParams: () => ({
    get: (key: string) => (key === "submitted_nodes" ? submittedNodesParam : null),
  }),
}));

function reviewPayload(overrides: Record<string, unknown> = {}) {
  return {
    review: {
      id: "review-1",
      status: "COMPLETED",
      overall_rating: "SUCCESS",
      overall_summary: "Structured review completed with findings.",
    },
    cards: [
      {
        id: "card-2",
        node_expectation_id: "exp-2",
        node_logical_id: "key_outputs",
        node_title: "Key outputs",
        criterion: "Quality",
        criterion_description: "Quality criterion",
        evaluation_element_name: "Key-output quality",
        expectation_guidance_note: "Show output relevance.",
        rating: "SUCCESS",
        feedback_text: "Second feedback",
      },
      {
        id: "card-1",
        node_expectation_id: "exp-1",
        node_logical_id: "academic_profile",
        node_title: "Academic profile",
        criterion: "Quality",
        criterion_description: "Quality criterion",
        evaluation_element_name: "Peer-exceeding quality",
        expectation_guidance_note: "Provide concrete evidence.",
        rating: "SUCCESS",
        feedback_text: "Feedback text",
      },
    ],
    ...overrides,
  };
}

function wf0059ProofFallbackPayload() {
  return reviewPayload({
    call_id: null,
    call_code: "erc_stg_2026_full",
    ordering_source: "review_payload_fallback",
  });
}

describe("ReviewDetailPage", () => {
  it("wf0059_review_detail_fallback_guard", async () => {
    submittedNodesParam = "b1_part1_scientific_proposal,b1_cv_track_record";
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/reviews/review-1")) {
        return new Response(JSON.stringify(wf0059ProofFallbackPayload()), {
          status: 200,
        });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
        status: 404,
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ReviewDetailPage />);

    expect(
      await screen.findByText("Call metadata unavailable; using review payload order."),
    ).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: b1_part1_scientific_proposal, b1_cv_track_record",
    );
    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/calls/")),
    ).toBe(false);
  });

  it("uses call-driven ordering and labels when call metadata is available", async () => {
    submittedNodesParam = "academic_profile,key_outputs";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-1",
                call_code: "nwo_veni_2025_preproposal",
                ordering_source: "call_nodes",
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-1/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-1",
                  logical_id: "academic_profile",
                  title: "2a. Academic Profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-2",
                  logical_id: "key_outputs",
                  title: "2b. Key Outputs",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: true,
                },
                {
                  id: "node-3",
                  logical_id: "research_idea",
                  title: "3. Research Idea",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 3,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
          status: 404,
        });
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: 2a. Academic Profile, 2b. Key Outputs",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: 3. Research Idea",
    );
    expect(screen.queryByText("Call metadata unavailable; using review payload order.")).toBeNull();

    const pageText = document.body.textContent ?? "";
    expect(pageText.indexOf("Reviewed section: 2a. Academic Profile")).toBeLessThan(
      pageText.indexOf("Reviewed section: 2b. Key Outputs"),
    );
  });

  it("wf0059_review_detail_proof_path_uses_call_linked_ordering", async () => {
    submittedNodesParam = "wrong_query_node";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc-stg",
                call_code: "erc_stg_2026_full",
                submitted_node_logical_ids: [
                  "b1_part1_scientific_proposal",
                  "b1_cv_track_record",
                ],
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-b1-cv",
                    node_expectation_id: "exp-b1-cv",
                    node_logical_id: "b1_cv_track_record",
                    node_title: "Curriculum Vitae and Track Record",
                    criterion: "Excellence",
                    criterion_description: "ERC excellence criterion",
                    evaluation_element_name: "PI evidence of creative and original thinking",
                    expectation_guidance_note: "Demonstrate track record quality.",
                    rating: "SUCCESS",
                    feedback_text: "Strong track record evidence.",
                  },
                  {
                    id: "card-b1-part1",
                    node_expectation_id: "exp-b1-part1",
                    node_logical_id: "b1_part1_scientific_proposal",
                    node_title: "Part I of the Scientific Proposal",
                    criterion: "Excellence",
                    criterion_description: "ERC excellence criterion",
                    evaluation_element_name: "Objectives are ambitious and advance frontier of knowledge",
                    expectation_guidance_note: "Show frontier ambition.",
                    rating: "SUCCESS",
                    feedback_text: "Ambition is clear.",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-stg/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-b1",
                  logical_id: "b1",
                  title: "Part B1",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-b1-part1",
                  logical_id: "b1_part1_scientific_proposal",
                  title: "Part I of the Scientific Proposal",
                  parent_node_id: "node-b1",
                  node_type: "SUBSECTION",
                  order_index: 2,
                  has_expectations: true,
                },
                {
                  id: "node-b1-cv",
                  logical_id: "b1_cv_track_record",
                  title: "Curriculum Vitae and Track Record",
                  parent_node_id: "node-b1",
                  node_type: "SUBSECTION",
                  order_index: 3,
                  has_expectations: true,
                },
                {
                  id: "node-b2",
                  logical_id: "b2",
                  title: "Part B2",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 4,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
          status: 404,
        });
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: Part I of the Scientific Proposal, Curriculum Vitae and Track Record",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: Part B1, Part B2",
    );
    expect(screen.queryByText(/wrong_query_node/)).toBeNull();

    const pageText = document.body.textContent ?? "";
    expect(pageText.indexOf("Reviewed section: Part I of the Scientific Proposal")).toBeLessThan(
      pageText.indexOf("Reviewed section: Curriculum Vitae and Track Record"),
    );
  });

  it("uses review payload fallback ordering for legacy review detail", async () => {
    submittedNodesParam = "academic_profile,key_outputs";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: null,
                call_code: null,
                ordering_source: "review_payload_fallback",
              }),
            ),
            { status: 200 },
          );
        }
        return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
          status: 404,
        });
      }),
    );

    render(<ReviewDetailPage />);

    expect(
      await screen.findByText("Call metadata unavailable; using review payload order."),
    ).toBeInTheDocument();
    const pageText = document.body.textContent ?? "";
    expect(pageText.indexOf("Reviewed section: Key outputs")).toBeLessThan(
      pageText.indexOf("Reviewed section: Academic profile"),
    );
  });

  it("shows legacy fallback note for mixed-version payload without new fields", async () => {
    submittedNodesParam = "academic_profile";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(JSON.stringify(reviewPayload()), { status: 200 });
        }
        return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
          status: 404,
        });
      }),
    );

    render(<ReviewDetailPage />);

    expect(
      await screen.findByText("Call metadata unavailable; using review payload order."),
    ).toBeInTheDocument();
    expect(screen.getByText("Coverage summary")).toBeInTheDocument();
  });

  it("guardrail: review detail path contains no hardcoded VENI constants", () => {
    const source = fs.readFileSync("src/app/app/reviews/[reviewId]/page.tsx", "utf-8");
    const legacyLabels = ["VENI", "NODE", "LABELS"].join("_");
    const legacyOrder = ["VENI", "NODE", "ORDER"].join("_");
    expect(source.includes(legacyLabels)).toBe(false);
    expect(source.includes(legacyOrder)).toBe(false);
  });
});
