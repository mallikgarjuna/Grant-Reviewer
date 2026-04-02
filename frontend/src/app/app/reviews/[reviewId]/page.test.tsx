// frontend/src/app/app/reviews/[reviewId]/page.test.tsx
import "@testing-library/jest-dom/vitest";
import fs from "node:fs";
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ReviewDetailPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useParams: () => ({ reviewId: "review-1" }),
}));

function reviewPayload(overrides: Record<string, unknown> = {}) {
  return {
    detail_mode: "legacy_cards",
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

function atomicReviewPayload(overrides: Record<string, unknown> = {}) {
  return reviewPayload({
    detail_mode: "reviewed_node_findings",
    cards: undefined,
    reviewed_nodes: [
      {
        proposal_node_id: "node-1",
        proposal_node_logical_id: "academic_profile",
        proposal_node_title: "Academic profile",
        node_role: "PRIMARY",
        findings: [
          {
            finding_id: "finding-1",
            evaluation_criterion: "Structured quality",
            evaluation_element: "Structured node quality",
            severity: "WARNING",
            assessment_status: "ASSESSED",
            issue_summary: "Academic profile needs sharper evidence.",
            evidence_basis: "The profile text stays too general.",
            actionable_feedback: "Add concrete achievements tied to the call.",
          },
        ],
      },
      {
        proposal_node_id: "node-2",
        proposal_node_logical_id: "scientific_proposal",
        proposal_node_title: "Scientific proposal",
        node_role: "PRIMARY",
        findings: [
          {
            finding_id: "finding-2",
            evaluation_criterion: "Structured quality",
            evaluation_element: "Structured node quality",
            severity: "SUCCESS",
            assessment_status: "REQUIREMENTS_MET",
            issue_summary: "Research idea requirements are met.",
            evidence_basis:
              "The idea text already addresses the evaluation element.",
            actionable_feedback:
              "Keep the current specificity in the final version.",
          },
        ],
      },
    ],
    ...overrides,
  });
}

function ercPocNodesPayload() {
  return {
    nodes: [
      {
        id: "node-1",
        logical_id: "poc_idea_innovation",
        title: "Idea innovation",
        parent_node_id: null,
        node_type: "SECTION",
        order_index: 1,
        has_expectations: true,
      },
      {
        id: "node-2",
        logical_id: "poc_approach_methodology",
        title: "Approach and methodology",
        parent_node_id: null,
        node_type: "SECTION",
        order_index: 2,
        has_expectations: true,
      },
      {
        id: "node-3",
        logical_id: "poc_pi_strategic_leadership",
        title: "PI strategic leadership",
        parent_node_id: null,
        node_type: "SECTION",
        order_index: 3,
        has_expectations: true,
      },
      {
        id: "node-4",
        logical_id: "poc_market_translation",
        title: "Market translation",
        parent_node_id: null,
        node_type: "SECTION",
        order_index: 4,
        has_expectations: true,
      },
    ],
  };
}

function mockReviewDetailFetch(
  reviewOverrides: Record<string, unknown> = {},
  nodePayload: Record<string, unknown> = ercPocNodesPayload(),
) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/bff/reviews/review-1")) {
        return new Response(
          JSON.stringify(
            reviewPayload({
              call_id: "call-erc-poc",
              call_code: "ERC-2026-PoC",
              detail_state: "call_linked",
              ordering_source: "call_nodes",
              detail_projection: {
                version: "wf0080_launch_wedge_v1",
                headline_state: "action_required",
                ordered_card_ids: ["card-1", "card-2"],
                top_action_card_ids: ["card-1", "card-2"],
                ranking_basis: "assessment_status_then_rating_then_existing_order",
              },
              ...reviewOverrides,
            }),
          ),
          { status: 200 },
        );
      }
      if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
        return new Response(JSON.stringify(nodePayload), { status: 200 });
      }
      return new Response(
        JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
        { status: 404 },
      );
    }),
  );
}

