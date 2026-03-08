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
  it("wf0067_review_detail_tracer_surfaces_source_basis_fields_in_reading_flow", async () => {
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
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "academic_profile",
                    node_title: "Academic profile",
                    criterion: "Quality",
                    criterion_description: "Quality criterion",
                    evaluation_element_name: "Peer-exceeding quality",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback text",
                    source_basis_label: "Call for Proposals (Veni 2025) §4.3.1",
                    source_basis_state: "available",
                  },
                ],
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
                  title: "Academic profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Official source basis: Call for Proposals (Veni 2025) §4.3.1",
      ),
    ).toBeInTheDocument();
  });

  it("wf0067_review_detail_tracer_unavailable_source_basis_card", async () => {
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
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "academic_profile",
                    node_title: "Academic profile",
                    criterion: "Quality",
                    criterion_description: "Quality criterion",
                    evaluation_element_name: "Peer-exceeding quality",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback text",
                    source_basis_label: null,
                    source_basis_state: "unavailable",
                  },
                ],
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
                  title: "Academic profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(
      screen.getByText("Official source basis: unavailable."),
    ).toBeInTheDocument();
  });

  it("wf0067_review_card_trust_metadata_shows_available_and_unavailable_basis", async () => {
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
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "academic_profile",
                    node_title: "Academic profile",
                    criterion: "Quality",
                    criterion_description: "Quality criterion",
                    evaluation_element_name: "Peer-exceeding quality",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback text",
                    source_basis_label: "Call for Proposals (Veni 2025) §4.3.1",
                    source_basis_state: "available",
                  },
                  {
                    id: "card-2",
                    node_expectation_id: "exp-2",
                    node_logical_id: "key_outputs",
                    node_title: "Key outputs",
                    criterion: "Quality",
                    criterion_description: "Quality criterion",
                    evaluation_element_name: "Network visibility",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Feedback text",
                    source_basis_label: null,
                    source_basis_state: "unavailable",
                  },
                ],
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
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getAllByText("Evaluation criterion: Quality")).toHaveLength(2);
    expect(screen.getByText("Peer-exceeding quality")).toBeInTheDocument();
    expect(screen.getByText("Network visibility")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Official source basis: Call for Proposals (Veni 2025) §4.3.1",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Official source basis: unavailable."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Reviewed section context: 2a. Academic Profile"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Reviewed section context: 2b. Key Outputs"),
    ).toBeInTheDocument();
  });

  it("wf0067_review_card_trust_not_assessable_label", async () => {
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
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "academic_profile",
                    node_title: "Academic profile",
                    criterion: "Quality",
                    criterion_description: "Quality criterion",
                    evaluation_element_name: "Peer-exceeding quality",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Feedback text",
                    assessment_status: "NOT_ASSESSABLE",
                    not_assessable_reason: "insufficient_evidence",
                    source_basis_label: null,
                    source_basis_state: "legacy_fallback",
                  },
                ],
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
                  title: "Academic profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(
      screen.getByText("Status: Not assessable (insufficient_evidence)"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Official source basis: unavailable (legacy fallback)."),
    ).toBeInTheDocument();
  });

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

  it("wf0060_review_detail_renders_explicit_compatibility_notes_for_legacy_erc_evidence", async () => {
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
                submitted_leaf_ids: ["proposal_summary"],
                legacy_ambiguous_container_ids: ["b1", "b2"],
                moved_legacy_node_references: ["resources_time_commitment"],
                compatibility_notes: [
                  {
                    note_type: "deprecated_container_submission",
                    node_logical_ids: ["b1", "b2"],
                    message:
                      "Deprecated container submissions are preserved as ambiguous legacy evidence.",
                  },
                  {
                    note_type: "moved_legacy_node_reference",
                    node_logical_ids: ["resources_time_commitment"],
                    message:
                      "Legacy moved-node references were mapped to corrected leaf identities.",
                  },
                  {
                    note_type: "mixed_version_review",
                    node_logical_ids: ["proposal_summary", "b1", "b2"],
                    message:
                      "Mixed-version review detected; corrected leaf IDs remain the only proven reviewed coverage.",
                  },
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
                  id: "n4",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                },
                {
                  id: "n5",
                  logical_id: "b1",
                  title: "Part B1",
                  parent_node_id: "n4",
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: false,
                },
                {
                  id: "n6",
                  logical_id: "proposal_summary",
                  title: "Proposal Summary",
                  parent_node_id: "n5",
                  node_type: "SUBSECTION",
                  order_index: 3,
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

    expect(await screen.findByText("Compatibility notes")).toBeInTheDocument();
    expect(
      screen.getByText(
        /deprecated_container_submission: Deprecated container submissions are preserved as ambiguous legacy evidence\./,
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /moved_legacy_node_reference: Legacy moved-node references were mapped to corrected leaf identities\./,
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /mixed_version_review: Mixed-version review detected; corrected leaf IDs remain the only proven reviewed coverage\./,
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: Part B / Part B1 / Proposal Summary",
    );
  });

  it("wf0060_erc_review_detail_blocks_legacy_fallback_leakage", async () => {
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
                cards: [],
                submitted_leaf_ids: ["proposal_summary"],
                legacy_ambiguous_container_ids: [],
                moved_legacy_node_references: [],
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
                  id: "n4",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                },
                {
                  id: "n5",
                  logical_id: "b1",
                  title: "Part B1",
                  parent_node_id: "n4",
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: false,
                },
                {
                  id: "n6",
                  logical_id: "proposal_summary",
                  title: "Proposal Summary",
                  parent_node_id: "n5",
                  node_type: "SUBSECTION",
                  order_index: 3,
                  has_expectations: true,
                },
                {
                  id: "n7",
                  logical_id: "b2",
                  title: "Part B2",
                  parent_node_id: "n4",
                  node_type: "SECTION",
                  order_index: 4,
                  has_expectations: false,
                },
                {
                  id: "n8",
                  logical_id: "b2_part2_scientific_proposal",
                  title: "Part II of the Scientific Proposal",
                  parent_node_id: "n7",
                  node_type: "SUBSECTION",
                  order_index: 5,
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
      "Reviewed sections: Part B / Part B1 / Proposal Summary",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: Part B / Part B2 / Part II of the Scientific Proposal",
    );
    expect(screen.queryByText("Call metadata unavailable; using review payload order.")).toBeNull();
  });

  it("wf0063_review_detail_labels_primary_evaluated_supporting_context_and_not_part_of_review", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-msca",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["excellence"],
                cards: [
                  {
                    id: "card-excellence",
                    node_expectation_id: "exp-excellence",
                    node_logical_id: "excellence",
                    node_title: "Excellence",
                    criterion: "Excellence",
                    criterion_description: "Criterion",
                    evaluation_element_name: "Element",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-msca/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "n1",
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
                {
                  id: "n2",
                  logical_id: "abstract",
                  title: "Abstract",
                  parent_node_id: null,
                  node_type: "SUBSECTION",
                  order_index: 2,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n3",
                  logical_id: "impact",
                  title: "Impact",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 3,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Primary evaluated:/)).toHaveTextContent(
      "Primary evaluated: Excellence",
    );
    expect(screen.getByText(/Supporting context:/)).toHaveTextContent(
      "Supporting context: None",
    );
    expect(
      screen.getByText(/Visible but not part of this review:/),
    ).toHaveTextContent("Visible but not part of this review: Abstract, Impact");
  });

  it("wf0064_review_detail_shows_visible_supporting_nodes_with_empty_supporting_context_ids", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-msca",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["excellence"],
                cards: [
                  {
                    id: "card-excellence",
                    node_expectation_id: "exp-excellence",
                    node_logical_id: "excellence",
                    node_title: "Excellence",
                    criterion: "Excellence",
                    criterion_description: "Criterion",
                    evaluation_element_name: "Element",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-msca/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "n1",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n2",
                  logical_id: "abstract",
                  title: "Abstract",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 2,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n3",
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 3,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Supporting context:/)).toHaveTextContent(
      "Supporting context: None",
    );
    expect(
      screen.getByText(/Visible but not part of this review:/),
    ).toHaveTextContent(
      /^Visible but not part of this review: Part B \/ Abstract$/,
    );
  });

  it("wf0064_review_detail_coverage_ignores_expectations_proxy_and_containers", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-msca",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["excellence"],
                cards: [
                  {
                    id: "card-excellence",
                    node_expectation_id: "exp-excellence",
                    node_logical_id: "excellence",
                    node_title: "Excellence",
                    criterion: "Excellence",
                    criterion_description: "Criterion",
                    evaluation_element_name: "Element",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-msca/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "n1",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n2",
                  logical_id: "abstract",
                  title: "Abstract",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 2,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n3",
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 3,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
                {
                  id: "n4",
                  logical_id: "part_c",
                  title: "Part C",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 4,
                  has_expectations: false,
                  node_role: "PRIMARY",
                },
                {
                  id: "n5",
                  logical_id: "impact",
                  title: "Impact",
                  parent_node_id: "n4",
                  node_type: "SUBSECTION",
                  order_index: 5,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: Part B / Abstract, Part C / Impact",
    );
    expect(screen.getByText(/Not reviewed sections:/)).not.toHaveTextContent("Part C,");
  });

  it("wf0064_review_detail_visible_not_reviewed_lists_supporting_only_not_all_not_reviewed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-msca",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["excellence"],
                cards: [
                  {
                    id: "card-excellence",
                    node_expectation_id: "exp-excellence",
                    node_logical_id: "excellence",
                    node_title: "Excellence",
                    criterion: "Excellence",
                    criterion_description: "Criterion",
                    evaluation_element_name: "Element",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-msca/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "n1",
                  logical_id: "part_b",
                  title: "Part B",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n2",
                  logical_id: "abstract",
                  title: "Abstract",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 2,
                  has_expectations: false,
                  node_role: "SUPPORTING",
                },
                {
                  id: "n3",
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 3,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
                {
                  id: "n4",
                  logical_id: "implementation",
                  title: "Implementation",
                  parent_node_id: "n1",
                  node_type: "SUBSECTION",
                  order_index: 4,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: Part B / Abstract, Part B / Implementation",
    );
    expect(
      screen.getByText(/Visible but not part of this review:/),
    ).toHaveTextContent(
      /^Visible but not part of this review: Part B \/ Abstract$/,
    );
  });

  it("wf0063_non_opted_in_calls_preserve_legacy_behavior", async () => {
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
                submitted_leaf_ids: ["academic_profile"],
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
                  title: "Academic Profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-2",
                  logical_id: "research_idea",
                  title: "Research Idea",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Primary evaluated:/)).toHaveTextContent(
      "Primary evaluated: Academic Profile",
    );
    expect(screen.getByText(/Supporting context:/)).toHaveTextContent(
      "Supporting context: None",
    );
  });

  it("wf0064_review_detail_preserves_legacy_behavior_without_proof_opt_in", async () => {
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
                primary_evaluated_node_logical_ids: ["academic_profile"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["academic_profile"],
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
                  title: "Academic Profile",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-2",
                  logical_id: "research_idea",
                  title: "Research Idea",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: true,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(
      screen.queryByText(/Visible but not part of this review:/),
    ).not.toBeInTheDocument();
  });

  it("wf0064_review_detail_preserves_legacy_behavior_for_msca_when_node_roles_absent", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-msca",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                submitted_leaf_ids: ["excellence"],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-msca/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-1",
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                  node_role: null,
                },
                {
                  id: "node-2",
                  logical_id: "impact",
                  title: "Impact",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: true,
                  node_role: null,
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(
      screen.queryByText(/Visible but not part of this review:/),
    ).not.toBeInTheDocument();
  });

  it("guardrail: review detail path contains no hardcoded VENI constants", () => {
    const source = fs.readFileSync("src/app/app/reviews/[reviewId]/page.tsx", "utf-8");
    const legacyLabels = ["VENI", "NODE", "LABELS"].join("_");
    const legacyOrder = ["VENI", "NODE", "ORDER"].join("_");
    expect(source.includes(legacyLabels)).toBe(false);
    expect(source.includes(legacyOrder)).toBe(false);
  });
});
