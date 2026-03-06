// frontend/src/app/app/reviews/[reviewId]/page.test.tsx
import "@testing-library/jest-dom/vitest";
import fs from "node:fs";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ReviewDetailPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useParams: () => ({ reviewId: "review-1" }),
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
    submitted_leaf_ids: ["academic_profile", "key_outputs"],
    legacy_ambiguous_container_ids: [],
    moved_legacy_node_references: [],
    ...overrides,
  };
}

describe("ReviewDetailPage", () => {
  it("uses call-driven ordering and labels when call metadata is available", async () => {
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

  it("uses review payload fallback ordering for legacy review detail", async () => {
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

  it("wf0060_review_detail_uses_corrected_leaf_grouping_and_ordering", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc",
                call_code: "erc_stg_2026_full",
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-summary",
                    node_expectation_id: "exp-summary",
                    node_logical_id: "proposal_summary",
                    node_title: "Proposal Summary",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Project quality",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Strong summary.",
                  },
                ],
                submitted_leaf_ids: [
                  "resources_time_commitment",
                  "proposal_summary",
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "n1",
                  logical_id: "part_a",
                  title: "Part A",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                },
                {
                  id: "n2",
                  logical_id: "budget",
                  title: "Budget",
                  parent_node_id: "n1",
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: false,
                },
                {
                  id: "n3",
                  logical_id: "resources_time_commitment",
                  title: "Resources and Time Commitment",
                  parent_node_id: "n2",
                  node_type: "SECTION",
                  order_index: 3,
                  has_expectations: true,
                },
                {
                  id: "n4",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 4,
                  has_expectations: false,
                },
                {
                  id: "n5",
                  logical_id: "b1",
                  title: "Part B1",
                  parent_node_id: "n4",
                  node_type: "SECTION",
                  order_index: 5,
                  has_expectations: false,
                },
                {
                  id: "n6",
                  logical_id: "proposal_summary",
                  title: "Proposal Summary",
                  parent_node_id: "n5",
                  node_type: "SUBSECTION",
                  order_index: 6,
                  has_expectations: true,
                },
                {
                  id: "n7",
                  logical_id: "b2",
                  title: "Part B2",
                  parent_node_id: "n4",
                  node_type: "SECTION",
                  order_index: 7,
                  has_expectations: false,
                },
                {
                  id: "n8",
                  logical_id: "b2_part2_scientific_proposal",
                  title: "Part II of the Scientific Proposal",
                  parent_node_id: "n7",
                  node_type: "SUBSECTION",
                  order_index: 8,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          {
            status: 404,
          },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: Part A / Budget / Resources and Time Commitment, Part B / Part B1 / Proposal Summary",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: Part B / Part B2 / Part II of the Scientific Proposal",
    );
    expect(screen.getByText("Reviewed section: Part B / Part B1 / Proposal Summary")).toBeInTheDocument();
  });

  it("guardrail: review detail path contains no hardcoded VENI constants", () => {
    const source = fs.readFileSync("src/app/app/reviews/[reviewId]/page.tsx", "utf-8");
    const legacyLabels = ["VENI", "NODE", "LABELS"].join("_");
    const legacyOrder = ["VENI", "NODE", "ORDER"].join("_");
    expect(source.includes(legacyLabels)).toBe(false);
    expect(source.includes(legacyOrder)).toBe(false);
  });
});