function installExportDoubles() {
  const clipboardWriteText = vi.fn().mockResolvedValue(undefined);
  Object.defineProperty(window, "isSecureContext", {
    configurable: true,
    value: true,
  });
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText: clipboardWriteText },
  });

  let downloadedBlob: Blob | null = null;
  vi.stubGlobal(
    "URL",
    Object.assign(URL, {
      createObjectURL: vi.fn((blob: Blob) => {
        downloadedBlob = blob;
        return "blob:review-export";
      }),
      revokeObjectURL: vi.fn(),
    }),
  );
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

  return {
    clipboardWriteText,
    getDownloadedBlob: () => downloadedBlob,
  };
}

describe("ReviewDetailPage", () => {
  it("wf0081_review_detail_header_surfaces_funding_call_when_available", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc-poc",
                call_code: "ERC-2026-PoC",
                detail_state: "call_linked",
                ordering_source: "call_nodes",
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
          return new Response(JSON.stringify(ercPocNodesPayload()), { status: 200 });
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
      screen.getByText((_, element) => {
        return element?.textContent === "Funding call: ERC-2026-PoC";
      }),
    ).toBeInTheDocument();
  });

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
    expect(screen.getByText("Feedback text")).toBeInTheDocument();
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
    expect(screen.getByText("Feedback text")).toBeInTheDocument();
  });

  it("wf0081_review_detail_renders_grouped_reviewed_node_findings", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              atomicReviewPayload({
                call_id: "call-erc-poc",
                call_code: "ERC-2026-PoC",
                detail_state: "call_linked",
                ordering_source: "call_nodes",
                submitted_node_logical_ids: [
                  "academic_profile",
                  "scientific_proposal",
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
          return new Response(JSON.stringify(ercPocNodesPayload()), {
            status: 200,
          });
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    expect(
      within(reviewRegion).getByText("Reviewed section: Academic profile"),
    ).toBeInTheDocument();
    expect(
      within(reviewRegion).getByText("Reviewed section: Scientific proposal"),
    ).toBeInTheDocument();
    expect(
      within(reviewRegion).getAllByText("Evaluation criterion: Structured quality"),
    ).toHaveLength(2);
    expect(
      within(reviewRegion).getAllByText("Evaluation element: Structured node quality"),
    ).toHaveLength(2);
    expect(within(reviewRegion).getAllByText("Evidence basis")).toHaveLength(2);
    expect(within(reviewRegion).getByText("Actionable feedback")).toBeInTheDocument();
    expect(within(reviewRegion).getByText("Positive guidance")).toBeInTheDocument();
    expect(
      within(reviewRegion).getByText("Requirements met"),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Criterion: Quality"),
    ).not.toBeInTheDocument();
  });

  it("wf0081_review_detail_legacy_cards_still_render_without_findings", async () => {
    mockReviewDetailFetch({
      detail_mode: "legacy_cards",
      cards: [
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
          feedback_text: "Legacy review card feedback.",
        },
      ],
      reviewed_nodes: undefined,
    });

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    expect(
      within(reviewRegion).getByText("Reviewed section: Academic profile"),
    ).toBeInTheDocument();
    expect(screen.getByText("Legacy review card feedback.")).toBeInTheDocument();
    expect(
      screen.queryByText("Evaluation element: Structured node quality"),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Requirements met")).not.toBeInTheDocument();
  });

  it("wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful", async () => {
    const { clipboardWriteText, getDownloadedBlob } = installExportDoubles();
    mockReviewDetailFetch(
      {
        ...atomicReviewPayload({
          call_id: "call-erc-poc",
          call_code: "ERC-2026-PoC",
          detail_state: "call_linked",
          ordering_source: "call_nodes",
          reviewed_nodes: [
            {
              proposal_node_id: "node-2",
              proposal_node_logical_id: "scientific_proposal",
              proposal_node_title: "Scientific proposal",
              node_role: "PRIMARY",
              findings: [
                {
                  finding_id: "finding-2",
                  evaluation_criterion: "Structured quality",
                  evaluation_element: "Structured node quality",
                  severity: "SUCCESS",
                  assessment_status: "REQUIREMENTS_MET",
                  issue_summary: "",
                  evidence_basis: "",
                  actionable_feedback:
                    "Keep the current specificity in the final version.",
                },
              ],
            },
          ],
        }),
      },
      ercPocNodesPayload(),
    );

    render(<ReviewDetailPage />);

    await screen.findByText("Reviewed section: Scientific proposal");

    fireEvent.click(
      screen.getByRole("button", { name: "Copy deterministic text" }),
    );
    expect(
      await screen.findByText("Copied deterministic review text to clipboard."),
    ).toBeInTheDocument();
    expect(clipboardWriteText).toHaveBeenCalledTimes(1);
    expect(clipboardWriteText.mock.calls[0][0]).toContain(
      "Reviewed section: Scientific proposal",
    );
    expect(clipboardWriteText.mock.calls[0][0]).toContain(
      "Evaluation criterion: Structured quality",
    );
    expect(clipboardWriteText.mock.calls[0][0]).toContain("Requirements met");
    expect(clipboardWriteText.mock.calls[0][0]).toContain(
      "Positive guidance: Keep the current specificity in the final version.",
    );
    expect(clipboardWriteText.mock.calls[0][0]).not.toContain("Cards:");
    expect(clipboardWriteText.mock.calls[0][0]).not.toContain("Criterion:");

    fireEvent.click(
      screen.getByRole("button", { name: "Download deterministic .txt" }),
    );
    expect(
      await screen.findByText("Downloaded deterministic review as .txt."),
    ).toBeInTheDocument();
    expect(await getDownloadedBlob()?.text()).toContain(
      "Reviewed section: Scientific proposal",
    );
    expect(await getDownloadedBlob()?.text()).toContain(
      "Positive guidance: Keep the current specificity in the final version.",
    );
  });

  it("wf0081_review_detail_requirements_met_render_without_empty_issue_shells", async () => {
    mockReviewDetailFetch(
      {
        ...atomicReviewPayload({
          call_id: "call-erc-poc",
          call_code: "ERC-2026-PoC",
          detail_state: "call_linked",
          ordering_source: "call_nodes",
          reviewed_nodes: [
            {
              proposal_node_id: "node-2",
              proposal_node_logical_id: "scientific_proposal",
              proposal_node_title: "Scientific proposal",
              node_role: "PRIMARY",
              findings: [
                {
                  finding_id: "finding-2",
                  evaluation_criterion: "Structured quality",
                  evaluation_element: "Structured node quality",
                  severity: "SUCCESS",
                  assessment_status: "REQUIREMENTS_MET",
                  issue_summary: "",
                  evidence_basis: "",
                  actionable_feedback:
                    "Keep the current specificity in the final version.",
                },
              ],
            },
          ],
        }),
      },
      ercPocNodesPayload(),
    );

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    expect(within(reviewRegion).getByText("Requirements met")).toBeInTheDocument();
    expect(
      within(reviewRegion).getByText("Positive guidance"),
    ).toBeInTheDocument();
    expect(
      within(reviewRegion).getByText(
        "Keep the current specificity in the final version.",
      ),
    ).toBeInTheDocument();
    expect(within(reviewRegion).queryByText("Issue summary")).not.toBeInTheDocument();
    expect(within(reviewRegion).queryByText("Evidence basis")).not.toBeInTheDocument();
  });

  it("wf0081_review_detail_legacy_copy_and_export_remain_card_based", async () => {
    const { clipboardWriteText, getDownloadedBlob } = installExportDoubles();
    mockReviewDetailFetch({
      detail_mode: "legacy_cards",
      cards: [
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
          feedback_text: "Legacy review card feedback.",
        },
      ],
      reviewed_nodes: undefined,
    });

    render(<ReviewDetailPage />);

    await screen.findByText("Legacy review card feedback.");

    fireEvent.click(
      screen.getByRole("button", { name: "Copy deterministic text" }),
    );
    expect(
      await screen.findByText("Copied deterministic review text to clipboard."),
    ).toBeInTheDocument();
    expect(clipboardWriteText.mock.calls[0][0]).toContain("Cards:");
    expect(clipboardWriteText.mock.calls[0][0]).toContain("Criterion: Quality");
    expect(clipboardWriteText.mock.calls[0][0]).not.toContain(
      "Reviewed section: Academic profile",
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Download deterministic .txt" }),
    );
    expect(await getDownloadedBlob()?.text()).toContain("Cards:");
    expect(await getDownloadedBlob()?.text()).toContain("Criterion: Quality");
  });

  it("wf0081_review_detail_missing_detail_mode_fails_closed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          const payload = reviewPayload();
          delete (payload as { detail_mode?: string }).detail_mode;
          return new Response(JSON.stringify(payload), { status: 200 });
        }
        return new Response(
          JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }),
          { status: 404 },
        );
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Unable to load review")).toBeInTheDocument();
    expect(
      screen.getByText("Review detail payload is missing an explicit detail mode."),
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
    expect(screen.getAllByText("Feedback text")).toHaveLength(2);
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
    expect(screen.getByText("Feedback text")).toBeInTheDocument();
  });

  it("wf0067_review_detail_boundary_no_generated_cards_distinct_from_visible_not_reviewed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-1",
                call_code: "erc_stg_2026_full",
                ordering_source: "call_nodes",
                cards: [],
                primary_evaluated_node_logical_ids: [],
                supporting_context_node_logical_ids: [],
                visible_not_reviewed_node_logical_ids: [
                  "b1_part1_scientific_proposal",
                ],
                no_generated_cards_node_logical_ids: ["proposal_summary"],
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
                  logical_id: "proposal_summary",
                  title: "Proposal Summary",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-2",
                  logical_id: "b1_part1_scientific_proposal",
                  title: "Part B1 Scientific Proposal",
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
      screen.getByText(
        "Visible but not reviewed sections: Part B1 Scientific Proposal",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No generated card sections: Proposal Summary"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Visible but not reviewed section: Part B1 Scientific Proposal"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No generated cards section: Proposal Summary"),
    ).toBeInTheDocument();
  });

  it("wf0067_review_detail_boundary_explicit_empty_buckets_do_not_fallback_to_inference", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-1",
                call_code: "MSCA-PF-2025",
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "excellence",
                    node_title: "Excellence",
                    criterion: "Excellence",
                    criterion_description: "Criterion description",
                    evaluation_element_name: "Quality and credibility",
                    expectation_guidance_note: null,
                    rating: "SUCCESS",
                    feedback_text: "Feedback text",
                    source_basis_label: "Official source",
                    source_basis_state: "available",
                  },
                ],
                primary_evaluated_node_logical_ids: ["excellence"],
                supporting_context_node_logical_ids: [],
                visible_not_reviewed_node_logical_ids: [],
                no_generated_cards_node_logical_ids: [],
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
                  logical_id: "excellence",
                  title: "Excellence",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                  node_role: "PRIMARY",
                },
                {
                  id: "node-2",
                  logical_id: "impact",
                  title: "Impact",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 2,
                  has_expectations: true,
                  node_role: "SUPPORTING",
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
      screen.queryByText(/Visible but not reviewed sections:/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/No generated card sections:/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Visible but not reviewed section:/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/No generated cards section:/),
    ).not.toBeInTheDocument();
  });

  it("wf0067_review_detail_boundary_limitation_copy_for_legacy_and_mixed_version", async () => {
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
                detail_state: "legacy_fallback",
                ordering_source: "review_payload_fallback",
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: null,
                    node_title: "Legacy section",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Legacy element",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Legacy feedback",
                    source_basis_label: null,
                    source_basis_state: "legacy_fallback",
                  },
                ],
                compatibility_notes: [
                  {
                    note_type: "mixed_version_review",
                    node_logical_ids: ["proposal_summary", "legacy_node"],
                    message:
                      "Mixed-version review detected; corrected leaf IDs remain the only proven reviewed coverage.",
                  },
                ],
              }),
            ),
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
      screen.getByText("Call metadata unavailable; using review payload order."),
    ).toBeInTheDocument();
    expect(screen.getByText("Compatibility notes")).toBeInTheDocument();
    expect(
      screen.getByText(
        /mixed_version_review: Mixed-version review detected; corrected leaf IDs remain the only proven reviewed coverage\./,
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Legacy feedback")).toBeInTheDocument();
  });

  it.each([
    "nwo_veni_2025_preproposal",
    "erc_stg_2026_full",
    "MSCA-PF-2025",
  ])(
    "wf0067_review_detail_representative_calls_render_trust_surface_%s",
    async (callCode) => {
      vi.stubGlobal(
        "fetch",
        vi.fn(async (input: RequestInfo | URL) => {
          const url = String(input);
          if (url.includes("/api/bff/reviews/review-1")) {
            return new Response(
              JSON.stringify(
                reviewPayload({
                  call_id: "call-1",
                  call_code: callCode,
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
                      source_basis_label: "Official source",
                      source_basis_state: "available",
                    },
                  ],
                  supporting_context_node_logical_ids: [],
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
      expect(screen.getByText("Feedback text")).toBeInTheDocument();
      expect(screen.getByText("Supporting context: None")).toBeInTheDocument();
    },
  );

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
      screen.getByText(/Visible but not reviewed sections:/),
    ).toHaveTextContent("Visible but not reviewed sections: Abstract");
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
      screen.getByText(/Visible but not reviewed sections:/),
    ).toHaveTextContent(
      /^Visible but not reviewed sections: Part B \/ Abstract$/,
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
      screen.getByText(/Visible but not reviewed sections:/),
    ).toHaveTextContent(
      /^Visible but not reviewed sections: Part B \/ Abstract$/,
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
      screen.queryByText(/Visible but not reviewed sections:/),
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
      screen.queryByText(/Visible but not reviewed sections:/),
    ).not.toBeInTheDocument();
  });

  it("guardrail: review detail path contains no hardcoded VENI constants", () => {
    const source = fs.readFileSync("src/app/app/reviews/[reviewId]/page.tsx", "utf-8");
    const legacyLabels = ["VENI", "NODE", "LABELS"].join("_");
    const legacyOrder = ["VENI", "NODE", "ORDER"].join("_");
    expect(source.includes(legacyLabels)).toBe(false);
    expect(source.includes(legacyOrder)).toBe(false);
  });

  it("wf0079_review_detail_renders_optional_companion_block", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc-poc",
                call_code: "ERC-2026-PoC",
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "poc_idea_innovation",
                    node_title: "Idea innovation",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Breakthrough innovation potential",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Deterministic innovation feedback.",
                    synthesized_companion_text:
                      "Additive innovation companion guidance.",
                    source_basis_label: "Official ERC PoC source",
                    source_basis_state: "available",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-1",
                  logical_id: "poc_idea_innovation",
                  title: "Idea innovation",
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
    expect(screen.getByText("Deterministic innovation feedback.")).toBeInTheDocument();
    expect(screen.getByText("LLM companion guidance")).toBeInTheDocument();
    expect(
      screen.getByText("Additive innovation companion guidance."),
    ).toBeInTheDocument();
  });

  it("wf0079_review_detail_copy_and_download_remain_deterministic_only", async () => {
    const clipboardWriteText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(window, "isSecureContext", {
      configurable: true,
      value: true,
    });
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: clipboardWriteText },
    });
    let downloadedBlob: Blob | null = null;
    vi.stubGlobal(
      "URL",
      Object.assign(URL, {
        createObjectURL: vi.fn((blob: Blob) => {
          downloadedBlob = blob;
          return "blob:review-export";
        }),
        revokeObjectURL: vi.fn(),
      }),
    );
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc-poc",
                call_code: "ERC-2026-PoC",
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "poc_idea_innovation",
                    node_title: "Idea innovation",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Breakthrough innovation potential",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Deterministic innovation feedback.",
                    synthesized_companion_text:
                      "Additive innovation companion guidance.",
                    source_basis_label: "Official ERC PoC source",
                    source_basis_state: "available",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-1",
                  logical_id: "poc_idea_innovation",
                  title: "Idea innovation",
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

    fireEvent.click(
      screen.getByRole("button", { name: "Copy deterministic text" }),
    );
    expect(
      await screen.findByText("Copied deterministic review text to clipboard."),
    ).toBeInTheDocument();
    expect(clipboardWriteText).toHaveBeenCalledTimes(1);
    expect(clipboardWriteText.mock.calls[0][0]).toContain(
      "Deterministic innovation feedback.",
    );
    expect(clipboardWriteText.mock.calls[0][0]).not.toContain(
      "Additive innovation companion guidance.",
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Download deterministic .txt" }),
    );
    expect(
      await screen.findByText("Downloaded deterministic review as .txt."),
    ).toBeInTheDocument();
    expect(downloadedBlob).not.toBeNull();
    expect(await downloadedBlob?.text()).toContain(
      "Deterministic innovation feedback.",
    );
    expect(await downloadedBlob?.text()).not.toContain(
      "Additive innovation companion guidance.",
    );
  });

  it("wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify(
              reviewPayload({
                call_id: "call-erc-poc",
                call_code: "ERC-2026-PoC",
                ordering_source: "call_nodes",
                cards: [
                  {
                    id: "card-1",
                    node_expectation_id: "exp-1",
                    node_logical_id: "poc_idea_innovation",
                    node_title: "Idea innovation",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Breakthrough innovation potential",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Deterministic innovation feedback.",
                    synthesized_companion_text:
                      "Additive innovation companion guidance.",
                    source_basis_label: "Official ERC PoC source",
                    source_basis_state: "available",
                  },
                  {
                    id: "card-2",
                    node_expectation_id: "exp-2",
                    node_logical_id: "poc_pi_strategic_leadership",
                    node_title: "PI strategic leadership",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Leadership",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Deterministic leadership feedback.",
                    synthesized_companion_text: null,
                    source_basis_label: "Official ERC PoC source",
                    source_basis_state: "available",
                  },
                ],
              }),
            ),
            { status: 200 },
          );
        }
        if (url.includes("/api/bff/calls/call-erc-poc/nodes")) {
          return new Response(
            JSON.stringify({
              nodes: [
                {
                  id: "node-1",
                  logical_id: "poc_idea_innovation",
                  title: "Idea innovation",
                  parent_node_id: null,
                  node_type: "SECTION",
                  order_index: 1,
                  has_expectations: true,
                },
                {
                  id: "node-2",
                  logical_id: "poc_pi_strategic_leadership",
                  title: "PI strategic leadership",
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
    expect(screen.getAllByText("LLM companion guidance")).toHaveLength(1);
    expect(
      screen.getByText("Deterministic leadership feedback."),
    ).toBeInTheDocument();

    cleanup();

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
                detail_state: "legacy_fallback",
                ordering_source: "review_payload_fallback",
                cards: [
                  {
                    id: "legacy-card-1",
                    node_expectation_id: "legacy-exp-1",
                    node_logical_id: null,
                    node_title: "Legacy section",
                    criterion: "Excellence",
                    criterion_description: "Excellence criterion",
                    evaluation_element_name: "Legacy element",
                    expectation_guidance_note: null,
                    rating: "NOTE",
                    feedback_text: "Legacy deterministic feedback.",
                    synthesized_companion_text: null,
                    source_basis_label: null,
                    source_basis_state: "legacy_fallback",
                  },
                ],
              }),
            ),
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
      screen.queryByText("LLM companion guidance"),
    ).not.toBeInTheDocument();
    expect(screen.getByText("Legacy deterministic feedback.")).toBeInTheDocument();
  });

  it("wf0080_review_detail_groups_all_findings_by_reviewed_section", async () => {
    mockReviewDetailFetch({
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: "Lead with the breakthrough claim.",
          rating: "NOTE",
          feedback_text: "Innovation feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
        {
          id: "card-2",
          node_expectation_id: "exp-2",
          node_logical_id: "poc_approach_methodology",
          node_title: "Approach and methodology",
          criterion: "Excellence",
          criterion_description: "Approach criterion",
          evaluation_element_name: "Methodology",
          expectation_guidance_note: "Clarify feasibility.",
          rating: "WARNING",
          feedback_text: "Methodology feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
        {
          id: "card-3",
          node_expectation_id: "exp-3",
          node_logical_id: "poc_pi_strategic_leadership",
          node_title: "PI strategic leadership",
          criterion: "Excellence",
          criterion_description: "Leadership criterion",
          evaluation_element_name: "Leadership",
          expectation_guidance_note: "Show delivery plan.",
          rating: "CRITICAL",
          feedback_text: "Leadership feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
        {
          id: "card-4",
          node_expectation_id: "exp-4",
          node_logical_id: "poc_market_translation",
          node_title: "Market translation",
          criterion: "Excellence",
          criterion_description: "Translation criterion",
          evaluation_element_name: "Translation",
          expectation_guidance_note: "Show adoption path.",
          rating: "SUCCESS",
          feedback_text: "Translation feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "action_required",
        ordered_card_ids: ["card-3", "card-2", "card-1", "card-4"],
        top_action_card_ids: ["card-3", "card-2", "card-1"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
    });

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    const sectionGroups = within(reviewRegion).getAllByRole("heading", {
      level: 2,
      name: /Reviewed section:/,
    });
    expect(sectionGroups).toHaveLength(4);
    expect(sectionGroups[0]).toHaveTextContent(
      "Reviewed section: Idea innovation",
    );
    expect(sectionGroups[1]).toHaveTextContent(
      "Reviewed section: Approach and methodology",
    );
    expect(sectionGroups[2]).toHaveTextContent(
      "Reviewed section: PI strategic leadership",
    );
    expect(sectionGroups[3]).toHaveTextContent(
      "Reviewed section: Market translation",
    );
    expect(screen.queryByText("Top actions")).not.toBeInTheDocument();
    expect(screen.queryByText("Other findings")).not.toBeInTheDocument();
    expect(screen.getByText("Translation feedback")).toBeInTheDocument();
  });

  it("wf0080_review_detail_falls_back_to_payload_grouping_when_projection_is_missing", async () => {
    mockReviewDetailFetch({
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: null,
          rating: "NOTE",
          feedback_text: "Innovation feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
      detail_projection: undefined,
    });

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    expect(
      within(reviewRegion).getByText("Reviewed section: Idea innovation"),
    ).toBeInTheDocument();
    expect(screen.queryByText("Prioritized launch view unavailable")).not.toBeInTheDocument();
  });

  it("wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success", async () => {
    mockReviewDetailFetch({
      review: {
        id: "review-1",
        status: "COMPLETED",
        overall_rating: "SUCCESS",
        overall_summary: "All clear.",
      },
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: "Lead with the breakthrough claim.",
          rating: "SUCCESS",
          feedback_text: "Innovation feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "no_critical_blockers",
        ordered_card_ids: ["card-1"],
        top_action_card_ids: ["card-1"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
    });

    render(<ReviewDetailPage />);

    expect(await screen.findByText("No critical blockers found")).toBeInTheDocument();
    expect(screen.queryByText("Action required")).not.toBeInTheDocument();
  });

  it("wf0080_review_detail_renders_deterministic_feedback_as_bullets", async () => {
    mockReviewDetailFetch({
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: "Lead with the breakthrough claim.",
          rating: "WARNING",
          feedback_text:
            "Lead with the breakthrough claim. Show why the idea is high risk.",
        },
      ],
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "action_required",
        ordered_card_ids: ["card-1"],
        top_action_card_ids: ["card-1"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
    });

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    const groupedCards = within(reviewRegion).getAllByTestId(/^review-card-/);
    const bulletItems = within(groupedCards[0]).getAllByRole("listitem");
    expect(bulletItems).toHaveLength(2);
    expect(bulletItems[0]).toHaveTextContent("Lead with the breakthrough claim.");
    expect(bulletItems[1]).toHaveTextContent("Show why the idea is high risk.");
  });

  it("wf0080_review_detail_removes_supporting_evidence_block", async () => {
    mockReviewDetailFetch({
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: "Lead with the breakthrough claim.",
          rating: "WARNING",
          feedback_text: "Innovation feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
        {
          id: "card-2",
          node_expectation_id: "exp-2",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Approach criterion",
          evaluation_element_name: "Methodology",
          expectation_guidance_note: "Clarify feasibility.",
          rating: "NOTE",
          feedback_text: "Methodology feedback",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "action_required",
        ordered_card_ids: ["card-1", "card-2"],
        top_action_card_ids: ["card-1"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
    });

    render(<ReviewDetailPage />);

    const reviewRegion = await screen.findByRole("region", {
      name: "Review feedback by section",
    });
    const groupedCards = within(reviewRegion).getAllByTestId(/^review-card-/);
    expect(
      within(groupedCards[0]).queryByText("Supporting evidence"),
    ).not.toBeInTheDocument();
    expect(
      within(groupedCards[0]).queryByText("Official source basis: Official ERC PoC source"),
    ).not.toBeInTheDocument();
    expect(
      within(groupedCards[1]).queryByText("Supporting evidence"),
    ).not.toBeInTheDocument();
  });

  it(
    "wf0080_review_detail_handles_pending_timeout_and_failure_honestly",
    async () => {
      vi.useFakeTimers();
      try {
        mockReviewDetailFetch({
          review: {
            id: "review-1",
            status: "PENDING",
            overall_rating: null,
            overall_summary: null,
          },
          cards: [],
          detail_projection: {
            version: "wf0080_launch_wedge_v1",
            headline_state: "action_required",
            ordered_card_ids: [],
            top_action_card_ids: [],
            ranking_basis: "assessment_status_then_rating_then_existing_order",
          },
        });

        render(<ReviewDetailPage />);

        await act(async () => {
          await Promise.resolve();
        });
        expect(screen.getByText(/Still processing\./)).toBeInTheDocument();
        await act(async () => {
          await vi.advanceTimersByTimeAsync(90_000);
        });
        expect(
          screen.getByText(/Still processing after 90 seconds/),
        ).toBeInTheDocument();
      } finally {
        vi.useRealTimers();
        cleanup();
      }

      mockReviewDetailFetch({
        review: {
          id: "review-1",
          status: "FAILED",
          overall_rating: null,
          overall_summary: null,
        },
        cards: [],
      });

      render(<ReviewDetailPage />);

      expect(await screen.findByText("Review Failed")).toBeInTheDocument();
      expect(
        screen.getByText("Retry uses your previous draft with a new idempotency key."),
      ).toBeInTheDocument();
    },
    15000,
  );

  it("wf0080_review_detail_export_copy_stays_truthful_about_projection_scope", async () => {
    const clipboardWriteText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(window, "isSecureContext", {
      configurable: true,
      value: true,
    });
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: clipboardWriteText },
    });
    mockReviewDetailFetch({
      cards: [
        {
          id: "card-1",
          node_expectation_id: "exp-1",
          node_logical_id: "poc_idea_innovation",
          node_title: "Idea innovation",
          criterion: "Excellence",
          criterion_description: "Innovation criterion",
          evaluation_element_name: "Innovation",
          expectation_guidance_note: null,
          rating: "NOTE",
          feedback_text: "Innovation feedback",
          synthesized_companion_text: "Companion guidance",
          assessment_status: "ASSESSED",
          source_basis_label: "Official ERC PoC source",
          source_basis_state: "available",
        },
      ],
      detail_projection: {
        version: "wf0080_launch_wedge_v1",
        headline_state: "action_required",
        ordered_card_ids: ["card-1"],
        top_action_card_ids: ["card-1"],
        ranking_basis: "assessment_status_then_rating_then_existing_order",
      },
    });

    render(<ReviewDetailPage />);

    await screen.findByText("Innovation feedback");
    fireEvent.click(screen.getByRole("button", { name: "Copy deterministic text" }));
    expect(
      await screen.findByText(
        "Copy/download include deterministic review text only. Additive companion guidance is not included in this export.",
      ),
    ).toBeInTheDocument();
    expect(clipboardWriteText).toHaveBeenCalledTimes(1);
    expect(clipboardWriteText.mock.calls[0][0]).toContain(
      "Additive companion guidance is not included in this export.",
    );
  });
});
